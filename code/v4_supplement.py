"""Executed inside the Word build after original supplementary tables."""
def tab(caption,headers,rows,widths):table(supp,caption,headers,rows,widths,newpage=True)
tab('Table S1c. Northern H1 minus BU-rain under complete quality-control refits. Differences and year-block intervals are in millimetres.',['Treatment','Difference','95% interval'],[['Isotonic','−0.541','−0.951 to −0.154'],['Positive-part','−0.507','−0.927 to −0.113'],['Signed predictors','−0.493','−0.918 to −0.093']],[2.5,1.6,2.7])
om=pd.read_csv(V4/'multiyear_influence.csv');rows=[]
for r in om.itertuples():
 if r.omission=='Exhaustive five-year omissions':rows.append([r.baseline,'Every five-year omission',f'{r.minimum:+.3f} to {r.maximum:+.3f}',f'{100*r.fraction_favourable:.2f}% favourable'])
 else:rows.append([r.baseline,r.omission,f'{r.delta:+.3f}',f'{int(r.better_years)}/{int(r.remaining_years)} favourable'])
tab('Table S14. Northern score omissions. The selected five years are 2000, 2008, 2010, 2016 and 2019. All 15504 five-year combinations are also enumerated; no model is refitted.',['Reference','Omitted scores','Mean or range (mm)','Direction'],rows,[1.1,2.05,1.85,1.8])
mm=pd.read_csv(V4/'matched_validation_summary.csv');rows=[[r.domain,SHORT[r.method],f'{r.loyo_crps:.3f}',f'{r.forward_crps:.3f}',f'{r.forward_minus_loyo:+.3f}'] for r in mm.itertuples()]
tab('Table S15. Matched-period comparison on 2015–2019. LOYO uses permitted years on either side of the verification year; forward fitting ends in 2014. Scores are millimetres.',['Code','Method','LOYO','Forward','Difference'],rows,[.6,2.3,1.25,1.25,1.4])
cv=pd.read_csv(V4/'coverage/annual_scores.csv').query('lead=="D28"');rows=[[SHORT[m]]+[f'{cv.query("domain==@k and method==@m").crps.mean():.3f}' for k in EXTRA_DOMAINS] for m in ['Raw','Bottom_up','Weekly_climate_BU','H0','H1']]
tab('Table S16a. Additional-domain 28-day CRPS (mm) from the unchanged ECMWF fitting protocol. Every specified domain is retained.',['Method',*EXTRA_DOMAINS],rows,[2.4,1.1,1.1,1.1,1.1])
po=pd.read_csv(V4/'coverage/pooled_comparisons.csv');rows=[[SHORT[r.baseline],f'{r.delta:+.3f}',f'{r.lower:+.3f} to {r.upper:+.3f}',f'{r.holm_p:.4f}',f'{r.fraction:.2f}'] for r in po.itertuples()]
tab('Table S16b. H1 minus each comparator, averaged equally across the four added domains after normalisation by raw CRPS. Common year vectors preserve spatial dependence. Four exploratory comparisons use Holm adjustment; the final column is the fraction of domains with favourable point estimates.',['Reference','Change (%)','95% interval','Adjusted p','Fraction'],rows,[1.4,1.1,2.2,1.1,1.0])
aa=pd.read_csv(V4/'access_s2/annual_scores.csv').query('lead=="D28"');rows=[[SHORT[m],f'{aa.query("method==@m").crps.mean():.3f}'] for m in ['Raw','Bottom_up','Weekly_climate_BU','H0','H1']]
tab('Table S17a. Northern ACCESS-S2 28-day CRPS (mm), 228 monthly origins during 2000–2018, nine members. This sample differs from the ECMWF origins and ensemble.',['Method','Mean CRPS'],rows,[4.3,2.5])
aa=pd.read_csv(V4/'access_s2/season_comparisons.csv')
# Use the same annual bootstrap output as the main text and Fig. 5.
annual_access=pd.read_csv(V4/'access_s2/comparisons.csv').query('lead=="D28"').set_index('baseline')
for idx,r in aa.query('season=="Annual"').iterrows():
 for field in ['delta','lower','upper']:aa.loc[idx,field]=annual_access.loc[r.baseline,field]
