# Climate information and temporal reconciliation of subseasonal rainfall forecasts in eight Australian domains

Musong Yang and Ce Yang

Beijing Institute of Technology, Beijing, China

Corresponding author: Ce Yang, yangce@bit.edu.cn

## Abstract

Climate predictors may improve rainfall calibration, but their value depends on where they enter a coherent forecast and which baseline is used. We compare weekly, aggregate and all-node climate adjustments for subseasonal rainfall in eight Australian domains using nested ECMWF validation, ACCESS-S2 and a previously unused 2020 forecast period. In retrospective ECMWF comparisons, H1, which adjusts aggregate forecasts before reconciliation, changes 28-day continuous ranked probability score by −5.82% relative to raw forecasts, −0.78% relative to rainfall-only weekly summation, −1.05% relative to climate-informed weekly summation and −0.33% relative to rainfall-only reconciliation, expressed as percentages of raw score. Their 95% intervals are respectively [−7.56, −4.14], [−1.42, −0.26], [−1.50, −0.61] and [−0.74, 0.06]%; the first three comparisons pass Holm adjustment. Weekly-only climate adjustment with reconciliation performs similarly to H1, whereas adjusting every node worsens scores. ACCESS-S2 also favours H1 over climate-informed summation, but that comparator underperforms rainfall-only summation in seven domains. In 2020, H1 improves on rainfall-only summation in three domains, and its predeclared comparison with climate-informed summation remains inconclusive. All-node deterioration persists under common covariance in both systems, while circulation describes the seasonal setting rather than a reliable gain predictor. Larger climate-fitting samples and stronger regularisation reduce the all-node penalty in both systems, consistent with unstable climate adjustments contributing to the differences. Temporal benefit remains uncertain.

Keywords: Australia; subseasonal prediction; precipitation; temporal reconciliation; climate indices; probabilistic calibration; ensemble dependence; forecast verification.

## 1 Introduction

Weekly rainfall forecasts support field operations, while longer accumulations inform planting and water management. Four weekly amounts and their 28-day total describe the same weather sequence and should agree when added. This property, temporal coherence, holds for each dynamical ensemble member but can be lost when accumulation scales are calibrated separately.

Bottom-up aggregation sums calibrated weekly samples. Temporal reconciliation combines them with direct forecasts of longer accumulations and adjusts the scales together. Both are coherent; reconciliation adds value only when aggregate forecasts supply useful information or correct errors left by weekly summation.

Temporal hierarchies and probabilistic reconciliation are established approaches (Athanasopoulos et al. 2017; Jeon et al. 2019; Panagiotelis et al. 2023; Girolimetto et al. 2024). Rainfall applications show mixed effects across basins and scales, and interactions with temporal dependence reconstruction (Jahangir and Quilty 2022; Bellier et al. 2023). The open question here is where additional climate information should enter a rainfall hierarchy, and whether its apparent benefit survives comparison with simpler coherent forecasts.

Australia provides contrasting rainfall settings. The northern wet season is influenced by the monsoon and Madden–Julian Oscillation (MJO), whereas southwestern rainfall is concentrated in cooler months. Relationships with El Niño–Southern Oscillation (ENSO), the Indian Ocean Dipole (IOD) and the Southern Annular Mode (SAM) vary with location and season (Risbey et al. 2009; Wheeler et al. 2009). Climate indices may help predict longer accumulations, but may also duplicate information already represented by the dynamical ensemble or improve weekly forecasts without direct aggregates.

Australian calibration and bridging studies already combine statistical and dynamical predictors, including daily rainfall reordering (Schepen et al. 2014, 2018). ACCESS-S2 and studies of rainy-season retreat, southwestern rainfall and moisture transport provide the forecasting context (Wedd et al. 2022; Cowan et al. 2024; Firth et al. 2024; Reid et al. 2024). Recent subseasonal machine-learning work further motivates comparison with strong calibrated baselines (Guan et al. 2026).

We isolate climate adjustments at weekly nodes, aggregate nodes or both, retaining raw forecasts, rainfall-only weekly sums and rainfall-only reconciliation. Eight-domain ECMWF validation is followed by an ACCESS-S2 check and a previously unused 2020 forecast period. Common-covariance and conditional learning experiments separate information placement, reconciliation weights and climate-coefficient stability. These extensions follow earlier results and are identified as exploratory; the locally dated 2020 protocol precedes its scoring. The aim is to identify the added value and limits of information placement, rather than assume that more adjusted scales improve a forecast.

## 2 Data and experimental design

### 2.1 Domains and observations

Four fixed 3° by 3° domains represent northern, northeastern, southeastern and southwestern Australia (N, NE, SE and SW). An exploratory extension adds equally sized boxes in the western Kimberley (NW), central interior (CA), eastern coast (EC) and Tasmania (TAS), fixed before fitting and all retained (Table 1; Fig. 1). Each contains four archived 1.5° ECMWF cells. They are geographical supports, not official climate regions.

Verification uses 0.05° AGCD/AWAP version 1.0.1 daily rainfall from NCI (Australian Bureau of Meteorology 2023; Jones et al. 2009). Valid land cells receive exact domain-overlap and latitude-dependent area weights; forecast cells use the same bounds. AGCD totals end at 09:00 local time. For origin t, dates t + 1 through t + 28 are paired with UTC forecast accumulations, leaving a subdaily boundary offset of approximately half an hour to two hours depending on domain and daylight saving. Alternative daily pairings are retained. The late-2019 targets require 2020 observations, and the issued-2020 test requires observations through 28 January 2021.

### 2.2 Forecast archives and quality control

