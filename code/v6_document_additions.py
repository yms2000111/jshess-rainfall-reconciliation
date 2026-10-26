"""Inserted into the common Word/LaTeX builder after the V5 tables."""
R6=ROOT/'revision/review_v6'
# Rebuild Table 6 from all four comparisons, then renumber in citation order.
rows=[]
for label,d in [('ECMWF CV',po5.assign(method='H1')),('ACCESS-S2',ac5)]:
 for r in d.itertuples():rows.append([label,r.method+' − '+SHORT.get(r.baseline,r.baseline),f'{r.delta:+.3f}',f'{r.lower:+.3f} to {r.upper:+.3f}',f'{r.holm_p:.5f}'])
rr=pd.read_csv(R5/'operational/confirmatory_contrast.csv').iloc[0]
rows.append(['2020 test','H1 − BU-clim',f'{rr.delta:+.3f}',f'{rr.lower:+.3f} to {rr.upper:+.3f}','Single test'])
TABLES[5]=('Table 6. Complete pooled baseline comparisons at 28 days. Negative changes favour H1. Effects are percentages of each domain’s raw CRPS, using training scores for 2020. The four ECMWF and three ACCESS-S2 comparisons form separate exploratory Holm families. Common-year intervals apply to hindcasts; four-origin blocks apply to 2020.',['Evaluation','Comparison','Change (%)','95% interval','Holm p'],rows,[1.1,1.7,.9,2.1,1.0])
TABLES[6]=('Table 7. Evidence and scope of the main conclusions.',['Conclusion','Evidence','Scope'],[
 ['H1 improves on several retrospective baselines','ECMWF pooled comparisons favour H1 over raw, BU-rain and BU-clim, but not clearly over H0.','Exploratory eight-domain synthesis'],
 ['BU-clim alone is an insufficient benchmark','ACCESS-S2 BU-clim is worse than BU-rain in seven domains; H1 minus BU-rain spans zero.','Baseline-dependent benefit'],
 ['All-node deterioration is not explained solely by weights','H2 is worse than H1 with both own and common H0 covariance in both systems.','Cross-system descriptive ablation'],
 ['Climate-adjustment stability contributes to the contrast','More climate-fitting years and stronger penalties reduce H2 deterioration and narrow the H1 versus BU-clim difference.','Conditional cross-system mechanism evidence'],
 ['Temporal benefit remains uncertain','Northern forward ordering reverses; the 2020 interval crosses zero.','One new forecast year'],
 ['Physical context does not supply a gain rule','Wet-season monsoon conditions are clear; annual wind–gain association is uncertain.','Background interpretation']],[1.9,3.3,1.6])
table_order=[0,1,5,2,3,4,6]
table_map={1:1,2:2,6:3,3:4,4:5,5:6,7:7}
TABLES=[(re.sub(r'^Table \d+\.',f'Table {i+1}.',TABLES[j][0]),*TABLES[j][1:]) for i,j in enumerate(table_order)]
MOVED_CAPTIONS=[(CAPTIONS[6][0],CAPTIONS[6][1].replace('Fig. 7.','Fig. S9.')),(CAPTIONS[9][0],CAPTIONS[9][1].replace('Fig. 10.','Fig. S10.'))]
figure_order=[0,1,2,4,3,5,8,7]
CAPTIONS=[(CAPTIONS[j][0],re.sub(r'^Fig\. \d+\.',f'Fig. {i+1}.',CAPTIONS[j][1])) for i,j in enumerate(figure_order)]
CAPTIONS=[(n,re.sub(r'Table (\d+)',lambda m:'Table '+str(table_map[int(m[1])]),c)) for n,c in CAPTIONS]
