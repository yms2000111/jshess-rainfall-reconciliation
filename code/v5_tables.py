"""Main tables and captions, inserted after V4 definitions."""
R5=ROOT/'revision/review_v5'
original_document=document
def document():
 d=original_document();d.styles['Caption'].paragraph_format.alignment=WD_ALIGN_PARAGRAPH.JUSTIFY
 return d
po5=pd.read_csv(R5/'eight_domain_comparisons.csv')
ac5=pd.read_csv(R5/'access_s2/pooled_comparisons.csv')
pl5=pd.read_csv(R5/'placement/pooled_comparisons.csv')
rows=[]
for label,d in [('ECMWF CV',po5.assign(method='H1')),('Placement',pl5),('ACCESS-S2',ac5)]:
 for r in d.itertuples():
  if label=='ECMWF CV' and r.baseline not in ['Weekly_climate_BU','H0']:continue
  if label=='Placement' and r.baseline!='H1':continue
  rows.append([label,r.method+' − '+SHORT.get(r.baseline,r.baseline),f'{r.delta:+.3f}',f'{r.lower:+.3f} to {r.upper:+.3f}',f'{r.holm_p:.5f}' if hasattr(r,'holm_p') else 'Descriptive'])
rr=pd.read_csv(R5/'operational/confirmatory_contrast.csv').iloc[0]
rows.append(['2020 test','H1 − BU-clim',f'{rr.delta:+.3f}',f'{rr.lower:+.3f} to {rr.upper:+.3f}','Single test'])
TABLES[5]=('Table 6. Eight-domain 28-day CRPS contrasts. Negative values favour the first method. Retrospective effects are percentages of each domain’s raw mean CRPS; the 2020 denominator uses training raw scores. Retrospective intervals resample common years, and the 2020 interval uses four-origin blocks. Holm adjustment is separate for the four ECMWF and three ACCESS comparisons. Placement intervals are descriptive.',['Evaluation','Comparison','Change (%)','95% interval','Adjusted p'],rows,[1.05,1.85,.85,1.85,1.2])
TABLES[6]=('Table 7. Conclusions and the evidence supporting them. Each statement applies to its stated configuration and evaluation sample.',['Conclusion','Evidence','Scope'],[
 ['Direct aggregates can improve on weekly climate summation','H1 minus BU-clim is negative in all eight domains of both retrospective systems.','Supported within those comparisons'],
 ['Aggregate climate placement alone does not explain that gain','Hweekly and H1 have similar scores; H2 is worse than H1.','ECMWF configuration comparison'],
 ['A stable incremental climate effect remains uncertain','H1 minus H0 has an interval crossing zero in both pooled systems.','Unresolved'],
 ['Temporal transfer is not confirmed','Northern 2015–2019 forward ordering reverses; the 2020 pooled interval crosses zero.','Confirmation criterion not met'],
 ['Monsoon conditions explain the seasonal setting','Summer is humid and westerly; annual wind–gain association is uncertain.','Physical context, not a selection rule']],[1.9,3.25,1.65])
CAPTIONS[1]=('Fig02_design','Fig. 2. (a) Accumulation hierarchy. (b) Information placement and nested fitting: inner held-out errors estimate covariance; all outer forecasts use permitted training data. (c) Example outer year exclusion. H0, Hweekly, H1 and H2 adjust no nodes, weeks, aggregates and all nodes, respectively; bottom-up uses weekly nodes only.')
CAPTIONS[4]=('Fig05_transfer','Fig. 5. H1 minus H0 and BU-clim in each of the eight domains for (a) ECMWF and (b) ACCESS-S2. Hollow squares show mean differences; bars are descriptive 95% common-year bootstrap intervals. Negative values favour H1. Different origins, members and grids preclude direct rankings of the systems’ absolute scores.')
CAPTIONS[7]=('Fig08_holdout','Fig. 8. Previously unused ECMWF issued forecasts in 2020. (a) Domain CRPS for the raw ensemble, BU-clim and H1. (b) The fixed equal-domain H1-minus-BU-clim contrast and 95% circular block intervals. Every interval crosses zero. The four-origin block is primary; six and eight are sensitivity checks.')
CAPTIONS[9]=('Fig10_circulation','Fig. 10. Independent NCEP/NCAR reanalysis at 850 hPa: specific humidity and wind in (a) DJF and (b) JJA, 2000–2019. Dashed red boxes define the monsoon-flow diagnostic; the small black box is domain N. (c) Annual DJF wind versus H1-minus-H0 CRPS. Hollow squares denote twenty calendar-year pairs; the correlation interval resamples years. Monthly composites describe the seasonal setting, not individual MJO events.')
