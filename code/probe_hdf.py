import sys,pathlib,io,urllib.request,json
ROOT=pathlib.Path(__file__).resolve().parents[1]; sys.path.append(str(ROOT/'_deps'))
import truststore; truststore.inject_into_ssl()
import h5py,fsspec,xarray as xr
url='https://object-store.os-api.cci1.ecmwf.int/s2s-ai-challenge/data/training-input/0.3.0/netcdf/ecmwf-hindcast-tp-20200102.nc'
f=fsspec.open(url,block_size=65536,cache_type='blockcache').open()
h=h5py.File(f,'r')
for k,v in h.items():print(k,v.shape,v.chunks,dict(v.attrs),flush=True)
ds=xr.open_dataset(f,engine='h5netcdf',decode_timedelta=True)
print(ds,flush=True)
print(ds.tp.isel(forecast_time=0,realization=0,lead_time=7).sel(latitude=slice(-10,-40),longitude=slice(114,153)).load(),flush=True)
