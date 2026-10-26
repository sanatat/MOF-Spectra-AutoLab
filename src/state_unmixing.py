"""Synthetic mixture-recovery stress test using *measured* P-4/D-4 endmember spectra.
This does not establish photokinetics, physical concentrations, or actual mixtures.
"""
import argparse, json
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.optimize import lsq_linear

DOI='10.5061/dryad.rxwdbrvqg'

def load_endmembers(path, lo=250, hi=650):
    df=pd.read_csv(path)
    for c in ('P-4_raw_wavelength_nm','D-4_raw_wavelength_nm','P-4_raw_abs_au','D-4_raw_abs_au'):
        if c not in df: raise ValueError(f'Missing {c}')
    w1=df['P-4_raw_wavelength_nm'].to_numpy(float)
    w2=df['D-4_raw_wavelength_nm'].to_numpy(float)
    if not np.allclose(w1,w2,atol=0.02):raise ValueError('Wavelength grids differ; interpolation required')
    order=np.argsort(w1); w=w1[order]
    mask=(w>=lo)&(w<=hi)
    if mask.sum()<50:raise ValueError('Insufficient points in range')
    p=df['P-4_raw_abs_au'].to_numpy(float)[order][mask]
    d=df['D-4_raw_abs_au'].to_numpy(float)[order][mask]
    if not np.isfinite(np.concatenate([p,d,w[mask]])).all():raise ValueError('Nonfinite data')
    return w[mask],p,d

def fit_fraction(w, signal, p, d, baseline=True):
    """Estimate x in y=x P+(1-x)D+b0+b1 scaled wavelength; bound x in [0,1]."""
    diff=p-d
    x=(w-w.mean())/np.ptp(w)
    if baseline:
        design=np.column_stack((diff,np.ones_like(w),x))
        target=signal-d
        fit=lsq_linear(design,target,bounds=([0,-np.inf,-np.inf],[1,np.inf,np.inf]),tol=1e-11)
    else:
        design=diff[:,None]
        fit=lsq_linear(design,signal-d,bounds=(0,1),tol=1e-11)
    fraction=float(fit.x[0]); residual=target-design@fit.x if baseline else signal-d-design@fit.x
    return fraction, float(np.sqrt(np.mean(residual**2)))

def run(csv, output, seed=42, repetitions=80, noise_levels=(0.002,0.01,0.03), drift=0.01):
    if repetitions<5 or any(n<0 for n in noise_levels):raise ValueError('Invalid parameters')
    w,p,d=load_endmembers(csv)
    rng=np.random.default_rng(seed)
    amp=float(max(np.max(p),np.max(d)))
    truths=np.linspace(0,1,11)
    rows=[]
    for noise in noise_levels:
        for truth in truths:
            for rep in range(repetitions):
                b0=rng.normal(0,drift*amp)
                b1=rng.normal(0,drift*amp)
                clean=truth*p+(1-truth)*d
                y=clean+b0+b1*(w-w.mean())/np.ptp(w)+rng.normal(0,noise*amp,len(w))
                estimate,rmse=fit_fraction(w,y,p,d,True)
                naive,_=fit_fraction(w,y,p,d,False)
                rows.append(dict(noise_relative_to_max=noise,true_P_fraction=float(truth),estimated_P_fraction=estimate,
                                 naive_P_fraction=naive,fit_rmse=rmse,replicate=rep))
    out=Path(output);out.mkdir(parents=True,exist_ok=True)
    data=pd.DataFrame(rows)
    data.to_csv(out/'synthetic_mixture_recovery.csv',index=False)
    summaries=[]
    for level,part in data.groupby('noise_relative_to_max'):
        error=part.estimated_P_fraction-part.true_P_fraction
        naive_err=part.naive_P_fraction-part.true_P_fraction
        # bootstrapping over the 80 independent repeated trials (each has 11 mixtures)
        per_rep=part.assign(ae=error.abs()).groupby('replicate').ae.mean().to_numpy()
        boots=np.mean(rng.choice(per_rep,size=(2000,len(per_rep)),replace=True),axis=1)
        summaries.append(dict(relative_noise=float(level),n_mixtures=len(part),mae=float(np.mean(abs(error))),
                              naive_mae=float(np.mean(abs(naive_err))),rmse_fraction=float(np.sqrt(np.mean(error**2))),
                              mae_bootstrap_95pct=[float(x) for x in np.quantile(boots,[.025,.975])],
                              fraction_at_bound_pct=float(np.mean((part.estimated_P_fraction<1e-8)|(part.estimated_P_fraction>1-1e-8))*100)))
    condition=np.linalg.cond(np.column_stack([p-d,np.ones_like(w),(w-w.mean())/np.ptp(w)]))
    report={'source_doi':DOI,'source_file':Path(csv).name,'measured_content':'Two reported experimental endmember spectra only',
            'generated_content':'Simulated linear mixtures, noise and baseline drift (no measured mixtures or kinetic timepoints)',
            'model':'y = f*P + (1-f)*D + intercept + linear baseline + Gaussian noise, 0<=f<=1',
            'chosen_wavelength_nm':[float(w.min()),float(w.max())],'wavelength_points':len(w),
            'condition_number_design':float(condition),'seed':seed,'repetitions_per_fraction':repetitions,
            'baseline_drift_scale_relative_to_max':drift,'noise_results':summaries,
            'limitations':['Performance is an in-model recovery test: mixtures created using same endmembers used for fitting',
                           'No time series or actual mixture standards are included, so no chemical conversion fraction or rate can be inferred',
                           'Linear absorbance mixing, constant paths and drift shape are assumptions, not experimentally checked',
                           'The source is a non-MOF photochemical thin film; this is not MOF thin-film growth spectroscopy',
                           'Bootstrap intervals quantify variation under the chosen simulation only, not experimental confidence']}
    (out/'mixture_recovery_report.json').write_text(json.dumps(report,indent=2)+'\n')
    fig,ax=plt.subplots(figsize=(7.6,5))
    for lv in noise_levels:
        sub=data[data.noise_relative_to_max==lv]
        g=sub.groupby('true_P_fraction').estimated_P_fraction.agg(['mean','std'])
        ax.errorbar(g.index,g['mean'],yerr=g['std'],marker='o',capsize=2,label=f'noise {lv:.1%} of max')
    ax.plot([0,1],[0,1],linestyle='--',color='black',lw=1,label='ideal')
    ax.set(xlabel='True synthetic P fraction',ylabel='Recovered P fraction',title='Recovery on synthetic mixtures of experimental endmembers')
    ax.legend(fontsize=8);fig.tight_layout();fig.savefig(out/'mixture_recovery.png',dpi=170);plt.close(fig)
    return report

if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--csv',default='data/published_uvvis/2_UV-Vis_P-4_thin-film_310nm.csv');a.add_argument('--output',default='results/mixture_recovery');a.add_argument('--seed',type=int,default=42);a.add_argument('--repetitions',type=int,default=80)
    z=a.parse_args();print(json.dumps(run(z.csv,z.output,z.seed,z.repetitions),indent=2))
