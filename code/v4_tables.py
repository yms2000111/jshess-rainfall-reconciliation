"""Executed inside the manuscript builder; final main tables and captions."""
V4=ROOT/'revision/review_v4';AR=pd.read_csv(V4/'adaptive/annual_scores.csv');AC=pd.read_csv(V4/'adaptive/comparisons.csv')
SHORT={'Bottom_up':'BU-rain','Weekly_climate_BU':'BU-clim','Raw':'Raw','H0':'H0','H1':'H1','Constant':'Constant mixture','Equal':'Equal mixture','Seasonal':'Seasonal mixture','State':'State mixture','Select_global':'Global selection','Select_season':'Seasonal selection'}
EXTRA_DOMAINS=json.loads((V4/'coverage/domains.json').read_text())
all_domains={**REGIONS,**EXTRA_DOMAINS}
TABLES[0]=('Table 1. Primary and additional 3° domains. Forecasts and AGCD use the same boundaries, with AGCD restricted to valid land cells.',['Code','Domain','Longitude','Latitude'],[[k,r['name'],f'{r["lon"][0]:.2f}–{r["lon"][1]:.2f}°E',f'{abs(r["lat"][1]):.2f}–{abs(r["lat"][0]):.2f}°S'] for k,r in all_domains.items()],[.5,2.5,1.9,1.9])
rows=TABLES[1][2]+[['BU-clim']+[f'{CS.query("domain==@k and method==\"Weekly_climate_BU\" and lead==\"D28\"").iloc[0].crps:.3f}' for k in REGIONS]]
TABLES[1]=('Table 2. ECMWF 28-day CRPS (mm), 2000–2019, from purged year validation. H0 uses rainfall predictors; H1 adds aggregate climate predictors. Reconciled forecasts use nonnegative projection.',['Method','N','NE','SE','SW'],rows,[2.4,1.1,1.1,1.1,1.1])
TABLES[2]=('Table 3. Original primary factorial tests. Effects are percentages of climatological CRPS, with equal domain weights. Intervals use common year blocks; p values use annual sign flips and Holm adjustment. Negative differences favour the first method.',*TABLES[2][1:])
TABLES[3]=('Table 4. ECMWF 28-day uncertainty and upper-tail verification. Intervals have nominal 80% coverage. Tail scores use the training seasonal 90th percentile; BSS compares with training exceedance probabilities. There are 1060 origins per domain.',*TABLES[3][1:])
rows=[[SHORT[m]]+[f'{FW.loc[(k,m)]:.3f}' for k in REGIONS] for m in ['Raw','Bottom_up','Weekly_climate_BU','H0','H1']]
TABLES[4]=('Table 5. Forward ECMWF 28-day CRPS (mm), 2015–2019, with training ending in 2014. Cross-validation results are reported separately in Table 2.',['Method','N','NE','SE','SW'],rows,[2.4,1.1,1.1,1.1,1.1])
rows=[]
for design in ['LOYO','Forward']:
 for m in ['Equal','Constant','Seasonal','State']:
  rows.append([design,SHORT[m]]+[f'{AR.query("validation==@design and domain==@k and method==@m and lead==\"D28\"").crps.mean():.3f}' for k in REGIONS])
TABLES[5]=('Table 6. Coherent mixture 28-day CRPS (mm). LOYO is purged year validation over 2000–2019; forward verification covers 2015–2019. Every learned weight uses inner held-out scores.',['Design','Mixture','N','NE','SE','SW'],rows,[.95,2.05,.95,.95,.95,.95])
TABLES[6]=('Table 7. Evidence supporting the study conclusions. Strength refers to the stated comparison and study scope.',['Conclusion','Evidence','Strength'],[
 ['Added hierarchy nodes contribute little','Original factorial contrast near zero; intervals include zero.','Consistent within this archive'],
 ['Northern climate effect depends on setting','Year concentration; small ACCESS-S2 H1–H0 contrast.','Exploratory'],
 ['Climate information can help without reconciliation','BU-clim captures part of the northern improvement.','Comparator dependent'],
 ['State weights do not improve on constant pooling','Primary-domain contrast and northern forward check.','Supported for this specification'],
 ['Covariance gain estimates are optimistic','All sixteen domain-season cases below agreement.','Diagnostic within this study']],[1.9,3.25,1.65])
CAPTIONS[0]=('Fig01_domains','Fig. 1. (a) Four primary and four additional domains. (b) AGCD mean monthly rainfall, 2000–2019. Boxes show verification support, not official climate-region boundaries; the North arrow is separate from domain N. The Natural Earth outline provides geographic context.')
CAPTIONS[1]=('Fig02_design','Fig. 2. (a) Aggregation hierarchy. (b) Nested fitting for component forecasts and combination weights. Covariance estimation adds a further split within each inner training set. (c) An outer fold: orange is verified, grey excluded and blue permitted for fitting.')
CAPTIONS[2]=('Fig03_weekly_skill','Fig. 3. ECMWF weekly CRPSS relative to training seasonal climatology over 1060 held-out origins per primary domain. Positive values indicate skill. H0 and H1 use seven-node nonnegative reconciliation; BU-rain retains the calibrated weekly distributions.')
CAPTIONS[3]=('Fig04_factorial','Fig. 4. Primary factorial 28-day CRPS contrasts as percentages of climatological CRPS. Hollow squares mark means and bars descriptive 95% common-year bootstrap intervals. Negative differences favour H1 or the larger hierarchy. Multiplicity-adjusted tests are in Table 3.')
CAPTIONS[4]=('Fig05_transfer','Fig. 5. (a) H1-minus-H0 CRPS at the eight ECMWF domain centres; coloured square outlines encode millimetres. (b) H1 minus H0 and BU-clim, with descriptive 95% year-block intervals. ACCESS N is a separately fitted monthly ACCESS-S2 sample, not a matched comparison of forecast systems.')
CAPTIONS[5]=('Fig06_coverage','Fig. 6. Observed versus nominal coverage of central 28-day intervals across the four primary domains. The diagonal denotes nominal coverage. Curves pool 1060 held-out origins; the 80% widths appear in Table 4.')
CAPTIONS[6]=('Fig07_mechanism','Fig. 7. Variance-based versus observed 28-day mean-square-error gain relative to BU-rain: (a) linear and (b) nonnegative reconciliation. Each hollow square is a domain-season case. Bias is observed minus predicted gain in percentage points; slopes are descriptive. All sixteen cases lie below agreement.')
CAPTIONS[7]=('Fig08_forward','Fig. 8. (a) Northern annual forward CRPS and (b) cross-validation and forward scores on the same 2015–2019 years. The raw forecast is identical between designs. Lines connect methods across matched evaluation periods.')
CAPTIONS[8]=('Fig09_annual_influence','Fig. 9. Northern H1 differences by year and after individual-year score omissions. Negative values favour H1. Omissions summarise existing held-out scores and do not refit the forecasts. Hollow squares identify years.')
CAPTIONS.append(('Fig10_mixtures','Fig. 10. State-weighted pooling and inner seasonal selection minus the constant mixture: (a) year-block validation and (b) forward 2015–2019. Hollow squares and bars show mean differences and descriptive 95% year-block intervals. Negative values favour the more flexible rule.'))
# Use the same short labels in tables, captions and the manuscript.
def naming(x):
 return str(x).replace('Bottom-up','BU-rain').replace('bottom-up','BU-rain').replace('H0, seven nodes','H0').replace('H1, seven nodes','H1').replace('H0, seven','H0').replace('H1, seven','H1')
TABLES=[(c,h,[[naming(x) for x in row] for row in rows],w) for c,h,rows,w in TABLES]
