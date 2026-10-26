"""Original publication figures from archived observations and test predictions."""
from common import *
import numpy as np,pandas as pd,json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon,Rectangle,FancyArrowPatch
from matplotlib.colors import TwoSlopeNorm
F=ROOT/'figures';F.mkdir(exist_ok=True)
plt.rcParams.update({'font.family':'DejaVu Serif','font.size':9,'axes.titlesize':10,'axes.labelsize':9,'legend.fontsize':8,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42,'svg.fonttype':'none','savefig.facecolor':'white'})
S=pd.read_csv(ROOT/'results/scores.csv');C=pd.read_csv(ROOT/'results/case_scores.csv');B=pd.read_csv(ROOT/'results/paired_comparisons.csv');H=pd.read_csv(ROOT/'results/climate_conditions.csv')
METHODS=['Raw','Seasonal BC','OLS','XGBoost','XGB + WLS-R']
LABEL={'Raw':'ECMWF (QC)','Seasonal BC':'Seasonal correction','OLS':'OLS','XGBoost':'XGBoost','XGB + WLS-R':'XGBoost + WLS','XGB + OLS-R':'XGBoost + OLS reconciliation'}
COL={'Raw':'#333333','Seasonal BC':'#929292','OLS':'#0072B2','XGBoost':'#D55E00','XGB + WLS-R':'#009E73'}
RC={'N':'#CC6677','NE':'#44AA99','SE':'#4477AA','SW':'#AA4499'}
countries=json.loads((ROOT/'data/support/countries.geojson').read_text(encoding='utf-8'))
aus=[v for v in countries['features'] if v['properties'].get('ADMIN')=='Australia'][0]['geometry']
def save(fig,name):
 for ext in ['png','pdf','svg']:fig.savefig(F/f'{name}.{ext}',dpi=600,bbox_inches='tight')
 plt.close(fig)
def base_map(ax):
 polys=aus['coordinates'] if aus['type']=='MultiPolygon' else [aus['coordinates']
 ]
 for poly in polys:ax.add_patch(Polygon(poly[0],facecolor='#f4f4f1',edgecolor='#555555',lw=.6,zorder=1))
 ax.set(xlim=(111,155),ylim=(-44.5,-9),xticks=[115,125,135,145,155],yticks=[-40,-30,-20,-10])
 ax.set_xticklabels(['115°E','125°E','135°E','145°E','155°E']);ax.set_yticklabels(['40°S','30°S','20°S','10°S']);ax.set_aspect(1.12);ax.grid(lw=.3,alpha=.3,zorder=0)
def panel(ax,label):ax.text(-.13,1.11,label,transform=ax.transAxes,fontweight='bold',fontsize=11,va='bottom',ha='left',clip_on=False)

# Figure 1: exact study support and observed seasonal cycles.
daily=pd.read_csv(ROOT/'data/processed/agcd_daily_regional_mm.csv',index_col=0,parse_dates=True).loc['2000':'2012']
fig=plt.figure(figsize=(10.6,5.6));gs=fig.add_gridspec(2,3,width_ratios=[1.65,1,1],wspace=.42,hspace=.55)
ax=fig.add_subplot(gs[:,0]);base_map(ax);panel(ax,'(a)')
for k,r in REGIONS.items():
 x0,x1=r['lon'];y0,y1=r['lat'];ax.add_patch(Rectangle((x0,y0),x1-x0,y1-y0,fc=RC[k],ec='black',lw=.7,zorder=2));ax.annotate(k,((x0+x1)/2,(y0+y1)/2),xytext=(8,8),textcoords='offset points',weight='bold',color=RC[k])
