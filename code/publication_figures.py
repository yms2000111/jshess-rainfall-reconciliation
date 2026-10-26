"""Journal-sized original figures, open symbols and clearly separated panel labels."""
from common import *
import numpy as np,pandas as pd,json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon,Rectangle
F=ROOT/'figures';F.mkdir(exist_ok=True)
plt.rcParams.update({'font.family':'Arial','font.size':8,'axes.titlesize':8,'axes.labelsize':8,'xtick.labelsize':7,'ytick.labelsize':7,'legend.fontsize':7,'axes.linewidth':.8,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42,'svg.fonttype':'none'})
S=pd.read_csv(ROOT/'results/scores.csv');C=pd.read_csv(ROOT/'results/case_scores.csv');B=pd.read_csv(ROOT/'results/core_comparisons.csv')
METHODS=['Raw','Quantile mapping','CSG EMOS','EMOS bottom-up','EMOS MinT-NN','XGBoost']
LABEL={'Raw':'ECMWF (QC)','Quantile mapping':'Quantile mapping','CSG EMOS':'EMOS','EMOS bottom-up':'EMOS bottom-up','EMOS MinT-NN':'EMOS MinT-NN','XGBoost':'XGBoost'}
COL=dict(zip(METHODS,['#222222','#999999','#0072B2','#CC79A7','#D55E00','#6F6F00']))
STYLE=dict(zip(METHODS,['-','--','-','--','-','-.']));MARK=dict(zip(METHODS,['o','s','D','^','o','v']))
RC=dict(zip(REGIONS,['#AA4499','#44AA99','#4477AA','#CC6677']))
def save(fig,name):
 for ext in ['png','pdf','svg']:fig.savefig(F/f'{name}.{ext}',dpi=600)
 plt.close(fig)
def panel(ax,l):ax.text(-.06 if ax.get_position().width>.6 else -.12,1.10,l,transform=ax.transAxes,fontsize=8,fontweight='bold',va='bottom',clip_on=False)
def line(ax,x,y,m):ax.plot(x,y,label=LABEL[m],color=COL[m],ls=STYLE[m],marker=MARK[m],mfc='white',mec=COL[m],mew=.9,ms=4,lw=1)
def four(top=.87):
 fig,axs=plt.subplots(2,2,figsize=(6.8,5.7));fig.subplots_adjust(left=.11,right=.97,bottom=.10,top=top,wspace=.35,hspace=.57)
 for ax,(k,r),l in zip(axs.flat,REGIONS.items(),'abcd'):panel(ax,f'({l})');ax.set_title(k+'  '+r['name'].replace(' Australia',''),pad=9)
 return fig,axs
def legend(fig,ax,ncol=3):
 h,l=ax.get_legend_handles_labels();fig.legend(h,l,loc='upper center',ncol=ncol,frameon=False,bbox_to_anchor=(.53,.995),columnspacing=1.4)

countries=json.loads((ROOT/'data/support/countries.geojson').read_text(encoding='utf-8'));aus=next(f['geometry'] for f in countries['features'] if f['properties'].get('ADMIN')=='Australia')
fig,axs=plt.subplots(1,2,figsize=(6.8,3.7));fig.subplots_adjust(left=.08,right=.98,bottom=.16,top=.85,wspace=.37)
ax=axs[0]
for poly in aus['coordinates']:ax.add_patch(Polygon(poly[0],fc='#f7f7f7',ec='#555555',lw=.6))
ax.set(xlim=(111,155),ylim=(-45,-9),xticks=[115,135,155],yticks=[-40,-30,-20,-10]);ax.set_xticklabels(['115°E','135°E','155°E']);ax.set_yticklabels(['40°S','30°S','20°S','10°S']);ax.set_aspect(1.1)
for k,r in REGIONS.items():
 x0,x1=r['lon'];y0,y1=r['lat'];ax.add_patch(Rectangle((x0,y0),x1-x0,y1-y0,fc=RC[k],ec='black',lw=.6));ax.annotate(k,((x0+x1)/2,(y0+y1)/2),xytext=(5,6),textcoords='offset points',weight='bold',fontsize=8)
