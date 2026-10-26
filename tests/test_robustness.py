import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import numpy as np
import pytest
from robustness import analyze_spectrum
from validation import seeded_simulation

def test_blank_correction_recovers_peak():
    wl=np.linspace(400,700,301)
    blank=.05+.0001*(wl-400)
    peak=np.exp(-.5*((wl-530)/24)**2)
    result=analyze_spectrum(wl,blank+1.2*peak,blank+.8*peak,blank,blank)
    assert result['peak_nm']==530
    assert result['polarization_contrast']==pytest.approx(.2)
    assert not result['qc_flags']

def test_bad_inputs():
    with pytest.raises(ValueError):analyze_spectrum(np.arange(10)[::-1],np.ones(10),np.ones(10))
    with pytest.raises(ValueError):analyze_spectrum(np.arange(10),np.ones(10),np.ones(10),np.zeros(10),None)

def test_common_point_noise_reproducible():
    pt=[.6,.5]
    assert seeded_simulation(pt,30)==seeded_simulation(pt,30)
    assert seeded_simulation(pt,30)!=seeded_simulation(pt,31)
