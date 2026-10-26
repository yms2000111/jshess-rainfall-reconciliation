# Climate information and temporal reconciliation of subseasonal rainfall forecasts

Musong Yang and Ce Yang, Beijing Institute of Technology.

This repository contains the analysis source for the study in eight Australian geographical domains. The study evaluates where climate predictors enter weekly and aggregate rainfall forecasts, against raw forecasts and simple bottom-up baselines.

## Public research snapshot

Download the versioned archive and SHA-256 checksum from [Releases](https://github.com/yms2000111/jshess-rainfall-reconciliation/releases). The 26 October 2026 snapshot contains 700 files: Python source, processed regional inputs, score tables, source metadata, mathematical checks, the V5 manuscript, supplementary materials and equation explanations. Extract the ZIP into an empty directory to retain the analysis paths.

The Git repository exposes the source code; the ZIP supplies its data and document dependencies. Large fitting caches, global source archives and installed environments are omitted. Refitting those caches requires the supplied source retrieval and fitting scripts and may take substantial time. No independent clean-environment reproduction is claimed yet.

## Scope and validation

- ECMWF: eight domains, historical year-block validation and information-placement controls.
- ACCESS-S2: eight domains with a different start-date and ensemble-member schedule.
- 2020: a separate archived-period test with models frozen before scoring; a single year cannot quantify interannual uncertainty.
- 99 year-block permutations, mathematical audits and physical-background diagnostics are retained.

The original locally dated [2020 test plan](revision/review_v5/operational_test_plan_20261025.md) is preserved. This repository was created on **26 October 2026**, after the analysis. Its timestamp is a public deposit date, not proof of prospective preregistration.

## Running the analyses

Use Python with `requirements.txt`, and run commands from the extracted project root. `code/common.py` resolves paths relative to that root.

The baseline and nested validation implementations are in `revision_cv.py`, `extension_cv.py`, and `review_controls.py`. Eight-domain extensions use `coverage_extension.py`; V5 ACCESS processing and validation use `v5_access_download.py` and `v5_access_analysis.py`. Information-placement and permutation experiments use `v5_new_experiments.py`, followed by `v5_placement_inference.py`. The archived-period check uses `v5_operational_download.py`, `v5_operational_analysis.py` and `v5_operational_audit.py`.

Run `python code/audit_v5_mathematics.py` after its archived prediction dependencies have been regenerated. Word rendering additionally requires Microsoft Word and its MML2OMML transform; numerical analyses do not require Word. Historical document builders are retained as provenance, and are not interchangeable with the V5 builder.

## Interpretation and version status

This is a research snapshot during manuscript revision, not a final journal publication. Later editorial and experimental changes will be recorded separately. Cross-validation gains do not establish universal operational improvement. In particular, comparisons against BU-clim should be read alongside BU-rain, raw forecasts and H0.

## Rights and attribution

Source data retain their provider licences and attribution requirements. The ACCESS-S2 licence is retained in the archive at `revision/review_v4/access_s2/license.txt`. Original code and manuscript rights remain with the authors; this initial deposit does not assign an additional blanket reuse licence. No DOI or Zenodo deposit is claimed.
