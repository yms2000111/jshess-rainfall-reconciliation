"""Chronological model fitting, empirical joint calibration and reconciliation."""
from common import *
import numpy as np,pandas as pd,json,itertools,importlib.metadata
import xgboost as xgb
OUT=ROOT/'results';OUT.mkdir(exist_ok=True)
DATA=ROOT/'data/processed'
DUR=np.array([7.,7.,7.,7.,28.]);LEADS=['W1','W2','W3','W4','D28']
METHODS=['Climatology','Raw','Seasonal BC','Quantile mapping','CSG EMOS','OLS','XGBoost','XGB pooled','XGB no indices','XGB + OLS-R','XGB + WLS-R']
SEED=20261023;NENS=200
def distance(a,b):
 d=np.abs(np.asarray(a)[...,None]-np.asarray(b));return np.minimum(d,366-d)
def features(raw,dates,climate,indices=True):
 phase=2*np.pi*(dates.dayofyear.to_numpy()-1)/365.2425
 seasonal=np.column_stack([np.sin(phase),np.cos(phase),np.sin(2*phase),np.cos(2*phase)])
 fields=[]
 for k in range(5):
  a=np.column_stack([np.log1p(raw[:,:,k].mean(1)/DUR[k]),np.log1p(raw[:,:,k].std(1,ddof=1)/DUR[k]),seasonal])
  if indices:a=np.column_stack([a,climate])
  fields.append(a)
 return np.stack(fields,axis=1)
def fit_predict(kind,X,y,train,pred,param=None,pooled=False):
 result=np.zeros((len(pred),5));models=[]
 groups=[[0,1,2,3],[4]] if pooled else [[k] for k in range(5)]
 for ks in groups:
  xt=X[train][:,ks,:].reshape(-1,X.shape[-1]);yt=np.log1p(y[train][:,ks]/DUR[ks]).ravel()
  xp=X[pred][:,ks,:].reshape(-1,X.shape[-1])
  if kind=='OLS':
   mu=xt.mean(0);sd=xt.std(0);sd[sd<1e-10]=1
   beta=np.linalg.lstsq(np.column_stack([np.ones(len(xt)),(xt-mu)/sd]),yt,rcond=None)[0]
   yp=np.column_stack([np.ones(len(xp)),(xp-mu)/sd])@beta
   models.append(dict(k=ks,beta=beta.tolist(),mu=mu.tolist(),sd=sd.tolist()))
  else:
   params=dict(objective='reg:squarederror',max_depth=param['depth'],eta=.04,min_child_weight=10,reg_lambda=10,subsample=1,colsample_bytree=1,seed=SEED,nthread=2,tree_method='hist')
   model=xgb.train(params,xgb.DMatrix(xt,label=yt),num_boost_round=param['rounds'])
   yp=model.predict(xgb.DMatrix(xp));models.append(model)
  result[:,ks]=yp.reshape(len(pred),len(ks))
 return result,models
def reconcile(samples,weights):
 """Exact diagonal weighted nonnegative projection onto total=sum(weeks)."""
 v=np.asarray(samples);w=np.asarray(weights);active=np.ones(v[...,:4].shape,bool)
 for _ in range(5):
  lam=((v[...,:4]*active).sum(-1)-v[...,4])/(w[4]+(w[:4]*active).sum(-1))
  b=v[...,:4]-lam[...,None]*w[:4]
  new=active&(b>0)
  if np.array_equal(new,active):break
  active=new
 b=np.maximum(b,0)*active
 return np.concatenate([b,b.sum(-1,keepdims=True)],axis=-1)
def crps(samples,y,fair=False):
 m=samples.shape[1];s=np.sort(samples,axis=1);coef=(2*np.arange(1,m+1)-m-1)[None,:,None]
 return np.abs(samples-y[:,None,:]).mean(1)-(s*coef).sum(1)/(m*(m-1) if fair else m*m)
def block_indices(n,B=2000,L=8):
 rng=np.random.default_rng(SEED+L);starts=rng.integers(0,n,(B,int(np.ceil(n/L))))
 return ((starts[:,:,None]+np.arange(L))%n).reshape(B,-1)[:,:n]
def bh(p):
 p=np.array(p);o=np.argsort(p);z=np.minimum.accumulate((p[o]*len(p)/np.arange(1,len(p)+1))[::-1])[::-1];q=np.empty(len(p));q[o]=np.minimum(z,1);return q
