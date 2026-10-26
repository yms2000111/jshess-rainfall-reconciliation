# Untouched forecast-period test fixed on 25 October 2026

This protocol is written before downloading or scoring the 2020 forecast rainfall. Only archive metadata and availability have been inspected. Earlier hindcast verification used a few early-2020 AGCD dates to complete late-2019 targets; those targets are excluded from this test's training. No 2020 issued forecast has been evaluated previously in this project.

## Fixed question and data

Test whether aggregate climate information with seven-node reconciliation (H1) improves 28-day CRPS relative to climate-informed weekly summation (BU-clim) on the previously unused 2020 issued ECMWF forecasts in all eight predefined domains. Use all 53 Thursday origins, including late-December forecasts verified into January 2021. Retain every domain and all available origins. Do not select dates, regions or predictors from these outcomes.

Train the unchanged models on 2000–2019 hindcast origins whose targets end by 31 December 2019. No 2020 verification observations enter any fit, template, covariance, seasonal threshold or model selection. Use the first eleven archived member identifiers (control 0 and perturbed 1–10), fixed without inspecting their performance, to match the hindcast ensemble size. Preserve the original lags and regularisation. Refit Raw, BU-rain, BU-clim, H0, H1, Hweekly and H2 once. Parameter files and forecast samples must be saved before reading verification scores.

This is a retrospective transfer to previously unused issued forecasts. The calibration archive pools hindcasts produced across 2020 configurations, so it does not reconstruct the exact hindcasts available to an operational forecaster on each date. Archived climate indices also include revisions. These distinctions must remain explicit.

## Test and decision rule

The single confirmatory contrast is the mean across eight domains of H1 minus BU-clim 28-day CRPS, normalised by each domain's raw 2000–2019 training score, with equal domain weights. Negative values favour H1. Report the unnormalised domain differences and fraction favourable as descriptive quantities.

Use a circular moving-block bootstrap over the 53 weekly origins, with four consecutive origins per block, 50000 resamples and common origin indices across domains. Report the two-sided percentile 95% interval; repeat with block lengths six and eight as sensitivity analyses. The fixed success criterion is a negative point estimate and an upper confidence bound below zero for the four-origin block interval. This condition supports this forecast-year contrast only; one held-out year cannot establish interannual generalisation. No year-block p value is possible with one year. The original and extension Holm families remain separate, and this single predeclared contrast does not inherit their significance.

Report all other model comparisons descriptively, including performance against raw ECMWF. Do not change the hypothesis, loss function or forecast configurations after inspecting the scores. If the criterion fails, report that the new forecast-period test does not support transfer of the retrospective advantage.
