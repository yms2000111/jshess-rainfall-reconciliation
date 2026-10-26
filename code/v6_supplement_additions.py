"""Append new tables and complete protocol without altering the older record."""
R6=ROOT/'revision/review_v6'
pr=pd.read_csv(R6/'2020_precision.csv')
tab('Table S27. Post hoc conditional precision of the 2020 contrast. The normal-approximation detectable effect uses 80% power and a two-sided 5% criterion. It describes within-year variability, not interannual power. Values are percentages of raw training CRPS.',['Block length','Bootstrap SE','Approximate detectable effect'],[[str(r.block_length),f'{r.conditional_bootstrap_se:.3f}',f'{r.normal_approximation_mde80:.3f}'] for r in pr.itertuples()],[1.4,2.0,3.4])
me=pd.read_csv(R6/'mechanism/contrasts.csv')
for suffix,system in [('a','ECMWF'),('b','ACCESS')]:
 tab('Table S28'+suffix+'. '+system+' covariance ablation. Changes are percentages of domain raw CRPS, with equal domain weights and descriptive common-year 95% intervals. These post hoc contrasts do not replace a primary Holm family.',['Contrast','Change (%)','95% interval'],[[r.contrast,f'{r.delta:+.3f}',f'{r.lower:+.3f} to {r.upper:+.3f}'] for r in me.query('system==@system').itertuples()],[3.6,1.0,2.2])
ms=pd.read_csv(R6/'mechanism/domain_scores.csv')
tab('Table S28c. Complete ACCESS-S2 information-placement comparison, mean 28-day CRPS in millimetres. Each configuration uses its own inner-fold covariance.',['Domain','H0','H1','Hweekly','H2'],[[r.domain]+[f'{getattr(r,m):.3f}' for m in ['H0_own','H1_own','Hweekly_own','H2_own']] for r in ms.query('system=="ACCESS"').itertuples()],[1.0,1.45,1.45,1.45,1.45])
protocol=(R5/'operational_test_plan_20261025.md').read_text(encoding='utf-8')
paragraphs(supp,'''## Supplementary Note 7 Original 2020 protocol and subsequent precision analysis

The following protocol is reproduced from the locally dated file without changing its decision rule. The first external public deposit was made on 26 October 2026 in GitHub commit 9605a8a5cd5a9c3f580a9d4a44afabb6510cc2bd. That timestamp verifies this deposit, not prospective preregistration. The original file remains accessible in release v0.1.0 of https://github.com/yms2000111/jshess-rainfall-reconciliation.
''')
paragraphs(supp,protocol.replace('# Untouched forecast-period test fixed on 25 October 2026','### Original locally dated protocol').replace('## Fixed question and data','### Fixed question and data').replace('## Test and decision rule','### Test and decision rule'))
paragraphs(supp,'''### Post hoc precision calculation

After observing the single-year result, a planning sensitivity was calculated from the standard deviation of the 50000 circular-block bootstrap means. Under a normal approximation, a two-sided 5% test with 80% power requires an effect approximately (1.960 + 0.842) times that standard error. Four-origin blocks give SE = 0.766 percentage points and a detectable effect of 2.145 percentage points of raw training CRPS. Six- and eight-origin values are in Table S27. This is conditional on the observed within-year variability and block assumptions. It does not estimate power across independent years, prove the effect absent or replace the original percentile-interval decision rule.
''')
paragraphs(supp,(R6/'supporting_detail.md').read_text(encoding='utf-8'))
paragraphs(supp,'''## Supplementary Note 9 Information-placement and covariance ablation

This post hoc experiment retains all eight domains, twenty ECMWF years and nineteen ACCESS-S2 years, giving 312 outer fits. The weekly and aggregate marginal parameters are reused from the same nested fitting sets. Four configurations, H0, H1, Hweekly and H2, are evaluated with their own inner-error covariance and with a common covariance estimated from H0 errors in that outer fold. Quantiles, historical templates, tie-breaking seeds, nonnegative projection and year exclusions are held unchanged. H0 is therefore identical between the two covariance conditions.

The score interaction is (L_H2 − L_Hweekly) − (L_H1 − L_H0), where L denotes mean 28-day CRPS. It measures whether adjusting weeks changes the incremental scoring effect of adjusting aggregates. Before pooling, each domain-year contrast is divided by that domain’s full-record raw mean CRPS and multiplied by 100; eight domains receive equal weight. Positive interaction indicates that aggregate adjustment becomes less favourable when weeks are already adjusted. It is not mutual information and does not quantify physical causation.

Each system uses 50000 common-year bootstrap draws. Intervals are descriptive, and these comparisons are not retrospectively assigned primary status. Recomputed baseline scores match the archived annual scores within 0.00001 mm; the small ECMWF H1 discrepancy comes from equivalent independently optimised climate fits. All forecasts remain nonnegative and exactly coherent. The common-weight result rules out covariance re-estimation as the sole explanation of H2 deterioration, but does not separate estimation noise, repeated predictor information and distributional changes. No claim of a validated forecast-selection rule follows from this ablation.
''')
for name,caption in MOVED_CAPTIONS:figure(supp,name,caption)
figure(supp,'FigS11_covariance_ablation','Fig. S11. Information-placement contrasts under own and common H0 covariance for (a) ECMWF and (b) ACCESS-S2. Hollow squares show equal-domain effects as percentages of raw CRPS; bars are descriptive common-year 95% bootstrap intervals. Positive H2-minus-H1 values favour H1. The score interaction measures the change in aggregate-adjustment benefit when weeks are also adjusted.')
lr=pd.read_csv(R6/'learning/contrasts.csv')
labels={'years10':'10 years; 0.05','years15':'15 years; 0.05','full':'All years; 0.05','ridge020':'All years; 0.20','ridge050':'All years; 0.50'}
for suffix,system in [('a','ECMWF'),('b','ACCESS')]:
 tab('Table S29'+suffix+'. '+system+' conditional climate-adjustment learning experiment. All configurations use common H0 covariance. Effects are percentages of raw CRPS; intervals are descriptive common-year bootstrap intervals. All permitted years means 16–18 years after exclusions.',['Climate fit; penalty','Contrast','Change (%)','95% interval'],[[labels[r.scenario],r.contrast,f'{r.delta:+.3f}',f'{r.lower:+.3f} to {r.upper:+.3f}'] for r in lr.query('system==@system').itertuples()],[1.6,2.1,1.0,2.1])