def run_region(key):
 d=np.load(DATA/f'{key}.npz');dates=pd.DatetimeIndex(d['dates']);raw=d['raw'];y=d['y'];climate=d['climate'];doy=dates.dayofyear.to_numpy()
 valid=np.isfinite(y).all(1)&np.isfinite(raw).all((1,2));end=dates+pd.Timedelta(days=28)
 train=np.flatnonzero(valid&(end<pd.Timestamp('2011-01-01')))
 val=np.flatnonzero(valid&(dates>=pd.Timestamp('2011-01-01'))&(end<pd.Timestamp('2013-01-01')))
 fit=np.flatnonzero(valid&(end<pd.Timestamp('2013-01-01')))
 cal=np.flatnonzero(valid&(dates>=pd.Timestamp('2013-01-01'))&(end<pd.Timestamp('2015-01-01')))
 test=np.flatnonzero(valid&(dates>=pd.Timestamp('2015-01-01'))&(dates<pd.Timestamp('2020-01-01')))
 assert end[fit].max()<dates[cal].min() and end[cal].max()<dates[test].min()
 X=features(raw,dates,climate);tuning=[]
 for dep,nr in itertools.product([2,3],[100,250]):
  par=dict(depth=dep,rounds=nr);pv,_=fit_predict('XGB',X,y,train,val,par)
  loss=float(np.mean((pv-np.log1p(y[val]/DUR))**2));tuning.append(dict(**par,validation_log_mse=loss))
 best=min(tuning,key=lambda v:v['validation_log_mse']);print(key,'tuning',best,flush=True)
 n=len(test);pred={};pred['Raw']=raw[test];rng=np.random.default_rng(SEED)
 clim=np.zeros((n,NENS,5));bc=raw[test].copy();climmean=np.zeros((n,5));threshold=np.zeros((n,5));residx=[]
 for i,t in enumerate(test):
  near=fit[distance(doy[t],doy[fit]).ravel()<=45]
  assert len(near)>=50
  clim[i]=y[rng.choice(near,NENS,replace=True)]
  climmean[i]=y[near].mean(0);threshold[i]=np.quantile(y[near],2/3,axis=0)
  ratio=y[near].mean(0)/np.maximum(raw[near].mean((0,1)),.1)
  bc[i]*=ratio
  residual_pool=np.flatnonzero(distance(doy[t],doy[cal]).ravel()<=60)
  if len(residual_pool)<20:residual_pool=np.arange(len(cal))
  residx.append(rng.choice(residual_pool,NENS,replace=True))
 pred['Climatology']=clim;pred['Seasonal BC']=bc;residx=np.asarray(residx)
 model_info={}
 for method,kind,indices,pooled in [('OLS','OLS',True,False),('XGBoost','XGB',True,False),('XGB pooled','XGB',True,True),('XGB no indices','XGB',False,False)]:
  xx=X if indices else features(raw,dates,climate,False)
  pp,models=fit_predict(kind,xx,y,fit,np.r_[cal,test],best,pooled)
  pc,pt=pp[:len(cal)],pp[len(cal):]
  residual=np.log1p(y[cal]/DUR)-pc
  samples=np.maximum(np.expm1(np.clip(pt[:,None,:]+residual[residx],-30,10)),0)*DUR
  pred[method]=samples
  if method=='XGBoost':
   errors=y[cal]-np.maximum(np.expm1(pc),0)*DUR
   weights=np.maximum(np.var(errors,axis=0,ddof=1),.01)
   pred['XGB + OLS-R']=reconcile(samples,np.ones(5));pred['XGB + WLS-R']=reconcile(samples,weights)
   model_info['wls_weights_mm2']=weights.tolist()
   for j,model in enumerate(models):model.save_model(OUT/f'{key}_xgb_{j}.json')
  if method=='OLS':model_info['ols_parameters']=models
 from rainfall_baselines import baseline_predictions
 qm,emos,emos_records,emos_exact=baseline_predictions(raw,y,dates,fit,test)
 pred['Quantile mapping']=qm;pred['CSG EMOS']=emos
 (OUT/f'{key}_emos_fit.json').write_text(json.dumps(emos_records,indent=2),encoding='utf-8')
 np.save(OUT/f'{key}_emos_exact_crps.npy',emos_exact)
 print(key,'EMOS fits',sum(q['success'] for q in emos_records),'/',len(emos_records),flush=True)
 obs=y[test];bi=block_indices(n);scores=[];cases=[];bootstrap=[]
 for method in METHODS:
  ens=pred[method];mean=ens.mean(1);c=crps(ens,obs);fc=crps(ens,obs,True);p=(ens>threshold[:,None,:]).mean(1);event=obs>threshold;bs=(p-event)**2;err=mean-obs
  lo,hi=np.quantile(ens,[.1,.9],axis=1);cover=((obs>=lo)&(obs<=hi)).astype(float)
  cref=crps(clim,obs);bref=((clim>threshold[:,None,:]).mean(1)-event)**2
  incoherence=np.abs(ens[:,:,4]-ens[:,:,:4].sum(2)).mean()
  for k,lead in enumerate(LEADS):
   pa=mean[:,k]-climmean[:,k];oa=obs[:,k]-climmean[:,k]
   acc=np.corrcoef(pa,oa)[0,1] if np.std(pa)>1e-10 and np.std(oa)>1e-10 else np.nan
   ci=np.quantile(c[bi,k].mean(1),[.025,.975])
   scores.append(dict(region=key,method=method,lead=lead,n=n,rmse=np.mean(err[:,k]**2)**.5,mae=np.abs(err[:,k]).mean(),bias=err[:,k].mean(),acc=acc,nse=1-np.sum(err[:,k]**2)/np.sum((obs[:,k]-obs[:,k].mean())**2),crps=c[:,k].mean(),fair_crps=fc[:,k].mean(),crpss=1-c[:,k].mean()/cref[:,k].mean(),crps_lo=ci[0],crps_hi=ci[1],brier=bs[:,k].mean(),bss=1-bs[:,k].mean()/bref[:,k].mean(),coverage80=cover[:,k].mean(),width80=(hi[:,k]-lo[:,k]).mean(),coherence_mae=incoherence))
   for i,t in enumerate(test):cases.append(dict(region=key,method=method,lead=lead,date=str(dates[t].date()),observed=obs[i,k],mean=mean[i,k],crps=c[i,k],brier=bs[i,k],probability=p[i,k],event=int(event[i,k]),threshold=threshold[i,k],climatology=climmean[i,k],lower80=lo[i,k],upper80=hi[i,k],rmm_amp=float(np.hypot(*climate[t,:2])),rmm_phase=int(d['rmm_phase'][t]),nino_sst=climate[t,2],nino_anomaly=d['enso_anom'][t],qc_max_decrease=d['qc_max_decrease'][t]))
   if method!='XGBoost':
    diff=c[:,k]-crps(pred['XGBoost'],obs)[:,k];bm=diff[bi].mean(1);ci=np.quantile(bm,[.025,.975]);pval=(np.sum(abs(bm-diff.mean())>=abs(diff.mean()))+1)/(len(bm)+1)
    bootstrap.append(dict(region=key,method=method,lead=lead,delta_crps=float(diff.mean()),lower=ci[0],upper=ci[1],p=pval))
 # Observational date sensitivity, with fixed trained distributions and targets shifted by one day.
 sens=[]
 for shift,ys in [(-1,d['y_shift_minus'][test]),(1,d['y_shift_plus'][test])]:
  for method in METHODS:
   c=crps(pred[method],ys).mean(0)
   for k,l in enumerate(LEADS):sens.append(dict(region=key,shift_days=shift,method=method,lead=l,crps=c[k]))
 # Archive every test trajectory to make figures and scores directly reproducible.
 np.savez_compressed(OUT/f'{key}_predictions.npz',dates=dates[test].values,observed=obs,threshold=threshold,climate=climate[test],**{m.replace(' ','_'):a for m,a in pred.items()})
 report=dict(region=key,train_n=len(train),validation_n=len(val),fit_n=len(fit),calibration_n=len(cal),test_n=len(test),fit_last_valid=str(end[fit].max()),calibration_first_origin=str(dates[cal].min()),calibration_last_valid=str(end[cal].max()),test_first_origin=str(dates[test].min()),tuning=tuning,best=best,**model_info)
 (OUT/f'{key}_design.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
 return scores,cases,bootstrap,sens
if __name__=='__main__':
 import argparse
 parser=argparse.ArgumentParser();parser.add_argument('--positive-part',action='store_true');args=parser.parse_args()
 if args.positive_part:DATA=ROOT/'data/processed_positive_part';OUT=ROOT/'results_positive_part';OUT.mkdir(exist_ok=True)
 allscores=[];allcases=[];allboot=[];allsens=[]
 for key in REGIONS:
  s,c,b,se=run_region(key);allscores.extend(s);allcases.extend(c);allboot.extend(b);allsens.extend(se)
 score=pd.DataFrame(allscores);case=pd.DataFrame(allcases);boot=pd.DataFrame(allboot)
 primary=(boot.method=='XGB + WLS-R')&(boot.lead!='W1');boot.loc[primary,'q_primary']=bh(boot.loc[primary,'p'])
 score.to_csv(OUT/'scores.csv',index=False);case.to_csv(OUT/'case_scores.csv',index=False);boot.to_csv(OUT/'paired_comparisons.csv',index=False);pd.DataFrame(allsens).to_csv(OUT/'date_sensitivity.csv',index=False)
 versions={m:importlib.metadata.version(m) for m in ['numpy','pandas','xgboost','scipy','matplotlib','xarray','h5py']}
 (OUT/'software_versions.json').write_text(json.dumps(versions,indent=2));print(score.query("lead=='D28'")[['region','method','crps','crpss','coherence_mae']].to_string(index=False),flush=True)
