"""Empirical quantile mapping and censored-shifted-gamma EMOS.
CSG CRPS follows Scheuerer & Hamill (2015), Baran & Nemoda (2016).
Season-specific exchangeable-member parameterisation is stated explicitly.
"""
from common import *
import numpy as np,json
from scipy.special import gammainc,beta
from scipy.stats import gamma
from scipy.optimize import minimize

def csg_crps(y,mu,var,shift):
 k=mu*mu/var;theta=var/mu;c=shift/theta;z=(y+shift)/theta
 fc=gammainc(k,c)
 return (y+shift)*(2*gammainc(k,z)-1)-mu/np.pi*beta(.5,k+.5)*(1-gammainc(2*k,2*c))+mu*(1+2*fc*gammainc(k+1,c)-fc*fc-2*gammainc(k+1,z))-shift*fc*fc

def baseline_predictions(raw,y,dates,fit,test,seed=20261023):
 doy=dates.dayofyear.to_numpy();qm=np.empty_like(raw[test]);month=dates.month.to_numpy();season=(month%12)//3
 for i,t in enumerate(test):
  dist=np.abs(doy[fit]-doy[t]);near=fit[np.minimum(dist,366-dist)<=45]
  for k in range(5):
   a=np.sort(raw[near,:,k].ravel());unique,first,count=np.unique(a,return_index=True,return_counts=True)
   prob=(first+(count-1)/2+.5)/len(a);p=np.interp(raw[t,:,k],unique,prob)
   qm[i,:,k]=np.quantile(y[near,k],p)
 rng=np.random.default_rng(seed+77);u=rng.uniform(1e-8,1-1e-8,(len(test),200,5));out=np.empty_like(u);records=[];exact=np.empty((len(test),5))
 for s in range(4):
  tr=fit[season[fit]==s];ix=np.flatnonzero(season[test]==s)
  for k in range(5):
   scale=max(float(y[tr,k].mean()),.1);x=raw[tr,:,k].mean(1)/scale;obs=y[tr,k]/scale
   def decode(p,xx):
    a,b,c,d,shift=np.exp(p);return a+b*xx,c+d*xx,shift
   def objective(p):
    mu,var,shift=decode(p,x);v=csg_crps(obs,mu,var,shift);return float(np.mean(v)) if np.isfinite(v).all() else 1e10
   fits=[]
   for start in [[.1,1,.1,1,.1],[.5,.5,1,1,.5]]:
    res=minimize(objective,np.log(start),method='L-BFGS-B',bounds=[(-10,5)]*5,options={'maxiter':400,'ftol':1e-10,'maxls':40});fits.append(res)
   best=min(fits,key=lambda r:r.fun);mu,var,shift=decode(best.x,raw[test[ix],:,k].mean(1)/scale);shape=mu*mu/var;theta=var/mu
   out[ix,:,k]=np.maximum(gamma.ppf(u[ix,:,k],shape[:,None],scale=theta[:,None])-shift,0)*scale
   exact[ix,k]=csg_crps(y[test[ix],k]/scale,mu,var,shift)*scale
   records.append(dict(season=int(s),lead=int(k),train_n=len(tr),scale_mm=scale,parameters=np.exp(best.x).tolist(),success=bool(best.success),message=str(best.message),objective=float(best.fun),iterations=int(best.nit)))
 return qm,out,records,exact
