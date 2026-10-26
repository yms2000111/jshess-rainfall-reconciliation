"""Produce revised Word files with the complete main and supplementary evidence."""
from common import ROOT

source=(ROOT/'code/build_final_word.py').read_text(encoding='utf-8')
source=source.replace("OUT=ROOT/'revision/submission'","OUT=ROOT/'revision/review_v3/submission'")
source=source.replace("F=ROOT/'revision/final_figures'","F=ROOT/'revision/review_v3/figures'")
source=source.replace("ROOT/'revision/manuscript_final.md'","ROOT/'revision/review_v3/manuscript.md'")
source=source.replace("TO_INSERT|TODO|PLACEHOLDER", "TO_INSERT|TODO|PLACEHOLDER|SPATIAL_RESULT_V3")
source=source.replace("['Domain',", "['Code',")
source=source.replace("for i,args in enumerate(TABLES):table(doc,*args,newpage=i in [0,2])","for i,args in enumerate(TABLES):table(doc,*args,newpage=i in [0,2,4,5,6])")
source=source.replace("assert audit['abstract_words']<=250", "audit['table_cell_words']=sum(len(str(c).split()) for _,headers,rows,_ in TABLES for row in [headers,*rows] for c in row)\naudit['all_inclusive_words']=audit['main_and_captions_words']+audit['table_cell_words']\nassert audit['all_inclusive_words']<=7500\nassert audit['abstract_words']<=250")
source=source.replace("    if not last.text:last._p.getparent().remove(last._p)","    if not last.text:last._p.getparent().remove(last._p)\n    for p in args[0].paragraphs:\n        if p.text==args[1]:p.paragraph_format.space_before=Pt(10)\n    current=args[0].tables[-1]\n    for row in current.rows:\n        for cell in row.cells:\n            if re.match(r'^[+−-]?\\d',cell.text):\n                for p in cell.paragraphs:p.alignment=WD_ALIGN_PARAGRAPH.CENTER")
source=source.replace("    current=args[0].tables[-1]", "    current=args[0].tables[-1]\n    if len(current.rows)>=20:\n        for row in current.rows:\n            for cell in row.cells:\n                for p in cell.paragraphs:p.paragraph_format.space_before=Pt(3);p.paragraph_format.space_after=Pt(3)")

