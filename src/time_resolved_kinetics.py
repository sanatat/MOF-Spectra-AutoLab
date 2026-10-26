"""Fit measured single-wavelength time traces from external experiments.
Input: CSV with columns time_s and delta_absorbance; one row per actual time.
No inferred/digitized time points, no manufactured dataset supplied.
"""
import argparse, csv, json
import numpy as np
from scipy.optimize import curve_fit

def decay(t, offset, amplitude, rate_s_inv):
    return offset + amplitude * np.exp(-rate_s_inv*t)

def fit_experimental_trace(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        rows=list(csv.DictReader(f))
    if len(rows)<8:
        raise ValueError("At least eight independent measured time points required")
    t=np.asarray([float(r["time_s"]) for r in rows]); y=np.asarray([float(r["delta_absorbance"]) for r in rows])
    if not np.isfinite(t).all() or not np.isfinite(y).all() or np.any(np.diff(t)<=0):
        raise ValueError("Finite, strictly increasing measured times required")
    if np.ptp(t)<=0 or np.std(y)<1e-12: raise ValueError("No informative time/response variation")
    amp=float(y[0]-y[-1]); duration=float(t[-1]-t[0]); rate0=1.0/duration
    pars,cov=curve_fit(decay,t-t[0],y,p0=[float(y[-1]),amp,rate0],bounds=([-np.inf,-np.inf,0],[np.inf,np.inf,np.inf]),maxfev=20000)
    residual=y-decay(t-t[0],*pars)
    return {"data_origin":"external measured kinetics, as documented by data provider", "model":"single exponential; check residuals and mechanism before interpretation", "n_points":len(t),"time_unit":"seconds", "rate_s_inv":float(pars[2]),"lifetime_s":float(1/pars[2]) if pars[2]>0 else None,"offset":float(pars[0]),"amplitude":float(pars[1]),"rmse":float(np.sqrt(np.mean(residual**2))),"residuals":residual.tolist(),"time_s":t.tolist(),"observed":y.tolist(),"fitted":decay(t-t[0],*pars).tolist()}

if __name__=="__main__":
    a=argparse.ArgumentParser();a.add_argument('measured_csv');a.add_argument('--output',default='kinetics_fit.json');args=a.parse_args()
    result=fit_experimental_trace(args.measured_csv)
    with open(args.output,'w') as f: json.dump(result,f,indent=2)
    print('Saved',args.output)