The ECMWF S2S AI Challenge archive contains 53 Thursday production dates in 2020, each with 20 corresponding hindcast dates during 2000–2019 and 11 members, giving 1060 origins per domain (ECMWF 2021; Vitart et al. 2017). These hindcasts use configurations associated with the production dates rather than systems operating in each verification year. Cumulative fields at days 7, 14, 21 and 28 yield four weeks, two nonoverlapping fortnights and a 28-day total, which is not a calendar month.

GRIB comparisons show that a NetCDF missing-value code also represents the lowest rainfall bin; each file's packing parameters restore it. Cumulative rainfall can decrease near the documented day-16 resolution transition (ECMWF 2026). In the primary domains, 4893/186560 member-week increments are negative, including 4070 in Week 3. Isotonic regression repairs the first three endpoints between zero and the archived day-28 total, which remains the accounting reference. Positive-part and signed-predictor refits assess sensitivity; the raw comparator is labelled ECMWF (QC) (Supplementary Table S1 and Note 5).

ACCESS-S2 research hindcasts supply nine members and 228 monthly first-day origins during 2000–2018 in every domain (Wedd et al. 2022; Australian Bureau of Meteorology, undated a). The first 28 daily fluxes are converted to millimetres, with exact cell-overlap averaging. Midpoint timestamps define UTC daily means; missing time-bound metadata are documented. Different origins, grids and ensemble sizes require within-system comparisons.

The separate issued-forecast test uses all 53 Thursday ECMWF origins in 2020 and members 0–10, fixed to match the hindcast ensemble size. Training origins and targets end by 31 December 2019; forecasts were saved before scoring. Revised indices and pooled 2020 hindcast configurations prevent interpreting this archived-period check as an exact reconstruction of historical operations.

### 2.3 Predictors and validation

RMM1 and RMM2 represent MJO state (Wheeler and Hendon 2004), alongside Niño3.4 sea surface temperature, DMI and station-based SAM (Marshall 2003). RMM is lagged two days and monthly indices two months. Every fitting sample supplies its own standardisation; the index set and lags are common across domains. Sources and archive revisions are documented in Supplementary Note 5. Independent monthly NCEP/NCAR 850 hPa winds and humidity provide physical context rather than fitting inputs (Kalnay et al. 1996; Supplementary Note 8).

Outer validation holds out each year and excludes its neighbours and all origins whose targets end in excluded years. ECMWF folds contain 897–954 training and 53 validation origins; ACCESS-S2 verifies twelve origins per fold. Five inner consecutive-year blocks, each with adjacent-year exclusions, provide held-out mean errors for covariance estimation. Parameters, standardisation, rank templates and climatology use only permitted fitting observations. Permitted years can lie on either side of the outer year, so forward verification is assessed separately. Dated plans distinguish original primary tests from later extensions (Fig. 2).

## 3 Forecast construction and verification

### 3.1 Marginal rainfall calibration

Ensemble model output statistics (EMOS) relates a predictive distribution to ensemble summary statistics (Gneiting et al. 2005). For rainfall we use a censored shifted gamma distribution, which permits a point mass at zero and a continuous positive tail (Scheuerer and Hamill 2015a; Baran and Nemoda 2016):

[[EQ3]]

In Eqn 1, Y is the nonnegative rainfall amount and Z is a latent gamma variable with positive shape κ and scale θ. The nonnegative shift δ creates a probability mass at zero: all values of Z at or below δ become dry forecasts. The gamma mean μ and variance σ², before shifting and censoring, depend on ensemble rainfall predictors:

[[EQ4]]

In Eqn 2, x̄ is the ensemble mean and s²ₓ is its sample variance across members. The six fitted parameters are a, b, c, d, e and δ; a and c provide baseline mean and variance, while b, d and e control their response to the ensemble. Positive μ and σ² give the gamma shape and scale through the last two identities. These are moments of Z, not of censored rainfall Y. Parameters minimise closed-form CRPS, a distributional forecast loss in rainfall units. Monthly fits use training origins within 45 calendar days of the month's fifteenth day, wrapping across the year boundary. Rainfall is scaled by its training mean for optimisation and returned to millimetres. Comparators include simpler seasonal EMOS, training climatology, member-wise quantile mapping and ECMWF (QC); implementation details are in Supplementary Note 5.

We call the rainfall-only predictor design H0. In H1, the weekly distributions remain exactly those of H0. Only the fortnightly and 28-day gamma means receive a climate adjustment:

[[EQ5]]

In Eqn 3, z contains standardised RMM1, RMM2, Niño 3.4, DMI and SAM values, and β contains their five fitted coefficients. The transpose makes βᵀz a scalar, dimensionless climate adjustment. Its exponential is positive, so the adjusted latent mean remains positive. H0 variance and shift remain fixed; β = 0 recovers the base distribution. Coefficients start at zero, are bounded to [−1, 1], and minimise CRPS divided by training mean rainfall plus 0.05 times their squared norm. The same regularisation applies everywhere.

Two further configurations complete the placement comparison. Hweekly applies the same adjustment only to the four weeks, retains rainfall-only direct aggregates and reconciles them. H2 adjusts all seven nodes and reconciles them. Both reuse the corresponding fitted weekly and aggregate marginals, while covariance is re-estimated from their own inner errors. BU-clim sums the climate-adjusted weeks without direct aggregates. Aggregate-only climate information has no effect on bottom-up forecasts because that construction discards aggregate nodes; weekly-only and all-node summation both equal BU-clim. Supplementary Table S22 gives the distinct configurations and avoids counting duplicate baselines.

### 3.2 Hierarchies and joint forecast samples

Let b contain the four weekly amounts. Each node denotes one forecast accumulation. The five-node hierarchy contains the weeks and their total; the seven-node hierarchy also includes the two fortnights:

[[EQ1]]

The seven-node summing matrix is

[[EQ2]]

