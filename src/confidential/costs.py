"""Explicit unmeasured overhead scenarios; throughput penalty != energy penalty."""
from dataclasses import dataclass, asdict
import math


@dataclass(frozen=True)
class Overhead:
    throughput_loss: float = .10
    power_increase: float = .05
    setup_seconds: float = 30.
    setup_kw: float = 1.
    broker_kwh_per_job: float = .001
    fixed_chf_per_job: float = 0.

    def __post_init__(self):
        for name, value in asdict(self).items():
            upper = .95 if name == 'throughput_loss' else 1e6
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or not 0 <= value <= upper:
                raise ValueError('Ungültige Confidential-Computing-Annahme: ' + name)

    def runtime(self, baseline_seconds):
        if not math.isfinite(baseline_seconds) or baseline_seconds <= 0:
            raise ValueError('Ungültige Basislaufzeit.')
        return baseline_seconds / (1 - self.throughput_loss) + self.setup_seconds

    def estimate(self, baseline_seconds, active_kw=1., price=.3325):
        for value in (active_kw, price):
            if isinstance(value, bool) or not math.isfinite(value) or value < 0:
                raise ValueError('Ungültige Leistung oder Preis.')
        baseline = active_kw * baseline_seconds / 3600
        compute = active_kw * (1 + self.power_increase) * baseline_seconds / (1 - self.throughput_loss) / 3600
        host = compute + self.setup_kw * self.setup_seconds / 3600
        total = host + self.broker_kwh_per_job
        return dict(baseline_seconds=baseline_seconds, protected_seconds=self.runtime(baseline_seconds),
                    baseline_kwh=baseline, protected_host_kwh=host, broker_kwh=self.broker_kwh_per_job,
                    total_kwh=total, additional_kwh=total-baseline,
                    electricity_chf=total*price, additional_chf=(total-baseline)*price+self.fixed_chf_per_job,
                    assumptions=asdict(self), measured=False,
                    scope='Aktiver Einzelauftrag inklusive Setup und angenommener Brokerenergie; keine Flotten-/Wärmebilanz oder Hardware-/Lizenzkosten.')
