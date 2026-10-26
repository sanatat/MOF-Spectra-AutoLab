# Independent inspection of published Baumgartner-associated experimental data

Source: user-supplied `data upload.zip`, associated with *Porphyrins on acid: kinetics of the photoinduced-protonation of tetrakis(4-carboxyphenyl)-porphyrin* (PCCP, 2024), DOI: 10.1039/D4CP02542C.

The archive contains **20 transient-absorption CSV matrices** and **8 steady-state absorption TXT spectra**. Spectral matrices store wavelengths across the first row, a nonmonotonic first-column delay/acquisition coordinate, and transient signal intensities in the interior. Negative and repeated values occur. A true chemical kinetic fit is **not** reported without verifying the time unit and acquisition convention, and the multicomponent kinetic model in the paper.

The program produces the raw-data inventory, a heatmap and a representative trace from measured signals — none are synthetic. It does not claim to reproduce literature rates.

The 2021 polarized ATR-FTIR MOF film supplementary PDF was inspected. It contains instrumental parameters, polarized FTIR figures, orientation model Eq. S2, and an automated layer-by-layer deposition workflow; it contains no downloadable numeric FTIR curve arrays. Digitization of pictures is **not** equivalent to raw spectra.

To run: `python src/baumgartner_raw_inventory.py /path/to/data_upload.zip` (optional; precomputed figures already shipped).
