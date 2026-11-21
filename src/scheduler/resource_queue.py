"""Resource/policy admission queue, independent from payloads and executors.

Documented ideas from Kueue, KAI/Run:ai and Slurm; our own small implementation.
Reservations are scheduler accounting, NOT operating-system or GPU memory isolation.
"""
from dataclasses import dataclass, asdict, replace
from src.confidential.costs import Overhead
import math
import threading
import time

CLASSES = {'public':0,'internal':1,'confidential':2}
TASKS = ('text_analysis','literature','virtual_screening','microscopy')


def next_maintenance(node):
    values=[v for v in (node.maintenance_due_at,node.server_service_due_at,node.cooling_service_due_at) if v is not None]
    return min(values) if values else None


def number(value, name, low, high, integer=False):
    if isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value) or not low<=value<=high or (integer and type(value) is not int):
        raise ValueError(f'Ungültig: {name} ({low} bis {high}).')
    return value


@dataclass(frozen=True)
class Requirements:
    gpu_count: int = 0
    gpu_memory_gb: float = 0.  # per device, never aggregate VRAM
    ram_gb: float = 1.
    cpu_cores: int = 1
    gpu_model: str = ''
    classification: str = 'public'
    region: str = ''

    def __post_init__(self):
        number(self.gpu_count,'gpu_count',0,64,True)
        number(self.gpu_memory_gb,'gpu_memory_gb',0,1024)
        number(self.ram_gb,'ram_gb',.1,4096)
        number(self.cpu_cores,'cpu_cores',1,256,True)
        if not isinstance(self.classification,str) or self.classification not in CLASSES:raise ValueError('Unbekannte Datenklasse.')
        if not isinstance(self.gpu_model,str) or len(self.gpu_model)>60 or not isinstance(self.region,str) or len(self.region)>40:
            raise ValueError('Ungültige GPU-/Standortangabe.')
        if self.gpu_count==0 and (self.gpu_memory_gb or self.gpu_model):raise ValueError('GPU-Speicher/-Modell benötigt gpu_count > 0.')
        if self.gpu_count and not self.gpu_memory_gb:raise ValueError('GPU-Speicher je Karte fehlt.')

    @classmethod
    def parse(cls, data):
        if not isinstance(data,dict) or set(data)-set(cls.__dataclass_fields__):
            raise ValueError('Unbekannte Ressourcenfelder; Freigaben und Prioritäten sind Betreiberwerte.')
        return cls(**data)


@dataclass(frozen=True)
class Customer:
    id: str
    priority: int = 2  # 0 highest, operator controlled
    max_running: int = 4
    max_classification: str = 'public'
    allowed_regions: tuple = ()
    gpu_quota: int = 64
    weight: float = 1.

    def __post_init__(self):
        if not isinstance(self.id,str) or not 1<=len(self.id)<=80 or not isinstance(self.max_classification,str) or self.max_classification not in CLASSES:raise ValueError('Ungültiger Kunde.')
        if not isinstance(self.allowed_regions,(tuple,list)) or any(not isinstance(r,str) or not r for r in self.allowed_regions):raise ValueError('Ungültige Kundenstandorte.')
        number(self.priority,'priority',0,3,True)
        number(self.max_running,'max_running',1,128,True)
        number(self.gpu_quota,'gpu_quota',0,4096,True)
        number(self.weight,'weight',.1,100)


