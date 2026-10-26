import csv
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import numpy as np
import pytest
from validation import repeated_measurement,export_example_csv,load_spectrum_csv,csv_spectrum_features,benchmark

def test_repeats_reproducible():
    a=repeated_measurement(.7,.4,seed=7,repeats=4)
    b=repeated_measurement(.7,.4,seed=7,repeats=4)
    assert a==b and a['sample_std']>0

def test_import_and_features(tmp_path):
    path=tmp_path/'spectra.csv';export_example_csv(path)
    d=load_spectrum_csv(path)
    assert len(d['wavelength_nm'])==401
    assert 480<csv_spectrum_features(path)['peak_nm']<540

def test_invalid_csv(tmp_path):
    path=tmp_path/'bad.csv'
    path.write_text('wavelength_nm,parallel_absorbance,perpendicular_absorbance\n500,1,1\n')
    with pytest.raises(ValueError):load_spectrum_csv(path)

def test_benchmark_reproducible():
    a=benchmark(seed=3,runs=2,steps=6)
    b=benchmark(seed=3,runs=2,steps=6)
    assert a==b