ax.set_title('Four regional verification domains',pad=16)
monthly=daily.resample('MS').sum();cycle=monthly.groupby(monthly.index.month).mean()
for i,(k,r) in enumerate(REGIONS.items()):
 ax=fig.add_subplot(gs[i//2,i%2+1]);ax.bar(np.arange(1,13),cycle[k],color=RC[k],width=.8);ax.set(xticks=[1,4,7,10],xticklabels=['Jan','Apr','Jul','Oct'],ylabel='Rainfall (mm month$^{-1}$)',title=f'{k}  {r["name"].replace(" Australia","")}');panel(ax,f'({chr(98+i)})');ax.grid(axis='y',alpha=.2)
save(fig,'Fig01_regions')

# Figure 2: training chronology and the aggregation constraint.
fig,axs=plt.subplots(2,1,figsize=(10.6,5.8),gridspec_kw={'height_ratios':[1,1.4]});fig.subplots_adjust(hspace=.45)
ax=axs[0];ax.set_xlim(1999.5,2020);ax.set_ylim(-.8,1.6);ax.set_yticks([]);ax.set_xticks([2000,2005,2011,2013,2015,2020]);ax.set_xlabel('Hindcast origin year');panel(ax,'(a)')
for a,b,t,c in [(2000,2011,'Initial fit\n579 origins','#bdd8ea'),(2011,2013,'Tune\n102','#f4c7a1'),(2013,2015,'Calibrate\n102','#ddd2e7'),(2015,2020,'Independent test\n265','#badfcf')]:ax.add_patch(Rectangle((a,0),b-a,1,fc=c,ec='white'));ax.text((a+b)/2,.5,t,ha='center',va='center',fontsize=9)
ax.annotate('Refit selected models on 685 origins ending before 2013',xy=(2006.5,-.28),ha='center',fontsize=8)
ax.set_title('28-day verification windows are kept within training and calibration boundaries',pad=10)
ax=axs[1];ax.axis('off');panel(ax,'(b)')
def box(x,y,w,h,text,color):
 ax.add_patch(Rectangle((x,y),w,h,transform=ax.transAxes,fc=color,ec='#777777',lw=.8));ax.text(x+w/2,y+h/2,text,transform=ax.transAxes,ha='center',va='center',fontsize=9)
box(.01,.52,.24,.35,'ECMWF ensemble + season\nRMM at t − 2 days\nNiño 3.4 SST at t − 2 months','#edf3f7')
box(.34,.52,.27,.35,'Separate weekly and 28-day fits\nJoint seasonal residual sampling\n200 forecast trajectories','#faf0e5')
box(.70,.52,.28,.35,'Nonnegative reconciliation\nOLS or variance weighting\nOne coherent distribution','#e7f2eb')
for x in [.25,.61]:ax.annotate('',xy=(x+.085,.695),xytext=(x,.695),xycoords='axes fraction',arrowprops={'arrowstyle':'->','lw':1.2})
for i in range(4):box(.18+i*.16,.03,.13,.20,f'Week {i+1}\ndays {i*7+1}–{(i+1)*7}','#f5f5f5')
ax.text(.5,.34,'28-day rainfall = Week 1 + Week 2 + Week 3 + Week 4',transform=ax.transAxes,ha='center',weight='bold')
save(fig,'Fig02_design')

# Figure 3: skill by lead, and 28-day absolute CRPS.
fig,axs=plt.subplots(2,4,figsize=(11.4,6),gridspec_kw={'height_ratios':[1.15,1]});fig.subplots_adjust(wspace=.36,hspace=.55,top=.84)
for j,(k,r) in enumerate(REGIONS.items()):
 ax=axs[0,j];panel(ax,f'({chr(97+j)})');ax.set_title(k+'  '+r['name'].replace(' Australia',''),fontsize=9)
 for m in METHODS:
  d=S.query('region==@k and method==@m').set_index('lead').reindex(['W1','W2','W3','W4']);ax.plot([1,2,3,4],d.crpss,'o-',ms=4,lw=1.4,color=COL[m],mfc='white',mec=COL[m],mew=1.1,label=LABEL[m])
 ax.axhline(0,c='gray',ls='--',lw=.8);ax.set(xticks=[1,2,3,4],xlabel='Forecast week',ylim=(-.16,.64));ax.grid(alpha=.18)
 if j==0:ax.set_ylabel('CRPSS against climatology')
 ax=axs[1,j];panel(ax,f'({chr(101+j)})');dd=S.query("region==@k and lead=='D28'").set_index('method').loc[METHODS]
 ax.barh(np.arange(5),dd.crps,color=[COL[m] for m in METHODS],height=.6);ax.invert_yaxis();ax.set(yticks=np.arange(5),yticklabels=[LABEL[m] if j==0 else '' for m in METHODS],xlabel='28-day CRPS (mm)');ax.grid(axis='x',alpha=.18)
 for i,v in enumerate(dd.crps):ax.text(v+.12,i,f'{v:.2f}',va='center',fontsize=8)
 ax.set_xlim(0,dd.crps.max()*1.25)
handles,labels=axs[0,0].get_legend_handles_labels();fig.legend(handles,labels,loc='upper center',ncol=3,frameon=False,bbox_to_anchor=(.55,1))
save(fig,'Fig03_skill')

# Figure 4: paired differences and uncertainty, positive means worse.
fig,axs=plt.subplots(2,2,figsize=(9.5,6.2));fig.subplots_adjust(wspace=.40,hspace=.42)
for ax,(k,r),letter in zip(axs.flat,REGIONS.items(),'abcd'):
 panel(ax,f'({letter})');ax.set_title(k+'  '+r['name'].replace(' Australia',''));d=B.query("region==@k and method=='XGB + WLS-R'").set_index('lead').loc[['W1','W2','W3','W4','D28']]
 ax.errorbar(d.delta_crps,np.arange(5),xerr=[d.delta_crps-d.lower,d.upper-d.delta_crps],fmt='o',mfc='white',mec=RC[k],mew=1.3,ms=5.5,color=RC[k],capsize=3,lw=1.2);ax.axvline(0,c='gray',lw=.8,ls='--');ax.set(yticks=range(5),yticklabels=['Week 1','Week 2','Week 3','Week 4','28 days'],xlabel='ΔCRPS (mm): reconciled − XGBoost');ax.invert_yaxis();ax.grid(axis='x',alpha=.2)
save(fig,'Fig04_reconciliation')

# Figure 5: reliability and probability-use frequencies for weeks 2–4.
fig,axs=plt.subplots(2,2,figsize=(9.2,7.3));fig.subplots_adjust(wspace=.35,hspace=.38,top=.9)
for ax,(k,r),letter in zip(axs.flat,REGIONS.items(),'abcd'):
 panel(ax,f'({letter})');ax.set_title(k+'  '+r['name'].replace(' Australia',''));ax.plot([0,1],[0,1],c='#999999',ls='--',lw=1)
 for m in ['Raw','OLS','XGBoost','XGB + WLS-R']:
  d=C.query("region==@k and method==@m and lead in ['W2','W3','W4']").copy();d['bin']=np.minimum((d.probability*10).astype(int),9);g=d.groupby('bin').agg(p=('probability','mean'),o=('event','mean'),n=('event','size'));g=g[g.n>=20]
  ax.plot(g.p,g.o,'o-',lw=1.2,ms=4,color=COL[m],mfc='white',mec=COL[m],mew=1.1,label=LABEL[m])
 ax.set(xlim=(0,1),ylim=(0,1),xlabel='Forecast probability',ylabel='Observed relative frequency');ax.grid(alpha=.2)
 inset=ax.inset_axes([.10,.69,.35,.20]);d=C.query("region==@k and method=='XGB + WLS-R' and lead in ['W2','W3','W4']");inset.hist(d.probability,bins=np.linspace(0,1,11),color=COL['XGB + WLS-R'],alpha=.6);inset.set(xticks=[0,.5,1],yticks=[]);inset.tick_params(labelsize=6);inset.set_title('Forecast counts',fontsize=6)
h,l=axs[0,0].get_legend_handles_labels();fig.legend(h,l,loc='upper center',ncol=4,frameon=False)
save(fig,'Fig05_reliability')

# Figure 6: conditional differences with block-bootstrap intervals.
fig,axs=plt.subplots(2,4,figsize=(11.2,5.6));fig.subplots_adjust(wspace=.38,hspace=.65)
for j,(k,r) in enumerate(REGIONS.items()):
 for row,states in enumerate([['MJO weak','MJO active'],['Cool Nino34','Neutral Nino34','Warm Nino34']]):
  ax=axs[row,j];panel(ax,f'({chr(97+row*4+j)})');d=H.query("region==@k and lead=='D28'").set_index('state').loc[states]
  ax.errorbar(np.arange(len(d)),d.delta_crps,yerr=[d.delta_crps-d.lower,d.upper-d.delta_crps],fmt='o',mfc='white',mec=RC[k],mew=1.3,ms=5.5,c=RC[k],capsize=3);ax.axhline(0,c='gray',ls='--',lw=.8);ax.set(xticks=np.arange(len(d)),xticklabels=[s.split()[1] if row==0 else s.split()[0] for s in states]);ax.grid(axis='y',alpha=.2)
  for i,n in enumerate(d.n):ax.text(i,-.22,f'n={n}',ha='center',transform=ax.get_xaxis_transform(),fontsize=8)
  ax.set_xlim(-.5,len(d)-.5)
  if row==0:ax.set_title(k+'  '+r['name'].replace(' Australia',''),fontsize=9)
  if j==0:ax.set_ylabel('28-day ΔCRPS (mm)')
save(fig,'Fig06_climate')

# Supplementary annual lead-time skill matrices.
fig,axs=plt.subplots(3,4,figsize=(11.4,6.5),sharex=True,sharey=True);fig.subplots_adjust(wspace=.22,hspace=.35,right=.90)
for row,m in enumerate(['Raw','XGBoost','XGB + WLS-R']):
 for col,(k,r) in enumerate(REGIONS.items()):
  ax=axs[row,col];d=C.query('region==@k').copy();d['year']=pd.to_datetime(d.date).dt.year;z=d.groupby(['method','year','lead']).crps.mean();skill=(1-z.loc[m]/z.loc['Climatology']).unstack('year').reindex(['W1','W2','W3','W4'])
  im=ax.imshow(skill,aspect='auto',vmin=-.5,vmax=.6,cmap='BrBG',origin='upper');ax.set(xticks=range(5),xticklabels=range(2015,2020),yticks=range(4),yticklabels=['W1','W2','W3','W4']);ax.tick_params(labelsize=8);ax.set_title(k if row==0 else '',fontsize=10)
  if col==0:ax.set_ylabel(LABEL[m])
cax=fig.add_axes([.92,.18,.014,.64]);fig.colorbar(im,cax=cax,label='Annual CRPSS',extend='both')
save(fig,'FigS01_annual_skill')
print('Created 7 original figures in PNG, PDF and SVG.')