@dataclass
class Node:
    id: str
    ram_gb: float
    cpu_cores: int
    gpu_memory_gb: tuple = ()
    gpu_model: str = ''
    slots: int = 1
    executor: str = 'local_cpu_demo'
    region: str = 'LOCAL_DEMO'
    max_classification: str = 'public'
    approved_customers: tuple = ('demo',)
    approved_until: float | None = None
    maintenance: str = 'ready'  # ready/drain/isolated; operator only
    maintenance_due_at: float | None = None
    heat_enabled: bool = True
    heat_need_kw: float = 0.
    active_kw: float = 1.
    idle_kw: float = .23
    standby_kw: float = .01
    electricity_chf_kwh: float = .3325
    power_state: str = 'on'
    last_health_at: float | None = None
    require_health: bool = False
    advisory: str = ''
    max_gpu_temp_c: float | None = None
    site_id: str = 'local'
    server_service_due_at: float | None = None
    cooling_service_due_at: float | None = None
    tee_type: str = ''

    def __post_init__(self):
        if not isinstance(self.id,str) or not 1<=len(self.id)<=80 or not isinstance(self.max_classification,str) or self.max_classification not in CLASSES or self.maintenance not in ('ready','drain','isolated'):
            raise ValueError('Ungültiger Serverzustand.')
        number(self.ram_gb,'node RAM',.1,8192);number(self.cpu_cores,'node CPU',1,1024,True)
        number(self.slots,'slots',1,128,True)
        if self.executor not in ('local_cpu_demo','gpu','plan_only','confidential_coco') or self.power_state not in ('on','sleep','starting'):
            raise ValueError('Ungültiger Executor oder Betriebszustand.')
        for v in self.gpu_memory_gb:number(v,'VRAM je Karte',.1,1024)
        for v in (self.active_kw,self.idle_kw,self.standby_kw,self.heat_need_kw,self.electricity_chf_kwh):number(v,'Leistungs-/Preisannahme',0,100)
        if not self.standby_kw<=self.idle_kw<=self.active_kw:raise ValueError('Ungültiges Leistungsprofil.')
        if self.executor=='local_cpu_demo' and self.gpu_memory_gb:raise ValueError('CPU-Demo darf keine echten GPUs behaupten.')
        if self.executor=='confidential_coco':
            if self.tee_type!='tdx' or self.slots!=1 or len(self.gpu_memory_gb)>1:
                raise ValueError('CoCo benötigt hier einen dedizierten TDX-Host mit höchstens einer GPU und einem Auftrag.')
            if self.gpu_memory_gb and self.gpu_model not in ('H100','H200','B200'):
                raise ValueError('Keine freigegebene Confidential-GPU; L4 ist nicht unterstützt.')
        if self.max_gpu_temp_c is not None:number(self.max_gpu_temp_c,'Freigegebene Temperaturgrenze',1,115)
        if not isinstance(self.approved_customers,(tuple,list)) or any(not isinstance(c,str) or not c for c in self.approved_customers):raise ValueError('Ungültige Serverfreigaben.')
        if not isinstance(self.region,str) or not self.region or not isinstance(self.site_id,str) or not self.site_id:raise ValueError('Ungültiger Standort.')
        if type(self.heat_enabled) is not bool or type(self.require_health) is not bool:raise ValueError('Ungültige Betriebsfreigabe.')
        for v in (self.approved_until,self.maintenance_due_at,self.last_health_at,self.server_service_due_at,self.cooling_service_due_at):
            if v is not None:number(v,'Freigabe-/Wartungszeit',0,1e12)


@dataclass
class Ticket:
    id: str
    customer: str
    requirements: Requirements
    task_type: str
    submitted_at: float
    runtime_seconds: float
    deadline_at: float | None
    state: str = 'queued'
    reason: str = 'Wartet auf Zuteilung'
    node: str | None = None
    devices: tuple = ()
    reserved_at: float | None = None
    finish_by: float | None = None
    paused: bool = False
    baseline_runtime_seconds: float | None = None