In Eqns 4 and 5, b is a 4 × 1 column of weekly rainfall amounts. The superscript T denotes transpose. The seven entries of y₇ are ordered as Week 1, Week 2, Week 3, Week 4, days 1–14, days 15–28 and days 1–28. The 7 × 4 matrix S₇ copies the weeks in its first four rows and sums them in its last three rows. S₅ retains the first four rows and the final row, giving a 5 × 4 matrix. All amounts are in millimetres, and both summing matrices are dimensionless. Each additional aggregate has its own fitted marginal distribution. Fitting the aggregates separately allows them to contribute information beyond sums of the weekly forecasts.

Each marginal supplies 200 equally spaced midpoint quantiles. A Schaake shuffle assigns their ranks from observed rainfall trajectories sampled with replacement within 45 calendar days of the origin and within permitted training data (Clark et al. 2004). H0 and H1 share quantile positions, template cases and tie-breaking rules, including identical weekly samples before reconciliation.

A matched dependence benchmark uses ECC ranks from the 11 raw members and an 11-sample historical shuffle (Schefzik et al. 2013). Identical marginal quantiles isolate dependence effects after summation or reconciliation (Supplementary Table S2).

### 3.3 Bottom-up aggregation and nonnegative reconciliation

Bottom-up aggregation retains the four calibrated weekly samples and calculates all longer accumulations from them. It is the same reference for H0 and H1 because their weekly forecasts are unchanged. Reconciliation instead uses the direct aggregate samples as well. For a base forecast vector and positive-definite error covariance W, the unconstrained minimum-trace mapping is

[[EQ6]]

In Eqn 6, ŷ contains the separately calibrated forecasts, G maps them to four reconciled weeks, and S reconstructs every aggregate. For n = 5 or 7 nodes, S is n × 4, W is n × n and G is 4 × n. W is the covariance of observed-minus-predicted errors in mm²; the superscript −1 denotes matrix inverse. The identity GS = I₄ preserves an already coherent vector. Under unbiased base forecasts and the specified covariance, this mapping minimises reconciled error variance among linear unbiased mappings (Wickramasuriya et al. 2019). W is estimated separately for each information set and hierarchy from inner out-of-fold errors of the predictive means. We shrink the sample correlation matrix towards the identity and restore the marginal error scales. A small diagonal ridge ensures numerical invertibility. The shrinkage calculation and matrices are archived for every fold.

The linear mapping can produce negative rainfall. We therefore project each joint sample v onto the nonnegative coherent set (Wickramasuriya et al. 2020):

[[EQ7]]

In Eqn 7, v is one joint sample from the calibrated distributions, and b* is the nonnegative weekly vector that minimises its covariance-weighted squared adjustment. The inequality applies to each week; argmin returns the minimising vector. The output v* is obtained by summing b*, which ensures that its aggregates agree. Enumerating the 16 possible sets of weeks fixed at zero solves this four-variable problem. Every trajectory is nonnegative and coherent. Projection uses millimetres, where rainfall is additive.

The five-node diagonal case gives an intuitive explanation of the information being used:

[[EQ8]]

In Eqn 8, m̂ is the direct 28-day forecast, ŵₖ is the base forecast for week k, and w̃ₖ is its reconciled value. The diagonal covariance contains the weekly error variances σ²ₖ and total error variance σ²ₘ, all in mm²; s is the sum of the four weekly variances. This identity describes unconstrained linear reconciliation with diagonal W. The bracketed quantity is the direct total minus the sum of the weekly forecasts, in millimetres. A week with greater error variance receives a larger share of that discrepancy. That discrepancy combines any additional signal with calibration differences and estimation noise. The H0/H1 comparison tests whether the added climate information makes it useful for prediction. With full covariance, the weights also depend on cross-scale error correlations; positive weekly correlation alone does not determine the weight assigned to the total.

### 3.4 Scores, uncertainty and mechanism diagnostics

CRPS evaluates the full marginal predictive distribution (Gneiting and Raftery 2007). For M equally weighted samples it is

[[EQ9]]

In Eqn 9, y is the verifying rainfall amount and x⁽ⁱ⁾ is sample i at the same accumulation scale; M is the number of equally weighted samples. The first term is their mean absolute distance from the observation. The second uses all M² ordered sample pairs, including zero self-distances, and accounts for forecast spread. Together they give the CRPS of the empirical predictive distribution, in millimetres; lower is better. CRPSS is one minus mean CRPS divided by the score of permitted seasonal training climatology, evaluated on its full empirical support. Fair CRPS is reported for unequal ensemble sizes (Ferro 2014), alongside matched-size dependence controls because the deterministic quantiles are not independent random draws.

Upper-tail performance is evaluated with the 90th percentile q from permitted training origins within 45 calendar days of each origin, following the threshold-weighted scoring approach of Gneiting and Ranjan (2011). Threshold-weighted CRPS is computed by applying ordinary CRPS to the transformed samples and observation:

[[EQ10]]

In Eqn 10, max replaces each rainfall amount below q by q, for both forecasts and observations. This removes CRPS contributions below the threshold and retains the integrated loss above it, in millimetres. It scores every forecast case rather than only observed exceedances. Further diagnostics include exceedance Brier skill relative to training probabilities, interval coverage and width, and randomised probability integral transform (PIT) histograms. The Hersbach (2000) decomposition separates calibration error, termed reliability, from potential CRPS, which is uncertainty minus resolution. It describes statistical performance rather than a physical mechanism. Joint energy and variogram scores are reported in Supplementary Table S4 (Scheuerer and Hamill 2015b).

