"""Reproduce published single-exponential TA bleach lifetimes from original data.

Times in the instrument CSV are interpreted as microseconds, based on comparison
with the reported 0.6 us to 6.4 ms experimental time window. This is a
cross-checked interpretation, not an instrument-header declaration.
"""
import argparse
import io
import json
import zipfile
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.optimize import curve_fit
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

DATASETS = [
    {"key": "neutral", "hint": "Figure 2+S2/", "file_contains": "with0000mMMSA", "target_nm": 419.0, "published_tau_ms": 1.2, "published_label": "TCPP4−"},
    {"key": "fully_protonated", "hint": "Figure 2+S2/", "file_contains": "with1024mMMSA", "target_nm": 447.0, "published_tau_ms": 0.120, "published_label": "H2TCPP2+"},
]

def monoexp(t, amplitude, tau, offset):
    return amplitude*np.exp(-t/tau)+offset

def extract_trace(z, spec, min_delay_us=10, max_delay_us=8000):
    names=[n for n in z.namelist() if spec["hint"] in n and spec["file_contains"] in n and n.endswith('.csv')]
    if len(names)!=1: raise ValueError(f'Expected exactly one file for {spec["key"]}, found {names}')
    table=pd.read_csv(io.BytesIO(z.read(names[0])), header=None).to_numpy(float)
    t_us=table[1:,0]; wavelengths=table[0,1:]; matrix=table[1:,1:]
    if not (np.isfinite(t_us).all() and np.isfinite(wavelengths).all() and np.isfinite(matrix).all()): raise ValueError('Non-finite values')
    wave_index=int(np.argmin(np.abs(wavelengths-spec["target_nm"])))
    valid=(t_us>=min_delay_us)&(t_us<=max_delay_us)
    t=t_us[valid]/1000.; y=matrix[valid,wave_index]
    order=np.argsort(t);t=t[order];y=y[order]
    if len(t)<15: raise ValueError('Insufficient samples')
    return names[0],float(wavelengths[wave_index]),t,y

def fit_trace(t, y):
    p0=[float(y[0]-y[-1]),0.7,float(y[-1])]
    popt,pcov=curve_fit(monoexp,t,y,p0=p0,bounds=([-1,.001,-1],[1,20,1]),maxfev=20000)
    fit=monoexp(t,*popt)
    r2=1-float(np.sum((y-fit)**2)/np.sum((y-y.mean())**2))
    return popt,pcov,r2,fit

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--source-zip',required=True)
    parser.add_argument('--out',default='results/baumgartner_lifetimes')
    parser.add_argument('--bootstrap',type=int,default=500)
    args=parser.parse_args()
    if args.bootstrap<0: raise ValueError('bootstrap must be nonnegative')
    out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
    rng=np.random.default_rng(42)
    rows=[]
    fig,axes=plt.subplots(1,2,figsize=(11,4.4))
    with zipfile.ZipFile(args.source_zip) as z:
        for ax,spec in zip(axes,DATASETS):
            name,wavelength,t,y=extract_trace(z,spec)
            p,c,r2,yhat=fit_trace(t,y)
            boots=[]
            for _ in range(args.bootstrap):
                sample=yhat+rng.choice(y-yhat,size=len(y),replace=True)
                try: boots.append(float(fit_trace(t,sample)[0][1]))
                except (RuntimeError,ValueError): continue
            ci=[float(v) for v in np.quantile(boots,[.025,.975])] if boots else [None,None]
            row=dict(dataset=spec['key'],source_member=name,extracted_wavelength_nm=wavelength,n_points=len(t),time_unit_assumption='microseconds (cross-checked against article)',time_fit_range_us=[10,8000],fit_model='A exp(-time/tau)+offset',tau_ms=float(p[1]),tau_95pct_residual_bootstrap_ms=ci,r_squared=r2, amplitude=float(p[0]),offset=float(p[2]),published_tau_ms=spec['published_tau_ms'],relative_difference_pct=float(100*(p[1]-spec['published_tau_ms'])/spec['published_tau_ms']),bootstrap_successes=len(boots))
            rows.append(row)
            ax.scatter(t,y,s=10,alpha=.7,label='Observed (experimental)')
            xx=np.linspace(t.min(),t.max(),350)
            ax.plot(xx,monoexp(xx,*p),label=f'Fit: tau={p[1]:.3f} ms')
            ax.set_title(f"{spec['key']} · {wavelength:.1f} nm")
            ax.set(xlabel='Delay after excitation (ms)',ylabel='Differential absorbance (a.u.)')
            ax.legend(fontsize=8)
            ax.grid(alpha=.2)
    fig.suptitle('Independent monoexponential fits to published experimental TA data')
    fig.tight_layout()
    fig.savefig(out/'experimental_lifetime_reproduction.png',dpi=175)
    plt.close(fig)
    (out/'lifetime_results.json').write_text(json.dumps(dict(methodology_note='Descriptive fits; bootstrap assumes independent residuals and does not account for instrument/systematic uncertainty.',results=rows),indent=2)+'\n')
    print(json.dumps(rows,indent=2))

if __name__=='__main__': main()
