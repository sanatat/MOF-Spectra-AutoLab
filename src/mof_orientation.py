"""Reproduce limiting-case dichroic ratios from Baumgartner et al. (2021) ESI Eq S2.

Not a fitted or calibrated orientation measurement. Electric-field intensities
are assumed, not experimentally determined for a particular sample.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import numpy as np


def dichroic_ratio(S: float, alpha_deg: float, ex2: float = 1/3,
                   ey2: float = 1/3, ez2: float = 1/3) -> float:
    """Return p/s ATR dichroic ratio from published Eq S2.

    R = Ex²/Ey² + Ez²/Ey²*(1+S*(3cos²α-1))/(1-(S/2)*(3cos²α-1)).
    The equal-field default reproduces paper's ideal R=2 and R=1 limits;
    use (0.30,0.33,0.37) for the reported estimated MOF-field fractions.
    """
    if not 0 <= S <= 1 or not 0 <= alpha_deg <= 180:
        raise ValueError('S in [0,1] and alpha in [0,180] required')
    if min(ex2, ey2, ez2) <= 0 or not np.isfinite([S, alpha_deg, ex2, ey2, ez2]).all():
        raise ValueError('finite positive field intensities required')
    c = 3*np.cos(np.deg2rad(alpha_deg))**2 - 1
    den = 1-0.5*S*c
    if abs(den) < 1e-12:
        return float('inf')
    return float(ex2/ey2 + (ez2/ey2)*(1+S*c)/den)


def predicted_layer_thickness_nm(n_layers: int, layer_angstrom: float = 10.8) -> float:
    if n_layers < 0 or int(n_layers) != n_layers or layer_angstrom <= 0:
        raise ValueError('nonnegative integer layers and positive layer spacing required')
    return n_layers*layer_angstrom*0.1


def generate(out: Path) -> None:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    out.mkdir(parents=True, exist_ok=True)
    ss = np.linspace(0, 0.999, 300)
    fig, ax = plt.subplots(figsize=(7, 4.5))
    for angle in [0, 45, 90]:
        ax.plot(ss, [dichroic_ratio(float(s), angle, .30,.33,.37) for s in ss], label=f'alpha={angle} deg')
    ax.axhline(dichroic_ratio(0,90,.30,.33,.37), color='grey', linestyle=':',label='isotropic S=0')
    ax.set_xlabel('Order parameter S (assumed)')
    ax.set_ylabel('Predicted ATR dichroic ratio R = Ap / As')
    ax.set_yscale('log')
    ax.set_ylim(0.5, 300)
    ax.legend()
    ax.set_title('Eq. S2 sensitivity (estimated evanescent field fractions)')
    fig.tight_layout()
    fig.savefig(out/'orientation_eq_s2.png', dpi=180)
    plt.close(fig)
    layers = np.arange(0,51)
    fig, ax = plt.subplots(figsize=(7,4.5))
    ax.plot(layers, layers*1.08, label='10.8 Å/layer (ideal geometry)')
    ax.scatter([40],[50], marker='x',s=75,label='~50 nm measured (ESI)')
    ax.set_xlabel('Nominal deposited layers')
    ax.set_ylabel('Film thickness (nm)')
    ax.set_title('LbL film thickness: ideal vs published observation')
    ax.legend()
    fig.tight_layout()
    fig.savefig(out/'layer_growth.png',dpi=180)
    plt.close(fig)
    report = {
      'source': 'Baumgartner et al., Chemical Science (2021), DOI 10.1039/D1SC02370E, Supplementary Information pp. 6,8,13',
      'nature': 'analytical reproduction of published equation and reported layer thickness; no digitized or raw MOF spectral data',
      'field_intensities_paper_estimate': {'Ex2':0.30,'Ey2':0.33,'Ez2':0.37},
      'ratios_with_equal_fields': {'S0_alpha90':dichroic_ratio(0,90), 'S1_alpha90':dichroic_ratio(1,90),'S1_alpha0':'infinite'},
      'ratios_with_reported_fields': {'S0_alpha90':dichroic_ratio(0,90,.30,.33,.37),'S1_alpha90':dichroic_ratio(1,90,.30,.33,.37),'S1_alpha0':'infinite'},
      'layer_by_layer': {'monolayer_spacing_angstrom':10.8,'layers':40,'predicted_nm':predicted_layer_thickness_nm(40),'measured_approx_nm':50,'difference_nm':50-predicted_layer_thickness_nm(40),'observation_note':'Authors report approximately 50 nm for 3D SURMOFs; not a sample-wise calibration.'},
      'reported_porosity_estimates': {'CuBDC':0.81,'Cu2_NDC2_DABCO':0.91},
      'limitations':['Field fractions approximated from refractive-index and porosity assumptions', 'Dichroic ratio alone cannot uniquely infer S and alpha', 'No quantitative polarized FTIR data provided in this input PDF', 'Linear nominal layer thickness is a geometrical reference not a kinetic law']
    }
    (out/'mof_orientation_report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report,indent=2))


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--output', type=Path, default=Path('results/mof_orientation'))
    generate(p.parse_args().output)