The primary factorial comparisons are H1 versus H0 within the seven-node hierarchy, seven versus five nodes within H1, and H1 seven-node reconciliation versus bottom-up aggregation, all at 28 days. To compare domains with different rainfall scales, we divide each domain's annual CRPS difference by its full-record out-of-fold climatological score and average the four contributions equally. Effects are expressed as percentages of climatological CRPS, rather than percentages of the comparison method's score. Negative values favour the first method.

Primary intervals resample 20 complete origin years 10000 times, with common draws across domains. Two-sided annual sign flips use 100000 draws and Holm adjustment over the three primary contrasts. Descriptive intervals and adjusted tests answer different questions; an interval excluding zero need not imply adjusted rejection. Domain and seasonal contrasts retain descriptive intervals. Details and the earlier homogeneous family are in Supplementary Note 5.

Finally, we test whether training errors predict the benefit of combining scales. For each outer validation fold and season s, we estimate the proportional reduction in 28-day error variance relative to summing the four weeks:

[[EQ12]]

In Eqn 11, Vlin,s is the predicted error variance of the linearly reconciled 28-day total, and VBU,s is that of the weekly sum. Ωₛ is the 7 × 7 covariance of seasonal inner held-out mean errors, estimated with the same shrinkage rule as W. P is the fitted 7 × 7 linear projection. The subscript 77 selects the final diagonal entry, corresponding to the 28-day total. Ωₛ,bb is the upper-left 4 × 4 weekly block; 1₄ is a column of four ones. Its quadratic form sums all weekly variances and cross-covariances, giving the variance of their sum. Both V terms have units mm², so ĝₛ is dimensionless. A value of 0.10 predicts a 10% variance reduction; zero predicts no change, and a negative value predicts deterioration. Here s labels a season, independently of the variance sum used locally in Eqn 8.

A coherent observation is unchanged by P, so the reconciled error is P times the base error and its covariance is PΩₛPᵀ. We average the fold-specific predicted ratios and compare them with one minus the ratio of held-out mean squared errors across years. Mean squared error also includes squared bias. Agreement requires small bias and stable training-to-test error relationships; Eqn 11 does not predict CRPS improvement. It applies exactly to the fixed linear mapping, while the nonnegative sample projection is assessed separately as an empirical comparison. Bias, slope and Spearman association summarise the 16 domain-season cases; intervals resample common years.

### 3.5 Controls and mechanism experiments

Controls compare weekly climate information, an aggregate intercept, individual indices, monthly lags and dependence templates. Ninety-nine full year-block permutations refit every nested fold using the shuffled joint climate series. Their Monte Carlo test assumes approximately exchangeable years. Supplementary Note 1 gives the fitting rules.

Forward fitting ends in 2014 and verifies 2015–2019; matching cross-validation scores to these same years separates period and design effects. BCa intervals (Efron 1987), multiyear blocks and score omissions assess concentration in particular years. Geographical and ACCESS-S2 extensions retain the settings and test hypotheses motivated by earlier results (Supplementary Tables S14–S18). Probability-mixture and forecast-selection experiments are reported in Supplementary Notes 3 and 4, Tables S19–S21 and Fig. S6.



Eight-domain effects divide paired annual CRPS differences by each domain's raw score and average domains equally. Common-year bootstrap draws preserve cross-domain dependence. Four exploratory ECMWF comparisons form one Holm family; three ACCESS comparisons form a separate family. The 2020 denominator is frozen training raw CRPS, with common circular blocks of four weekly origins and a confirmation requirement that the entire 95% interval be negative. Supplementary Notes 7 and 8 give the full protocol and inference conventions.

The additional covariance ablation evaluates H0, H1, Hweekly and H2 with their own inner-fold covariance and, separately, one common H0 covariance within each outer fold. Marginal parameters, quantiles, templates and exclusions are unchanged. This holds the reconciliation metric fixed while varying information placement. All 312 system–domain–year combinations are retained; comparisons and score interactions are exploratory, with descriptive common-year intervals (Supplementary Note 9). A conditional learning experiment fixes the rainfall-only distributions, templates and H0 covariance while fitting climate coefficients on nested subsets of 10, 15 or all permitted years. Adjacent-year exclusions leave 16–18 years, not 19. Full-sample penalties of 0.05, 0.20 and 0.50 assess regularisation. These settings are compared without choosing a winner from outer scores (Supplementary Note 10).

## 4 Results

### 4.1 Calibration provides a competitive but imperfect baseline

Monthly EMOS has Week-1 CRPSS of 0.49–0.55 across the primary domains, falling by Week 4 to 0.038 in N, 0.002 in NE, 0.022 in SE and −0.007 in SW (Fig. 3). Direct 28-day rainfall-only EMOS improves on raw ECMWF over the full cross-validation period in every domain, although the more flexible monthly model worsens the simpler seasonal score in NE by 0.24 mm (Table 2).

Before adding climate predictors, five-node reconciliation changes 28-day CRPS by −0.16% of climatological score (95% interval −0.35 to 0.03%) relative to BU-rain; none of its primary comparisons passes Holm adjustment. Adding fortnightly nodes within H1 changes the normalised score by only +0.003% (−0.159 to 0.160%), with absolute domain changes below 0.02 mm. Additional nodes alone therefore contribute little (Supplementary Table S3).

### 4.2 Eight-domain comparisons depend on the reference forecast

Across ECMWF domains, H1 changes 28-day CRPS by −5.824% of raw score relative to raw forecasts (95% interval −7.564 to −4.140%; Holm p = 0.00004), −0.781% relative to BU-rain (−1.418 to −0.258%; p = 0.01462), −1.046% relative to BU-clim (−1.501 to −0.606%; p = 0.00084), and −0.331% relative to H0 (−0.742 to 0.056%; p = 0.13023). Favourable domains number eight, six, eight and five, respectively (Table 3; Fig. 4; Supplementary Table S23).

