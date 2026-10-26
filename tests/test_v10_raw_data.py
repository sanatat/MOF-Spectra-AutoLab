import sys,zipfile,io,tempfile
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from baumgartner_raw_inventory import inventory

def test_matrix_inventory():
    with tempfile.TemporaryDirectory() as d:
        p=Path(d)/'example.zip'
        with zipfile.ZipFile(p,'w') as z:z.writestr('test.csv','0,400,500\n2,0.1,0.2\n1,0.3,0.4\n')
        rec=inventory(p)
        assert len(rec)==1 and rec[0]['nonmonotonic_delay_axis']