class ResourceQueue:
    def __init__(self,nodes,customers,*,clock=time.time,aging_seconds=900.,health_ttl=120.,idle_sleep_seconds=300.,placement='pack',queue_order='priority',backfill=True,risk_threshold=.2,confidential_overhead=None):
        self.nodes={n.id:n for n in nodes};self.customers={c.id:c for c in customers}
        if len(self.nodes)!=len(nodes) or len(self.customers)!=len(customers):raise ValueError('Doppelte Server-/Kunden-ID.')
        self.clock=clock;self.aging_seconds=number(aging_seconds,'aging_seconds',1,86400)
        self.health_ttl=number(health_ttl,'health_ttl',1,86400)
        self.idle_sleep_seconds=number(idle_sleep_seconds,'idle_sleep_seconds',1,86400)
        if placement not in ('pack','spread') or queue_order not in ('priority','fifo') or type(backfill) is not bool:raise ValueError('Ungültige Schedulerstrategie.')
        self.placement=placement;self.queue_order=queue_order;self.backfill=backfill
        self.risk_threshold=number(risk_threshold,'risk_threshold',0,1)
        self.confidential_overhead=Overhead(**(confidential_overhead or {}))
        self.lock=threading.RLock();self.jobs={};self.usage={c.id:0. for c in customers}
        self.last_usage=clock();self.idle_since={n.id:clock() for n in nodes}

    def submit(self,jid,customer,requirements,task_type='literature',runtime_seconds=60,deadline_at=None):
        with self.lock:
            if jid in self.jobs or customer not in self.customers:raise ValueError('Unbekannter Kunde oder doppelte Auftrags-ID.')
            c=self.customers[customer];r=requirements
            if not isinstance(r,Requirements) or task_type not in TASKS:raise ValueError('Ungültiger Auftragstyp.')
            number(runtime_seconds,'runtime_seconds',.01,604800)
            if deadline_at is not None:number(deadline_at,'deadline_at',0,1e12)
            if CLASSES[r.classification]>CLASSES[c.max_classification]:raise PermissionError('Kunde ist für diese Datenklasse nicht freigegeben.')
            if c.allowed_regions and r.region and r.region not in c.allowed_regions:raise PermissionError('Standort ist für diesen Kunden nicht freigegeben.')
            if r.gpu_count>c.gpu_quota:raise PermissionError('GPU-Anforderung überschreitet das Kundenkontingent.')
            baseline=runtime_seconds
            if r.classification!='public':runtime_seconds=self.confidential_overhead.runtime(baseline)
            self.jobs[jid]=Ticket(jid,customer,r,task_type,self.clock(),runtime_seconds,deadline_at,baseline_runtime_seconds=baseline)
            return self.jobs[jid]

    def _held(self,node,at=None):
        # Overdue running work remains reserved until its executor acknowledges stop.
        return [j for j in self.jobs.values() if j.node==node and j.state=='running' and
                (at is None or j.finish_by is None or j.finish_by>at)]

    def _available(self,node,r,at=None):
        held=self._held(node.id,at)
        if len(held)>=node.slots:return None
        if sum(j.requirements.ram_gb for j in held)+r.ram_gb>node.ram_gb+1e-9:return None
        if sum(j.requirements.cpu_cores for j in held)+r.cpu_cores>node.cpu_cores:return None
        used={i for j in held for i in j.devices}
        free=[i for i,size in enumerate(node.gpu_memory_gb) if i not in used and size>=r.gpu_memory_gb]
        if len(free)<r.gpu_count:return None
        return tuple(free[:r.gpu_count])

    def _policy_reason(self,node,ticket,now,executors):
        r=ticket.requirements;c=self.customers[ticket.customer]
        due=next_maintenance(node)
        if node.executor not in executors:return 'Kein angeschlossener passender Executor'
        if r.classification!='public' and node.executor!='confidential_coco':return 'Vertrauliche Daten benötigen einen CoCo-Executor; keine CPU-/L4-Ausweichroute'
        if node.executor=='confidential_coco':
            if r.classification!='confidential':return 'Dedizierter vertraulicher Executor'
            if r.gpu_count!=len(node.gpu_memory_gb):return 'Vertraulicher Auftrag muss alle GPUs des dedizierten Hosts reservieren'
        if ticket.customer not in node.approved_customers:return 'Server nicht für diesen Kunden freigegeben'
        if CLASSES[r.classification]>CLASSES[node.max_classification]:return 'Sicherheitsfreigabe des Servers reicht nicht'
        if node.approved_until is not None and now>=node.approved_until:return 'Sicherheitsfreigabe abgelaufen'
        if (r.region and node.region!=r.region) or (c.allowed_regions and node.region not in c.allowed_regions):return 'Standortanforderung nicht erfüllt'
        if r.gpu_model and r.gpu_model!=node.gpu_model:return 'GPU-Modell passt nicht'
        if r.gpu_count>len(node.gpu_memory_gb) or sum(m>=r.gpu_memory_gb for m in node.gpu_memory_gb)<r.gpu_count:return 'GPU-Anzahl oder VRAM je Karte reicht nicht'
        if r.ram_gb>node.ram_gb or r.cpu_cores>node.cpu_cores:return 'RAM- oder CPU-Anforderung zu gross'
        if node.maintenance!='ready' or (due is not None and now>=due):return 'Wartungssperre'
        if node.require_health and (node.last_health_at is None or now-node.last_health_at>self.health_ttl):return 'Gesundheitsmeldung fehlt oder ist veraltet'
        if node.power_state!='on':return 'Server noch nicht betriebsbereit'
        if not node.heat_enabled:return 'Wartet auf Wärmefreigabe'
        if due is not None and now+ticket.runtime_seconds>due:return 'Auftrag passt nicht vor Wartungstermin'
        return ''

    def _order(self,j,now):
        if self.queue_order=='fifo':return (j.submitted_at,j.id)
        c=self.customers[j.customer]
        priority=max(0,c.priority-int((now-j.submitted_at)//self.aging_seconds))
        return (priority,self.usage[j.customer]/c.weight,j.deadline_at or math.inf,j.submitted_at,j.id)

    def _placement(self,node,ticket,now):
        held=self._held(node.id)
        r=ticket.requirements
        load=max(r.cpu_cores/node.cpu_cores,r.gpu_count/max(1,len(node.gpu_memory_gb)))
        incremental=(node.active_kw-node.idle_kw)*load+(node.idle_kw if not held else 0.)
        if r.classification!='public':incremental*=1+self.confidential_overhead.power_increase
        energy=incremental*ticket.runtime_seconds/3600
        if self.placement=='spread':return (len(held),node.id)
        # Prefer lower modelled incremental cost; useful heat breaks a tie, never a cash credit.
        return (energy*node.electricity_chf_kwh,not bool(held),-node.heat_need_kw,node.id)

    def dispatch(self,executors=('local_cpu_demo','gpu','plan_only'),max_assignments=None):
        with self.lock:
            now=self.clock()
            self.usage={k:v*math.exp(-(now-self.last_usage)/3600) for k,v in self.usage.items()}
            self.last_usage=now
            for j in self.jobs.values():
                if j.state=='queued' and j.deadline_at is not None and now+j.runtime_seconds>j.deadline_at:
                    j.state='expired';j.reason='Frist mit angegebener Laufzeit nicht mehr erreichbar'
            reservations={};assigned=[]
            waiting=[j for j in self.jobs.values() if j.state=='queued' and not j.paused]
            while waiting:
                if max_assignments is not None and len(assigned)>=max_assignments:break
                waiting.sort(key=lambda j:self._order(j,now));j=waiting.pop(0);c=self.customers[j.customer]
                held_customer=[t for t in self.jobs.values() if t.customer==j.customer and t.state=='running']
                if len(held_customer)>=c.max_running or sum(t.requirements.gpu_count for t in held_customer)+j.requirements.gpu_count>c.gpu_quota:
                    j.reason='Kundenkontingent ist belegt';continue
                candidates=[];reasons=[]
                for node in self.nodes.values():
                    reason=self._policy_reason(node,j,now,executors)
                    if reason:reasons.append(reason);continue
                    devices=self._available(node,j.requirements)
                    if devices is None:
                        # Conservative EASY-style reservation for a blocked higher-ranked job.
                        times=sorted({t.finish_by for t in self._held(node.id) if t.finish_by and t.finish_by>now})
                        earliest=next((t for t in times if self._available(node,j.requirements,t) is not None),None)
                        if earliest is not None:reservations[node.id]=min(reservations.get(node.id,math.inf),earliest)
                        elif self._held(node.id):reservations[node.id]=now
                        reasons.append('Passende Ressourcen sind belegt');continue
                    if node.id in reservations and now+j.runtime_seconds>reservations[node.id]+1e-9:
                        reasons.append('Wartet: reservierter Start eines höher gereihten Auftrags');continue
                    candidates.append((self._placement(node,j,now),node,devices))
                if not candidates:
                    j.reason='; '.join(dict.fromkeys(reasons)) or 'Kein passender Server'
                    if not self.backfill:break
                    continue
                _,node,devices=min(candidates,key=lambda v:v[0])
                j.state='running';j.reason='Zugewiesen';j.node=node.id;j.devices=devices;j.reserved_at=now;j.finish_by=now+j.runtime_seconds
                self.idle_since[node.id]=None
                # Immediate entry penalty avoids a burst from one tenant bypassing fairness.
                units=max(j.requirements.gpu_count,j.requirements.cpu_cores/8,j.requirements.ram_gb/64)
                self.usage[j.customer]+=units*j.runtime_seconds
                assigned.append(j)
            return assigned

    def can_run(self,jid):
        with self.lock:
            j=self.jobs[jid];now=self.clock()
            if j.state!='running':return False,'Auftrag hat keine aktive Reservierung'
            n=self.nodes[j.node]
            if j.requirements.classification!='public' and (n.executor!='confidential_coco' or n.tee_type!='tdx'):
                return False,'Geschützter Executor nicht mehr verfügbar'
            if j.finish_by is not None and now>=j.finish_by:return False,'Laufzeitlimit erreicht'
            if j.deadline_at is not None and now>=j.deadline_at:return False,'Frist erreicht'
            if n.maintenance=='isolated':return False,'Kritische Wartungssperre'
            due=next_maintenance(n)
            if due is not None and now>=due:return False,'Wartungstermin erreicht'
            if j.customer not in n.approved_customers or CLASSES[j.requirements.classification]>CLASSES[n.max_classification]:return False,'Sicherheitsfreigabe widerrufen'
            if n.require_health and (n.last_health_at is None or now-n.last_health_at>self.health_ttl):return False,'Gesundheitsmeldung fehlt oder ist veraltet'
            if n.approved_until is not None and now>=n.approved_until:return False,'Sicherheitsfreigabe abgelaufen'
            if not n.heat_enabled or j.paused:return False,'Verarbeitung pausiert'
            return True,''  # drain permits already running work to finish within its time limit

    def finish(self,jid,state='completed'):
        with self.lock:
            j=self.jobs[jid]
            if j.state in ('completed','cancelled','failed','expired'):return
            if state not in ('completed','cancelled','failed'):raise ValueError('Ungültiger Abschluss.')
            node=j.node;j.state=state;j.reason=state
            if node and not self._held(node):self.idle_since[node]=self.clock()

    def set_health(self,node_id,*,critical=False,maintenance_due_at=None,risk=None,empirically_validated=False,clear=False):
        """Trusted monitoring/operator interface; deliberately absent from customer API."""
        with self.lock:
            n=self.nodes[node_id];n.last_health_at=self.clock()
            if maintenance_due_at is not None:
                number(maintenance_due_at,'maintenance_due_at',0,1e12);n.maintenance_due_at=maintenance_due_at
            if risk is not None:
                number(risk,'risk',0,1)
                n.advisory=f'Wartungsrisiko nächste 30 Tage: {risk:.3f}'+('' if empirically_validated else ' · unvalidiert, nur Hinweis')
                if empirically_validated and risk>=self.risk_threshold:n.maintenance='drain'
            if clear:n.maintenance='ready'  # only explicit operator action clears a latched lock
            if critical:n.maintenance='isolated'

    def power_advice(self):
        """Recommendations only; no shutdown commands or fabricated boot acknowledgements."""
        with self.lock:
            now=self.clock();out=[]
            for n in self.nodes.values():
                if n.power_state=='sleep':
                    awake=replace(n,power_state='on')
                    demand=any(j.state=='queued' and not j.paused and not self._policy_reason(awake,j,now,(n.executor,)) for j in self.jobs.values())
                    if demand:out.append(dict(node=n.id,action='wake_recommended',reason='Passende wartende Arbeit; echte Bereitschaftsbestätigung erforderlich'))
                    continue
                idle=self.idle_since.get(n.id)
                if n.power_state=='on' and not self._held(n.id) and idle is not None and now-idle>=self.idle_sleep_seconds:
                    # Do not sleep a node with any eligible queued demand.
                    demand=any(j.state=='queued' and not j.paused and not self._policy_reason(n,j,now,(n.executor,)) for j in self.jobs.values())
                    if not demand:out.append(dict(node=n.id,action='sleep_recommended',reason='Keine passende wartende Arbeit; Leerlaufgrenze erreicht'))
            return out

    def snapshot(self,jid):
        with self.lock:
            j=self.jobs[jid];c=self.customers[j.customer]
            reason=j.reason
            if j.state=='running':
                allowed,current=self.can_run(jid)
                if not allowed:reason=current
            node=self.nodes.get(j.node)
            estimate=self.confidential_overhead.estimate(j.baseline_runtime_seconds,node.active_kw,node.electricity_chf_kwh) if node and j.requirements.classification!='public' else None
            return dict(state=j.state,waiting_reason=reason,assigned_server=j.node,gpu_devices=list(j.devices),resource_lease_active=j.state=='running',
                        requirements=asdict(j.requirements),customer_priority=c.priority,finish_by=j.finish_by,
                        baseline_runtime_seconds=j.baseline_runtime_seconds,estimated_runtime_seconds=j.runtime_seconds,confidential_cost_estimate=estimate)