extra=r'''
REVIEW=ROOT/'revision/review_v3'
CS=pd.read_csv(REVIEW/'control_scores.csv');CC=pd.read_csv(REVIEW/'controls_vs_H0.csv')
FW=pd.read_csv(REVIEW/'forward_annual.csv').query("lead=='D28'").groupby(['domain','method']).crps.mean()
BS=pd.read_csv(REVIEW/'brier_skill.csv')
def bss(k,m):return BS.query('domain==@k and method==@m').iloc[0].brier_skill_score
CAPTIONS[1]=('Fig02_design','Fig. 2. (a) Weekly, fortnightly and 28-day aggregation structure. H0 uses rainfall predictors; H1 adds climate information at aggregates. (b) The nested fitting and evaluation workflow. Inner year blocks supply held-out mean errors for covariance W; marginal forecasts and rank templates are fitted inside the outer permitted data. The power-map diagnostic adds a further cross-fit. (c) Outer validation illustrated for 2010: orange is held out, grey is excluded and blue is permitted for fitting.')
CAPTIONS[5]=('Fig06_coverage','Fig. 6. Observed versus nominal central-interval coverage for 28-day rainfall at six probability levels. The diagonal represents nominal coverage. All points, including low-coverage values, are shown. Each curve pools 1060 outer held-out origins. H0 and H1 have seven nodes; open squares distinguish forecast positions along the curves. The 80% interval widths are in Table 4.')
CAPTIONS[6]=('Fig07_mechanism','Fig. 7. Training-covariance-based gain versus observed reduction in 28-day mean-square error relative to bottom-up. (a) Linear mapping and (b) nonnegative sample means. Each hollow square is one domain-season combination; colours identify domains. The diagonal represents agreement. Bias is observed minus predicted gain, in percentage points. Slopes are descriptive least-squares slopes. All 16 cases lie below the diagonal; season-level values are supplied in the analysis tables.')
CAPTIONS.append(('Fig09_annual_influence','Fig. 9. Northern annual CRPS differences and influence of individual years. (a) H1 seven-node reconciliation minus bottom-up or H0. (b) The twenty-year mean difference after omitting each year’s scores. Negative values favour H1. These are descriptive analyses of existing held-out scores; omission does not refit the forecast models. Hollow squares mark years.'))
CAPTIONS=[(name,caption.replace('Open symbols','Open squares').replace('Open points','Open squares')) for name,caption in CAPTIONS]
rows4=[[k,lab,f'{score(k,m,"coverage80")*100:.1f}',f'{score(k,m,"width80"):.2f}',f'{score(k,m,"twcrps"):.3f}',f'{score(k,m,"brier90"):.3f}',f'{bss(k,m):.3f}',str(int(score(k,m,'events90')))] for k in REGIONS for m,lab in [('Bottom_up','Bottom-up'),('H0_7_NN','H0, seven'),('H1_7_NN','H1, seven')]]
TABLES[3]=('Table 4. Held-out 28-day uncertainty and upper-tail diagnostics. Central intervals have nominal coverage 80%. Tail CRPS and Brier scores use the 90th percentile of permitted training origins within 45 calendar days of each origin. BSS is the Brier skill score against empirical training exceedance probabilities. Events are observed exceedances among 1060 origins.',['ID','Method','Coverage (%)','Width (mm)','Tail CRPS (mm)','Brier score','BSS','Events'],rows4,[.45,1.3,.8,.85,.9,.8,.85,.85])
rows5=[]
for method,label in [('Weekly_climate_BU','Weekly climate, bottom-up'),('Intercept','Aggregate intercept, NN')]:
 rows5.append(['2000 to 2019',label]+[f'{CS.query("domain==@k and method==@method and lead==\"D28\"").iloc[0].crps:.3f}' for k in REGIONS])
for method,label in [('Raw','ECMWF (QC)'),('Bottom_up','Rainfall-only bottom-up'),('H0','H0, seven nodes'),('H1','H1, seven nodes'),('Weekly_climate_BU','Weekly climate, bottom-up')]:
 rows5.append(['2015 to 2019',label]+[f'{FW.loc[(k,method)]:.3f}' for k in REGIONS])
TABLES.append(('Table 5. Additional-information controls and forward-evaluation 28-day CRPS (mm). The first two rows use full purged year validation. The final five show raw ECMWF and forecasts whose parameters, covariance and templates use only 2000 to 2014. Lower is better. NN denotes nonnegative projection.',['Evaluation','Method','N','NE','SE','SW'],rows5,[1.15,2.25,.85,.85,.85,.85]))
rows6=[]
for method,label in [('Intercept','Intercept only'),('MJO','MJO'),('ENSO','Niño3.4'),('DMI','DMI'),('SAM','SAM'),('Placebo1','Placebo 1'),('Placebo2','Placebo 2'),('Placebo3','Placebo 3'),('Lag1','One-month monthly lags')]:
 r=CC.query('domain=="N" and method==@method').iloc[0];sc=CS.query('domain=="N" and method==@method and lead=="D28"').iloc[0].crps
 rows6.append([label,f'{sc:.3f}',f'{r.delta:+.4f}',f'{r.lower:+.4f} to {r.upper:+.4f}'])
TABLES.append(('Table 6. Exploratory northern aggregate controls. All use seven-node reconciliation and unchanged rainfall-only weekly marginals. Differences are from H0 (20.918 mm); the full H1 score is 20.546 mm. Placebos permute training predictor years within each fit. Intervals are descriptive year-bootstrap intervals, with no selection of a winning predictor.',['Aggregate adjustment','CRPS (mm)','Change (mm)','95% interval (mm)'],rows6,[2.3,1.1,1.15,2.25]))
rows7=[['Primary QC','H1 minus bottom-up','−0.541','−0.951 to −0.154'],['Positive-part QC','H1 minus bottom-up','−0.507','−0.927 to −0.113'],['Signed QC','H1 minus bottom-up','−0.493','−0.918 to −0.093'],['200 to 1000 samples','H1 minus bottom-up','−0.538 to −0.527','Three-seed means'],['Power-map fitting windows','Mapped minus original','−0.219','Mean across monthly windows'],['Power-map inner use','Mapped minus original','+0.173','Central-month application'],['Power-map outer use','Mapped minus original','+0.425','+0.180 to +0.665']]
TABLES.append(('Table 7. Northern core sensitivity and power-map results, in millimetres of CRPS. Archive corrections repeat the H1 factorial model and its own bottom-up reference. Sampling values average three seeds. Fitting-window and inner-application losses describe different case populations; their distinction explains part of the power-map failure. Bootstrap bounds apply where shown.',['Diagnostic','Comparison','CRPS change','95% interval or summary'],rows7,[1.9,1.75,1.15,2.0]))
TABLES[2]=(TABLES[2][0]+' Descriptive intervals do not represent Holm-adjusted rejection decisions.',*TABLES[2][1:])
'''
source=source.replace('doc=document();doc.core_properties.title=',extra+'\ndoc=document();doc.core_properties.title=',1)

