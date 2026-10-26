"""Case-level scores and year-block inference for the frozen factorial design."""
from extension_cv import *
from revision_statistics import hersbach,ci
from analyse import crps
from scipy.stats import spearmanr

def main():
 cases=[];summary=[];dec=[];cover=[];mechanism=[];audit=[]
 for key in REGIONS:
  folds=[np.load(EFOLDS/f'{key}_{yr}.npz') for yr in range(2000,2020)]
  y=np.concatenate([f['y'] for f in folds]);dates=pd.DatetimeIndex(np.concatenate([f['dates'] for f in folds]));q90=np.concatenate([f['threshold90'] for f in folds]);ref=np.concatenate([f['reference'] for f in folds]);season=np.array(['DJF','MAM','JJA','SON'])[(dates.month.to_numpy()%12)//3]
  for m in ['Raw','Bottom_up','H0_Direct','H1_Direct','H0_5_NN','H0_7_NN','H1_5_NN','H1_7_NN']:
   ens=np.concatenate([f[m] for f in folds]);c=crps(ens,y);fc=crps(ens,y,True);tc=crps(np.maximum(ens,q90[:,None,:]),np.maximum(y,q90));avg=ens.mean(1);err=avg-y;prob=(ens>q90[:,None,:]).mean(1);event=y>q90;bs=(prob-event)**2
   lo,hi=np.quantile(ens,[.1,.9],axis=1);pit=(ens<y[:,None,:]).mean(1)+np.random.default_rng(SEED).random(y.shape)*(ens==y[:,None,:]).mean(1)
   for k,lead in enumerate(NODES):
    h=hersbach(ens[:,:,k],y[:,k]);dec.append(dict(domain=key,method=m,lead=lead,**h))
    row=dict(domain=key,method=m,lead=lead,crps=c[:,k].mean(),fair_crps=fc[:,k].mean(),crpss=1-c[:,k].mean()/ref[:,k].mean(),twcrps=tc[:,k].mean(),brier90=bs[:,k].mean(),events90=int(event[:,k].sum()),rmse=np.mean(err[:,k]**2)**.5,bias=err[:,k].mean(),coverage80=np.mean((y[:,k]>=lo[:,k])&(y[:,k]<=hi[:,k])),width80=(hi[:,k]-lo[:,k]).mean());summary.append(row)
    cases.append(pd.DataFrame(dict(domain=key,method=m,lead=lead,date=dates,year=dates.year,season=season,observed=y[:,k],mean=avg[:,k],crps=c[:,k],fair_crps=fc[:,k],twcrps=tc[:,k],reference=ref[:,k],brier90=bs[:,k],prob90=prob[:,k],event90=event[:,k].astype(int),q90=q90[:,k],lower80=lo[:,k],upper80=hi[:,k],pit=pit[:,k])))
    for nominal in [.2,.4,.6,.8,.9,.95]:
     low,high=np.quantile(ens[:,:,k],[(1-nominal)/2,(1+nominal)/2],axis=1)
     cover.append(dict(domain=key,method=m,lead=lead,nominal=nominal,coverage=np.mean((y[:,k]>=low)&(y[:,k]<=high)),width=(high-low).mean()))
  original=np.load(ROOT/f'data/processed/{key}.npz');oy=expand(original['y']);odates=pd.DatetimeIndex(original['dates']);oseas=np.array(['DJF','MAM','JJA','SON'])[(odates.month.to_numpy()%12)//3]
  for year,f in zip(range(2000,2020),folds):
   meta=json.loads((EFOLDS/f'{key}_{year}.json').read_text());ix=f['train_index'];assert not np.isin(odates[ix].year,[year-1,year,year+1]).any();oi=f['oof_index'];oerr=oy[oi]-f['H1_oof'];W=f['H1_7_W'];G=np.linalg.solve(S7.T@np.linalg.solve(W,S7),S7.T@np.linalg.inv(W));P=S7@G
   ts=np.array(['DJF','MAM','JJA','SON'])[(pd.DatetimeIndex(f['dates']).month%12)//3]
   for ss in ['DJF','MAM','JJA','SON']:
    om,_=shrink(oerr[oseas[oi]==ss]);mask=ts==ss;obs=f['y'][mask,6];bu=f['H1_mean'][mask,:4].sum(1);lin=f['H1_7_linear'][mask,6];nn=f['H1_7_NN'][mask,:,6].mean(1)
    mechanism.append(dict(domain=key,year=year,season=ss,predicted=1-(P@om@P.T)[6,6]/om[:4,:4].sum(),mse_bu=np.mean((bu-obs)**2),mse_linear=np.mean((lin-obs)**2),mse_nn=np.mean((nn-obs)**2)))
   audit.append(dict(domain=key,year=year,base_failures=sum(not r['base_success'] for r in meta['records']),climate_failures=sum(not r['climate_success'] for r in meta['records']),n_train=len(ix),benchmark_reproduced=True))
  print('Extension scored',key,flush=True)
 C=pd.concat(cases);C.to_csv(EXT/'case_scores.csv.gz',index=False,compression='gzip');pd.DataFrame(summary).to_csv(EXT/'scores.csv',index=False);pd.DataFrame(dec).to_csv(EXT/'decomposition.csv',index=False);pd.DataFrame(cover).to_csv(EXT/'coverage_curves.csv',index=False);pd.DataFrame(audit).to_csv(EXT/'audit.csv',index=False)
 annual=C.groupby(['domain','method','lead','year'])[['crps','reference','twcrps','brier90']].mean();rng=np.random.default_rng(SEED+17);draw=rng.integers(0,20,(10000,20));flips=rng.choice([-1,1],(100000,20));years=np.arange(2000,2020)
 pairs=[('H1_7_NN','H0_7_NN'),('H1_7_NN','H1_5_NN'),('H1_7_NN','Bottom_up'),('H1_Direct','H0_Direct'),('H0_7_NN','H0_5_NN'),('H1_7_NN','H1_Direct')]
 comparisons=[];primary=[]
 for a,b in pairs:
  for key in REGIONS:
   for lead in NODES:
    for score in ['crps','twcrps','brier90']:
     aa=annual.loc[(key,a,lead)].reindex(years)[score].values;bb=annual.loc[(key,b,lead)].reindex(years)[score].values;diff=aa-bb;low,high=ci(diff,draw)
     comparisons.append(dict(domain=key,method=a,baseline=b,lead=lead,score=score,delta=diff.mean(),lower=low,upper=high,percent=100*(aa.mean()/bb.mean()-1),better_years=int((diff<0).sum())))
 for a,b in pairs[:3]:
  ds=[]
  for key in REGIONS:
   aa=annual.loc[(key,a,'D28')].reindex(years);bb=annual.loc[(key,b,'D28')].reindex(years);ds.append((aa.crps-bb.crps).values/aa.reference.mean())
  d=np.mean(ds,axis=0)*100;lo,hi=ci(d,draw);p=(1+np.sum(np.abs((flips*d).mean(1))>=abs(d.mean())))/(1+len(flips));primary.append(dict(method=a,baseline=b,delta_normalized_percent=d.mean(),lower=lo,upper=hi,p=p,better_years=int((d<0).sum())))
 order=np.argsort([r['p'] for r in primary]);adj=np.minimum(1,np.maximum.accumulate(np.array([primary[i]['p'] for i in order])*[3,2,1]))
 for i,p in zip(order,adj):primary[i]['p_holm']=p
 pd.DataFrame(comparisons).to_csv(EXT/'comparisons.csv',index=False);pd.DataFrame(primary).to_csv(EXT/'primary_comparisons.csv',index=False)
 M=pd.DataFrame(mechanism);M.to_csv(EXT/'mechanism_annual.csv',index=False);g=M.groupby(['domain','season'])[['predicted','mse_bu','mse_linear','mse_nn']].mean();g['real_linear']=1-g.mse_linear/g.mse_bu;g['real_nn']=1-g.mse_nn/g.mse_bu;g.to_csv(EXT/'mechanism_summary.csv');mat=np.array([df.set_index('year').reindex(years)[['predicted','mse_bu','mse_linear','mse_nn']].values for _,df in M.groupby(['domain','season'])]);corr=[]
 for dr in draw[:3000]:
  mm=mat[:,dr,:].mean(1);corr.append([spearmanr(mm[:,0],1-mm[:,j]/mm[:,1]).statistic for j in [2,3]])
 vals={l:dict(rho=float(spearmanr(g.predicted,g['real_'+l]).statistic),lower=float(np.quantile(np.array(corr)[:,j],.025)),upper=float(np.quantile(np.array(corr)[:,j],.975))) for j,l in enumerate(['linear','nn'])};(EXT/'mechanism_correlations.json').write_text(json.dumps(vals,indent=2))
 print(pd.DataFrame(primary).to_string(index=False),flush=True)
 print(pd.DataFrame(summary).query("lead=='D28'")[['domain','method','crps','twcrps','coverage80','width80']].to_string(index=False),flush=True)
if __name__=='__main__':main()