Hweekly and H1 have similar scores: their difference is +0.025% (−0.212 to 0.260%). Both improve on BU-clim by about 1%, whereas H2 minus BU-clim spans zero and H2 is worse than H1 in every domain. Thus the pooled result does not identify aggregate-only climate adjustment as uniquely effective (Supplementary Table S22).

### 4.3 ACCESS-S2 reveals the weakness of weekly climate adjustment

ACCESS-S2 H1 minus BU-clim is −5.726% of raw score (95% interval −7.659 to −3.900%; Holm p = 0.00009). Yet BU-clim is worse than BU-rain in seven domains and worse than raw forecasts in NE, NW and EC. In NE, BU-rain, H1 and BU-clim score 17.806, 17.997 and 19.775 mm. Across all eight domains, H1 minus BU-rain is only −0.069% (descriptive interval −0.946 to 0.774%). Improvement over BU-clim is consequently insufficient evidence of a gain over simple calibrated summation (Supplementary Tables S24 and S28).

H1 minus H0 is +0.468% (−0.556 to 1.451%; Holm p = 0.440). Northern H0 improves on BU-rain by −0.759 mm, but H1 adds only −0.025 mm relative to H0, with an interval of −1.166 to 1.431 mm. That interval contains both zero and the ECMWF northern difference. The second system is informative about baseline weakness, but insufficient to establish either replication or absence of the northern climate increment (Table 3).

### 4.4 The northern signal accompanies changes in the predictive distribution

The original four-domain H1-minus-H0 test gives −0.31% of climatological score (95% interval −0.70 to 0.06%; Holm p = 0.268; Table 4). Northern CRPS falls by 0.372 mm, with most of the effect in December–February, when it falls from 47.69 to 46.14 mm. March–May instead worsens from 16.93 to 17.11 mm. The northern finding was selected for examination after these results and remains exploratory (Fig. 5; Supplementary Fig. S4).

In N, bottom-up summation widens the central 80% interval to 109.68 mm and produces 88.8% coverage. H1 narrows it to 101.29 mm with 84.1% coverage (Fig. 6; Table 5). Relative to BU-rain, both reliability CRPS and potential CRPS decrease, by 0.085 and 0.456 mm, respectively. The difference is therefore not solely a spread correction. Seasonal 90th-percentile exceedances account for 68/1060 origins (6.4%) and 20.7% of direct-total CRPS. Wet-season amounts dominate millimetre-valued losses; event and joint-trajectory diagnostics retain mixed rankings (Supplementary Tables S4 and S7).

### 4.5 Robustness checks identify concentration rather than a universal climate effect

H1 improves on BU-rain in fourteen northern years (Fig. 7). Five years account for 87.0% of the net difference. Across all 15504 five-year omissions, the retained difference ranges from −0.884 to −0.094 mm, with median −0.543 mm. Against H0, three omissions reverse the sign. These are score-sensitivity distributions, not confidence intervals or refits (Supplementary Table S14; Fig. S8). Multiyear blocks widen uncertainty, and four constituent northern grid cells give H1-minus-BU-rain effects from −1.259 to +0.044 mm (Supplementary Tables S10 and S13).

The northern direction persists under quality-control alternatives and matched-size dependence controls, although absolute calibration changes (Supplementary Tables S1, S2, S5 and S9). Of 99 joint year-block permutations, two beat the identity score, giving a one-sided Monte Carlo p of 0.030 under approximate year exchangeability. Intercept, individual-index and lag controls do not identify a stable causal pathway; DMI's favourable single-index score was inspected post hoc (Supplementary Tables S8 and S18).

### 4.6 Forward and new-period tests change the ordering

Northern 2015–2019 forward scores favour raw ECMWF (17.847 mm), followed by BU-clim (18.225), H1 (18.639), H0 (19.134) and BU-rain (19.282). Climate information helps within the calibrated system while every individual calibrated alternative remains worse than raw forecasts (Table 6). On those same years, cross-validation gives H1 18.073 mm and BU-clim 18.182 mm. Both period and validation design matter (Supplementary Tables S12 and S15; Fig. S7).

In 2020, H1 beats BU-clim in six domains but BU-rain in only N, NW and EC. The frozen pooled H1-minus-BU-clim contrast is −0.923% of training raw CRPS (95% four-origin block interval −2.555 to 0.413%); longer blocks also include zero (Fig. 8). The confirmation criterion is unmet, leaving insufficient information about transfer rather than demonstrating no effect. A post hoc normal approximation gives an 80%-power effect size of about 2.15%, conditional on within-year block variability. It cannot quantify interannual power (Supplementary Note 7 and Tables S25 and S27).

### 4.7 All-node deterioration persists with common reconciliation weights

With each configuration's own covariance, H2 minus H1 is +0.978% of raw CRPS in ECMWF and +5.536% in ACCESS-S2. Fixing all four configurations to H0's covariance reduces these differences to +0.757% (95% descriptive interval 0.389–1.116%) and +3.849% (2.779–5.019%), respectively. Re-estimated weights therefore influence the magnitude but do not fully account for H2's disadvantage (Supplementary Table S28; Fig. S11).

The score interaction asks whether adjusting the weeks changes the incremental effect of aggregate adjustment. It is defined as (H2 minus Hweekly) minus (H1 minus H0), with positive values indicating less favourable aggregate adjustment when weeks are already adjusted. Under common H0 weights it is +1.083% (0.845–1.363%) in ECMWF and +2.249% (1.561–3.316%) in ACCESS-S2. This cross-system pattern supports a statistical interaction in the sampled forecasts. It does not identify information-theoretic redundancy, overfitting or a physical cause. Hweekly minus H1 remains uncertain with common weights in both systems.

