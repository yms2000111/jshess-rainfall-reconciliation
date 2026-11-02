# Amendment for the 2021–2022 frozen-model transfer assessment

Recorded on 2 November 2026 after the user's explicit request to pause further downloads and use 2021 and 2022. This changes the evaluation horizon before the new-period forecast scores are calculated. It does not retrospectively register earlier analyses.

## Scope and provenance
Keep the original 2021–2025 plan and its 260-origin completeness gate unchanged. Use a separate transfer_2021_2022 output directory. The present analysis covers every Thursday at 00 UTC in 2021 and 2022, 104 origins, eight unchanged domains, control plus perturbed members 1–10, and accumulations ending at 168, 336, 504 and 672 h. No origin is selected using forecast performance. Preserve all files already downloaded for later years without analysing their forecast scores. Pause both the sequential downloader and the worker waiting for all five years. Preserve remote request IDs for a later authorised restart.

## Forecast construction
Replay the archived 2020 samples to check the frozen 2000–2019 implementation. Use the archived parameters, transformations, climate lags, dependence templates and covariance estimates without refitting or selecting settings on new observations. This is a cross-cycle transfer assessment of a fixed calibration. It is not the separately documented version-matched hindcast calibration; downloads for that additional arm are also paused. Audit decoded member/date/step tuples, model cycles, cumulative precipitation units and signed-value QC before prediction. Use the already documented pure-Python simple-packing decoder and experimental reference accessor comparison; both share section framing, so the check is not fully independent end to end.

## Observations and alignment
Use a single AGCD v1.0.4 snapshot for 2021–2022 and January 2023, including all 28 verifying days following the final December 2022 origins. Dates t+1 through t+28 and the original domain weights are retained. No January 2026 BoM bridge is needed. Record the difference from training AGCD v1.0.1 and report the existing 2021/2022 snapshot comparison. Reproduce the primary result after omitting the four December 2022 origins whose targets extend into 2023; this is a fixed boundary check, not a new primary sample.

## Comparisons and uncertainty
Retain all four original contrasts: H1 minus H0, BU-rain, BU-clim and raw. Normalise each domain by its frozen training raw CRPS. Average first within each origin year and domain, then equally over the eight domains and two years. Report annual/domain effects, mean effects, favourable year/domain counts and all comparators, including adverse results. Calculate the common-year block bootstrap and exact two-sided sign-flip test with Holm across four contrasts, but label these as descriptive: two years provide only four sign patterns and the smallest attainable two-sided p is 0.5. Bootstrap annual bounds cannot establish climatological uncertainty.

Additionally report a conditional interval using circular four-origin blocks sampled separately within each year, with the same sampled origins across domains and methods. Six- and eight-origin blocks are fixed sensitivities. These intervals describe sampling variability conditional on 2021 and 2022; they do not replace the two-year limitation with more independent years. The result is an estimation and consistency assessment, not a pass/fail claim of general forecast superiority.

## Reporting
Keep 2020, retrospective validation and 2021–2022 results separate. Show the four contrasts and an annual/domain heatmap with a shared colour scale. Integrate actual scores into the abstract, Results, evidence table, Discussion, Conclusions and supplement only after audits pass. The retrospective nested penalty experiment remains exploratory and does not alter this frozen transfer arm.