supp=r'''
# Supplementary tables S7 onwards supply the additional controls and audits.
EC=pd.read_csv(E/'comparisons.csv');rows=[]
for k in REGIONS:
 for metric,label in [('twcrps','Tail CRPS'),('brier90','Brier score')]:
  rr=EC.query('domain==@k and method=="H1_7_NN" and baseline=="Bottom_up" and lead=="D28" and score==@metric').iloc[0]
  rows.append([k,label,f'{rr.delta:+.5f}',f'{rr.lower:+.5f} to {rr.upper:+.5f}'])
table(supp,'Table S7. H1 seven-node minus bottom-up upper-tail score changes. Thresholds are defined as in Table 4. Intervals use common year blocks.',['Code','Score','Difference','95% interval'],rows,[.7,1.5,1.5,3.1],newpage=True)
VC=pd.read_csv(REVIEW/'control_comparisons.csv');rows=[]
for k in REGIONS:
 for lead in ['W1','W2','W3','W4','D28']:
  r=VC.query('domain==@k and method=="Weekly_climate_BU" and baseline=="H1_7_NN" and lead==@lead and score=="crps"').iloc[0]
  rows.append([k,lead,f'{r.delta:+.3f}',f'{r.lower:+.3f} to {r.upper:+.3f}'])
table(supp,'Table S8. Climate-informed weekly aggregation minus aggregate H1 reconciliation. Positive values favour reconciliation; negative values favour weekly calibration and summation. Scores are millimetres.',['Code','Scale','CRPS difference','95% interval'],rows,[.7,.8,2.0,3.3],newpage=True)
rows=[]
for k in REGIONS:
 for dep in ['ECC','Schaake']:
  for m,label in [(dep+'_BU','Bottom-up'),('H0_'+dep+'_NN','H0, seven'),('H1_'+dep+'_NN','H1, seven')]:
   r=CS.query('domain==@k and method==@m and lead=="D28"').iloc[0];rows.append([k,dep,label,f'{r.crps:.3f}',f'{r.coverage80*100:.1f}',f'{r.width80:.2f}'])
table(supp,'Table S9. Matched 11-sample factorial dependence controls. ECC and Schaake use identical marginal quantiles before rank assignment. Absolute finite-sample scores and interval coverage should be compared at the same sample size.',['Code','Ranks','Method','CRPS (mm)','Coverage (%)','Width (mm)'],rows,[.6,1.0,1.45,1.25,1.25,1.25],newpage=True)
PR=pd.read_csv(REVIEW/'primary_robustness.csv');rows=[]
for r in PR.itertuples():rows.append([baseline_labels[r.baseline],f'{r.bca_lower:+.3f} to {r.bca_upper:+.3f}',f'{r.block2_lower:+.3f} to {r.block2_upper:+.3f}',f'{r.block3_lower:+.3f} to {r.block3_upper:+.3f}'])
table(supp,'Table S10a. Additional intervals for the three domain-averaged primary mean differences, in percent of climatological CRPS. Circular blocks retain adjacent origin years. These are sensitivity intervals, not new primary hypothesis tests.',['Comparison','BCa interval','Two-year blocks','Three-year blocks'],rows,[2.3,1.5,1.5,1.5],newpage=True)
SR=pd.read_csv(REVIEW/'small_sample_intervals.csv');rows=[]
for r in SR.query('domain=="N"').itertuples():rows.append([r.baseline,f'{r.bca_lower:+.3f} to {r.bca_upper:+.3f}',f'{r.block2_lower:+.3f} to {r.block2_upper:+.3f}',f'{r.block3_lower:+.3f} to {r.block3_upper:+.3f}'])
table(supp,'Table S10b. Northern descriptive interval sensitivities, in millimetres, for H1 seven-node minus each baseline.',['Baseline','BCa interval','Two-year blocks','Three-year blocks'],rows,[1.55,1.75,1.75,1.75])
rows=[]
for k in REGIONS:
 w=pd.read_csv(REVIEW/f'recalibration_windows_{k}.csv');r=pd.read_csv(REVIEW/f'recalibration_inner_{k}.csv');v=pd.read_csv(REVIEW/f'covariance_shift_{k}.csv');rows.append([k,f'{w.delta.mean():+.3f}',f'{r.inner_delta.mean():+.3f}',f'{r.outer_delta.mean():+.3f}',f'{v.relative_frobenius.mean():.3f}',f'{v.total_variance_ratio.mean():.3f}'])
table(supp,'Table S11. Power-map fitting and application audit. The first three changes are mapped minus original CRPS (mm). Fitting windows span 91 calendar days; inner application uses the central month. Matrix distance is the mean relative Frobenius distance between inner and outer W; the final column is the mean inner/outer total-error variance ratio. These diagnostics do not isolate a causal effect of covariance shift.',['Code','Window change','Inner use change','Outer use change','W distance','Variance ratio'],rows,[.6,1.2,1.3,1.3,1.2,1.2],newpage=True)
rows=[]
FA=pd.read_csv(REVIEW/'forward_annual.csv').query('lead=="D28"')
for k in REGIONS:
 for m in ['Raw','Bottom_up','H0','H1','Weekly_climate_BU']:
  aa=FA.query('domain==@k and method==@m').crps;rows.append([k,m,f'{aa.mean():.3f}',f'{aa.min():.3f} to {aa.max():.3f}'])
table(supp,'Table S12. Strictly forward 2015–2019 evaluation. The range describes the five annual mean CRPS values rather than a confidence interval. All model fitting ends in 2014.',['Code','Method','Mean CRPS (mm)','Annual range (mm)'],rows,[.65,2.15,1.5,2.5],newpage=True)
SP=pd.read_csv(REVIEW/'spatial/annual_scores.csv');rows=[]
for k in ['N_SW','N_SE','N_NW','N_NE']:
 for m in ['Raw','Bottom_up','H0','H1','Weekly_climate_BU']:
  a=SP.query('domain==@k and method==@m and lead=="D28"').crps;rows.append([k,m,f'{a.mean():.3f}'])
table(supp,'Table S13. Northern support sensitivity at the four exhaustive 1.5° cells inside the original N domain. SW and SE cells span 15.75 to 14.25°S; NW and NE span 14.25 to 12.75°S. Western cells span 131.25 to 132.75°E; eastern cells span 132.75 to 134.25°E. All cells use newly extracted AGCD support and the same nested protocol. Scores are descriptive.',['Cell','Method','28-day CRPS (mm)'],rows,[.9,3.2,2.7],newpage=True)
'''
source=source.replace("supp.save(OUT/'JSHESS_supplementary_material.docx')",supp+"\nsupp.save(OUT/'JSHESS_supplementary_material.docx')")
source=source.replace("The results show why forecast services should check", "The results show why forecast services should check")
exec(compile(source,'build_review_word_source','exec'))
from review_latex import write
write(globals())