### 4.8 More climate-fitting data and stronger regularisation reduce the penalty

With common H0 covariance, the H2-minus-H1 contrast decreases from +1.712% to +0.757% of raw CRPS as ECMWF climate fitting expands from ten to all permitted years. The paired difference is +0.955 percentage points (95% descriptive interval 0.633–1.277). ACCESS-S2 gives a corresponding decrease from +8.502% to +3.849%, a difference of +4.653 points (2.723–6.907). Fifteen-year fits lie between these endpoints (Supplementary Table S29; Fig. S12).

Increasing the full-sample penalty from 0.05 to 0.50 reduces H2 minus H1 to −0.010% in ECMWF and +0.729% in ACCESS-S2. H1's advantage over BU-clim also contracts, from −0.906% to −0.325% and from −4.514% to −1.041%, respectively. Both experiments are consistent with unstable climate adjustments contributing to the comparison. Because the rainfall-only model remains fixed, this is a learning curve for the climate adjustment, not the complete forecasting pipeline.

## 5 Discussion

The main finding is a contrast between partial and comprehensive climate adjustment. H1 and Hweekly retain rainfall-only forecasts at one level, whereas H2 adjusts every node. In both systems, H2's disadvantage persists when reconciliation uses the same covariance. The pattern therefore involves the component distributions and their joint adjustment, rather than only different estimated weights. The conditional learning curves strengthen this interpretation: larger climate-fitting samples and stronger penalties reduce H2 deterioration in both systems. They also narrow H1’s advantage over BU-clim. Retaining rainfall-only components can therefore act as a statistical constraint on variable climate adjustments in these experiments. The tests do not isolate that contribution from changes in marginal bias and spread.

Baseline choice determines the practical meaning of this pattern. ECMWF H1 improves on raw forecasts and both summation baselines in retrospective pooling, but not clearly on H0. ACCESS-S2 H1 substantially improves on a weak BU-clim comparator while remaining close to BU-rain overall. The interaction alone does not establish useful climate information beyond H0. Table 7 distinguishes the evidence supporting each conclusion.

Temporal transfer is less stable. Northern forward scores favour BU-clim over H1 and raw ECMWF over both; the 2020 pooled interval also crosses zero. A single new forecast year supplies a temporal check without estimating interannual uncertainty. Additional untouched years require an externally timestamped protocol, matched member counts and explicit treatment of model changes.

The physical setting helps interpret where large score differences arise. Northern summer has humid low-level westerlies and concentrated rainfall, consistent with MJO and rainy-season research (Wheeler et al. 2009; Cowan et al. 2024). However, the wind–gain correlation is −0.25 with an interval of −0.66 to 0.23. Circulation composites describe the wet-season background rather than predict reconciliation gains (Supplementary Table S26; Fig. S10). DMI's post hoc performance could reflect earlier or correlated ocean conditions; IOD events usually weaken with the summer monsoon (Australian Bureau of Meteorology, undated b).

Covariance-based theoretical gains are also optimistic in these fitted forecasts (Supplementary Note 8; Fig. S9). Linear minimum-trace theory does not guarantee improvements in CRPS after covariance estimation, nonnegative projection and temporal transfer. Results for particular autoregressive hierarchies do not resolve this application either (Neubauer and Filzmoser 2024). Dependence and power-map checks further show why dispersion changes should not automatically be interpreted as new predictive information (Supplementary Notes 1 and 2).

The evidence concerns eight geographical boxes and the sampled systems, not all Australia or the general usefulness of reconciliation. Operational evaluation should retain raw forecasts, both weekly sums and H0. More flexible mixtures and training-only selectors did not establish a consistently superior adaptive rule (Supplementary Notes 3 and 4).

## 6 Conclusions

In eight-domain ECMWF cross-validation, aggregate climate adjustment with reconciliation improves on raw forecasts and both weekly-summation baselines, but not clearly on rainfall-only reconciliation. ACCESS-S2 also favours it over climate-informed summation, whose poor performance against simpler forecasts limits that comparison.

Adjusting every node is less effective than adjusting aggregates alone in both systems. This deterioration persists under a common covariance, showing that differences in estimated reconciliation weights are not its sole explanation. More climate-fitting years and stronger regularisation reduce the penalty in both systems, supporting an estimation-stability explanation. This does not establish a physical mechanism or select an operational penalty.

The northern forward ordering and inconclusive 2020 test prevent a claim of stable temporal benefit. Physical diagnostics describe the wet-season setting but do not identify a reliable predictor of gain. Climate information should therefore be evaluated at the scale where it is introduced, against raw and simple coherent forecasts, with temporal transfer assessed separately from retrospective agreement.

## Data availability

Analysis source and the versioned research snapshot are available at https://github.com/yms2000111/jshess-rainfall-reconciliation (release v0.1.0, commit 9605a8a5cd5a9c3f580a9d4a44afabb6510cc2bd). The snapshot includes processed regional inputs, score tables, metadata, mathematical audits and manuscript materials; its manifest records file hashes. Large fitting caches and global source archives are excluded and can be regenerated using the supplied scripts. Later revisions are identified separately. The public deposit dated 26 October 2026 is not evidence of prospective preregistration. ECMWF inputs come from the S2S AI Challenge archive, AGCD from NCI (https://doi.org/10.25914/hjqj-0x55), ACCESS-S2 from the NCI research catalogue and NCEP/NCAR reanalysis from NOAA PSL through IRI. Source licences and attribution continue to apply. Natural Earth supplies the public-domain outline.

## Conflicts of interest

The authors declare that they have no known competing financial interests or personal relationships that could have appeared to influence the work reported in this paper.

## Declaration of funding

The authors received no specific funding for this work.

## Acknowledgements and use of AI

