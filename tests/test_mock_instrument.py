import sys
from pathlib import Path
import csv
import numpy as np
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from mock_instrument import MockFlowSpectrometer

def test_state_requires_prepare():
    m=MockFlowSpectrometer()
    with pytest.raises(RuntimeError):m.acquire()

def test_bad_settings():
    m=MockFlowSpectrometer()
    with pytest.raises(ValueError):m.prepare(.01,.4)

def test_no_repeat_prepare():
    m=MockFlowSpectrometer();m.prepare(.7,.4)
    with pytest.raises(RuntimeError):m.prepare(.7,.4)

def test_export_timeseries_and_metadata(tmp_path):
    m=MockFlowSpectrometer();delay=m.prepare(.7,.4)
    assert delay>0
    p,s=m.acquire();assert p.shape==(31,401)
    meta=m.export(tmp_path,p,s)
    assert 'SYNTHETIC' in meta['data_origin']
    assert m.state=='idle'
    with (tmp_path/'timeseries_synthetic.csv').open() as f:
        rows=list(csv.DictReader(f))
    assert len(rows)==31*401

def test_reproducible_seed():
    x=[]
    for _ in range(2):
        m=MockFlowSpectrometer(seed=99);m.prepare(.7,.4);x.append(m.acquire()[0])
    assert np.array_equal(x[0],x[1])