rows=[[r.season,SHORT[r.baseline],f'{r.delta:+.3f}',f'{r.lower:+.3f} to {r.upper:+.3f}'] for r in aa.query('season in ["Annual","DJF"]').itertuples()]
tab('Table S17b. ACCESS-S2 H1 minus each reference. Summer (DJF) has only three origins per year. Intervals resample nineteen common year blocks.',['Season','Reference','Difference (mm)','95% interval'],rows,[1.1,1.7,1.6,2.4])
tab('Table S18a. Original northern climate controls, retained without post hoc predictor selection. Differences are from H0; the full H1 score is 20.546 mm.',['Control','CRPS (mm)','H0 difference','95% interval'],rows6,[2.3,1.1,1.15,2.25])
pp=pd.read_csv(V4/'placebo/scores.csv');rows=[[str(int(r.permutation)),f'{r.crps:.3f}'] for r in pp.itertuples()]
tab('Table S18b. Twenty full year-block predictor permutations. Permutation zero is the unpermuted model. Every outer and inner fit is repeated. The Monte Carlo p value is 1/21 = 0.048; its exchangeability assumption is approximate for persistent climate indices.',['Permutation','28-day CRPS (mm)'],rows,[3.4,3.4])
rows=[]
for m in SHORT:
 rows.append([SHORT[m]]+[f'{AR.query("validation==\"LOYO\" and domain==@k and method==@m and lead==\"D28\"").crps.mean():.3f}' for k in [*REGIONS,'ACCESS_N']])
tab('Table S19a. All mixture and selection candidates in purged year validation. ACCESS N has nineteen monthly-origin years; the other columns have twenty ECMWF years. All scores are millimetres.',['Method','N','NE','SE','SW','ACCESS N'],rows,[2.0,.9,.9,.9,.9,1.2])
rows=[]
for mode in ['LOYO','Forward']:
 for k in [*REGIONS]+(['ACCESS_N'] if mode=='LOYO' else []):
  for b in ['Constant','Weekly_climate_BU']:
   r=AC.query('domain==@k and validation==@mode and lead=="D28" and method=="State" and baseline==@b').iloc[0];rows.append([mode,k,SHORT[b],f'{r.delta:+.3f}',f'{r.lower:+.3f} to {r.upper:+.3f}'])
tab('Table S19b. State mixture minus constant mixture or BU-clim. Intervals are descriptive paired year-block intervals, not simultaneous regional confidence bands.',['Design','Code','Reference','Change (mm)','95% interval'],rows,[.9,.75,1.8,1.1,2.25])
rows=[]
for cut in [2009,2012,2015]:
 for m in ['Raw','Bottom_up','Weekly_climate_BU','H0','H1','Constant','State']:
  mode='Rolling'+str(cut);rows.append([f'{cut+1}–{cut+3}',SHORT[m]]+[f'{AR.query("domain==@k and validation==@mode and method==@m and lead==\"D28\"").crps.mean():.3f}' for k in REGIONS])
tab('Table S20. Rolling forward checks. Training uses origins and targets ending by the year before each verification period. Scores are millimetres. These periods overlap the existing archive and are not independent operational tests.',['Verification','Method','N','NE','SE','SW'],rows,[1.0,2.0,.95,.95,.95,.95])
dd=pd.read_csv(V4/'adaptive/decision_summary.csv');rows=[]
for metric,threshold,label in [('RPS',0,'Tercile RPSS'),('Brier',50,'50 mm BSS'),('Brier',100,'100 mm BSS')]:
 for m in ['Raw','Weekly_climate_BU','H1','Constant','State']:
  rows.append([label,SHORT[m]]+[f'{dd.query("domain==@k and validation==\"LOYO\" and method==@m and metric==@metric and threshold==@threshold").iloc[0].skill:.3f}' for k in REGIONS])
