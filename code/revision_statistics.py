"""Scores, prespecified inference, calibration and mechanism diagnostics."""
from common import ROOT,REGIONS
import numpy as np,pandas as pd,json,argparse
from scipy.stats import spearmanr
from analyse import crps
from revision_cv import LEADS,FOLDS,OUT,SEED
from core_reconciliation import covariance_shrink,S

def hersbach(samples,y):
 """Hersbach reliability + potential, including empirical outlier frequencies.
 Potential = empirical uncertainty - resolution. Handles tied precipitation.
 """
 x=np.sort(np.asarray(samples),axis=1);y=np.asarray(y);n,m=x.shape
 widths=np.diff(x,axis=1)
 alpha=np.clip(y[:,None]-x[:,:-1],0,widths).mean(0)
 beta=np.clip(x[:,1:]-y[:,None],0,widths).mean(0)
 g=np.r_[0.,alpha+beta,0.];o=np.zeros(m+1)
 o[1:-1]=np.divide(beta,g[1:-1],out=np.zeros(m-1),where=g[1:-1]>0)
 o[0]=np.mean(y<=x[:,0]);o[-1]=np.mean(y<=x[:,-1])
 g[0]=np.maximum(x[:,0]-y,0).mean()/o[0] if o[0]>0 else 0
 g[-1]=np.maximum(y-x[:,-1],0).mean()/(1-o[-1]) if o[-1]<1 else 0
 p=np.arange(m+1)/m;reli=np.sum(g*(p-o)**2);potential=np.sum(g*o*(1-o))
 sy=np.sort(y);uncertainty=np.sum(sy*(2*np.arange(1,n+1)-n-1))/n**2
 return dict(reliability=reli,potential=potential,uncertainty=uncertainty,resolution=uncertainty-potential)

def ci(a,draw):return np.quantile(np.asarray(a)[draw].mean(1),[.025,.975])

def load_domain(key,qc):
 paths=[FOLDS/f'{qc}_{key}_{year}.npz' for year in range(2000,2020)]
 assert all(p.exists() for p in paths),f'Incomplete {qc} {key}'
 fold=[np.load(p) for p in paths]
 methods=[k for k in fold[0].files if fold[0][k].ndim==3]
 pred={m:np.concatenate([d[m] for d in fold]) for m in methods}
 data={k:np.concatenate([d[k] for d in fold]) for k in ['dates','y','mean_exact','crps_exact','threshold','climatology_crps','climatology_brier','mean_linear']}
 data['dates']=pd.DatetimeIndex(data['dates']);return pred,data,fold

