import sys
from pathlib import Path
import numpy as np
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from state_unmixing import fit_fraction, load_endmembers, run
CSV=Path(__file__).resolve().parents[1]/'data/published_uvvis/2_UV-Vis_P-4_thin-film_310nm.csv'

@pytest.mark.skipif(not (Path(__file__).resolve().parents[1] / "data/published_uvvis/2_UV-Vis_P-4_thin-film_310nm.csv").is_file(), reason="Download cited Dryad data separately")
def test_exact_recovery():
    w,p,d=load_endmembers(CSV)
    y=.37*p+.63*d+.012+.008*(w-w.mean())/np.ptp(w)
    f,rmse=fit_fraction(w,y,p,d)
    assert abs(f-.37)<1e-6 and rmse<1e-8

@pytest.mark.skipif(not (Path(__file__).resolve().parents[1] / "data/published_uvvis/2_UV-Vis_P-4_thin-film_310nm.csv").is_file(), reason="Download cited Dryad data separately")
def test_bounded_fraction():
    w,p,d=load_endmembers(CSV)
    f,_=fit_fraction(w,1.5*p-.5*d,p,d)
    assert 0<=f<=1

@pytest.mark.skipif(not (Path(__file__).resolve().parents[1] / "data/published_uvvis/2_UV-Vis_P-4_thin-film_310nm.csv").is_file(), reason="Download cited Dryad data separately")
def test_repeatable_results(tmp_path):
    a=run(CSV,tmp_path/'a',repetitions=5)
    b=run(CSV,tmp_path/'b',repetitions=5)
    assert a['noise_results']==b['noise_results']

@pytest.mark.skipif(not (Path(__file__).resolve().parents[1] / "data/published_uvvis/2_UV-Vis_P-4_thin-film_310nm.csv").is_file(), reason="Download cited Dryad data separately")
def test_source_has_no_time_axis():
    import pandas as pd
    assert not any(('time' in c.lower() or 'minute' in c.lower()) for c in pd.read_csv(CSV,nrows=1).columns)