tab('Table S21a. Tercile and fixed-threshold probability skill relative to permitted seasonal training observations. Tercile boundaries are fitted separately for every outer origin. Positive skill is favourable.',['Score','Method','N','NE','SE','SW'],rows,[1.15,1.85,.95,.95,.95,.95])
rows=[]
for k in REGIONS:
 for m in ['Constant','State']:
  a=dd.query('domain==@k and validation=="LOYO" and method==@m and metric=="Expense" and threshold==100 and ratio==0.2').iloc[0];rows.append([k,SHORT[m],f'{a.skill:.3f}',f'{a.lower:.3f} to {a.upper:.3f}'])
tab('Table S21b. Illustrative cost–loss value for a 100 mm event and cost/loss ratio 0.20. The denominator is the expense reduction from the training-climatology decision to a perfect decision. Ratios of pooled expenses are used; uncertainty resamples whole years. This is not an agricultural impact model.',['Code','Mixture','Relative value','95% interval'],rows,[.7,2.1,1.4,2.6])
notes=(V4/'supplementary_notes.md').read_text(encoding='utf-8').replace('(Fig. 8)','(Fig. S3)')
old_display=DISPLAY.copy();DISPLAY.update({14:'S1',15:'S2'});paragraphs(supp,notes);DISPLAY.clear();DISPLAY.update(old_display)
paragraphs(supp,'''## Supplementary Note 3 Mixture implementation and decision scoring

Three coherent empirical distributions receive common trajectory weights. The two free softmax coefficient vectors are bounded componentwise to [−6, 6]; the H1 vector is zero. All predictors include an intercept. Annual sine and cosine use a 366-day calendar. Standard deviations are floored at 10⁻⁶. The 28-day training rainfall scale is floored at 1 mm. Each inner year receives equal total weight, and the penalty is 0.01 times the mean squared coefficients, including intercepts. Optimisation uses analytic gradients and L-BFGS-B; all completed outer fits report successful convergence. The release includes coefficients, training indices, held-out scores and mixture weights.

Weighted empirical CRPS is checked against direct pairwise summation and every one-component limit. It scores the supplied finite distributions directly, without assuming independent marginal quantiles. Common weights across hierarchy nodes preserve the sum constraints.

Global or seasonal selection minimises equal-year inner 28-day CRPS among Raw, BU-rain, BU-clim, H0 and H1; the chosen component is refitted on permitted outer training observations. Original domains reuse cached triple-nested H1 trajectories, with identical exclusions for other inner components. ACCESS-S2 uses freshly fitted inner trajectories.

For threshold events, action is taken when the forecast probability exceeds cost divided by loss. Dividing expenses by loss gives expected expense c times the action indicator plus the event indicator when no action is taken. Training-climatology probabilities give the reference decisions; a perfect decision incurs c only when the event occurs. Relative value is the reduction from reference expense divided by the reduction attainable with perfect information. Negative values are retained. Thresholds 50 and 100 mm and ratios 0.05 to 0.95 were fixed before these scores were calculated. Year-block intervals do not make all points of a value curve simultaneous confidence statements.

The new full-block placebo experiment uses the same permutation for all five climate indices, preserving within-year variation and relationships among predictors. Donor years are assigned once per replicate and applied to both training and verification predictor streams; rainfall and exclusion indices remain unchanged. This tests a shuffled association, not an operational use of future climate measurements. It differs from the original three training-only controls. Interannual climate persistence limits exchangeability, so its Monte Carlo probability is a sensitivity measure.''')
figure(supp,'FigS03_power_map','Fig. S3. Original power-map diagnostic, retained as an implementation audit. The fit uses moving seasonal windows and applies the map to central months. This population mismatch limits interpretation of its adverse scores.')
figure(supp,'FigS04_seasons','Fig. S4. Seasonal H1-minus-H0 28-day CRPS in the four primary domains, with descriptive common-year bootstrap intervals. Negative changes favour H1; vertical scales differ.')
figure(supp,'FigS05_decision','Fig. S5. Idealised relative economic value for 28-day rainfall exceeding 100 mm in primary-domain cross-validation. Hollow squares mark the fixed cost/loss ratios; shading gives pointwise 95% year-block intervals. Negative values indicate higher expense than training-climatology decisions. All 50 mm curves and numeric uncertainty are included in the analysis tables.')
