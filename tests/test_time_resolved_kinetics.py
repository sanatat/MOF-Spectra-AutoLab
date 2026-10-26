import csv, sys
from pathlib import Path
import numpy as np
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from time_resolved_kinetics import fit_experimental_trace

def test_recovers_rate_from_software_fixture(tmp_path):
    # Software unit-test fixture only, NOT an experiment or reportable kinetic result.
    f=tmp_path/'fixture.csv'
    with f.open('w',newline='') as out:
        w=csv.writer(out);w.writerow(['time_s','delta_absorbance'])
        for t in np.linspace(0,4,25):w.writerow([t,0.2+0.5*np.exp(-1.7*t)])
    assert abs(fit_experimental_trace(f)['rate_s_inv']-1.7)<1e-3

def test_rejects_nonmonotonic(tmp_path):
    f=tmp_path/'bad.csv';f.write_text('time_s,delta_absorbance\n'+'\n'.join(f'{t},{v}' for t,v in zip([0,1,2,3,4,5,5,6],[1,.9,.8,.7,.6,.5,.4,.3])))
    with pytest.raises(ValueError):fit_experimental_trace(f)
