"""Strict one-channel UV-Vis CSV importer for separately obtained published data.

This script does not download data or claim that external data have been validated.
"""
from __future__ import annotations
import argparse
import csv
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def _read_rows(path: Path):
    with path.open(encoding='utf-8-sig', newline='') as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise ValueError('A header row is required')
        return reader.fieldnames, list(reader)


def import_single_spectrum(path: Path, wavelength_col: str, absorbance_col: str,
                           blank_col: str | None = None, min_points: int = 10):
    """Read a single UV–Vis trace; do not infer wavelength or intensity units."""
    fields, rows = _read_rows(Path(path))
    cols = [wavelength_col, absorbance_col] + ([blank_col] if blank_col else [])
    if any(name not in fields for name in cols):
        raise ValueError(f'Missing selected column. Available columns: {fields}')
    try:
        raw = np.asarray([[float(row[c]) for c in cols] for row in rows], dtype=float)
    except (TypeError, ValueError) as exc:
        raise ValueError('Selected columns must contain only numeric values') from exc
    if raw.ndim != 2 or len(raw) < min_points:
        raise ValueError(f'Need >= {min_points} spectral samples')
    if not np.isfinite(raw).all():
        raise ValueError('NaN or infinite values are not acceptable')
    wl, y = raw[:, 0], raw[:, 1]
    if not np.all(np.diff(wl) > 0):
        raise ValueError('Wavelengths must be strictly increasing: sort/review input first')
    corrected = y - raw[:, 2] if blank_col else y.copy()
    peak_idx = int(np.argmax(corrected))
    qc = []
    if peak_idx in (0, len(wl)-1): qc.append('maximum_at_window_boundary')
    if np.min(corrected) < -.03: qc.append('negative_corrected_absorbance')
    if np.max(corrected) <= 0: qc.append('no_positive_absorbance_maximum')
    return wl, corrected, {
        'peak_nm': float(wl[peak_idx]), 'peak_absorbance': float(corrected[peak_idx]),
        'integrated_absorbance_au_nm': float(np.trapezoid(corrected, wl)),
        'n_samples': len(wl), 'wavelength_range_nm': [float(wl[0]), float(wl[-1])],
        'blank_subtraction': 'provided_column' if blank_col else 'none',
        'qc_flags': qc,
        'interpretation': 'Descriptive spectrum statistics only; no polarization or quantum yield inferred.'}


def run(path: Path, wavelength_col: str, absorbance_col: str, output: Path,
        blank_col: str | None = None, source_doi: str | None = None):
    output.mkdir(parents=True, exist_ok=True)
    wl, spectrum, stats = import_single_spectrum(path, wavelength_col, absorbance_col, blank_col)
    stats.update({'input_file': Path(path).name, 'data_origin': 'user-supplied CSV',
                  'source_doi': source_doi, 'claim_of_real_measurement': False})
    (output / 'import_report.json').write_text(json.dumps(stats, indent=2) + '\n')
    fig, ax = plt.subplots(figsize=(7.5, 4.5))
    ax.plot(wl, spectrum, label='Imported absorbance')
    ax.axvline(stats['peak_nm'], color='gray', ls=':', label='Maximum in supplied window')
    ax.set(xlabel='Wavelength (nm; user-specified)', ylabel='Absorbance (user-provided units)',
           title='UV–Vis import and basic feature extraction')
    ax.legend(); fig.tight_layout(); fig.savefig(output / 'import_plot.png', dpi=160); plt.close(fig)
    print(json.dumps(stats, indent=2))
    return stats


if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--csv', type=Path, required=True)
    p.add_argument('--wavelength-col', required=True)
    p.add_argument('--absorbance-col', required=True)
    p.add_argument('--blank-col')
    p.add_argument('--source-doi')
    p.add_argument('--output', type=Path, default=Path('results/experimental_import'))
    a=p.parse_args()
    run(a.csv,a.wavelength_col,a.absorbance_col,a.output,a.blank_col,a.source_doi)
