import pytest
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from published_uvvis_analysis import analyze

@pytest.mark.skipif(not (Path(__file__).resolve().parents[1] / "data/published_uvvis/2_UV-Vis_P-4_thin-film_310nm.csv").is_file(), reason="Download cited Dryad data separately")
def test_published_uvvis_file(tmp_path):
    file=Path(__file__).resolve().parents[1]/'data/published_uvvis/2_UV-Vis_P-4_thin-film_310nm.csv'
    result=analyze(file,tmp_path)
    assert set(result['spectra'])=={'P-4','D-4'}
    assert result['spectra']['P-4']['sample_count']==501
    assert 199<result['spectra']['P-4']['wavelength_nm'][0]<201
    assert (tmp_path/'real_uvvis_report.json').exists()
