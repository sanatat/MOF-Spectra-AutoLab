# MOF Spectra AutoLab

**A small, reproducible synthetic demonstration of UV–Vis thin-film monitoring and closed-loop experimental design.**

This is a portfolio/educational prototype inspired by the general challenges of automated in-situ spectroscopy and self-driving laboratories. **No MOF was synthesised, no instrument was controlled, and no experimental spectra were acquired.** The response surface is invented to illustrate the software workflow; results must not be interpreted as kinetic, photophysical, or mechanistic findings.

## What it does

1. Simulates time-resolved, two-polarisation UV–Vis absorbance for a growing hypothetical thin film.
2. Estimates baseline-corrected peak wavelength, peak absorbance, and polarisation contrast.
3. Uses a Gaussian process and expected improvement to propose the next pair of *normalised* settings (precursor and flow).
4. Saves machine-readable observations, an optimisation trace, and spectra plots.

The score is deliberately simplistic: `baseline-corrected mean peak absorbance + 0.7 × polarisation contrast`. It is **not** an experimentally validated material-performance metric. Polarisation contrast is only a proxy, **not** a calibrated molecular orientation measurement. The optical model does not include multiple reflections, film-thickness fitting, realistic ATR geometry, or real MOF kinetics.

## Run

Requires Python 3.10+; runs on CPU without GPU.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python src/autolab.py --seed 42 --steps 14 --output results
python -m pytest -q tests/
```

## Files produced

- `results/observations.csv`: all settings, spectral features and per-run score
- `results/summary.json`: best observed conditions and caveats
- `results/spectra.png`: spectra over simulated growth times
- `results/optimization.png`: best-score progression

![Synthetic spectra](results/spectra.png)
![Synthetic Bayesian optimisation](results/optimization.png)

## What a real system would need

- Actual instrument driver integration for pumps, valves and spectrometers, plus fail-safe interlocks
- Dark/reference measurements, drift corrections, uncertainty quantification and replicates
- Spectral validation against genuine ATR–UV–Vis data and an appropriate optical forward model
- Optimization constraints representing material consumption, instrument time and safe operating ranges

## Suggested CV phrasing

> Built a Python simulation prototype for closed-loop UV–Vis thin-film spectroscopy: spectral feature extraction, Gaussian-process modelling, expected-improvement experiment selection, and reproducible reporting (synthetic data; no hardware integration).

## Validation extension (v2)

This extension tests whether the illustrated closed-loop policy is meaningfully better
than **uniform random search within the same synthetic response surface**, instead of
reporting only its own best-case score.

```bash
python src/validation.py --seed 42 --runs 5 --steps 12 --output results
python -m pytest -q tests/
```

The script creates:

- `benchmark.json` and `benchmark.png`: paired multi-seed benchmark, five common
  initial settings and equal experiment budgets. Envelopes show *min–max*, not
  confidence intervals. Do not claim statistical significance from five runs.
- `repeatability.json`: five repeat simulator evaluations at the same settings,
  reporting sample standard deviation and standard error.
- `example_synthetic_spectrum.csv` and `imported_features.json`: demonstration
  of a vendor-neutral one-timepoint spectrum import schema.

### CSV format

Required columns are `wavelength_nm`, `parallel_absorbance`, and
`perpendicular_absorbance`. Each row is one strictly increasing wavelength. This
is a **software ingestion interface**, not an instrument driver or validation
against actual ATR–UV–Vis data. The generic baseline rule is uncalibrated and
should not be used as a quantitative physical analysis pipeline without checking
blank spectra, drift, spectral geometry, and wavelength alignment.

### Honest limitations

The simulation uses a hand-designed response surface, so success in this benchmark
**does not establish** that Bayesian optimisation works for real MOF film synthesis.
The modeled measurement repeats change random noise but do not represent drift,
batch effects, substrate variability, or true technical replicates. No hardware
interlock, device integration, molecular orientation inference or experimental
benchmark has been demonstrated. A valuable next step would be to validate with
published/open real spectra or spectra acquired in a lab.

## Robustness extension (v3)

- `src/robustness.py` adds a blank-subtraction option for aligned paired-polarisation spectra and transparent QC flags. It is *not* a validated instrument calibration.
- The benchmark now uses deterministic **common point-wise measurement noise** for both policies within each replicate. This ensures the same settings produce the same noisy synthetic score, removing a confound in the earlier benchmark's shared initial observations.
- `tests/test_robustness.py` checks known synthetic peak recovery, invalid measurements and reproducibility.
- This remains entirely synthetic. Claim neither calibrated molecular orientation nor superior real-world optimization, and avoid extrapolating the benchmark to chemistry.

**Before any real laboratory deployment:** implement instrument abstraction, real dark/blank/reference scans, quantitative uncertainty estimates, safety interlocks, and experimental validation against established standards.

## Version 4: virtual flow-cell/spectrometer (simulation, not hardware)

`src/mock_instrument.py` implements a **virtual** preparation/flush/acquisition/export
state machine. It exports a long-form time-series CSV (31 × 401 wavelength/time
pairs, two polarisation channels) alongside a JSON event log and config. A
simple flush-time relation, sensor noise and baseline drift permit workflow
engineering tests, but are *not* validated descriptions of a laboratory flow
cell. No pumps, valves, devices or vendor SDKs are controlled.

```bash
python src/mock_instrument.py --output results/mock_instrument --seed 42
python -m pytest -q tests/
# For broader synthetic comparison, configurable (may be CPU-intensive):
python src/validation.py --runs 30 --steps 12 --output results/extended_validation
```

**Evidence boundary:** This project has no measured MOF-film spectra. Although
we investigated public spectroscopy repositories, no independently verified,
licensed and directly compatible dataset was integrated; it would be misleading
to label a simulated spectral CSV as an experimental dataset. The objective
is an arbitrary proxy, not a physical performance metric. The optimisation
comparison is illustrative and cannot validate thin-film growth physics.

**Next scientifically meaningful milestone:** acquire a DOI-linked, licensed
thin-film polarization time series with instrument metadata, run this analysis
on it, and assess reproducibility against independent experimental replicates.

## v5 — stronger reproducibility and simulator configuration checks

- **Bug fix:** `InstrumentConfig.noise_std` now affects the mock acquisition. It is **additional** Gaussian measurement noise on top of the fixed noise in `make_spectra`, not a calibration of an actual device. Invalid/nonfinite simulator parameters are rejected.
- **Uncertainty:** paired per-run BO–random differences now include a seeded nonparametric bootstrap 95% interval, paired sample SD and the complete raw traces. This interval estimates uncertainty **within the toy benchmark**, not across real material systems.
- **Fairness caveat:** both policies share five starting configurations and use identical deterministic point-wise noise within each run. Their subsequent candidate proposals depend on different pseudorandom streams and Gaussian process fitting.
- **Remaining caveats:** synthetic response surface favours a smooth, low-dimensional problem; no cost-aware acquisition, independent held-out MOF dataset, ATR optics, hardware controls, or physically calibrated signals are included. Avoid representing the benchmark as proof of real-world method superiority.

Run `python src/validation.py --runs 30 --steps 12 --bootstrap-samples 2000` and `python -m pytest -q tests/` from the project root.

## v6 — DOI-linked public spectra import, without falsely claiming a real-data run

A useful public **experimental** thin-film UV–Vis dataset was identified:
Nguyen et al., *Molecular solar thermal energy storage in Dewar Pyrimidone beyond 1.6 MJ/kg*, Dryad, **DOI: [10.5061/dryad.rxwdbrvqg](https://doi.org/10.5061/dryad.rxwdbrvqg)** (published 2026). The relevant dataset file is named `2_UV-Vis_P-4_thin-film_310nm.csv`. It concerns **photoactive pyrimidone thin films, not MOFs**, and does **not** constitute polarized ATR-UV–Vis kinetics. This is a **transfer test for the single-channel UV–Vis preprocessing stage only**.

**Important evidence boundary:** the public dataset was identified and documented, but its files could not be downloaded in this build environment. **No analysis result on this experimental dataset is included or claimed.** The importer has been tested only on independently generated test fixtures. Download the CSV yourself from Dryad and **inspect its structure**; some Dryad files contain multiple blocks. Export *one* numeric wavelength/absorbance block, strictly ascending in wavelength, to a conventional two-column CSV before importing.

```
python src/experimental_import.py \
  --csv /path/to/one_clean_spectral_block.csv \
  --wavelength-col wavelength_nm \
  --absorbance-col absorbance \
  --source-doi 10.5061/dryad.rxwdbrvqg \
  --output results/external_spectrum