ax.annotate('N',xy=(116,-14),xytext=(116,-21),ha='center',arrowprops={'arrowstyle':'->','lw':1})
length=1000/(111.195*np.cos(np.deg2rad(-41)));ax.plot([116,116+length],[-41,-41],c='black',lw=2);ax.text(116+length/2,-43,'1000 km at 41°S',ha='center',fontsize=7);panel(ax,'(a)');ax.set_title('Regional forecast domains',pad=12)
daily=pd.read_csv(ROOT/'data/processed/agcd_daily_regional_mm.csv',index_col=0,parse_dates=True).loc['2000':'2012'];monthly=daily.resample('MS').sum();cycle=monthly.groupby(monthly.index.month).mean();ax=axs[1]
for k in REGIONS:ax.plot(range(1,13),cycle[k],marker='o',mfc='white',ms=3.5,lw=1,color=RC[k],label=k)
ax.set(xticks=[1,4,7,10,12],xticklabels=['Jan','Apr','Jul','Oct','Dec'],ylabel='Monthly rainfall (mm)');panel(ax,'(b)');ax.set_title('AGCD seasonal rainfall',pad=12);ax.legend(frameon=False)
save(fig,'Fig01_regions')

fig,axs=plt.subplots(2,1,figsize=(6.8,4.5));fig.subplots_adjust(left=.08,right=.98,bottom=.05,top=.91,hspace=.55,height_ratios=None) if False else None
fig.subplots_adjust(left=.08,right=.98,bottom=.05,top=.91,hspace=.55)
ax=axs[0];panel(ax,'(a)');ax.set(xlim=(2000,2020),ylim=(-.45,1.35),yticks=[],xticks=[2000,2005,2011,2013,2015,2020]);ax.set_title('Chronological separation of fitting and evaluation',pad=12)
for a,b,label,c in [(2000,2013,'Fit: 685 origins','#d6e4ef'),(2013,2015,'Calibrate\n102','#eadced'),(2015,2020,'Test: 265 origins','#f6dfc9')]:ax.add_patch(Rectangle((a,0),b-a,.9,fc=c,ec='white'));ax.text((a+b)/2,.45,label,ha='center',va='center',fontsize=8)
ax.text(2006.5,-.28,'XGBoost tuning uses a nested 2011–2012 partition',ha='center',fontsize=7)
ax=axs[1];ax.axis('off');panel(ax,'(b)')
for x,label,c in [(.0,'Five marginal\nEMOS distributions','#d6e4ef'),(.35,'Historical rank shuffle\n200 joint samples','#eadced'),(.70,'Bottom-up or MinT-NN\ncoherent rainfall','#f6dfc9')]:
 ax.add_patch(Rectangle((x,.56),.30,.37,fc=c,ec='#777',lw=.7));ax.text(x+.15,.745,label,ha='center',va='center',fontsize=8)
for x in [.30,.65]:ax.annotate('',xy=(x+.05,.745),xytext=(x,.745),arrowprops={'arrowstyle':'->'})
ax.text(.5,.33,'28-day total = Week 1 + Week 2 + Week 3 + Week 4',ha='center',weight='bold',fontsize=8)
ax.text(.5,.09,'Days 1–7          Days 8–14          Days 15–21          Days 22–28',ha='center',fontsize=8)
save(fig,'Fig02_design')

fig,axs=four()
for ax,k in zip(axs.flat,REGIONS):
 for m in METHODS:
  d=S.query('region==@k and method==@m').set_index('lead').reindex(['W1','W2','W3','W4']);line(ax,[1,2,3,4],d.crpss,m)
 ax.axhline(0,c='.55',lw=.7,ls=':');ax.set(xticks=[1,2,3,4],xlabel='Forecast week',ylabel='CRPSS',ylim=(-.2,.65))
legend(fig,axs[0,0]);save(fig,'Fig03_skill')

fig,axs=four()
for ax,k in zip(axs.flat,REGIONS):
 for off,base,col,mark in [(-.10,'CSG EMOS','#0072B2','o'),(.10,'EMOS bottom-up','#D55E00','s')]:
  d=B.query('region==@k and baseline==@base').set_index('lead').loc[['W1','W2','W3','W4','D28']]
  ax.errorbar(d.delta_crps,np.arange(5)+off,xerr=[d.delta_crps-d.lower,d.upper-d.delta_crps],fmt=mark,mfc='white',mec=col,ms=4,c=col,capsize=2,lw=.9,label='Relative to '+LABEL[base])
 ax.axvline(0,c='.5',lw=.7,ls=':');ax.set(yticks=range(5),yticklabels=['Week 1','Week 2','Week 3','Week 4','28 days'],xlim=(-.8,.9),xlabel='MinT-NN minus baseline CRPS (mm)');ax.invert_yaxis()
