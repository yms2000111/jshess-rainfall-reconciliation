import sys,pathlib,importlib
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]/'_deps'))
for n in ['numpy','pandas','matplotlib.pyplot','scipy.optimize','h5py','netCDF4','xgboost','zarr','icechunk']:
 try:
  m=importlib.import_module(n); print(n,'OK',getattr(m,'__version__',''),flush=True)
 except Exception as e: print(n,type(e).__name__,str(e)[:180],flush=True)
