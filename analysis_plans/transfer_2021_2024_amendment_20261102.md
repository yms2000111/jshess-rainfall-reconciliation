# Four-year frozen-calibration transfer assessment, 2021–2024

Scope amendment recorded on 2 November 2026 at the user's request, before calculating the 2023–2024 forecast scores. The 2021–2022 results have already been inspected. Accordingly, report the new 2023–2024 extension separately as well as the pooled four-year assessment. This amendment does not retrospectively register the two-year results or replace the original five-year protocol.

## Sample and frozen implementation
Evaluate all 208 Thursday 00 UTC origins from 7 January 2021 through 26 December 2024, in the same eight domains, using control member 0 and perturbed members 1–10, with cumulative precipitation ending at 168, 336, 504 and 672 hours. Require complete tuples and the previously documented unit, QC, decoder and input-hash audits. Use existing downloaded files; no new ECDS requests or automatic download workers are required. Do not score 2025 forecasts.

Reuse the archived 2000–2019 calibration, climate lags, transformations, rank templates and covariance estimates without refitting. Verify the archived 2020 replay. This is cross-version transfer of a frozen calibration, not version-matched hindcast calibration. Report model-cycle composition from the audited metadata. Preserve the original five-year gate and the completed two-year outputs in their separate directories.

## Observations
Use AGCD v1.0.4 for 2021–2024 plus January 2025 to cover the last verification windows. Verify days t+1 through t+28, units, missingness and the unchanged regional weights. Record observation-file hashes and the difference from training AGCD v1.0.1. As a fixed sensitivity, omit origins 5, 12, 19 and 26 December 2024 whose windows extend into 2025, leaving 204 origins. No BoM January 2026 bridge enters this assessment.

## Contrasts and inference
Report H1 minus H0, BU-rain, BU-clim and raw, in that order, with negative differences denoting lower CRPS for H1. Divide domain CRPS differences by that domain's frozen training raw CRPS, multiply by 100, and average equally across domains and origin years. Publish annual/domain effects, pooled effects and favourable-year/domain counts for every contrast.

Use 50,000 common-year bootstrap resamples and exact two-sided sign flips over the four annual mean differences, followed by Holm adjustment across all four contrasts. Four years have 16 sign patterns and a minimum attainable two-sided p of 0.125. Annual bootstrap bounds describe the four observed years and provide limited information on interannual uncertainty. Also report circular four-origin blocks within each year, using common indices across domains and methods; six- and eight-origin blocks are fixed sensitivities. These conditional intervals do not establish significance across independent years.

Report 2023–2024 separately using the same estimand and two-year inference, and retain the earlier 2021–2022 result for chronological comparison. The pooled four-year and extension analyses are dependent and are not independent replications. No claim of equivalence or absence of an effect follows from a non-significant result.

## Reporting and limitations
Integrate only audited computed results into the main text, tables, figures and supplement. Retain the distinction between retrospective validation, 2020 assessment, the already inspected 2021–2022 sample and the 2023–2024 extension. Report adverse northern-domain results if present. Keep observational snapshot shifts, IFS cycle changes and limited interannual power separate from attribution to climate predictors.

The existing decoder comparison uses official experimental Python numeric accessors but shares section framing; an independent end-to-end native decoder comparison remains outstanding. Do not alter Windows Application Control. Retrospective expansion of penalty candidates is a separate exploratory analysis and does not change this frozen transfer arm.

Publish this protocol and derived data/audits through GitHub; do not publish manuscript files or restricted raw ECMWF data. Keep the cancelled scheduled task cancelled.
