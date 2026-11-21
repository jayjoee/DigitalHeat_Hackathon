"""Explicit scenario inputs, never presented as measured L4 characteristics."""
from dataclasses import dataclass, asdict
import math

@dataclass(frozen=True)
class Config:
    servers: int = 8
    active_kw: float = 1.0
    economy_kw: float = 0.75
    economy_speed: float = 0.80
    idle_kw: float = 0.23
    off_kw: float = 0.005
    startup_kw: float = 0.60
    startup_minutes: float = 2.0
    pump_kw: float = 0.03
    recovery: float = 0.8
    storage_kwh: float = 35.0
    storage_loss_per_hour: float = 0.001
    backup_cop: float = 2.5
    electricity_chf_kwh: float = 0.3325
    ml_host_kw: float = 0.10
    horizon_hours: int = 6
    seed: int = 2025

    def __post_init__(self):
        for k, v in asdict(self).items():
            if isinstance(v, bool) or not isinstance(v, (int,float)) or not math.isfinite(v):
                raise ValueError(f"Ungültiger Parameter: {k}")
        if type(self.seed) is not int or not 0 <= self.seed <= 2**32-1:
            raise ValueError("Zufallssaat muss eine nicht negative 32-Bit-Ganzzahl sein.")
        if max(self.active_kw,self.economy_kw,self.startup_kw,self.pump_kw,self.ml_host_kw)>100 or self.electricity_chf_kwh>10 or self.backup_cop>20 or self.storage_kwh>10000:
            raise ValueError("Eingabe ausserhalb des unterstützten Testbereichs.")
        if type(self.servers) is not int or not 1 <= self.servers <= 32:
            raise ValueError("1 bis 32 Server erforderlich.")
        if type(self.horizon_hours) is not int or not 1 <= self.horizon_hours <= 24:
            raise ValueError("Planungshorizont: 1 bis 24 Stunden.")
        if not 0 < self.economy_speed <= 1 or not 0 < self.recovery <= 1 or not 0 <= self.storage_loss_per_hour < 1:
            raise ValueError("Ungültiger Wirkungsgrad oder Speicherverlust.")
        if min(self.active_kw,self.economy_kw)<=0:
            raise ValueError("Aktive Leistung muss grösser als null sein.")
        if not 0 <= self.off_kw <= self.idle_kw <= min(self.economy_kw,self.active_kw):
            raise ValueError("Es muss gelten: aus ≤ Leerlauf ≤ aktive Leistung.")
        if min(self.startup_kw,self.pump_kw,self.storage_kwh,self.ml_host_kw,self.electricity_chf_kwh) < 0:
            raise ValueError("Verbrauch und Preise dürfen nicht negativ sein.")
        if self.backup_cop <= 0 or not 0 <= self.startup_minutes < 60:
            raise ValueError("Ungültige Ersatzheizung oder Startdauer.")

    def public(self):
        return {"values":asdict(self), "status":"Szenarioannahmen, keine gemessenen NVIDIA-L4-Profile",
                "sources":{"servers":"Case / Referenzkonfiguration", "active_kw":"Case: 1-kW-Referenzserver",
                 "recovery":"Case: 80 %", "storage_kwh":"Case: 35 kWh", "electricity_chf_kwh":"Projekt: IWB H4 2026",
                 "all_other_values":"Transparente Testannahmen; vor Pilot durch Messungen ersetzen"}}
