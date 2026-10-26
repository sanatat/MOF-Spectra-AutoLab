# PI-paper–grounded time-resolved spectroscopy extension (26 October 2026)

## Strongest relevant study by project supervisor
Prins, Rutkowska-Zbik, Pullen & **Bettina Baumgartner**, *Porphyrins on acid: kinetics of the photoinduced-protonation of tetrakis(4-carboxyphenyl)-porphyrin*, PCCP **2024**, 26, 24524–24532. DOI: https://doi.org/10.1039/D4CP02542C . Open article https://pmc.ncbi.nlm.nih.gov/articles/PMC11403973/ .

The paper reports **time-resolved transient absorption**, rather than simple irradiation-time UV–Vis monitoring. Figure 3 reports spectral slices at **0.6, 3.0, 9.1, 24, 63, 160 microseconds; 0.4, 1.0, 2.5 and 6.4 milliseconds**, and an illustration of global fitting. Quoted rates in the text for a particular acidic condition are **11.3, 8.0, 0.69 ms^-1**; these are **published values, not independently refitted results**. The study reports protonation trends with acid concentration. **Do not** fit one exponential to a multistate kinetics dataset and claim the same parameters: the publication uses a multistate/global kinetic model.

**Where are its data?** The Data availability section explicitly states: 'Raw and processed data for this article, including steady-state and transient absorption spectra ... are available at zenodo.org under the manuscript title.' During this run the exact record and raw spectrum files were not obtained. Figures alone cannot be passed off as raw time-resolved records. A local measured time-series file is therefore still needed before actual kinetics can be fitted.

## Other work by the PI
Baumgartner et al., *Infrared crystallography for framework and linker orientation in metal–organic framework films*, **Chemical Science (2021)**, DOI https://doi.org/10.1039/D1SC02370E . Uses polarized FTIR for orientation of MOF films; strong motivation for polarization-resolved module but **not** an independently verified machine-readable irradiation-time dataset.

Baumgartner et al., *Advancements in Understanding the Physicochemical Properties of Reticular Materials: An In Situ and Operando Spectroscopic Perspective*, **Advanced Materials (2025)**, DOI https://doi.org/10.1002/adma.202415135 . Review, not a primary raw time series.

Ham, Baumgartner & Reek (2026), institutional dataset DOI https://doi.org/10.21942/uva.32041101.v1 . The record is listed on PI's UvA profile; file inventory was **not verified in this session**. Do not claim kinetics or wavelength coverage without inspecting files.

## Scope of added code
`src/time_resolved_kinetics.py` accepts **measured** single-wavelength traces (`time_s,delta_absorbance`) and exports a single-exponential fit and residuals. This is an **ingestion/analysis capability, not validation on the professor's raw data**. Its unit test uses a synthetic mathematical fixture only to verify implementation. Real transient-absorption datasets require extra parsing (delay units, multiple probe wavelengths, replicates), global sequential/parallel model fitting, instrument response convolution where needed, residual diagnostics, and model selection.

## Original external UV–Vis sample in this project
The previously uploaded `2_UV-Vis_P-4_thin-film_310nm.csv` is experimental steady-state spectral data from a different study, **not the PI's paper**; it does not supply chronological repeated spectra sufficient to estimate kinetics.
