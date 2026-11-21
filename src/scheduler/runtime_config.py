"""Operator-only configuration and health-file adapter. Never exposed to customer HTTP."""
import hashlib
import json
import os
from pathlib import Path
import re
from datetime import date,datetime,time as day_time
from zoneinfo import ZoneInfo

from src.scheduler.resource_queue import Customer,Node,ResourceQueue,number


def load_config(path):
    data=json.loads(Path(path).read_text(encoding='utf-8'))
    customers=[];tokens={}
    for item in data['customers']:
        item=dict(item);variable=item.pop('token_env',None)
        customer=Customer(**item);customers.append(customer)
        if variable:
            if not isinstance(variable,str) or not re.fullmatch(r'[A-Z][A-Z0-9_]{0,79}',variable):raise ValueError('Ungültiger Token-Variablenname.')
            token=os.environ.get(variable,'')
            if len(token)<40:raise ValueError('Kundenschlüssel fehlt oder ist zu kurz; Wert wird nicht ausgegeben.')
            tokens[customer.id]=token
    return ResourceQueue([Node(**item) for item in data['nodes']],customers,**data.get('scheduler',{})),tokens


def apply_service_plan(queue,report,approve_dates=False):
    """Bridge to our service ML output. Synthetic risk is always advisory.

    Explicitly approved individual and shared calendar dates are combined by min;
    completing a job never resets either. Approval is an operator assertion.
    """
    planned={};individual={};common={};risk_updates={}
    def epoch(value):
        return datetime.combine(date.fromisoformat(value),day_time(),ZoneInfo('Europe/Zurich')).timestamp()
    for row in report.get('servers',[]):
        if row['server_id'] in queue.nodes:
            planned[row['server_id']]=epoch(row['next_routine_date'])
            individual[row['server_id']]=planned[row['server_id']]
            risk_updates[row['server_id']]=number(row['risk_next_30_days_without_service'],'30-Tage-Risiko',0,1)
    shared=report.get('site_service',{})
    dates=shared.get('scheduled_dates',[])
    if dates:
        due=min(epoch(d) for d in dates)
        for node in queue.nodes.values():
            if node.site_id==shared.get('site_id'):
                planned[node.id]=min(planned.get(node.id,float('inf')),due)
                common[node.id]=due
    if not planned:raise ValueError('Serviceplan passt zu keinem konfigurierten Server oder Standort.')
    validated=bool(approve_dates and not report.get('synthetic',True) and report.get('validated_for_real_hardware') is True)
    with queue.lock:
        for nid,due in planned.items():
            node=queue.nodes[nid]
            node.advisory='Serviceplan vorhanden; Termine '+('vom Betreiber übernommen' if approve_dates else 'noch nicht übernommen')
            if approve_dates:
                if nid in individual:node.server_service_due_at=individual[nid]
                if nid in common:node.cooling_service_due_at=common[nid]
            if nid in risk_updates:
                value=risk_updates[nid]
                node.advisory+=f'; 30-Tage-Risiko {value:.3f}'+('' if validated else ' unvalidiert, nur Hinweis')
                if validated and value>=queue.risk_threshold:node.maintenance='drain'
    return dict(matched_nodes=len(planned),calendar_applied=approve_dates,risk_validated=validated)


class HealthFile:
    """Validated states from a trusted operator-local file; stale input never refreshed artificially."""
    def __init__(self,path,queue):
        self.path=Path(path);self.queue=queue;self.digest=None
        for node in queue.nodes.values():node.require_health=True;node.last_health_at=None

    def poll(self):
        try:
            raw=self.path.read_bytes()
            digest=hashlib.sha256(raw).hexdigest()
            if digest==self.digest:return
            data=json.loads(raw);observed=number(data['observed_at'],'observed_at',0,1e12)
            if observed>self.queue.clock()+5:raise ValueError('Gesundheitsmeldung liegt in der Zukunft.')
            rows=data['nodes']
            if len({r['id'] for r in rows})!=len(rows):raise ValueError('Doppelte Gesundheitsmeldung.')
            # Validate the complete document before applying any state change.
            for row in rows:
                if set(row)-{'id','critical','clear','empirically_validated','risk','maintenance_due_at','powered','gpu_temp_c','flow_lpm'}:
                    raise ValueError('Unbekanntes Feld in Gesundheitsmeldung.')
                if row['id'] not in self.queue.nodes:raise ValueError('Unbekannter Server in Gesundheitsmeldung.')
                for key in ('critical','clear','empirically_validated','powered'):
                    if key in row and type(row[key]) is not bool:raise ValueError('Ungültiger Gesundheitsstatus.')
                if row.get('risk') is not None:number(row['risk'],'risk',0,1)
                if row.get('maintenance_due_at') is not None:number(row['maintenance_due_at'],'maintenance_due_at',0,1e12)
                if row.get('gpu_temp_c') is not None:number(row['gpu_temp_c'],'gpu_temp_c',0,150)
                if row.get('flow_lpm') is not None:number(row['flow_lpm'],'flow_lpm',0,100)
            with self.queue.lock:
                for row in rows:
                    # An old file cannot clear a newer latched emergency lock.
                    node=self.queue.nodes[row['id']]
                    if node.last_health_at is not None and observed<=node.last_health_at:continue
                    if self.queue.clock()-observed>self.queue.health_ttl:
                        node.advisory='Gesundheitsdatei veraltet';continue
                    params={k:v for k,v in row.items() if k in ('critical','clear','empirically_validated','risk','maintenance_due_at')}
                    if row.get('powered') and row.get('flow_lpm')==0:params['critical']=True
                    temp=row.get('gpu_temp_c')
                    if node.max_gpu_temp_c is not None and temp is not None and temp>=node.max_gpu_temp_c:params['critical']=True
                    self.queue.set_health(row['id'],**params)
                    node.last_health_at=observed
            self.digest=digest
        except (OSError,ValueError,KeyError,TypeError):
            with self.queue.lock:
                for n in self.queue.nodes.values():
                    n.advisory='Gesundheitsdatei fehlt oder ist ungültig'
                    n.last_health_at=None
