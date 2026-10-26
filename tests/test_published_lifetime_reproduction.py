import sys
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from published_lifetime_reproduction import monoexp,fit_trace

def test_recover_known_lifetime():
    t=np.linspace(.01,7,100)
    y=monoexp(t,-.08,.55,-.003)
    p,_,r2,_=fit_trace(t,y)
    assert abs(p[1]-.55)<1e-4
    assert r2>.99999

def test_offset_and_negative_amplitude():
    t=np.geomspace(.01,6,90)
    y=monoexp(t,-.03,.12,-.001)
    p,_,_,_=fit_trace(t,y)
    assert np.allclose(p,[-.03,.12,-.001],atol=1e-5)
