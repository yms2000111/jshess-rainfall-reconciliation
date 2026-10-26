from analyse import reconcile,crps
import numpy as np
from scipy.optimize import nnls
rng=np.random.default_rng(42);S=np.vstack([np.eye(4),np.ones(4)])
for _ in range(30):
 v=rng.exponential(20,5);w=rng.uniform(.1,10,5);out=reconcile(v,w)
 ref=nnls(S/np.sqrt(w[:,None]),v/np.sqrt(w))[0]
 assert np.allclose(out[:4],ref,rtol=1e-9,atol=1e-8)
 assert out.min()>=0 and abs(out[4]-out[:4].sum())<1e-9
x=rng.normal(size=(7,11,5));y=rng.normal(size=(7,5))
brute=np.abs(x-y[:,None,:]).mean(1)-.5*np.abs(x[:,:,None,:]-x[:,None,:,:]).mean((1,2))
assert np.allclose(crps(x,y),brute)
coherent=rng.exponential(10,(8,20,4));coherent=np.concatenate([coherent,coherent.sum(-1,keepdims=True)],-1)
assert np.allclose(reconcile(coherent,np.ones(5)),coherent)
print('PASS: nonnegative reconciliation agrees with independent NNLS; coherent forecasts invariant; CRPS agrees with pairwise formula.')
from rainfall_baselines import csg_crps
from scipy.integrate import quad
from scipy.stats import gamma
for mu,var,shift,y0 in [(2.,3.,.4,0.),(2.,3.,.4,4.),(.4,2.,1.,.01),(10.,3.,.2,12.)]:
 k=mu*mu/var;theta=var/mu
 f=lambda x:gamma.cdf(x+shift,k,scale=theta)
 ref=quad(lambda x:f(x)**2,0,y0)[0]+quad(lambda x:(1-f(x))**2,y0,np.inf)[0]
 assert np.isclose(csg_crps(y0,mu,var,shift),ref,atol=1e-7)
print('PASS: closed-form censored-shifted-gamma CRPS agrees with independent numerical CDF integration.')
from core_reconciliation import project,covariance_shrink
for _ in range(40):
 A=rng.normal(size=(5,5));W=A@A.T+np.eye(5)*.2;v=rng.exponential(20,5);L=np.linalg.cholesky(np.linalg.inv(W)).T
 expected=nnls(L@S,L@v)[0];actual=project(v,W)
 assert np.allclose(actual[:4],expected,atol=1e-7)
assert np.allclose(project(coherent,W),coherent,atol=1e-8)
v=np.array([1.,1.,1.,1.,8.]);assert np.allclose(project(v,np.diag([1,1,1,1,4]),False),[1.5,1.5,1.5,1.5,6])
W,lam=covariance_shrink(rng.normal(size=(102,5)));assert np.linalg.eigvalsh(W).min()>0 and 0<=lam<=1
print('PASS: full covariance projection agrees with independent NNLS; diagonal example and covariance positivity verified.')
