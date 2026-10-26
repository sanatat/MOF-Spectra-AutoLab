import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import numpy as np
import pytest
from autolab import make_spectra, features, score, run


def test_shape_and_bounds():
    p, s = make_spectra(.7, .4, np.random.default_rng(42))
    assert p.shape == s.shape == (31, 401)
    assert np.all(p >= 0) and np.all(s >= 0)
    assert 480 < features(p, s)['peak_nm'] < 540


def test_reproducibility():
    a = make_spectra(.7, .4, np.random.default_rng(5))
    b = make_spectra(.7, .4, np.random.default_rng(5))
    assert np.array_equal(a[0], b[0]) and np.array_equal(a[1], b[1])


def test_out_of_range():
    with pytest.raises(ValueError):
        make_spectra(1.3, .4, np.random.default_rng(0))


def test_run_outputs(tmp_path):
    s = run(tmp_path, seed=4, steps=6)
    assert s['n_experiments'] == 6
    assert s['best_score'] >= s['initial_best_score']
    assert all((tmp_path / x).exists() for x in ['summary.json','observations.csv','spectra.png','optimization.png'])