lc=pd.read_csv(R6/'learning/changes_vs_full.csv')
tab('Table S29c. Paired changes in the H2-minus-H1 contrast relative to the full-sample 0.05-penalty fit. Units are percentage points of raw CRPS.',['System','Climate fit; penalty','Change','95% interval'],[[r.system,labels[r.scenario],f'{r.change_vs_full:+.3f}',f'{r.lower:+.3f} to {r.upper:+.3f}'] for r in lc.query('contrast=="H2 minus H1"').itertuples()],[1.2,2.0,1.2,2.4])
paragraphs(supp,'''## Supplementary Note 10 Conditional learning and regularisation

This exploratory experiment asks whether the information-placement contrast changes when climate coefficients are estimated more stably. The analysis plan was deposited in GitHub commit afd622c7d46515746781cbe504783c675b12e52a after two pilot folds and before the full learning experiment. It is not a prospective confirmation of an unseen hypothesis.

Within each of the 312 outer folds, the rainfall-only gamma parameters, scaling, historical rank templates and H0 covariance remain fixed at their full permitted-training estimates. Only the climate coefficients and predictor standardisation change. A seeded permutation of permitted years supplies nested subsets of ten, fifteen and all available years. The seed is 2026102603 plus the outer year; identical year subsets are used across domains within each system. Excluding the validation year and its neighbours leaves sixteen to eighteen years. These are therefore conditional climate-adjustment curves, not learning curves for the entire calibration pipeline.

The three sample-size fits use the original penalty 0.05. Full-sample fits additionally use penalties 0.20 and 0.50. Monthly fitting windows, coefficient bounds, quantiles and coupling remain unchanged. Each coefficient fit minimises the same normalised CRPS plus the squared-coefficient penalty. An optimisation retry resolves one nonconverged numerical fit; all final fits report success. No setting is selected using its outer performance. The full-sample 0.05 forecasts reproduce the common-covariance ablation before accepting a fold.

Each system retains all domains and all validation years. Fifty thousand common-year bootstrap samples describe score contrasts and paired changes between settings. The contrasts are exploratory and do not enter a new primary testing family. One nested year-subset realisation is used per fold, so the curves are conditional on that selection rather than averages over every possible subset. The public score and parameter files retain every setting, including effects on BU-clim and the score interaction.

More climate-fitting data and stronger penalties reduce H2 deterioration and narrow H1's advantage over BU-clim in both systems. These responses support a contribution from estimation instability. They do not by themselves distinguish coefficient noise from changes in marginal bias and dispersion, identify a physical pathway, or validate an operational tuning rule.
''')
figure(supp,'FigS12_learning','Fig. S12. Conditional climate-adjustment learning curves for ECMWF and ACCESS-S2. Upper panels vary the number of climate-fitting years at penalty 0.05; lower panels vary the penalty with all permitted years. H0 marginal forecasts, covariance and rank templates remain fixed within each fold. Hollow squares show H2-minus-H1 effects as percentages of raw CRPS, with descriptive common-year 95% intervals. Positive values favour aggregate-only climate adjustment. All means 16–18 permitted years.')
