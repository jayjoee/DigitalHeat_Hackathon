"""Actual gradient-boosted forecast; no observations from a future target enter features.

Train Jan–May, calibrate June, evaluate Jul–Dec. Forecast runs use the repository's conservative
8-hour publication-delay assumption, not an assertion of verified historical release times.
"""
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
import math
import time
import numpy as np
from sklearn.ensemble import HistGradientBoostingRegressor
from threadpoolctl import threadpool_limits
from src.scheduler.zusage import prognose_laden

FEATURES = ["forecast_temperature", "hour_sin", "hour_cos", "year_sin", "year_cos",
            "heat_previous_hour", "heat_previous_day", "heat_previous_week", "horizon_hours"]

class Forecast:
    def __init__(self, profile, weather=None):
        self.profile=profile
        self.weather=weather if weather is not None else prognose_laden()
        if self.weather["time"] != [p["zeit"] for p in profile]:
            raise ValueError("Wetter und Wärmeprofil haben unterschiedliche Zeitachsen.")
        self.heat=np.array([p["heizung"]+p["ww"] for p in profile])
        zone=ZoneInfo("Europe/Zurich")
        self.times=[datetime.fromisoformat(p["zeit"]).replace(tzinfo=zone).astimezone(timezone.utc) for p in profile]
        self.model=None
        self.seconds=0.0
        self.margin=0.0
        self.train_indices=[]

    def weather_value(self, origin, target):
        for n in (1,2):
            available=self.times[target]-timedelta(hours=24*n)+timedelta(hours=8)
            if available <= self.times[origin]:
                value=self.weather[f"temperature_2m_previous_day{n}"][target]
                if value is None or not math.isfinite(float(value)):
                    continue
                return float(value), available
        raise ValueError("Keine zum Entscheidzeitpunkt verfügbare Wetterprognose.")

    def features(self, origin, target):
        if not 168 <= origin < target < len(self.profile) or target-origin > 24:
            raise ValueError("Prognose braucht vergangene Woche und 1–24 Stunden Horizont.")
        t=datetime.fromisoformat(self.profile[target]["zeit"])
        temp,_=self.weather_value(origin,target)
        return [temp, math.sin(t.hour*math.tau/24),math.cos(t.hour*math.tau/24),
                math.sin(t.timetuple().tm_yday*math.tau/365),math.cos(t.timetuple().tm_yday*math.tau/365),
                self.heat[origin-1],self.heat[origin-24],self.heat[origin-168],target-origin]

    def dataset(self, start, end):
        x=[]; y=[]; indices=[]
        for target,p in enumerate(self.profile):
            if start <= p["zeit"][:10] < end:
                for horizon in (1,3,6,12,24):
                    origin=target-horizon
                    if origin < 168:continue
                    x.append(self.features(origin,target)); y.append(self.heat[target]); indices.append(target)
        if not x:raise ValueError("Zu wenige Daten für Training oder Kalibrierung.")
        return np.asarray(x), np.asarray(y), indices

    def fit(self):
        start=time.perf_counter()
        x,y,self.train_indices=self.dataset('2025-01-01','2025-06-01')
        self.model=HistGradientBoostingRegressor(max_iter=100,max_leaf_nodes=15,
                    l2_regularization=1.0,early_stopping=False,random_state=2025)
        # Limit tiny prediction batches to one thread; do not change the user's global environment.
        with threadpool_limits(limits=1):
            self.model.fit(x,y)
            cx,cy,_=self.dataset('2025-06-01','2025-07-01')
            residual=cy-self.model.predict(cx)
            self.margin=max(0,float(np.quantile(residual,.90)))
        self.seconds+=time.perf_counter()-start
        self.info={"model":"HistGradientBoostingRegressor", "features":FEATURES,
                   "training":"2025-01-01 bis 2025-05-31", "calibration":"2025-06-01 bis 2025-06-30",
                   "evaluation":"2025-07-01 bis 2025-12-31", "training_rows":len(y),
                   "calibration_rows":len(cy), "safety_margin_kwh":self.margin,
                   "uncertainty":"90%-Quantil der Kalibrierresiduen; keine garantierte Abdeckung im Test",
                   "target":"Synthetischer Case-Wärmebedarf, keine echten Hausmessungen",
                   "weather_availability":"previous_day1/2 mit angenommenen 8 h Veröffentlichungsverzug"}
        return self

    def predict(self, origin, horizon):
        if self.model is None:raise ValueError("Modell wurde noch nicht trainiert.")
        start=time.perf_counter()
        targets=list(range(origin+1,min(origin+horizon+1,len(self.profile))))
        if not targets:return []
        with threadpool_limits(limits=1):
            values=np.maximum(0,self.model.predict(np.asarray([self.features(origin,t) for t in targets])))
        self.seconds+=time.perf_counter()-start
        return [float(v) for v in values]

    def persistence(self, origin, horizon):
        # Same hours yesterday; no future observations, even across the training/test boundary.
        return [float(self.heat[t-24]) for t in range(origin+1,min(origin+horizon+1,len(self.profile)))]
