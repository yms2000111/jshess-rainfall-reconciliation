# Mechanism experiments, 26 October 2026

These are exploratory extensions motivated by the inspected H2 disadvantage, not confirmatory tests on a new archive. The completed common-covariance experiment is retained in full.

The next experiment isolates uncertainty in the climate adjustment. Hold rainfall-only EMOS marginals, historical rank templates and the outer-fold H0 covariance fixed at their existing full permitted training sample. Fit only climate coefficients and their standardisation with 10, 15 and all available permitted years. The all-year count is 16–18 depending on system and fold; 19 years is incompatible with the existing adjacent-year embargo. For each held-out year, a seeded common permutation of permitted years defines nested subsets, identical across domains within a system. This is a climate-adjustment learning curve, not a learning curve for the entire forecasting pipeline.

Evaluate H0, H1, Hweekly, H2 and BU-clim on every outer fold. Use all eight domains, both systems and all available years. A separate regularisation sensitivity uses the full permitted training sample with coefficients penalised at 0.05, 0.20 and 0.50. Retain all results without selecting a favourable penalty. Compare paired mean CRPS, the H2-minus-H1 contrast, score interaction, coefficient norms and predictive width. Descriptive common-year bootstrap intervals preserve domain dependence.

The planned interpretation is conditional. A smaller H2 disadvantage with more climate-fitting years or stronger regularisation would be consistent with estimation noise but would not prove it is the only mechanism. Absence of this pattern will also be reported. Because the rainfall-only system remains fixed, the analysis does not quantify the value of increasing the full hindcast archive. Existing historical years are not relabelled as independent confirmation.

The user's current instruction is to complete mechanism experiments without ECDS credentials. Multi-year 2021–2025 issued-forecast validation remains pending data access; the original 2020 result and criterion remain unchanged.

