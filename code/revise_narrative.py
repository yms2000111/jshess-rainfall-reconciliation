"""Assemble the focused manuscript using the frozen, computed result tables."""
from common import *
import pandas as pd,json
p=ROOT/'manuscript.md';old=p.read_text(encoding='utf-8')
if not (ROOT/'manuscript_previous.md').exists():(ROOT/'manuscript_previous.md').write_text(old,encoding='utf-8')
data=old.split('## 2 Data and experimental design')[1].split('## 3 Forecast methods')[0]
data=data.replace('Two additional analyses assess this convention. One refits the entire experiment after replacing negative weekly increments by zero and summing the resulting weeks. The other evaluates the fitted primary forecasts only at test origins for which no member has an endpoint decrease exceeding 0.1 mm. The latter is a selected-subset diagnostic, since such screening can change the sampled rainfall distribution.','The supplementary XGBoost experiment is also refitted after replacing negative weekly increments by zero and summing the resulting weeks. This alternative sensitivity concerns the XGBoost branch; it is not an alternative EMOS fit. The archive audit and all adjusted endpoints are retained so that the rainfall accounting can be checked independently.')
data=data.replace('### 2.3 Climate predictors and chronological partitions','### 2.3 Chronological partitions and auxiliary predictors')
back='## Data availability'+old.split('## Data availability')[1]
extra=[
'Baran S, Nemoda D (2016) Censored and shifted gamma distribution based EMOS model for probabilistic quantitative precipitation forecasting. Environmetrics 27, 280–292. https://doi.org/10.1002/env.2391',
'Clark M, Gangopadhyay S, Hay L, Rajagopalan B, Wilby R (2004) The Schaake shuffle: a method for reconstructing space–time variability in forecasted precipitation and temperature fields. Journal of Hydrometeorology 5, 243–262. https://doi.org/10.1175/1525-7541(2004)005<0243:TSSAMF>2.0.CO;2',
'Panagiotelis A, Gamakumara P, Athanasopoulos G, Hyndman RJ (2023) Probabilistic forecast reconciliation: properties, evaluation and score optimisation. European Journal of Operational Research 306, 693–706. https://doi.org/10.1016/j.ejor.2022.07.040']
pre,refs=back.split('## References');refs=sorted(set(refs.strip().split('\n\n')+extra));back=pre+'## References\n\n'+'\n\n'.join(refs)
S=pd.read_csv(ROOT/'results/scores.csv');B=pd.read_csv(ROOT/'results/core_comparisons.csv')
def val(k,m,col='crps',lead='D28'):return S.query('region==@k and method==@m and lead==@lead').iloc[0][col]
def seq(m,col='crps',fmt='.2f'):return ', '.join(format(val(k,m,col),fmt) for k in REGIONS)
gains=[100*(1-val(k,'EMOS MinT-NN')/val(k,'CSG EMOS')) for k in REGIONS]
head=f'''# Temporal coherence and probabilistic skill of subseasonal rainfall forecasts in four Australian regions

[Author names]

[Affiliations]

Corresponding author: [name and email]

## Abstract

Separate calibration of weekly and four-week rainfall forecasts can produce incompatible totals. We examine whether restoring temporal coherence improves probabilistic skill using ECMWF subseasonal hindcasts and Australian Gridded Climate Data in four regional domains. The dataset contains 1060 origins in 2000–2019; 265 origins in 2015–2019 form an independent test. Censored shifted gamma ensemble model output statistics (EMOS) provides five marginal rainfall distributions. Historical rank reordering supplies their dependence structure. We compare these forecasts with bottom-up aggregation and sample-wise nonnegative reconciliation using a shrunk error covariance matrix. Reconciliation lowers 28-day continuous ranked probability score (CRPS) relative to direct EMOS by {gains[0]:.2f}%, {gains[1]:.2f}%, {gains[2]:.2f}% and {gains[3]:.2f}% in the northern, northeastern, southeastern and southwestern domains. However, bottom-up aggregation performs better in the northeastern and southeastern domains, and weekly CRPS increases in 13 of 16 regional comparisons. Removing the historical dependence structure worsens reconciled 28-day CRPS in every domain. Quantile mapping, ordinary least squares and XGBoost comparisons show that neither greater model complexity nor temporal coherence gives a uniform skill advantage. The results separate the value of statistical correction from that of combining direct aggregate and weekly forecasts. Coherence is exact, whereas its contribution to rainfall skill depends on scale, region and predictive dependence.

Keywords: Australia; subseasonal prediction; precipitation; temporal reconciliation; probabilistic forecasting; EMOS; forecast calibration; ensemble dependence; forecast verification.

## 1 Introduction

Rainfall forecasts support decisions over different planning horizons. Weekly totals help schedule field operations, while four-week accumulations inform water allocation and planting. These products describe the same rainfall over nested intervals. Their totals should therefore agree. An unaltered dynamical ensemble already has this property when each weekly amount is derived from the same member trajectory. Separate statistical correction of the weekly and aggregate products can break it.

The practical question is what is gained by restoring that agreement. One solution is to retain the corrected weekly forecasts and sum them. Another is to combine the weekly forecasts with an independently corrected aggregate forecast. The second approach uses more information, but it also imports the aggregate forecast's errors into the weekly products. A coherent forecast can consequently improve one accumulation scale while worsening another.

The S2S Prediction Project provides a setting in which to examine this trade-off (Vitart et al. 2017). Subseasonal rainfall skill varies with forecast lead and climate regime. Australia's northern monsoon, eastern rainfall and southern cool-season rainfall also have different seasonal and large-scale controls (Risbey et al. 2009; Wheeler et al. 2009). A regional comparison can reveal whether aggregate information contributes similarly across these contrasting conditions.

Precipitation postprocessing must represent skewness and a probability mass at zero. Censored shifted gamma EMOS supplies a parsimonious distributional model for these features (Scheuerer and Hamill 2015; Baran and Nemoda 2016). Empirical quantile mapping offers a conventional alternative, while regression and tree boosting provide additional comparisons. None of these marginal methods automatically maintains the relationship between independently calibrated accumulation periods.

Temporal hierarchies formalise that relationship through linear aggregation constraints (Athanasopoulos et al. 2017). Minimum-trace reconciliation uses forecast error covariances to combine information across the hierarchy (Wickramasuriya et al. 2019). Nonnegative reconciliation extends the optimisation to quantities such as rainfall (Wickramasuriya et al. 2020). Applying the transformation to samples produces a coherent predictive distribution, whose marginal scores must then be evaluated empirically (Panagiotelis et al. 2023; Girolimetto et al. 2024).

This study asks one question: at which weekly and 28-day scales does probabilistic reconciliation improve on direct statistical correction and bottom-up aggregation? The EMOS comparison is central. XGBoost is a secondary benchmark, and climate-state analyses are supplementary. We retain Week 1 throughout because all four weeks are needed to define the 28-day total. Lead-dependent results describe where the trade-off occurs rather than a separate claim of methodological novelty.

## 2 Data and experimental design'''+data+'''## 3 Forecast methods and verification

### 3.1 Temporal support and baseline forecasts

For an origin t, Week k covers forecast days 7(k − 1) + 1 through 7k. The hierarchy has four non-overlapping weekly amounts and one 28-day amount. In total-first notation,

[[EQ1]]

[[EQ2]]

The code stores the same quantities in weekly-first order and applies the corresponding row permutation of S. This ordering convention changes neither the constraint nor the optimisation. The 28-day product is an accumulation from the same origin, not a calendar month or a forecast issued after Week 4.

Seasonal climatology draws 200 complete observed vectors from the pre-2013 fitting sample within a circular ±45-day calendar window. The dynamical baseline retains the 11 ECMWF (QC) members. Seasonal mean correction applies a separate multiplicative observed-to-model mean ratio at each scale, with a 0.1 mm denominator floor. Quantile mapping estimates each scale's model distribution from all training members in the same calendar window and maps test members to empirical observation quantiles. Ties use midpoint ranks, probabilities are interpolated, and values outside the training range use the endpoint probabilities. These empirical corrections preserve neither member-wise temporal totals nor unrestricted tail extrapolation.

### 3.2 Marginal EMOS and dependence reconstruction

EMOS is fitted separately for each region, accumulation scale and meteorological season: DJF, MAM, JJA and SON. Rainfall is divided by the corresponding training mean, floored at 0.1 mm, for numerical conditioning. In these scaled units the predictive distribution is

[[EQ3]]

Here the gamma distribution has shape κ = μ²/σ² and scale θ = σ²/μ; the shift δ and coefficients a, b, c and d are positive. The ensemble mean enters both the mean and variance links. Parameters minimise the exact mean censored shifted gamma CRPS over the fitting data. L-BFGS-B uses two initial parameter vectors, at most 400 iterations and log-parameter bounds from −10 to 5. All 80 region–season–scale fits converge. This explicitly defined exchangeable-member model is a precipitation EMOS baseline rather than a claim to reproduce every parameterisation in earlier studies.

Each fitted marginal distribution is represented by 200 equally spaced midpoint quantiles, transformed back to millimetres. Historical reordering follows the Schaake-shuffle principle (Clark et al. 2004). For each test origin, 200 complete observed vectors are sampled with replacement from fitting dates within ±45 calendar days. Their component-wise ranks reorder the five sets of predictive quantiles; ties are broken randomly with a fixed seed. Reordering preserves every marginal distribution while supplying a seasonally conditioned dependence template. It does not by itself enforce exact additivity after marginal calibration.

The direct EMOS forecast, M2, consists of these reordered samples. Bottom-up EMOS, M3, retains its four weekly samples and replaces the direct 28-day sample by their sum. Thus M2 and M3 have identical weekly forecasts. Their aggregate difference measures the effect of discarding the direct aggregate forecast. The comparison of M3 with reconciliation measures the value of incorporating that direct aggregate information.

### 3.3 Covariance estimation and nonnegative reconciliation

For unbiased linear base forecasts, the condition GS = I ensures that reconciliation preserves unbiasedness. Writing the base error as e = y − ŷ gives reconciled error SGe and covariance SGWGᵀSᵀ. With a positive-definite base error covariance W, generalised least squares gives

[[EQ4]]

This linear result motivates the weighting; it does not establish marginal CRPS optimality for skewed rainfall distributions. The main method, M4 or MinT-NN, applies a nonnegative quadratic projection to each joint sample v in millimetres:

[[EQ5]]

All 16 active sets of the four weekly variables are enumerated, and the feasible solution with the smallest objective is retained. Tests compare this solution with an independent nonnegative least-squares solver. Every resulting trajectory is nonnegative and exactly coherent. The transformation is nonlinear when constraints become active, so the linear unbiasedness result is not asserted for the constrained forecast.

The 102 calibration origins in 2013–2014 supply errors of the exact EMOS predictive means at all five scales. Errors are centred and standardised to obtain a correlation matrix R. We shrink its off-diagonal entries towards zero: the working correlation is (1 − λ)R + λI. The shrinkage intensity is the sum of estimated variances of off-diagonal sample correlations divided by the sum of their squared values, clipped to [0, 1]. Each variance is estimated as the mean squared deviation of standardised cross-products divided by the calibration sample size. Multiplying by the original error standard deviations recovers W; a relative diagonal ridge of 10⁻⁸ ensures numerical stability. This fully specified plug-in rule is a regularisation convention, not a CRPS-trained covariance model.

Calibration errors have temporal dependence, so this covariance rule does not account for their full effective sample size. We retain the estimated matrix and compare it with a diagonal version. W is fixed within each region; the EMOS marginal variance changes with predicted rainfall, but the reconciliation covariance does not. The latter distinction identifies a natural extension to conditional covariance estimation.

For interpretation, a diagonal W gives the following unconstrained adjustment:

[[EQ6]]

[[EQ7]]

The mismatch between the direct total and the sum of weekly forecasts is allocated according to error variances. With weekly variances of one, total variance of four, weekly forecasts of one and a direct total of eight, the solution gives four weekly values of 1.5 and a total of six. The general covariance case also includes correlations between the direct-total error and weekly errors. Positive inter-week correlation alone therefore does not determine whether the direct total receives more weight.

Two additional comparisons isolate implementation choices. One applies the unconstrained full-covariance projection, truncates the four weekly amounts at zero and recomputes the total. The other independently permutes each EMOS marginal sample before constrained reconciliation, removing the historical dependence template while retaining the same marginal values. These comparisons use the same fitted parameters and test cases as M4.

### 3.4 Regression and machine-learning comparisons

OLS and XGBoost predict log(1 + y/d), where d is seven days for a weekly total and 28 for the aggregate. Predictors are log-transformed ensemble mean daily rainfall and spread, annual and semiannual sine and cosine terms, and the lagged climate indices described in Section 2.3. OLS includes an intercept and standardises predictors using fitting-period moments. Separate models are fitted at each scale.

XGBoost uses squared-error loss, learning rate 0.04, minimum child weight 10 and L2 penalty 10 (Chen and Guestrin 2016). A validation grid combines depths 2 and 3 with 100 and 250 boosting rounds. All regions select depth 2 and 100 rounds. Complete five-component transformed residual vectors from 2013–2014 are sampled within ±60 calendar days, using the full pool when fewer than 20 origins are available. Adding each vector to the point prediction and applying the inverse transformation, truncated at zero, produces 200 trajectories. Supplementary experiments share a model across the four weekly leads, remove the climate predictors, and apply diagonal nonnegative reconciliation. These models remain distinct from the main EMOS parameterisation.

### 3.5 Scores and uncertainty

CRPS is the primary score (Gneiting and Raftery 2007). For an empirical forecast with M values and an observed amount y,

[[EQ8]]

CRPSS is one minus mean forecast CRPS divided by mean seasonal-climatology CRPS. The reference uses fitting-period observations only, with no test-year data. This is a chronological holdout experiment rather than leave-one-year-out validation. Keeping all fitting and calibration years before the test also avoids future information entering model selection.

We report Brier skill for exceeding the seasonal training upper tercile, reliability diagrams, and the coverage and width of central 80% intervals. RMSE, MAE and mean bias of the predictive mean are auxiliary diagnostics. Reliability diagrams pool Weeks 2–4 and show only probability bins with at least 20 cases. Bottom-up and direct EMOS curves coincide for these weeks because the two methods differ only at the aggregate scale.

Ordinary CRPS evaluates the delivered finite predictive distributions. Fair CRPS is archived as a sensitivity diagnostic for ensemble-size comparisons (Ferro 2014), but its independent-sampling interpretation does not apply directly to stratified EMOS quantiles or dependent reconciled samples. Exact analytic EMOS CRPS is also retained to check the 200-quantile approximation. Reconciliation comparisons all use the same number of samples.

Paired uncertainty intervals resample the five complete test-origin years with replacement, 5000 times, retaining every within-year origin and lead. Each year contains 53 origins. This preserves within-year clustering, including overlapping forecast windows. The limited number of years and windows crossing year boundaries remain constraints on inference. Intervals are presented as descriptive resampling uncertainty, not evidence of broad climatic generality. A 40-comparison table contains centred-bootstrap p values and Benjamini–Hochberg adjustments for the two reference methods, four regions and five scales (Benjamini and Hochberg 1995); conclusions emphasise effect sizes and their scale dependence.

## 4 Results

### 4.1 Correction skill varies across regions

'''
results=f'''Table 2 compares the 28-day scores, and Fig. 3 shows their weekly counterparts. Direct EMOS gives aggregate CRPS values of {seq('CSG EMOS')} mm in N, NE, SE and SW, respectively. Quantile mapping gives {seq('Quantile mapping')} mm. ECMWF (QC) remains competitive, with values of {seq('Raw')} mm. OLS has the lowest 28-day CRPS among the displayed methods in N, while bottom-up EMOS is best in NE and SE and reconciled EMOS is best in SW. No single correction dominates all four domains.

The improvement attributable to correction is distinct from that attributable to aggregation. In NE, direct EMOS already improves on ECMWF (QC), and bottom-up aggregation then lowers CRPS further. In N, both direct and reconciled EMOS remain behind the dynamical forecast. The use of a rainfall distribution with an explicit zero mass is therefore useful modelling structure, but not sufficient by itself to establish better predictive skill.

### 4.2 Direct aggregate information has uneven value

MinT-NN gives 28-day CRPS values of {seq('EMOS MinT-NN')} mm. Relative to direct EMOS, the reductions are {', '.join(f'{v:.2f}%' for v in gains)}. Relative to bottom-up aggregation, however, the changes are −0.052, +0.454, +0.040 and −0.099 mm. Thus the direct aggregate contributes useful information in N and SW in this sample, while its inclusion weakens the aggregate score in NE and SE (Fig. 4).

The year-block intervals for the 28-day change relative to direct EMOS are −0.430 to +0.272 mm in N, −0.675 to +0.051 mm in NE, −0.451 to −0.033 mm in SE and −0.202 to +0.215 mm in SW. Relative to bottom-up aggregation, the corresponding intervals are −0.320 to +0.216, +0.206 to +0.846, −0.019 to +0.111 and −0.158 to −0.054 mm. The strongest contrast in these aggregate results is the opposite response of NE and SW to inclusion of the direct-total forecast.

Weekly outcomes do not follow the aggregate ranking. Reconciliation increases CRPS in 13 of the 16 region–week comparisons; the remaining improvements occur in SE Week 3 and SW Weeks 3 and 4. The largest weekly deterioration is 0.125 mm in NE Week 4. Since bottom-up aggregation leaves weekly forecasts unchanged, the weekly comparisons with direct EMOS and bottom-up are identical. Small aggregate gains should therefore be interpreted alongside changes in the individual weekly products.

### 4.3 Coherence and calibration measure different properties

The direct, historically reordered EMOS forecasts have mean absolute sample-wise aggregation discrepancies of {seq('CSG EMOS','coherence_mae')} mm. Both bottom-up and MinT-NN remove these discrepancies to numerical precision. Exact agreement follows from the construction of the forecasts and is not itself a measure of predictive accuracy.

At 28 days, central 80% interval coverage changes from {', '.join(f'{100*val(k,"CSG EMOS","coverage80"):.1f}%' for k in REGIONS)} under direct EMOS to {', '.join(f'{100*val(k,"EMOS MinT-NN","coverage80"):.1f}%' for k in REGIONS)} under MinT-NN. Table 3 gives the associated widths. Figure 5 shows upper-tercile reliability, and Fig. 6 compares interval coverage across all five scales. These diagnostics reveal features that an aggregate CRPS ranking alone cannot describe.

The predictive dependence template has a larger aggregate effect than several changes in the reconciliation weights. Independently permuting the same marginal EMOS values before MinT-NN gives 28-day CRPS values of {seq('EMOS independent-NN')} mm, worse than historical reordering in every region. This comparison changes dependence without changing the base marginal quantiles. It demonstrates that specifying marginal rainfall distributions is not enough for a meaningful probabilistic aggregation experiment.

### 4.4 Weighting and nonnegative treatment

Estimated correlation-shrinkage intensities are 0.224, 0.178, 0.115 and 0.112 in N, NE, SE and SW. Full-covariance MinT-NN is not uniformly better than its diagonal counterpart, whose 28-day scores are {seq('EMOS diagonal-NN')} mm. The small differences indicate that covariance estimation, as well as the choice of covariance structure, contributes to the final performance.

Truncating the unconstrained weekly projection and recomputing the total gives scores of {seq('EMOS clip-sum')} mm. These are close to the constrained optimum in this sample, although the operations are mathematically different. The explicit constrained method provides the minimum of the stated weighted objective without relying on a subsequent clipping rule.

Annual skill matrices, climate-state contrasts and observation-date sensitivities are supplied in the supplementary material. Climate indices are not used by the EMOS forecasts, so those contrasts describe the conditions under which the same correction and reconciliation procedures are evaluated. They are not additional fitted subgroup models.

## 5 Discussion

The main result is a distinction between consistency and information. Summing calibrated weekly forecasts guarantees a coherent total while discarding the independently calibrated aggregate. Reconciliation includes that aggregate, but its value depends on its error structure relative to the weekly forecasts. The northeastern and southwestern results show that the same operation can respectively weaken and strengthen a coherent aggregate product.

The diagonal formula makes the compromise transparent: only the mismatch between the direct total and the weekly sum drives the linear adjustment. Yet neither its magnitude nor its sign establishes whether the adjustment is useful. Errors shared across scales can make apparently independent aggregate information redundant. In the general covariance case, correlations between the total and its components also matter. For this reason, the empirical bottom-up comparison is more informative than a claim that coherence alone produces skill.

Probabilistic dependence is central to this interpretation. Historical reordering preserves seasonal relationships among observed rainfall totals while allowing independently fitted marginal distributions. The marked degradation after independent permutation shows that an arbitrary joint distribution can distort the reconciliation experiment even when every base marginal is unchanged. An operational extension could use forecast-conditioned dependence or ensemble copula coupling, evaluated against the historical template used here.

The forecast uncertainty also has two distinct roles. EMOS allows marginal variance to change with predicted rainfall; the covariance matrix used in reconciliation summarises calibration-period point errors. A fixed regional matrix cannot express every flow-dependent relationship. Estimating a conditional matrix could improve the weighting, but would require enough calibration cases to avoid replacing a stable approximation with a noisy one. The present full-versus-diagonal comparison quantifies the difference attainable with the available calibration period.

The analysis uses a strict chronological test rather than interleaved cross-validation. It reflects a forecasting sequence in which past years determine future corrections. Five test years nevertheless contain few independent climate episodes, and 53 origins per year do not provide 53 independent 28-day outcomes. Whole-year resampling addresses much of the within-year clustering but does not create additional years. Repeating the study over additional held-out periods would test the stability of the regional contrasts.

Data support further defines the interpretation. These four boxes sample contrasting regimes; they are not official NRM climate-region polygons or national coverage. Regional averaging reduces displacement errors and can conceal local failures. The 2020 production-date archive also contains a documented accumulated-field discontinuity, and its quality-control treatment cannot reconstruct unavailable native-grid rainfall. The AGCD local-day convention introduces a separate temporal-support issue. These details are part of the forecast product being assessed and are recorded with the data extracts.

For forecast services, the practical implication is to assess a coherent set of products rather than select a method from a single aggregate score. A modest improvement in the 28-day CRPS may coexist with weekly degradation or changed interval coverage. Bottom-up aggregation is a particularly useful benchmark because it answers whether the direct aggregate forecast contributes information beyond the weekly forecasts already available to users.

## 6 Conclusions

Probabilistic temporal reconciliation restores exact agreement between four weekly rainfall accumulations and their 28-day total. In this ECMWF–AGCD experiment it slightly improves the direct EMOS aggregate score in all four domains, but improves on bottom-up aggregation in only two. Most weekly CRPS changes are adverse, and the dependence template materially affects the aggregate result.

These outcomes support an evaluation centred on scale-specific trade-offs. Separate calibration, bottom-up aggregation and covariance-weighted reconciliation answer different forecasting questions. Their comparison shows when direct aggregate information helps and when a simpler coherent forecast performs better. The accompanying Python workflow, archived forecasts, quality audits and original figures make these distinctions reproducible.

'''
p.write_text(head+results+back+'\n',encoding='utf-8')
print('Manuscript words',len((head+results).split()))
