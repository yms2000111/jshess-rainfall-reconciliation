"""Independent identities, numerical integration and archived Eqn 11 checks."""
from common import ROOT
import numpy as np,pandas as pd,json
from scipy.integrate import quad
from scipy.stats import gamma
from scipy.optimize import nnls
from extension_cv import S5,S7,reconcile,shrink,expand
from revision_cv import mean_csg
from rainfall_baselines import csg_crps
R=ROOT/'revision/review_v5';rng=np.random.default_rng(20261025);checks={}
for n,S in [(5,S5),(7,S7)]:
 residuals=[];nnerrors=[];varerrors=[]
 for _ in range(40):
  A=rng.normal(size=(n,n));W=A@A.T+np.eye(n);G=np.linalg.solve(S.T@np.linalg.solve(W,S),np.linalg.solve(W,S).T);P=S@G
  residuals.extend([np.max(abs(G@S-np.eye(4))),np.max(abs(P@P-P)),np.max(abs(P@S-S))])
  v=rng.normal(2,8,size=n);L=np.linalg.cholesky(W)
  expected=nnls(np.linalg.solve(L,S),np.linalg.solve(L,v))[0]
  actual=reconcile(v,W,S,True);nnerrors.append(np.max(abs(actual-S@expected)))
  B=rng.normal(size=(n,n));O=B@B.T
  varerrors.append(abs((P@O@P.T)[-1,-1]-P[-1]@O@P[-1]))
 checks[f'{n}_node_projection']={'max_identity_error':max(residuals),'max_nonnegative_vs_scipy_nnls_error':max(nnerrors),'max_covariance_identity_error':max(varerrors)}
 assert max(residuals+nnerrors+varerrors)<1e-9
err=[]
for _ in range(100):
 variances=np.exp(rng.normal(size=5));v=rng.normal(size=5);w=v[:4]+variances[:4]/variances.sum()*(v[4]-v[:4].sum())
 err.append(np.max(abs(reconcile(v,np.diag(variances),S5,False)-S5@w)))
checks['Eqn_8_diagonal_closed_form_max_error']=max(err);assert max(err)<1e-9
integrals=[]
for mu,var,shift,y in [(3,4,.5,0),(3,4,.5,6),(.5,.8,2,0),(20,100,2,30)]:
 k=mu**2/var;theta=var/mu
 F=lambda z:gamma.cdf(z+shift,k,scale=theta)
 numerical=quad(lambda z:F(z)**2,0,y,epsabs=1e-9)[0]+quad(lambda z:(1-F(z))**2,y,np.inf,epsabs=1e-9)[0]
 closed=float(csg_crps(y,mu,var,shift));mn=quad(lambda z:1-F(z),0,np.inf)[0]
 integrals.append({'mean':mu,'variance':var,'shift':shift,'observation':y,'crps_absolute_error':abs(closed-numerical),'censored_mean_absolute_error':abs(float(mean_csg(mu,var,shift))-mn)})
 assert abs(closed-numerical)<1e-7 and abs(float(mean_csg(mu,var,shift))-mn)<1e-7
checks['CSG_closed_form_vs_CDF_integration']=integrals
def empirical(x,y):return np.mean(abs(x-y))-.5*np.mean(abs(x[:,None]-x[None,:]))
xs=np.array([0.,0.,2.,5.,9.]);y=4.;q=3.
cuts=sorted(set([q,y]+xs[xs>=q].tolist()));numeric=sum((b-a)*((xs<((a+b)/2)).mean()-float(y<((a+b)/2)))**2 for a,b in zip(cuts[:-1],cuts[1:]))
checks['Eqn_10_threshold_identity_error']=abs(empirical(np.maximum(xs,q),max(y,q))-numeric);assert checks['Eqn_10_threshold_identity_error']<1e-12
components=[rng.gamma(2,3,size=m) for m in [11,31,43]];weights=np.array([.2,.3,.5]);target=4
weighted=sum(w*np.mean(abs(x-target)) for w,x in zip(weights,components))-.5*sum(weights[j]*weights[k]*np.mean(abs(components[j][:,None]-components[k][None,:])) for j in range(3) for k in range(3))
x=np.concatenate(components);w=np.concatenate([np.full(len(x),p/len(x)) for p,x in zip(weights,components)])
direct=w@abs(x-target)-.5*np.einsum('i,ij,j->',w,abs(x[:,None]-x[None,:]),w)
checks['Eqn_S4_mixture_identity_error']=abs(weighted-direct);assert abs(weighted-direct)<1e-12
weekly=rng.gamma(2,5,size=(100,4));T=weekly.sum(1);s0=20;a=.1;b=-.2;g=s0*np.exp(a)*(T/s0)**np.exp(b);mapped=weekly/T[:,None]*g[:,None]
checks['Eqns_S1_S2_max_coherence_error']=float(np.max(abs(mapped.sum(1)-g)));assert checks['Eqns_S1_S2_max_coherence_error']<1e-10
record=pd.read_csv(ROOT/'revision/extension/mechanism_annual.csv');errs=[]
for key in ['N','NE','SE','SW']:
 original=np.load(ROOT/f'data/processed/{key}.npz');oy=expand(original['y']);dates=pd.DatetimeIndex(original['dates']);seasons=np.array(['DJF','MAM','JJA','SON'])[(dates.month.to_numpy()%12)//3]
 for year in range(2000,2020):
  with np.load(ROOT/f'revision/extension/folds/{key}_{year}.npz') as f:
   W=f['H1_7_W'];G=np.linalg.solve(S7.T@np.linalg.solve(W,S7),np.linalg.solve(W,S7).T);P=S7@G;ix=f['oof_index'];errors=oy[ix]-f['H1_oof']
   for season in ['DJF','MAM','JJA','SON']:
    O,_=shrink(errors[seasons[ix]==season]);Vlin=float(P[6]@O@P[6]);Vbu=float(np.ones(4)@O[:4,:4]@np.ones(4));gain=1-Vlin/Vbu
    stored=float(record.query('domain==@key and year==@year and season==@season').predicted.iloc[0]);errs.append(abs(gain-stored))
checks['Eqn_11_archived_fold_season_checks']={'cases':len(errs),'max_absolute_difference':max(errs),'passed':max(errs)<1e-10}
assert max(errs)<1e-10
checks['interpretation']=['Variance excludes squared bias; MSE includes it.','The fixed linear projection covariance identity does not extend unchanged to a nonlinear nonnegative projection.','Predicted gains average fold ratios; realised gains are ratios of year-averaged MSEs.','No numerical research results changed.']
(R/'mathematics_audit.json').write_text(json.dumps(checks,indent=2),encoding='utf-8');print(json.dumps(checks,indent=2))
