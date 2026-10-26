"""Fixed northern monsoon diagnostic from independent reanalysis fields."""
from common import ROOT
import netCDF4 as nc,numpy as np,pandas as pd,json,hashlib
from scipy.stats import spearmanr,rankdata
R=ROOT/'revision/review_v5';C=R/'circulation';fields={};metadata={}
for file,var in [('uwnd','u'),('vwnd','v'),('shum','qa')]:
 path=C/(file+'_850_monthly.nc');ds=nc.Dataset('memory',memory=path.read_bytes());t=np.asarray(ds.variables['T'][:]);lat=np.asarray(ds.variables['Y'][:]);lon=np.asarray(ds.variables['X'][:]);p=np.asarray(ds.variables['P'][:]);a=ds.variables[var][:]
 assert np.array_equal(p,[850]) and a.shape==(240,1,13,23) and not np.ma.getmaskarray(a).any()
 assert np.allclose(t,np.arange(480,720)+.5)
 fields[file]=np.asarray(a[:,0],float);metadata[file]={'units':ds.variables[var].units,'time_units':ds.variables['T'].units,'calendar':ds.variables['T'].calendar,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()};ds.close()
assert metadata['uwnd']['units']=='m/s' and metadata['vwnd']['units']=='m/s'
assert metadata['shum']['units'] in ['unitless','kg/kg','kg kg-1']
dates=pd.date_range('2000-01-01',periods=240,freq='MS')
# IRI's monthly coordinate uses a 360-calendar indexing convention. Month
# identities, not fictitious daily timestamps, are matched to Gregorian months.
y0=np.maximum(lat-1.25,-15);y1=np.minimum(lat+1.25,-5);wy=np.maximum(0,np.sin(np.deg2rad(y1))-np.sin(np.deg2rad(y0)))
wx=np.maximum(0,np.minimum(lon+1.25,140)-np.maximum(lon-1.25,120));w=wy[:,None]*wx[None,:];w/=w.sum()
u=(fields['uwnd']*w).sum((1,2));q=(fields['shum']*w).sum((1,2))*1000
monthly=pd.DataFrame({'u850':u,'q850_gkg':q},index=dates)
rain=pd.read_csv(ROOT/'data/processed/agcd_daily_regional_mm.csv',index_col=0,parse_dates=True).loc['2000':'2019','N'].resample('MS').sum();monthly['rainfall_mm']=rain
monthly.to_csv(C/'monthly_monsoon.csv',index_label='month')
case=pd.read_csv(ROOT/'revision/extension/case_scores.csv.gz').query('domain=="N" and lead=="D28" and season=="DJF" and method in ["H0_7_NN","H1_7_NN"]')
s=case.groupby(['year','method']).crps.mean().unstack();annual=monthly[monthly.index.month.isin([12,1,2])].groupby(lambda d:d.year).mean();annual['h1_minus_h0_crps']=s.H1_7_NN-s.H0_7_NN
annual.to_csv(C/'annual_djf_diagnostic.csv',index_label='year')
idx=np.random.default_rng(2026102531).integers(0,20,(50000,20));x=annual.u850.values;y=annual.h1_minus_h0_crps.values
rx=rankdata(x[idx],axis=1);ry=rankdata(y[idx],axis=1);rx-=rx.mean(1)[:,None];ry-=ry.mean(1)[:,None];corr=(rx*ry).sum(1)/np.sqrt((rx*rx).sum(1)*(ry*ry).sum(1));lo,hi=np.quantile(corr,[.025,.975])
summary={'spearman':float(spearmanr(x,y).statistic),'lower':float(lo),'upper':float(hi),'years':20,'calendar_handling':'Map 480.5 through 719.5 months since January 1960 to January 2000 through December 2019; no daily interpretation of 360-day coordinates.','source':'NCEP/NCAR Reanalysis 1 distributed by IRI Data Library; retrieved as bounded NetCDF subsets.','fields':metadata}
for season,months in [('DJF',[12,1,2]),('JJA',[6,7,8])]:
 summary[season]=monthly[monthly.index.month.isin(months)].mean().to_dict()
(C/'summary.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2))
np.savez_compressed(C/'verified_fields.npz',**fields,lat=lat,lon=lon,dates=dates.values)
