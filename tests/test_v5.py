import sys
from pathlib import Path
import numpy as np
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from mock_instrument import InstrumentConfig, MockFlowSpectrometer
from validation import benchmark

def test_bad_instrument_configuration():
    for kwargs in [{'noise_std':-1},{'dead_volume_ml':0},{'flush_volumes':float('nan')},{'drift_per_min':-0.01}]:
        with pytest.raises(ValueError):
            InstrumentConfig(**kwargs)

def test_additional_noise_is_applied_reproducibly():
    def acquire(std):
        inst=MockFlowSpectrometer(seed=17,config=InstrumentConfig(noise_std=std))
        inst.prepare(.7,.4)
        return inst.acquire()
    p0,s0=acquire(0)
    p1,s1=acquire(.03)
    p2,s2=acquire(.03)
    assert np.array_equal(p1,p2) and np.array_equal(s1,s2)
    assert not np.array_equal(p0,p1)

def test_bootstrap_benchmark_deterministic_and_bounded():
    a=benchmark(seed=31,runs=3,steps=7,bootstrap_samples=200)
    b=benchmark(seed=31,runs=3,steps=7,bootstrap_samples=200)
    assert a==b
    lo,hi=a['mean_difference_bootstrap_95pct_ci']
    assert lo<=a['mean_paired_difference']<=hi
    assert len(a['paired_final_differences'])==3
