"""Mock flow-cell/spectrometer interface. SIMULATION ONLY: never controls hardware."""
from __future__ import annotations
from dataclasses import dataclass, asdict
from pathlib import Path
import csv
import json
import numpy as np
from autolab import WAVELENGTHS, TIMES, make_spectra

@dataclass(frozen=True)
class InstrumentConfig:
    dead_volume_ml: float = 0.3
    noise_std: float = 0.004
    drift_per_min: float = 0.00002
    flush_volumes: float = 3.0

    def __post_init__(self):
        import math
        vals = (self.dead_volume_ml, self.noise_std, self.drift_per_min, self.flush_volumes)
        if not all(math.isfinite(v) for v in vals):
            raise ValueError('Instrument parameters must be finite')
        if self.dead_volume_ml <= 0 or self.flush_volumes <= 0 or self.noise_std < 0 or self.drift_per_min < 0:
            raise ValueError('Volumes must be positive; noise and drift nonnegative')

class MockFlowSpectrometer:
    """Finite-state simulation: idle -> flushed -> acquired -> idle.

    The pump/valve/optical data are entirely virtual; delay and drift are
    illustrative engineering stress tests, not experimentally calibrated.
    """
    def __init__(self, seed=42, config=None):
        self.config = config or InstrumentConfig()
        self.rng = np.random.default_rng(seed)
        self.state = 'idle'
        self.settings = None
        self.log = []

    def prepare(self, concentration: float, flow: float):
        if self.state != 'idle':
            raise RuntimeError('Instrument must be idle before preparation')
        if not (0.2 <= concentration <= 1.0 and 0.1 <= flow <= 0.9):
            raise ValueError('Settings outside synthetic simulation domain')
        self.settings = (float(concentration), float(flow))
        flush_time = self.config.flush_volumes * self.config.dead_volume_ml / flow
        self.log.append({'event':'virtual_flush', 'flush_time_min':flush_time,
                         'precursor_setting':concentration,'flow_setting':flow})
        self.state = 'flushed'
        return flush_time

    def acquire(self):
        if self.state != 'flushed':
            raise RuntimeError('Must flush virtual flow cell before acquisition')
        c, flow = self.settings
        p, s = make_spectra(c, flow, self.rng)
        # Apply an illustrative slowly drifting common baseline.
        drift = TIMES[:,None] * self.config.drift_per_min
        # make_spectra already has fixed intrinsic simulator noise (0.004).
        # noise_std models *additional* instrument noise, not total noise.
        p = np.maximum(0, p + drift + self.rng.normal(0, self.config.noise_std, p.shape))
        s = np.maximum(0, s + drift + self.rng.normal(0, self.config.noise_std, s.shape))
        self.state = 'acquired'
        self.log.append({'event':'virtual_acquire', 'frames':len(TIMES),
                         'channels':['parallel','perpendicular']})
        return p,s

    def export(self, output: Path, p: np.ndarray, s: np.ndarray):
        if self.state != 'acquired':
            raise RuntimeError('Cannot export without acquisition')
        if p.shape != s.shape or p.shape != (len(TIMES), len(WAVELENGTHS)):
            raise ValueError('Spectrum dimensions are invalid')
        output=Path(output)
        output.mkdir(parents=True,exist_ok=True)
        with (output/'timeseries_synthetic.csv').open('w',newline='') as f:
            writer=csv.writer(f)
            writer.writerow(['time_min','wavelength_nm','parallel_absorbance','perpendicular_absorbance'])
            for t,prow,srow in zip(TIMES,p,s):
                writer.writerows((float(t),float(wl),float(a),float(b)) for wl,a,b in zip(WAVELENGTHS,prow,srow))
        meta={'data_origin':'SYNTHETIC; NO PHYSICAL HARDWARE OR MEASURED DATA',
              'noise_note':'Additional Gaussian instrument noise; base spectral simulator already includes 0.004 noise',
              'settings':self.settings,'config':asdict(self.config),'event_log':self.log}
        (output/'instrument_metadata.json').write_text(json.dumps(meta,indent=2)+'\n')
        self.state='idle'
        self.log=[]
        return meta

def main():
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,default=Path('results/mock_instrument'))
    parser.add_argument('--seed',type=int,default=42)
    args=parser.parse_args()
    instrument=MockFlowSpectrometer(seed=args.seed)
    instrument.prepare(.7,.4)
    p,s=instrument.acquire()
    print(json.dumps(instrument.export(args.output,p,s),indent=2))

if __name__=='__main__':main()
