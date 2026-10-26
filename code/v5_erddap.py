from common import ROOT
import truststore;truststore.inject_into_ssl()
import requests,json
R=ROOT/'revision/review_v5/circulation';R.mkdir(exist_ok=True)
base='https://upwell.pfeg.noaa.gov/erddap/'
for var in ['uwnd','vwnd','shum']:
 data=requests.get(base+'search/index.json',params={'page':1,'itemsPerPage':100,'searchFor':var+' monthly'},timeout=60).json()
 (R/(var+'_search.json')).write_text(json.dumps(data))
 rows=[r for r in data['table']['rows'] if ('monthly mean' in r[7].lower() and 'from the NCEP Reanalysis' in r[7] and '1948' in r[7] and 'sig995' not in r[7] and '10m' not in r[7])]
 print(var,[(r[-1],r[7]) for r in rows],flush=True)
 if len(rows)!=1:continue
 ident=rows[0][-1];info=requests.get(base+'info/'+ident+'/index.json',timeout=60);info.raise_for_status();(R/(var+'_info.json')).write_text(info.text)
 r=requests.get(base+'griddap/'+ident+'.dds',timeout=60);r.raise_for_status();(R/(var+'_dds.txt')).write_text(r.text);print(r.text,flush=True)
 (R/(var+'_dataset.txt')).write_text(ident)
 query=var+'[(2000-01-01T00:00:00Z):1:(2019-12-01T00:00:00Z)][(850)][(5):1:(-25)][(100):1:(155)]'
 target=R/(var+'_850_monthly.nc')
 if not target.exists():
  response=requests.get(base+'griddap/'+ident+'.nc?'+query,timeout=120);response.raise_for_status()
  assert response.content.startswith(b'CDF') or response.content.startswith(b'\x89HDF')
  target.write_bytes(response.content);print('Downloaded',var,len(response.content),flush=True)