The authors used OpenAI Codex for literature retrieval, code development, analysis, figures and language editing, and take responsibility for the final manuscript.

## References

Athanasopoulos G, Hyndman RJ, Kourentzes N, Petropoulos F (2017) Forecasting with temporal hierarchies. European Journal of Operational Research 262, 60–74. https://doi.org/10.1016/j.ejor.2017.02.046

Australian Bureau of Meteorology (2023) Australian Gridded Climate Data (AGCD) v1.0.1 / Australian Water Availability Project (AWAP). National Computational Infrastructure. https://doi.org/10.25914/hjqj-0x55

Australian Bureau of Meteorology (undated a) ACCESS-S research hindcast data. https://s2dprediction.nci.org.au/access-s/reference/hindcast_data.html/ (accessed 24 October 2026).

Australian Bureau of Meteorology (undated b) Indian Ocean Dipole. https://www.bom.gov.au/resources/learn-and-explore/climate-knowledge-centre/climate-factors/indian-ocean-dipole (accessed 24 October 2026).

Baran S, Nemoda D (2016) Censored and shifted gamma distribution based EMOS model for probabilistic quantitative precipitation forecasting. Environmetrics 27, 280–292. https://doi.org/10.1002/env.2391

Bellier J, Whitin B, Scheuerer M, Brown J, Hamill TM (2023) A Multi-Temporal-Scale Modulation Mechanism for the Postprocessing of Precipitation Ensemble Forecasts: Benefits for Streamflow Forecasting. Journal of Hydrometeorology 24, 659–673. https://doi.org/10.1175/JHM-D-22-0119.1

Clark M, Gangopadhyay S, Hay L, Rajagopalan B, Wilby R (2004) The Schaake Shuffle: A Method for Reconstructing Space–Time Variability in Forecasted Precipitation and Temperature Fields. Journal of Hydrometeorology 5, 243–262. https://doi.org/10.1175/1525-7541(2004)005<0243:TSSAMF>2.0.CO;2

Cowan T, Hinds E, Marshall AG, Wheeler MC, de Burgh-Day C (2024) Observing and forecasting the retreat of northern Australia’s rainy season. Journal of Southern Hemisphere Earth Systems Science 74, ES23022. https://doi.org/10.1071/ES23022

ECMWF (2021) CliMetLab S2S AI Challenge data access package. https://github.com/ecmwf-lab/climetlab-s2s-ai-challenge (accessed 23 October 2026).

ECMWF (2026) Issues with data: issue with accumulated fields at day 16. S2S documentation. https://confluence.ecmwf.int/pages/viewpage.action?pageId=639218194 (accessed 23 October 2026).

Efron B (1987) Better Bootstrap Confidence Intervals. Journal of the American Statistical Association 82, 171–185. https://doi.org/10.1080/01621459.1987.10478410

Ferro CAT (2014) Fair scores for ensemble forecasts. Quarterly Journal of the Royal Meteorological Society 140, 1917–1923. https://doi.org/10.1002/qj.2270

Firth R, Kala J, Hudson D, Hawke K, Marshall A (2024) ACCESS-S2 seasonal forecasts of rainfall and the SAM–rainfall relationship during the grain growing season in south-west Western Australia. Journal of Southern Hemisphere Earth Systems Science 74, ES24004. https://doi.org/10.1071/ES24004

Girolimetto D, Athanasopoulos G, Di Fonzo T, Hyndman RJ (2024) Cross-temporal probabilistic forecast reconciliation: Methodological and practical issues. International Journal of Forecasting 40, 1134–1151. https://doi.org/10.1016/j.ijforecast.2023.10.003

Gneiting T, Raftery AE (2007) Strictly Proper Scoring Rules, Prediction, and Estimation. Journal of the American Statistical Association 102, 359–378. https://doi.org/10.1198/016214506000001437

Gneiting T, Raftery AE, Westveld AH, Goldman T (2005) Calibrated Probabilistic Forecasting Using Ensemble Model Output Statistics and Minimum CRPS Estimation. Monthly Weather Review 133, 1098–1118. https://doi.org/10.1175/MWR2904.1

Gneiting T, Ranjan R (2011) Comparing Density Forecasts Using Threshold- and Quantile-Weighted Scoring Rules. Journal of Business & Economic Statistics 29, 411–422. https://doi.org/10.1198/jbes.2010.08110

Guan H, Mouatadid S, Orenstein P, Cohen J, Dong H, Ni Z, Berman J, Flaspohler G, Lu A, Schloer J, Talib J, Weyn JA, Mackey L (2026) Advancing subseasonal forecasting with machine learning. Nature 658, 951–957. Published online 14 October 2026. https://doi.org/10.1038/s41586-026-11126-x

Hersbach H (2000) Decomposition of the Continuous Ranked Probability Score for Ensemble Prediction Systems. Weather and Forecasting 15, 559–570. https://doi.org/10.1175/1520-0434(2000)015<0559:DOTCRP>2.0.CO;2

Jahangir MS, Quilty J (2022) Temporal Hierarchical Reconciliation for Consistent Water Resources Forecasting Across Multiple Timescales: An Application to Precipitation Forecasting. Water Resources Research 58, e2021WR031862. https://doi.org/10.1029/2021WR031862

Jeon J, Panagiotelis A, Petropoulos F (2019) Probabilistic forecast reconciliation with applications to wind power and electric load. European Journal of Operational Research 279, 364–379. https://doi.org/10.1016/j.ejor.2019.05.020

Jones DA, Wang W, Fawcett R (2009) High-quality spatial climate data-sets for Australia. Australian Meteorological and Oceanographic Journal 58, 233–248. https://doi.org/10.22499/2.5804.003