def score_qc(qc):
 rows=[];cases=[];decomp=[];mechanism=[];fitdiag=[];audits=[];approx=[]
 for key in REGIONS:
  pred,data,fold=load_domain(key,qc);y=data['y'];dates=data['dates'];year=dates.year.to_numpy();season=np.array(['DJF','MAM','JJA','SON'])[(dates.month.to_numpy()%12)//3]
  rng=np.random.default_rng(SEED);u=rng.random(y.shape);ref=data['climatology_crps'];bref=data['climatology_brier'];threshold=data['threshold'];event=y>threshold
  for m,ens in pred.items():
   c=crps(ens,y);fc=crps(ens,y,True);avg=ens.mean(1);err=avg-y;accuracy=np.abs(ens-y[:,None,:]).mean(1);dispersal=accuracy-c
   if m=='Climatology':c=ref.copy()
   lo,hi=np.quantile(ens,[.1,.9],axis=1);coverage=(y>=lo)&(y<=hi);prob=(ens>threshold[:,None,:]).mean(1);brier=(prob-event)**2
   if m=='Climatology':brier=bref.copy()
   pit=(ens<y[:,None,:]).mean(1)+u*(ens==y[:,None,:]).mean(1);coherence=np.abs(ens[:,:,4]-ens[:,:,:4].sum(2)).mean(1)
   for k,lead in enumerate(LEADS):
    h=hersbach(ens[:,:,k],y[:,k]);assert abs(h['reliability']+h['potential']-crps(ens,y)[:,k].mean())<1e-8
    decomp.append(dict(domain=key,method=m,lead=lead,**h))
    rows.append(dict(domain=key,method=m,lead=lead,n=len(y),crps=c[:,k].mean(),fair_crps=fc[:,k].mean(),crpss=1-c[:,k].mean()/ref[:,k].mean(),rmse=np.mean(err[:,k]**2)**.5,bias=err[:,k].mean(),mae=np.abs(err[:,k]).mean(),coverage80=coverage[:,k].mean(),width80=(hi[:,k]-lo[:,k]).mean(),ensemble_sd=ens[:,:,k].std(1).mean(),brier=brier[:,k].mean(),bss=1-brier[:,k].mean()/bref[:,k].mean(),coherence=coherence.mean(),accuracy=accuracy[:,k].mean(),dispersal=dispersal[:,k].mean()))
    cases.append(pd.DataFrame(dict(domain=key,method=m,lead=lead,date=dates.strftime('%Y-%m-%d'),year=year,season=season,observed=y[:,k],mean=avg[:,k],crps=c[:,k],fair_crps=fc[:,k],reference=ref[:,k],brier=brier[:,k],brier_reference=bref[:,k],probability=prob[:,k],event=event[:,k].astype(int),threshold=threshold[:,k],lower80=lo[:,k],upper80=hi[:,k],pit=pit[:,k],accuracy=accuracy[:,k],dispersal=dispersal[:,k],coherence=coherence)))
   if m=='Direct_EMOS':
    for k,l in enumerate(LEADS):approx.append(dict(domain=key,lead=l,exact=data['crps_exact'][:,k].mean(),sample=c[:,k].mean(),delta=(c-data['crps_exact'])[:,k].mean()))
  for yr,f in zip(range(2000,2020),fold):
   datesf=pd.DatetimeIndex(f['dates']);seas=np.array(['DJF','MAM','JJA','SON'])[(datesf.month.to_numpy()%12)//3]
   original=np.load(ROOT/f'data/processed/{key}.npz');oi=f['oof_index'];odates=pd.DatetimeIndex(original['dates'])[oi];oseas=np.array(['DJF','MAM','JJA','SON'])[(odates.month.to_numpy()%12)//3];oerrors=original['y'][oi]-f['oof_mean']
   W=f['W'];G=np.linalg.solve(S.T@np.linalg.solve(W,S),S.T@np.linalg.inv(W));P=S@G
   for ss in ['DJF','MAM','JJA','SON']:
    ix=seas==ss;obs=f['y'][ix,4];bu=f['mean_exact'][ix,:4].sum(1);linear=f['mean_linear'][ix,4];nn=f['MinT_NN'][ix,:,4].mean(1)
    omega,_=covariance_shrink(oerrors[oseas==ss]);gain=1-(P@omega@P.T)[4,4]/omega[:4,:4].sum()
    mechanism.append(dict(domain=key,year=yr,season=ss,gain_predicted=float(gain),unconditional_gain=float(f['gain_predicted']),mse_bu=np.mean((bu-obs)**2),mse_linear=np.mean((linear-obs)**2),mse_nn=np.mean((nn-obs)**2)))
   meta=json.loads((FOLDS/f'{qc}_{key}_{yr}.json').read_text());orig=pd.DatetimeIndex(np.load(ROOT/f'data/processed/{key}.npz')['dates'])
   excluded=meta['excluded_years'];tr=np.array(meta['train']);assert not np.isin(orig[tr].year,excluded).any();assert not np.isin((orig[tr]+pd.Timedelta(days=28)).year,excluded).any()
   for split in meta['inner']:
    a=np.array(split['train']);b=np.array(split['validation']);assert set(a)<=set(tr) and set(b)<=set(tr) and not set(a)&set(b)
    assert not np.isin(orig[a].year,split['excluded_years']).any();assert not np.isin((orig[a]+pd.Timedelta(days=28)).year,split['excluded_years']).any()
   assert sorted(np.concatenate([z['validation'] for z in meta['inner']]).tolist())==sorted(tr.tolist())
   audits.append(dict(domain=key,year=yr,n_train=len(tr),n_oof=meta['n_residuals'],shrinkage=meta['shrinkage'],min_eigenvalue=meta['min_eigenvalue'],all_exclusions_pass=True))
   for k,lead in enumerate(LEADS):fitdiag.append(dict(domain=key,year=yr,lead=lead,in_sample_exact=f['insample_exact'][:,k].mean(),outer_exact=f['crps_exact'][:,k].mean(),legacy_exact=f['legacy_exact'][:,k].mean() if f['legacy_exact'].size else np.nan))
  print('Scored',qc,key,flush=True)
 output=OUT/qc;output.mkdir(exist_ok=True)
 C=pd.concat(cases,ignore_index=True);C.to_csv(output/'case_scores.csv.gz',index=False,compression='gzip');pd.DataFrame(rows).to_csv(output/'scores.csv',index=False);pd.DataFrame(decomp).to_csv(output/'decomposition.csv',index=False);pd.DataFrame(mechanism).to_csv(output/'mechanism_annual.csv',index=False);pd.DataFrame(fitdiag).to_csv(output/'fit_diagnostics.csv',index=False);pd.DataFrame(audits).to_csv(output/'fold_audit.csv',index=False);pd.DataFrame(approx).to_csv(output/'quantile_accuracy.csv',index=False)
 inference(C,output)

def inference(C,output):
 annual=C.groupby(['domain','method','lead','year'],sort=True)[['crps','reference']].mean();years=np.arange(2000,2020);rng=np.random.default_rng(SEED+17);draw=rng.integers(0,20,(10000,20));flips=rng.choice([-1,1],(100000,20));contrasts=[]
 for key in REGIONS:
  for lead in LEADS:
   for method,base in [('MinT_NN','Bottom_up'),('MinT_NN','Direct_EMOS'),('Bottom_up','Direct_EMOS'),('ECC11_NN','Schaake11_NN'),('ECC11_BU','Schaake11_BU'),('Direct_EMOS','Raw'),('Direct_EMOS','Seasonal_EMOS')]:
    if method not in C.method.unique() or base not in C.method.unique():continue
    a=annual.loc[(key,method,lead)].reindex(years).crps.to_numpy();b=annual.loc[(key,base,lead)].reindex(years).crps.to_numpy();diff=a-b;lower,upper=ci(diff,draw);pct=100*(a[draw].mean(1)/b[draw].mean(1)-1)
    contrasts.append(dict(domain=key,method=method,baseline=base,lead=lead,delta=diff.mean(),lower=lower,upper=upper,percent=100*(a.mean()/b.mean()-1),percent_lower=np.quantile(pct,.025),percent_upper=np.quantile(pct,.975),better_years=int((diff<0).sum())))
 pd.DataFrame(contrasts).to_csv(output/'comparisons.csv',index=False)
 primary=[];ayears=[]
 for title,base,leads in [('D28 versus bottom-up','Bottom_up',['D28']),('D28 versus direct','Direct_EMOS',['D28']),('Weekly versus bottom-up','Bottom_up',LEADS[:4])]:
  pieces=[];rawpieces=[]
  for key in REGIONS:
   for lead in leads:
    a=annual.loc[(key,'MinT_NN',lead)].reindex(years);b=annual.loc[(key,base,lead)].reindex(years);pieces.append((a.crps-b.crps).to_numpy()/a.reference.mean());rawpieces.append((a.crps-b.crps).to_numpy())
  d=np.mean(pieces,axis=0)*100;lower,upper=ci(d,draw);p=(1+np.sum(np.abs((flips*d).mean(1))>=abs(d.mean())))/(1+len(flips))
  primary.append(dict(comparison=title,delta_normalized_percent=d.mean(),lower=lower,upper=upper,p=p,better_years=int((d<0).sum()),absolute_mm=np.mean(rawpieces)))
  for yr,val in zip(years,d):ayears.append(dict(comparison=title,year=yr,delta_normalized_percent=val))
 order=np.argsort([r['p'] for r in primary]);adj=np.maximum.accumulate(np.array([primary[i]['p'] for i in order])*np.array([3,2,1]));adj=np.minimum(adj,1)
 for i,a in zip(order,adj):primary[i]['p_holm']=a
 pd.DataFrame(primary).to_csv(output/'primary_comparisons.csv',index=False);pd.DataFrame(ayears).to_csv(output/'primary_annual.csv',index=False)
 print(pd.DataFrame(primary).to_string(index=False),flush=True)
 # Mechanism intervals use the same year selections in every domain/season.
 M=pd.read_csv(output/'mechanism_annual.csv');g=M.groupby(['domain','season'])[['gain_predicted','mse_bu','mse_linear','mse_nn']].mean();g['gain_real_linear']=1-g.mse_linear/g.mse_bu;g['gain_real_nn']=1-g.mse_nn/g.mse_bu
 g.to_csv(output/'mechanism_summary.csv');mat=np.array([df.set_index('year').reindex(years)[['gain_predicted','mse_bu','mse_linear','mse_nn']].values for _,df in M.groupby(['domain','season'])]);corr=[]
 for sample in draw[:3000]:
  mean=mat[:,sample,:].mean(1);corr.append([spearmanr(mean[:,0],1-mean[:,j]/mean[:,1]).statistic for j in [2,3]])
 mc={}
 for j,label in enumerate(['linear','nn']):mc[label]=dict(rho=float(spearmanr(g.gain_predicted,g['gain_real_'+label]).statistic),lower=float(np.quantile(np.array(corr)[:,j],.025)),upper=float(np.quantile(np.array(corr)[:,j],.975)),n_cases=16,bootstrap=3000)
 (output/'mechanism_correlations.json').write_text(json.dumps(mc,indent=2))

def checks():
 rng=np.random.default_rng(77)
 for n,m in [(25,11),(100,200),(1,2),(30,1)]:
  x=np.maximum(rng.normal(size=(n,m)),0);y=np.maximum(rng.normal(size=n),0)
  h=hersbach(x,y);c=crps(x[:,:,None],y[:,None]).mean();assert np.isclose(h['reliability']+h['potential'],c,atol=1e-12)
 x=np.ones((5,11));y=np.array([0,1,1,1,3]);h=hersbach(x,y);assert np.isclose(h['reliability']+h['potential'],.6)
 print('PASS: Hersbach decomposition equals pairwise CRPS, including ties, outliers and degenerate ensembles.',flush=True)

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--qc',default='primary');p.add_argument('--test',action='store_true');args=p.parse_args();checks()
 if not args.test:
  for qc in (['primary','positive','signed'] if args.qc=='all' else [args.qc]):score_qc(qc)
