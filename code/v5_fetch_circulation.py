"""Download a bounded NOAA monthly 850 hPa circulation subset."""
from common import ROOT
import urllib.request,urllib.parse,json,time,hashlib
R=ROOT/'revision/review_v5/circulation';R.mkdir(parents=True,exist_ok=True)
plan='''# Exploratory circulation diagnostic specified 25 October 2026

Forecast skill and northern summer concentration have already been inspected. Obtain monthly NCEP/NCAR Reanalysis 1 850 hPa specific humidity and horizontal winds for 2000–2019, 100–155 E and 25 S–5 N. Compare summer and winter climatological circulation, then relate calendar-year DJF mean zonal wind over 120–140 E, 5–15 S to that year's northern H1-minus-H0 28-day CRPS. Use all twenty years and a year-bootstrap descriptive interval for Spearman correlation. This fixed box describes the broad monsoon flow and is distinct from the rainfall verification domain. A monthly diagnostic cannot resolve individual MJO passages or prove that DMI causes a forecast improvement. Products of monthly humidity and wind describe mean-flow moisture transport only, excluding submonthly covariance and vertical integration. Do not tune the domain or season after viewing these fields.
'''
(R/'plan.md').write_text(plan,encoding='utf-8')
log=[]
for var in ['uwnd','vwnd','shum']:
 target=R/(var+'_850_monthly.nc')
 if target.exists():continue
 params={'var':var,'north':5,'south':-25,'west':100,'east':155,'horizStride':1,'time_start':'2000-01-01T00:00:00Z','time_end':'2019-12-31T23:59:59Z','timeStride':1,'vertCoord':850,'accept':'netcdf3'}
 for folder in ['ncep.reanalysis/Monthlies/pressure','ncep.reanalysis.derived/pressure']:
  url='https://psl.noaa.gov/thredds/ncss/grid/Datasets/'+folder+'/'+var+'.mon.mean.nc?'+urllib.parse.urlencode(params)
  try:
   req=urllib.request.Request(url,headers={'User-Agent':'Research data retrieval'})
   with urllib.request.urlopen(req,timeout=60) as response:data=response.read()
   if not (data.startswith(b'CDF') or data.startswith(b'\x89HDF')):raise ValueError('Not a NetCDF response')
   target.write_bytes(data);log.append(dict(variable=var,url=url,bytes=len(data),sha256=hashlib.sha256(data).hexdigest()));print(var,len(data),flush=True);break
  except Exception as exc:log.append(dict(variable=var,url=url,error=str(exc)));print(var,str(exc),flush=True)
 (R/'retrieval.json').write_text(json.dumps(log,indent=2),encoding='utf-8')
