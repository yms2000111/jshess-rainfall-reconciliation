# Mechanism experiment revision v0.2.0

This package extends the public v0.1.0 research snapshot. Extract that snapshot first, then this package into the same directory. The v0.1.0 deposit is at https://github.com/yms2000111/jshess-rainfall-reconciliation/releases/tag/v0.1.0.

The current manuscripts are in revision/review_v6/submission_final. The matching LaTeX source is in revision/review_v6/latex. This revision adds a common-covariance information-placement experiment and conditional climate-adjustment learning curves across 312 system-domain-year folds. Full archived scores, fitting records and all five learning settings are included.

## Reproduce score tables and figures

Install requirements.txt in a Python environment. From the project root run:

    python code/v6_mechanism_inference.py
    python code/v6_learning_inference.py

The first command reads the mechanism annual scores and archived baseline annual scores. The second reads the learning annual scores and fit records. They reproduce descriptive common-year intervals and Figures S11/S12 (Figure S11 is generated separately with python code/v6_figure.py). Run python code/v6_climate_learning.py --score to reconstruct learning annual scores from the included per-fold NPZ files.

Full refitting uses code/v6_mechanism.py and code/v6_climate_learning.py. It additionally requires the regional source inputs and climate series from v0.1.0 and the earlier fitted calibration pipeline described by the source scripts. Large original global fields and older fitted caches are not duplicated here. Score-table reproduction is distinct from an independent end-to-end scientific replication.

## Interpretation

The base rainfall forecasts, templates and H0 covariance are fixed in the learning experiment. Only climate-coefficient samples and penalties change. This is not a learning curve for the complete forecasting system. Ten and fifteen years are compared with all 16–18 permitted years; penalties are 0.05, 0.20 and 0.50. No outer performance selects a setting. The experiments are exploratory, not new multi-year confirmation. No forecasts after 2020 were added.

The mechanism plan has an external record in commit afd622c7d46515746781cbe504783c675b12e52a. That record follows two pilot folds and earlier exploratory findings. Neither this release nor the earlier release retroactively preregisters those findings. No DOI has been assigned. Existing source-data licences and attribution continue to apply.
