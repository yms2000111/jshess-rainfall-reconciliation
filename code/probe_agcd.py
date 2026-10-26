import sys,pathlib,urllib.request
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.append(str(ROOT/'_deps'))
import truststore;truststore.inject_into_ssl()
import xarray as xr
u='https://thredds.nci.org.au/thredds/dodsC/zv2/agcd/v1-0-1/precip/total/r005/01day/agcd_v1-0-1_precip_total_r005_daily_2000.nc'
ds=xr.open_dataset(u,engine='pydap')
print(ds,ds.attrs,ds.precip.attrs,flush=True)
print(ds.lat.values[:5],ds.lon.values[:5],ds.time.values[:5],flush=True)
tiny=ds.precip.isel(time=slice(0,7)).sel(lat=slice(-15.75,-12.75),lon=slice(131.25,134.25)).load()
print(tiny.shape,flush=True)
tiny.to_netcdf(ROOT/'data/agcd_sample.nc',engine='h5netcdf')
(ROOT/'data/agcd_metadata.txt').write_text(str(ds)+'\n'+repr(ds.attrs)+'\n'+repr(ds.precip.attrs),encoding='utf-8')
