import csv
import json
import sys
from pathlib import Path
import numpy as np
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1] / 'src'))
from experimental_import import import_single_spectrum, run


def fixture_csv(tmp_path, bad=False):
    p=tmp_path/'spectrum.csv'
    with p.open('w',newline='') as f:
        w=csv.writer(f);w.writerow(['nm','abs','blank'])
        for j in range(41):
            wl=400+5*j
            if bad and j==20: wl=490
            w.writerow([wl, 0.02+np.exp(-.5*((wl-500)/20)**2), .02])
    return p


def test_import_detects_peak_and_blank(tmp_path):
    wl, values, report=import_single_spectrum(fixture_csv(tmp_path),'nm','abs','blank')
    assert report['peak_nm']==500
    assert abs(report['peak_absorbance']-1)<1e-6
    assert report['qc_flags']==[]
    assert len(wl)==41


def test_requires_column(tmp_path):
    with pytest.raises(ValueError,match='Missing'):
        import_single_spectrum(fixture_csv(tmp_path),'wavelength','abs')


def test_rejects_unsorted(tmp_path):
    with pytest.raises(ValueError,match='strictly increasing'):
        import_single_spectrum(fixture_csv(tmp_path,bad=True),'nm','abs')


def test_output_reproducible(tmp_path):
    source=fixture_csv(tmp_path)
    a=run(source,'nm','abs',tmp_path/'first',blank_col='blank')
    b=run(source,'nm','abs',tmp_path/'second',blank_col='blank')
    assert a==b
    assert (tmp_path/'first'/'import_plot.png').exists()
    assert json.loads((tmp_path/'first'/'import_report.json').read_text())==a