legend(fig,axs[0,0],2);save(fig,'Fig04_reconciliation')

core=['Raw','CSG EMOS','EMOS bottom-up','EMOS MinT-NN']
fig,axs=four()
for ax,k in zip(axs.flat,REGIONS):
 ax.plot([0,1],[0,1],c='.6',ls=':',lw=.8)
 for m in core:
  d=C.query("region==@k and method==@m and lead in ['W2','W3','W4']").copy();d['bin']=np.minimum((d.probability*10).astype(int),9);g=d.groupby('bin').agg(p=('probability','mean'),o=('event','mean'),n=('event','size'));g=g[g.n>=20];line(ax,g.p,g.o,m)
 ax.set(xlim=(0,1),ylim=(0,1),xlabel='Forecast probability',ylabel='Observed frequency')
legend(fig,axs[0,0],2);save(fig,'Fig05_reliability')

fig,axs=four()
for ax,k in zip(axs.flat,REGIONS):
 for m in core:
  d=S.query('region==@k and method==@m').set_index('lead').loc[['W1','W2','W3','W4','D28']];line(ax,range(5),100*d.coverage80,m)
 ax.axhline(80,c='.5',ls=':',lw=.8);ax.set(xticks=range(5),xticklabels=['W1','W2','W3','W4','28 days'],ylim=(35,100),ylabel='Central 80% interval coverage (%)',xlabel='Forecast accumulation')
legend(fig,axs[0,0],2);save(fig,'Fig06_coverage')

fig,axs=plt.subplots(3,4,figsize=(6.8,5.2),sharex=True,sharey=True);fig.subplots_adjust(left=.11,right=.88,bottom=.12,top=.90,hspace=.25,wspace=.18)
for row,m in enumerate(['CSG EMOS','EMOS bottom-up','EMOS MinT-NN']):
 for col,k in enumerate(REGIONS):
  ax=axs[row,col];d=C.query('region==@k').copy();d['year']=pd.to_datetime(d.date).dt.year;z=d.groupby(['method','year','lead']).crps.mean();skill=(1-z.loc[m]/z.loc['Climatology']).unstack('year').reindex(['W1','W2','W3','W4']);im=ax.imshow(skill,aspect='auto',vmin=-.5,vmax=.6,cmap='BrBG');ax.set(xticks=[0,2,4],xticklabels=['2015','2017','2019'],yticks=range(4),yticklabels=['W1','W2','W3','W4'])
  if row==0:ax.set_title(k,pad=8)
  if col==0:ax.set_ylabel(LABEL[m],fontsize=7)
cax=fig.add_axes([.91,.2,.018,.6]);fig.colorbar(im,cax=cax,label='Annual CRPSS',extend='both');save(fig,'FigS01_annual_skill')

fig,axs=four(.91)
for ax,k in zip(axs.flat,REGIONS):
 a=C.query("region==@k and method=='CSG EMOS' and lead=='D28'").sort_values('date');b=C.query("region==@k and method=='EMOS MinT-NN' and lead=='D28'").sort_values('date');diff=b.crps.to_numpy()-a.crps.to_numpy();amp=a.rmm_amp.to_numpy();nino=a.nino_anomaly.to_numpy();masks=[amp<1,amp>=1,nino<-.5,abs(nino)<=.5,nino>.5];x=[0,1,3,4,5]
 ax.plot(x,[diff[q].mean() for q in masks],'o',mfc='white',mec=RC[k],color=RC[k],ms=5);ax.axhline(0,c='.5',ls=':',lw=.8);ax.set(xticks=x,xticklabels=['Weak','Active','Cool','Neutral','Warm'],ylabel='28-day ΔCRPS (mm)',ylim=(-.7,.5),xlim=(-.5,5.5))
 for pos,q in zip(x,masks):ax.text(pos,-.22,f'n={q.sum()}',transform=ax.get_xaxis_transform(),ha='center',fontsize=7)
save(fig,'FigS02_climate')
print('Created six main and two supplementary figures, 600 dpi PNG and vector PDF/SVG.')