```

Column names must exactly match your own CSV's headers. A `--blank-col` can be supplied *only when the CSV contains an independently measured aligned blank*. By default **no baseline subtraction** is performed on external data (rather than making a blind edge-of-window assumption). Results are descriptive: max-position, max-absorbance, integrated trace, and simple QC flags. A source DOI supplied by the user is metadata, **not proof of data provenance**. No comparison to external literature reference values has been performed.

### Interpretation limits

- Never label the public pyrimidone spectra MOF spectra.
- Never interpret a single polarization-free absorption spectrum as molecular orientation.
- Do not optimize actual reaction conditions on this dataset: it does not contain the required closed-loop control space.
- This script is a starting point for inspecting *one* experimental spectrum, not a generalized parser for Dryad's potentially complex multi-block files.

### Additional v6 tests

```
python -m pytest -q tests/
```

Test cases cover correctly aligned blank removal, peak recovery, missing columns, unsorted wavelengths, and output reproducibility.

## Version 7: published experimental thin-film UV–Vis data

The user-provided `data/published_uvvis/2_UV-Vis_P-4_thin-film_310nm.csv` is from Dryad DOI [10.5061/dryad.rxwdbrvqg](https://doi.org/10.5061/dryad.rxwdbrvqg). Please check the source record for reuse/license terms before redistributing. This is **a non-MOF molecular photoswitch thin film**, not a MOF film. P-4 and D-4 denote molecular forms, **not optical polarizations**. Columns marked `raw` and `normalized` are alternative representations, not independent experiments.

The new script reads and validates the 8-column original file (including descending wavelengths), compares **raw** P-4 and D-4 absorbance curves, and exports a figure and descriptive JSON:

```bash
python src/published_uvvis_analysis.py
python -m pytest -q tests/
```

Outputs: `results/real_uvvis/real_uvvis_overlay.png` and `results/real_uvvis/real_uvvis_report.json`. This validates the **spectral ingestion and exploratory analysis pipeline** on real published measurements, but *does not* validate the Bayesian optimizer, simulated thin-film growth kinetics, instrument model, or any MOF-specific chemistry. No uncertain peak deconvolution or quantum-yield estimates are asserted.

## v8 — Spectral-state unmixing stress test (published endmembers, **synthetic mixtures**)

The published Dryad `2_UV-Vis_P-4_thin-film_310nm.csv` has *two endpoint spectra*, **not a time series**. We therefore cannot infer a photochemical rate constant, time-dependent conversion, quantum yield or experimental mixture fractions from it. This new module asks a narrower, testable question: **If measured P-4 and D-4 spectra were linearly mixed, could a constrained spectral fit recover known synthetic fractions under noise and drifting baseline?**

```bash
python src/state_unmixing.py --csv data/published_uvvis/2_UV-Vis_P-4_thin-film_310nm.csv --output results/mixture_recovery --seed 42 --repetitions 80
python -m pytest -q tests/
```

The model is `A(λ) = f A_P(λ) + (1-f) A_D(λ) + b0 + b1 λ_centered + ε`, constrained to `0 ≤ f ≤ 1`. We use raw endmember absorbance over approximately 250–650 nm, 11 known synthetic fractions and 80 simulated replicates per fraction at each of three noise settings (2640 synthetic signals total). Noise amplitudes are 0.2%, 1% and 3% of the maximum endmember absorbance, with random baseline offset/slope of 1%. The script reports the mean absolute fraction error and a bootstrap interval over 80 replicate blocks, plus the equivalent naive fit without baseline terms. Random seed, code and resulting CSV allow reproduction.

**Important methodological limitation:** synthetic mixtures are built from exactly the same measured endmembers used by the inversion; thus this is an **in-model recovery/sensitivity demonstration, not independent experimental validation**. Unmodeled chemical shifts, scattering, optical effects, matrix effects or measurement drift can invalidate the recovered values. No experimental kinetic conclusion or MOF-specific finding follows from it. The included measured source is a non-MOF photochemical film. To estimate real conversions and reaction rates one must obtain spectra at known illumination times with suitable blanks, independent calibrations, and repeats.

Provenance: external published dataset: https://doi.org/10.5061/dryad.rxwdbrvqg ; provided CSV `2_UV-Vis_P-4_thin-film_310nm.csv`. Check the Dryad record's data-use license before redistributing beyond this exercise.

Outputs: `results/mixture_recovery/mixture_recovery_report.json`, `.png`, and `synthetic_mixture_recovery.csv`.

## v9 — PI-publication-grounded kinetics preparation
Read [research/BAUMGARTNER_PAPERS_AND_DATA_STATUS.md](research/BAUMGARTNER_PAPERS_AND_DATA_STATUS.md) for the supervisor's **2024 original time-resolved transient absorption study**, published rates, DOI, and exact status of raw-data access. Added `src/time_resolved_kinetics.py` to fit independently measured CSV time traces **if provided**. **No supervisor-paper raw kinetic spectra have been downloaded or refitted; no new experimental kinetic result is claimed.**

Expected measured CSV header: `time_s,delta_absorbance`. Example command (requires a real file): `python src/time_resolved_kinetics.py actual_measured_trace.csv --output trace_fit.json`. A single exponential is a deliberately limited demonstration and does **not** reproduce the paper's multistate global fit.


## V10: authentic Baumgartner research data

Inspected 20 time-resolved transient-absorption data matrices and 8 steady-state spectra from the original research data ZIP. See `research/EXPERIMENTAL_DATA_V10.md` and `results/baumgartner_raw_data/`. Actual measured signals are plotted without inventing time units or fitting unjustified rates. The companion MOF film PDF supplies polarized ATR-FTIR methods and figures, not numeric raw traces.


## v11: Independent reproduction of published bleach lifetimes (experimental data)

Source: Prins et al., *Physical Chemistry Chemical Physics* (2024), DOI: https://doi.org/10.1039/D4CP02542C; raw data provided by the user from the associated data deposit. Run:

```bash
python src/published_lifetime_reproduction.py --source-zip "/path/to/data upload.zip" --out results/baumgartner_lifetimes --bootstrap 500
```

Two source datasets (0 and 1024 mM MSA; Figure 2+S2) were fitted at the Soret bleach wavelengths with `A * exp(-t/tau) + offset`. The time coordinates were interpreted as microseconds based on agreement with the published 0.6 us–6.4 ms window, sorted and restricted to 10–8000 us. These are descriptive single-wavelength fits; not reproduction of the article's multistate global kinetic model. The residual bootstrap intervals are conditional on the chosen model and time window; no independent biological or instrument replicates. The original raw-data ZIP is deliberately NOT bundled; the user must supply it.

## v12 — MOF polarized ATR-FTIR orientation (paper-equation reproduction)

Implements Eq. S2 in the **actual MOF thin-film supplementary information** by Baumgartner et al., *Chemical Science* (2021), https://doi.org/10.1039/D1SC02370E, plus the reported 10.8 Å/layer geometric thickness check. This is a reproduction of **published analytical limiting cases** and published approximate thickness, **not** inverse fitting on raw FTIR spectra or a new MOF finding.

```bash
python src/mof_orientation.py --output results/mof_orientation
python -m pytest -q tests/
```

The equation is `R = Ex²/Ey² + (Ez²/Ey²) [1 + S(3 cos² α - 1)]/[1 - S(3 cos² α - 1)/2]`. The ESI reports estimated field intensity fractions `Ex² = 0.30, Ey² = 0.33, Ez² = 0.37`; isotropic `S=0` predicts `R ≈ 2.03`, aligned in-plane `S=1, α=90°` predicts `R ≈ 0.91`, and perfectly aligned normal `S=1, α=0°` diverges. Equal field fractions yield the publication's ideal limit descriptions `2`, `1`, and `infinity` exactly. These are **assumptions of the optical forward model**, not measured dichroic ratios from an experimental spectrum. An observed R does not independently identify both S and α.

The authors report a 10.8 Å geometric layer increment and approximately 50 nm thickness for 3D layer-by-layer-grown films. For 40 layers the ideal model gives 43.2 nm; these are approximate geometry and measurement values, not an inferred deposition efficiency or a growth rate.

Outputs: `results/mof_orientation/{mof_orientation_report.json,orientation_eq_s2.png,layer_growth.png}`. Tests include ideal limits, reported optical fractions, geometry, and invalid input handling. No spectra were digitised from the supporting PDF, and neither raw experimental FTIR nor measured alignment parameter is supplied.
