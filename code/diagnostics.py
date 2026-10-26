from analyse import *
scores=pd.read_csv(OUT/'scores.csv');cases=pd.read_csv(OUT/'case_scores.csv');boots=pd.read_csv(OUT/'paired_comparisons.csv')
print('PRIMARY COMPARISONS\n',boots.query("method=='XGB + WLS-R'").round(4).to_string(index=False))
print('DESIGN\n',(OUT/'N_design.json').read_text()[:600])
print('WEEKLY SKILL\n',scores.query("lead!='D28' and method in ['Raw','OLS','XGBoost','XGB + WLS-R','XGB pooled','XGB no indices']").pivot_table(index=['region','lead'],columns='method',values='crpss').round(3).to_string())
condition=[];robust=[];qc=[]
for key in REGIONS:
 d=np.load(ROOT/f'data/processed/{key}.npz');a=d['qc_max_decrease'];test=pd.DatetimeIndex(d['dates']).year>=2015
 qc.append(dict(region=key,origins=len(a),any_decrease=int((a>1e-4).sum()),decrease_over_01=int((a>.1).sum()),test_over_01=int((a[test]>.1).sum()),max_mm=float(a.max())))
 c=cases.query('region==@key');p=c.pivot(index=['date','lead'],columns='method',values='crps');meta=c.query("method=='XGBoost'").set_index(['date','lead'])
 delta=p['XGB + WLS-R']-p['XGBoost'];bi=block_indices(265)
 for lead in LEADS:
  sub=meta.xs(lead,level='lead');v=delta.xs(lead,level='lead').values
  for name,mask in [('MJO weak',sub.rmm_amp<1),('MJO active',sub.rmm_amp>=1),('Cool Nino34',sub.nino_anomaly<-.5),('Neutral Nino34',sub.nino_anomaly.between(-.5,.5)),('Warm Nino34',sub.nino_anomaly>.5)]:
   m=mask.values;den=m[bi].sum(1);bm=np.where(den>0,(v[bi]*m[bi]).sum(1)/np.maximum(den,1),np.nan);lo,hi=np.nanquantile(bm,[.025,.975]);condition.append(dict(region=key,lead=lead,state=name,n=int(m.sum()),delta_crps=float(v[m].mean()),lower=lo,upper=hi))
  mask=sub.qc_max_decrease<=.1
  robust.append(dict(region=key,lead=lead,experiment='no decrease over 0.1 mm',n=int(mask.sum()),delta_crps=float(v[mask].mean())))
  for L in [4,13,26]:
   bm=v[block_indices(len(v),L=L)].mean(1);lo,hi=np.quantile(bm,[.025,.975]);robust.append(dict(region=key,lead=lead,experiment=f'bootstrap block {L}',n=len(v),delta_crps=float(v.mean()),lower=lo,upper=hi))
 old=pd.read_csv(ROOT/'results_positive_part/scores.csv').query('region==@key').pivot(index='lead',columns='method',values='crps')
 for lead in LEADS:robust.append(dict(region=key,lead=lead,experiment='positive part full refit',n=265,delta_crps=float(old.loc[lead,'XGB + WLS-R']-old.loc[lead,'XGBoost'])))
pd.DataFrame(condition).to_csv(OUT/'climate_conditions.csv',index=False);pd.DataFrame(robust).to_csv(OUT/'robustness.csv',index=False);pd.DataFrame(qc).to_csv(OUT/'qc_summary.csv',index=False)
print('QC\n',pd.DataFrame(qc).to_string(index=False))
print('28DAY ROBUSTNESS\n',pd.DataFrame(robust).query("lead=='D28'").round(4).to_string(index=False))
print('28DAY CALIBRATION\n',scores.query("lead=='D28' and method in ['Raw','OLS','XGBoost','XGB + WLS-R']")[['region','method','rmse','bias','coverage80','width80','bss']].round(3).to_string(index=False))
