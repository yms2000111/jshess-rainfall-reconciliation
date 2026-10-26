from extension_cv import *
from analyse import crps
from scipy.optimize import nnls
from scipy.integrate import quad
rng=np.random.default_rng(19)
for Sx in [S5,S7]:
 a=rng.normal(size=(Sx.shape[0],Sx.shape[0]));W=a@a.T+np.eye(Sx.shape[0]);x=rng.normal(size=(10,Sx.shape[0]))*10
 got=reconcile(x,W,Sx);L=np.linalg.cholesky(np.linalg.inv(W)).T
 want=np.array([Sx@nnls(L@Sx,L@row)[0] for row in x]);assert np.allclose(got,want,atol=1e-6);assert got.min()>=0
 b=rng.uniform(size=(10,4));assert np.allclose(reconcile(b@Sx.T,W,Sx),b@Sx.T)
x=rng.exponential(2,(13,1));y=2.7;threshold=1.5
tc=crps(np.maximum(x[None],threshold),np.array([[max(y,threshold)]]))[0,0]
edges=np.unique(np.r_[threshold,x.ravel()[x.ravel()>threshold],y]);numeric=0.
for a,b in zip(edges[:-1],edges[1:]):numeric+=(b-a)*(np.mean(x<=(a+b)/2)-int(y<=(a+b)/2))**2
assert abs(tc-numeric)<1e-12
for key in REGIONS:
 d,dates,_,_=load_data(key,'primary');z,a=climate(dates,d);assert z.shape==(1060,5);assert (a.rmm_date<a.origin).all()
print('PASS: 5/7-node NNLS, coherent invariance, nonnegativity, upper-tail CRPS integral and predictor-date audit.')