Kalnay E, Kanamitsu M, Kistler R, Collins W, Deaven D, Gandin L, Iredell M, Saha S, White G, Woollen J, Zhu Y, Chelliah M, Ebisuzaki W, Higgins W, Janowiak J, Mo KC, Ropelewski C, Wang J, Leetmaa A, Reynolds R, Jenne R, Joseph D (1996) The NCEP/NCAR 40-Year Reanalysis Project. Bulletin of the American Meteorological Society 77, 437–472. https://doi.org/10.1175/1520-0477(1996)077<0437:TNYRP>2.0.CO;2

Marshall GJ (2003) Trends in the Southern Annular Mode from Observations and Reanalyses. Journal of Climate 16, 4134–4143. https://doi.org/10.1175/1520-0442(2003)016<4134:TITSAM>2.0.CO;2

Neubauer L, Filzmoser P (2024) Rediscovering Bottom-Up: Effective Forecasting in Temporal Hierarchies. arXiv preprint, version 1, 2407.02367. https://arxiv.org/abs/2407.02367v1

Panagiotelis A, Gamakumara P, Athanasopoulos G, Hyndman RJ (2023) Probabilistic forecast reconciliation: Properties, evaluation and score optimisation. European Journal of Operational Research 306, 693–706. https://doi.org/10.1016/j.ejor.2022.07.040

Reid KJ, Hudson D, King AD, Lane TP, Marshall AG (2024) Atmospheric water vapour transport in ACCESS-S2 and the potential for enhancing skill of subseasonal forecasts of precipitation. Quarterly Journal of the Royal Meteorological Society 150, 68–80. https://doi.org/10.1002/qj.4585

Risbey JS, Pook MJ, McIntosh PC, Wheeler MC, Hendon HH (2009) On the Remote Drivers of Rainfall Variability in Australia. Monthly Weather Review 137, 3233–3253. https://doi.org/10.1175/2009MWR2861.1

Schefzik R, Thorarinsdottir TL, Gneiting T (2013) Uncertainty Quantification in Complex Simulation Models Using Ensemble Copula Coupling. Statistical Science 28, 616–640. https://doi.org/10.1214/13-STS443

Schepen A, Wang QJ, Robertson DE (2014) Seasonal Forecasts of Australian Rainfall through Calibration and Bridging of Coupled GCM Outputs. Monthly Weather Review 142, 1758–1770. https://doi.org/10.1175/MWR-D-13-00248.1

Schepen A, Zhao T, Wang QJ, Robertson DE (2018) A Bayesian modelling method for post-processing daily sub-seasonal to seasonal rainfall forecasts from global climate models and evaluation for 12 Australian catchments. Hydrology and Earth System Sciences 22, 1615–1628. https://doi.org/10.5194/hess-22-1615-2018

Scheuerer M, Hamill TM (2015a) Statistical Postprocessing of Ensemble Precipitation Forecasts by Fitting Censored, Shifted Gamma Distributions. Monthly Weather Review 143, 4578–4596. https://doi.org/10.1175/MWR-D-15-0061.1

Scheuerer M, Hamill TM (2015b) Variogram-Based Proper Scoring Rules for Probabilistic Forecasts of Multivariate Quantities. Monthly Weather Review 143, 1321–1334. https://doi.org/10.1175/MWR-D-14-00269.1

Vitart F, Ardilouze C, Bonet A, Brookshaw A, Chen M, Codorean C, Déqué M, Ferranti L, Fucile E, Fuentes M, Hendon H, Hodgson J, Kang HS, Kumar A, Lin H, Liu G, Liu X, Malguzzi P, Mallas I, Manoussakis M, Mastrangelo D, MacLachlan C, McLean P, Minami A, Mladek R, Nakazawa T, Najm S, Nie Y, Rixen M, Robertson AW, Ruti P, Sun C, Takaya Y, Tolstykh M, Venuti F, Waliser D, Woolnough S, Wu T, Won DJ, Xiao H, Zaripov R, Zhang L (2017) The Subseasonal to Seasonal (S2S) Prediction Project Database. Bulletin of the American Meteorological Society 98, 163–173. https://doi.org/10.1175/BAMS-D-16-0017.1

Wedd R, Alves O, de Burgh-Day C, Down C, Griffiths M, Hendon HH, Hudson D, Li S, Lim EP, Marshall AG, Shi L, Smith P, Smith G, Spillman CM, Wang G, Wheeler MC, Yan H, Yin Y, Young G, Zhao M, Xiao Y, Zhou X (2022) ACCESS-S2: the upgraded Bureau of Meteorology multi-week to seasonal prediction system. Journal of Southern Hemisphere Earth Systems Science 72, 218–242. https://doi.org/10.1071/ES22026

Wheeler MC, Hendon HH (2004) An All-Season Real-Time Multivariate MJO Index: Development of an Index for Monitoring and Prediction. Monthly Weather Review 132, 1917–1932. https://doi.org/10.1175/1520-0493(2004)132<1917:AARMMI>2.0.CO;2

Wheeler MC, Hendon HH, Cleland S, Meinke H, Donald A (2009) Impacts of the Madden–Julian Oscillation on Australian Rainfall and Circulation. Journal of Climate 22, 1482–1498. https://doi.org/10.1175/2008JCLI2595.1

Wickramasuriya SL, Athanasopoulos G, Hyndman RJ (2019) Optimal Forecast Reconciliation for Hierarchical and Grouped Time Series Through Trace Minimization. Journal of the American Statistical Association 114, 804–819. https://doi.org/10.1080/01621459.2018.1448825

Wickramasuriya SL, Turlach BA, Hyndman RJ (2020) Optimal non-negative forecast reconciliation. Statistics and Computing 30, 1167–1182. https://doi.org/10.1007/s11222-020-09930-0
