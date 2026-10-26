"""Educational synthetic UV–Vis thin-film growth and closed-loop optimisation.

Not a physical spectrometer or a validated model of any particular MOF.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import numpy as np
from scipy.stats import norm
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import ConstantKernel, Matern, WhiteKernel
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

BOUNDS = np.array([[0.2, 1.0], [0.1, 0.9]])  # normalized precursor and flow settings
WAVELENGTHS = np.linspace(350, 750, 401)  # nm
TIMES = np.linspace(0, 60, 31)  # arbitrary simulated minutes


def make_spectra(concentration: float, flow: float, rng: np.random.Generator):
    """Return time-resolved, two-polarisation *synthetic* absorbance arrays."""
    if not (0.2 <= concentration <= 1.0 and 0.1 <= flow <= 0.9):
        raise ValueError('Settings outside the simulation domain')
    # Entirely illustrative response surface, not measured kinetics.
    growth = (1 - np.exp(-TIMES / (12 + 9 * flow)))[:, None]
    intensity = 0.2 + 1.2 * np.exp(-((concentration - .69) / .25)**2
                                   - ((flow - .43) / .30)**2)
    anisotropy = .07 + .22 * np.exp(-((concentration - .66) / .31)**2
                                   - ((flow - .48) / .28)**2)
    band = np.exp(-.5 * ((WAVELENGTHS - (510 + 12 * (flow - .5))) / 36)**2)[None, :]
    baseline = .02 + .000035 * (WAVELENGTHS - 350)[None, :]
    parallel = baseline + growth * band * intensity * (1 + anisotropy)
    perpendicular = baseline + growth * band * intensity * (1 - anisotropy)
    parallel += rng.normal(0, .004, parallel.shape)
    perpendicular += rng.normal(0, .004, perpendicular.shape)
    return np.maximum(parallel, 0), np.maximum(perpendicular, 0)


def features(parallel: np.ndarray, perpendicular: np.ndarray) -> dict:
    """Baseline-correct final spectrum and extract metrics, for the simulator."""
    baseline_p = float(np.mean(parallel[-1, -30:]))
    baseline_s = float(np.mean(perpendicular[-1, -30:]))
    p = np.maximum(parallel[-1] - baseline_p, 0)
    s = np.maximum(perpendicular[-1] - baseline_s, 0)
    peak_i = int(np.argmax((p + s) / 2))
    ppeak, speak = float(p[peak_i]), float(s[peak_i])
    return {
        'peak_nm': float(WAVELENGTHS[peak_i]),
        'mean_peak_absorbance': (ppeak + speak) / 2,
        'polarization_contrast': (ppeak - speak) / (ppeak + speak + 1e-12),
    }


def score(feat: dict) -> float:
    """Illustrative *user-defined* proxy combining absorbance and anisotropy."""
    return float(feat['mean_peak_absorbance'] + 0.7 * feat['polarization_contrast'])


def evaluate(point, rng):
    p, s = make_spectra(float(point[0]), float(point[1]), rng)
    f = features(p, s)
    return score(f), f, p, s


def next_point(x, y, rng, candidates=1800):
    """GP + expected improvement, with scaled inputs and a seeded candidate set."""
    lower, upper = BOUNDS[:, 0], BOUNDS[:, 1]
    xunit = (np.array(x) - lower) / (upper - lower)
    gp = GaussianProcessRegressor(
        kernel=ConstantKernel(1.0, (1e-2, 1e2)) * Matern(length_scale=[.4, .4],
               length_scale_bounds=(.05, 5), nu=2.5) + WhiteKernel(noise_level=.001,
               noise_level_bounds=(1e-5, .1)),
        normalize_y=True, random_state=0, n_restarts_optimizer=2)
    gp.fit(xunit, np.array(y))
    test = rng.uniform(0, 1, (candidates, 2))
    mean, std = gp.predict(test, return_std=True)
    improvement = mean - max(y) - .005
    z = improvement / np.maximum(std, 1e-12)
    ei = improvement * norm.cdf(z) + std * norm.pdf(z)
    # Avoid points nearly identical to previously tested settings.
    distances = np.linalg.norm(test[:, None, :] - xunit[None, :, :], axis=2)
    ei[np.min(distances, axis=1) < .03] = -np.inf
    return lower + test[int(np.argmax(ei))] * (upper - lower)


def run(output: Path, seed=42, steps=14):
    if steps < 5:
        raise ValueError('steps must be at least 5')
    output.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(seed)
    # Five seeded exploratory settings, followed by GP-guided choices.
    initial = np.array([[.25, .2], [.95, .2], [.25, .8], [.95, .8], [.6, .5]])
    observations, xs, ys = [], [], []
    example_spectra = None
    for index in range(steps):
        point = initial[index] if index < len(initial) else next_point(xs, ys, rng)
        value, feat, p, s = evaluate(point, rng)
        xs.append(point.tolist()); ys.append(value)
        observations.append({'step': index + 1, 'phase': 'initial' if index < 5 else 'bayes_opt',
           'precursor_setting': float(point[0]), 'flow_setting': float(point[1]),
           'score': value, **feat, 'best_so_far': float(max(ys))})
        if example_spectra is None or value >= max(ys):
            example_spectra = (p.copy(), s.copy())
    with (output / 'observations.csv').open('w') as f:
        import csv
        writer = csv.DictWriter(f, fieldnames=observations[0].keys()); writer.writeheader(); writer.writerows(observations)
    best_idx = int(np.argmax(ys))
    summary = {'type': 'synthetic simulation, not experimental measurements',
      'seed': seed, 'n_experiments': steps, 'best_step': best_idx + 1,
      'best_settings': xs[best_idx], 'best_score': ys[best_idx],
      'initial_best_score': max(ys[:5]), 'objective': 'baseline-corrected peak absorbance + 0.7 * polarization contrast',
      'limitations': 'illustrative kinetics, normalized settings, simplified Gaussian absorption, no hardware or experimental validation'}
    (output / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    p, s = example_spectra
    fig, ax = plt.subplots(figsize=(8, 5))
    for j in [0, 5, 10, 20, 30]:
        ax.plot(WAVELENGTHS, p[j], label=f't={TIMES[j]:.0f} (parallel)')
    ax.set(xlabel='Wavelength (nm)', ylabel='Simulated absorbance (a.u.)',
           title='Synthetic thin-film growth: polarised UV–Vis')
    ax.legend(fontsize=8); fig.tight_layout(); fig.savefig(output / 'spectra.png', dpi=160); plt.close(fig)
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.plot(np.arange(1, steps + 1), np.maximum.accumulate(ys), marker='o')
    ax.axvline(5.5, ls='--', color='gray', label='Bayesian optimisation starts')
    ax.set(xlabel='Simulated experiment number', ylabel='Best proxy score so far',
           title='Closed-loop optimisation (synthetic)')
    ax.legend(); fig.tight_layout(); fig.savefig(output / 'optimization.png', dpi=160); plt.close(fig)
    print(json.dumps(summary, indent=2))
    return summary


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, default=Path('results'))
    parser.add_argument('--seed', type=int, default=42)
    parser.add_argument('--steps', type=int, default=14)
    args = parser.parse_args()
    run(args.output, args.seed, args.steps)
