"""Inspect genuine transient-absorption measurement matrices; no unverified kinetic fits."""
import sys,zipfile,io,json
from pathlib import Path
import numpy as np
import pandas as pd

def inventory(zip_path):
    results=[]
    with zipfile.ZipFile(zip_path) as z:
        for name in z.namelist():
            if not name.endswith('.csv'): continue
            a=pd.read_csv(io.BytesIO(z.read(name)),header=None).to_numpy(float)
            assert a.shape[0]>2 and a.shape[1]>2
            results.append({'name':name,'delay_rows':a.shape[0]-1,'wavelength_columns':a.shape[1]-1,'nonmonotonic_delay_axis':bool(np.any(np.diff(a[1:,0])<0)),'finite_values':bool(np.isfinite(a).all())})
    return results

if __name__=='__main__':
    v=inventory(sys.argv[1]);print(json.dumps({'matrices':len(v),'summary':v},indent=2))
