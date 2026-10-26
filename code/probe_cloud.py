import sys,pathlib,json,urllib.request
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT/'_deps'))
import icechunk,xarray as xr
storage=icechunk.s3_storage(bucket='planette-ifs-46-day',prefix='reforecasts',region='us-east-2',anonymous=True)
repo=icechunk.Repository.open(storage)
session=repo.readonly_session('main')
ds=xr.open_zarr(session.store,group='single/1p5latx1p5lon',consolidated=False,chunks=None)
print(ds,flush=True)
for n in ['pr','init_time','lead','number','lat','lon']:
 print(n,ds[n].attrs, ds[n].encoding,flush=True)
 if n!='pr':print(ds[n].values[:40],ds[n].values[-10:],flush=True)
(ROOT/'data/cloud_metadata.txt').write_text(str(ds)+'\n'+repr(ds.pr.attrs)+'\n'+repr(ds.pr.encoding),encoding='utf-8')
tiny=ds.pr.isel(init_time=slice(0,2),number=slice(0,1),lead=slice(0,2),lat=slice(65,67),lon=slice(85,87)).load()
print(tiny, tiny.values,flush=True)
tiny.to_netcdf(ROOT/'data/cloud_sample.nc')
