# Rainfall forecast research data and code

This repository provides analysis plans, derived verification scores and numerical analysis code. Current manuscripts and document-generation scripts are kept locally.

## Current public data

Use [data/transfer_2021_2024_20261102](data/transfer_2021_2024_20261102) for the four-year transfer assessment, observation-snapshot checks, independent decoder audit and expanded nested-selection summaries.

Download `derived_scores.json`, `additional_checks.json` and `verify_public_summaries.py` to one directory, then run:

```
python verify_public_summaries.py .
```

The check uses only the Python standard library and reconstructs pooled effects, exact annual tests, Holm adjustment, domain means and selection summaries from public derived records. Raw-field decoding and model fitting are separate stages.

## Provenance and access

Dated plans are in [analysis_plans](analysis_plans). The 2023–2024 extension was specified after inspecting 2021–2022 and before scoring the additional years. Provider licences govern original meteorological data. Obtain restricted fields from their providers.

The current branch excludes the old manuscript file and document-generation scripts. Historical commits and legacy Release archives may still contain early document snapshots. Use the dated data directory above for current results. This repository is a research archive, not a journal publication or a DOI registration.
