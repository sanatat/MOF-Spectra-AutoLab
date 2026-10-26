"""Explicit simulated spectrum quality control; not an instrument calibration."""
from __future__ import annotations
import numpy as np


def analyze_spectrum(wavelength_nm, parallel, perpendicular, blank_parallel=None, blank_perpendicular=None):
    """Peak / polarization proxy with optional measured blank and basic QC flags."""
    wl=np.asarray(wavelength_nm,dtype=float)
    p=np.asarray(parallel,dtype=float)
    s=np.asarray(perpendicular,dtype=float)
    if any(a.ndim!=1 for a in (wl,p,s)) or len(wl)<10 or len(wl)!=len(p) or len(p)!=len(s):
        raise ValueError('Require >=10 aligned 1D wavelength/absorbance measurements')
    if not all(np.isfinite(a).all() for a in (wl,p,s)) or not np.all(np.diff(wl)>0):
        raise ValueError('Finite strictly ascending wavelength grid required')
    if blank_parallel is not None or blank_perpendicular is not None:
        if blank_parallel is None or blank_perpendicular is None:
            raise ValueError('Both blank polarization channels required')
        bp=np.asarray(blank_parallel,dtype=float);bs=np.asarray(blank_perpendicular,dtype=float)
        if bp.shape!=p.shape or bs.shape!=s.shape or not np.isfinite(bp).all() or not np.isfinite(bs).all():
            raise ValueError('Blank shape/value mismatch')
        p=p-bp;s=s-bs
        baseline_method='paired_blank'
    else:
        tail=max(3,int(np.ceil(.08*len(wl))))
        p=p-np.median(p[-tail:]);s=s-np.median(s[-tail:])
        baseline_method='tail_median_heuristic'
    avg=(p+s)/2
    peak_idx=int(np.argmax(avg))
    amp=float(avg[peak_idx]);denom=p[peak_idx]+s[peak_idx]
    flags=[]
    if peak_idx==0 or peak_idx==len(wl)-1:flags.append('peak_on_boundary')
    if amp<=0:flags.append('nonpositive_peak')
    if np.any(p<-.03) or np.any(s<-.03):flags.append('negative_corrected_absorbance')
    return {'peak_nm':float(wl[peak_idx]),'mean_peak_absorbance':amp,
            'polarization_contrast':float((p[peak_idx]-s[peak_idx])/denom) if abs(denom)>1e-9 else None,
            'baseline_method':baseline_method,'qc_flags':flags}
