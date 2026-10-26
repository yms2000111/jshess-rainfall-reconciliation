import sys, pathlib, urllib.request, concurrent.futures, json
sys.path.append( str(pathlib.Path(__file__).resolve().parents[1] / '_deps'))
urls = [
 'https://object-store.os-api.cci1.ecmwf.int/s2s-ai-challenge/data/training-input/0.3.0/netcdf/ecmwf-hindcast-tp-20200102.nc',
 'https://object-store.os-api.cci1.ecmwf.int/s2s-ai-challenge/data/training-input/0.3.0/netcdf/ecmf-hindcast-tp-20200102.nc',
 'https://object-store.os-api.cci1.ecmwf.int/s2s-ai-challenge/data/training-output-reference/tp-20200102.nc',
 'https://thredds.nci.org.au/thredds/dodsC/zv2/agcd/v1-0-1/precip/total/r005/01day/agcd_v1-0-1_precip_total_r005_daily_2000.nc.dds',
 'https://planette-ifs-46-day.s3.us-east-2.amazonaws.com/?list-type=2&prefix=reforecasts/&max-keys=5',
 'https://raw.githubusercontent.com/ecmwf-lab/climetlab-s2s-ai-challenge/main/climetlab_s2s_ai_challenge/training_input.yaml',
]
def probe(url):
 try:
  req=urllib.request.Request(url,headers={'Range':'bytes=0-2047'})
  with urllib.request.urlopen(req,timeout=45) as r:
   b=r.read(2048)
   return dict(url=url,status=r.status,headers=dict(r.headers),sample=repr(b[:1800]))
 except Exception as e:return dict(url=url,error=str(e))
if __name__=='__main__':
 with concurrent.futures.ThreadPoolExecutor(max_workers=6) as p:
  results=list(p.map(probe,urls))
 print(json.dumps(results,indent=2))
 out=pathlib.Path(__file__).resolve().parents[1]/'data'; out.mkdir(exist_ok=True)
 (out/'access_probe.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
