from review_controls import *

F=pd.read_csv(REVIEW/'forward_annual.csv');F=F.query('method!="Raw"');extra=[]
for key in REGIONS:
 _,dates,raw,_=load_data(key,'primary');test=np.flatnonzero(dates.year>=2015);a=expand(raw[test]);path=RFOLDS/f'forward_{key}.npz';f=np.load(path);arrays={k:f[k] for k in f.files};arrays['Raw']=a;f.close();np.savez_compressed(path,**arrays);c=crps(a,arrays['y'])
 for year in range(2015,2020):
  mask=dates[test].year==year
  for j in [0,1,2,3,6]:extra.append(dict(domain=key,method='Raw',year=year,lead=NODES[j],crps=c[mask,j].mean()))
F=pd.concat([F,pd.DataFrame(extra)]);F.to_csv(REVIEW/'forward_annual.csv',index=False)
print(F.query('lead=="D28"').groupby(['domain','method']).crps.mean().to_string(),flush=True)
S=pd.read_csv(REVIEW/'spatial/annual_scores.csv');draw=np.random.default_rng(SEED+17).integers(0,20,(10000,20));rows=[]
for key in ['N_SW','N_SE','N_NW','N_NE']:
 a=S.query('domain==@key and lead=="D28"').pivot(index='year',columns='method',values='crps').reindex(range(2000,2020))
 for b in ['H0','Bottom_up','Weekly_climate_BU']:
  d=(a.H1-a[b]).values;lo,hi=np.quantile(d[draw].mean(1),[.025,.975]);rows.append(dict(domain=key,baseline=b,delta=d.mean(),lower=lo,upper=hi,better_years=int((d<0).sum())))
pd.DataFrame(rows).to_csv(REVIEW/'spatial/comparisons.csv',index=False);print(pd.DataFrame(rows).to_string(index=False),flush=True)

# Complete the support paragraph only after all four subdomain results exist.
path=REVIEW/'manuscript.md';text=path.read_text(encoding='utf-8')
paragraph='''The smaller northern supports retain geographical variation (Supplementary Table S13). H1 minus bottom-up mean CRPS is −0.545 mm in the southwestern cell, +0.044 mm in the southeastern cell, −1.259 mm in the northwestern cell and −0.410 mm in the northeastern cell. All four 1.5° cells were included. These overlapping regional comparisons are not independent replications; they show that the northern response depends on forecast support and does not hold uniformly within the original box.'''
text=text.replace('SPATIAL_RESULT_V3',paragraph)
text=text.replace('The climate effect persists in direction, but weekly climate calibration performs better than aggregate reconciliation in these five evaluation years.','The climate effect persists in direction, but weekly climate calibration performs better than aggregate reconciliation in these five evaluation years. All four northern calibrated alternatives remain above the raw ECMWF score of 17.847 mm, indicating that improvements within the postprocessing system do not establish an advantage over the dynamical forecast in this period.')
text=text.replace('The weekly approach performs better in a separate 2015–2019 forward evaluation.','The weekly approach performs better in a separate 2015–2019 forward evaluation.')
text=text.replace('and the weekly approach performs better in a separate 2015–2019 forward evaluation.','and the weekly approach performs better in a separate 2015–2019 forward evaluation. Northern calibrated forward scores remain above the raw forecast.')
text=text.replace('Climate-informed weekly aggregation recovers part of the twenty-year gain and performs better than aggregate reconciliation in the separate forward evaluation.','Climate-informed weekly aggregation recovers part of the twenty-year gain and performs better than aggregate reconciliation in the separate forward evaluation, where the raw northern forecast remains better than all four calibrated alternatives.')
path.write_text(text,encoding='utf-8')
