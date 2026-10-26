import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import math
import pytest
from mof_orientation import dichroic_ratio, predicted_layer_thickness_nm

def test_isotropic_ideal(): assert dichroic_ratio(0,90)==pytest.approx(2.)
def test_aligned_in_plane_ideal(): assert dichroic_ratio(1,90)==pytest.approx(1.)
def test_aligned_z_diverges(): assert math.isinf(dichroic_ratio(1,0))
def test_reported_field_isotropic(): assert dichroic_ratio(0,20,.30,.33,.37)==pytest.approx(.67/.33)
def test_reported_field_in_plane(): assert dichroic_ratio(1,90,.30,.33,.37)==pytest.approx(.30/.33)
def test_layer(): assert predicted_layer_thickness_nm(40)==pytest.approx(43.2)
def test_validation():
    with pytest.raises(ValueError): dichroic_ratio(-.1,90)
    with pytest.raises(ValueError): dichroic_ratio(.4,90,ey2=0)
    with pytest.raises(ValueError): predicted_layer_thickness_nm(1.2)
