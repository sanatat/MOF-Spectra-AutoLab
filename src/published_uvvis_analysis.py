"""Analyze the externally published Dryad UV-Vis thin-film CSV (not MOF)."""
from pathlib import Path
import argparse,json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

COLUMNS = {"P-4": ("P-4_raw_wavelength_nm", "P-4_raw_abs_au", "P-4_normalized_abs_au"),
           "D-4": ("D-4_raw_wavelength_nm", "D-4_raw_abs_au", "D-4_normalized_abs_au")}
DOI = "10.5061/dryad.rxwdbrvqg"

def analyze(csv_path, output):
    df = pd.read_csv(csv_path)
    output=Path(output);output.mkdir(parents=True,exist_ok=True)
    out={"source_doi":DOI,"source_file":Path(csv_path).name,"origin":"external published experimental thin-film UV-Vis (not MOF)",
         "data_role":"independent test of file ingestion / descriptive feature extraction only; not BO validation",
         "spectra":{},"limitations":["P-4 and D-4 are chemical states, not polarization channels",
         "Raw and normalized values are alternate representations, not independent replicates",
         "No blank/reference traces or uncertainty/replicates supplied; do not infer quantum yield or kinetic rate",
         "Peaks at measurement-window boundaries should not be interpreted as resolved maxima"]}
    fig,ax=plt.subplots(figsize=(9,5))
    for key,(wx,raw,norm) in COLUMNS.items():
        for col in [wx,raw,norm]:
            if col not in df:raise ValueError('Missing required column: '+col)
        wl=df[wx].to_numpy(float); a=df[raw].to_numpy(float); normalized=df[norm].to_numpy(float)
        if not (np.isfinite(wl).all() and np.isfinite(a).all() and np.isfinite(normalized).all()):raise ValueError('nonfinite values')
        if len(wl)<10 or not (np.diff(wl)<0).all():raise ValueError('expected strictly descending wavelength')
        inds=np.argsort(wl); wl,a,normalized=wl[inds],a[inds],normalized[inds]
        peak=int(np.argmax(a)); flags=[]
        if peak in [0,len(wl)-1]:flags.append('maximum_on_measurement_boundary')
        if a.min()<0:flags.append('small_negative_signal_present_no_blank_correction')
        area=float(np.trapezoid(a,wl))
        out['spectra'][key]={"sample_count":len(wl),"wavelength_nm":[float(wl.min()),float(wl.max())],
          "raw_max_nm":float(wl[peak]),"raw_max_au":float(a[peak]),"raw_auc_au_nm":area,
          "raw_min_au":float(a.min()),"normalized_max_au":float(normalized.max()),"flags":flags}
        ax.plot(wl,a,label=key+' raw')
    ax.set(xlabel='Wavelength (nm)',ylabel='Reported raw absorbance (a.u.)',title='Published thin-film UV–Vis data: P-4 vs D-4 (not MOF)')
    ax.legend();fig.tight_layout();fig.savefig(output/'real_uvvis_overlay.png',dpi=180);plt.close(fig)
    (output/'real_uvvis_report.json').write_text(json.dumps(out,indent=2)+'\n')
    return out

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--csv',type=Path,default=Path('data/published_uvvis/2_UV-Vis_P-4_thin-film_310nm.csv'))
    p.add_argument('--output',type=Path,default=Path('results/real_uvvis'));args=p.parse_args()
    print(json.dumps(analyze(args.csv,args.output),indent=2))
