"""Publication figures linking rainfall seasonality to forecast diagnostics."""
from common import ROOT,REGIONS
import numpy as np,pandas as pd,json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon,Rectangle
P=ROOT/'revision/primary';F=ROOT/'revision/figures';F.mkdir(exist_ok=True)
S=pd.read_csv(P/'scores.csv');C=pd.read_csv(P/'case_scores.csv.gz');B=pd.read_csv(P/'comparisons.csv')
plt.rcParams.update({'font.family':'Arial','font.size':10,'axes.titlesize':10,'axes.labelsize':9.5,'xtick.labelsize':9,'ytick.labelsize':9,'legend.fontsize':8.5,'axes.linewidth':.8,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42,'svg.fonttype':'none'})
METHODS=['Raw','Quantile_mapping','Seasonal_EMOS','Direct_EMOS','Bottom_up','MinT_NN']
LABEL=dict(zip(METHODS,['ECMWF (QC)','Quantile mapping','Seasonal EMOS','Monthly EMOS','Bottom-up','MinT-NN']))
COL=dict(zip(METHODS,['#222222','#888888','#009E73','#0072B2','#CC79A7','#D55E00']))
MARK=dict(zip(METHODS,['o','s','v','D','^','o']));STYLE=dict(zip(METHODS,['-','--',':','-','--','-.']))
RC=dict(zip(REGIONS,['#AA4499','#009E73','#4477AA','#CC6677']))

def save(fig,name):
 for ext in ['png','pdf','svg']:fig.savefig(F/f'{name}.{ext}',dpi=600)
 plt.close(fig)

def panel(ax,l):ax.text(-.065 if ax.get_position().width>.6 else -.17,1.10,l,transform=ax.transAxes,fontsize=11,fontweight='bold',va='bottom',clip_on=False)
def line(ax,x,y,m):ax.plot(x,y,label=LABEL[m],color=COL[m],ls=STYLE[m],marker=MARK[m],mfc='white',mec=COL[m],mew=1,ms=4.8,lw=1.2)
def four(top=.84,height=6.5):
 fig,axs=plt.subplots(2,2,figsize=(6.8,height));fig.subplots_adjust(left=.12,right=.97,bottom=.10,top=top,wspace=.40,hspace=.67)
 for ax,(k,r),l in zip(axs.flat,REGIONS.items(),'abcd'):panel(ax,f'({l})');ax.set_title(k+'  '+r['name'].replace(' Australia',''),pad=12)
 return fig,axs
def legend(fig,ax,ncol=3):
 h,l=ax.get_legend_handles_labels();fig.legend(h,l,loc='upper center',ncol=ncol,frameon=False,bbox_to_anchor=(.53,.995),columnspacing=1.1,handlelength=2.3)

countries=json.loads((ROOT/'data/support/countries.geojson').read_text(encoding='utf-8'));aus=next(f['geometry'] for f in countries['features'] if f['properties'].get('ADMIN')=='Australia')
fig,axs=plt.subplots(1,2,figsize=(6.8,4.1));fig.subplots_adjust(left=.08,right=.98,bottom=.16,top=.80,wspace=.39)
ax=axs[0]
for poly in aus['coordinates']:ax.add_patch(Polygon(poly[0],fc='#f7f7f7',ec='#555555',lw=.7))
ax.set(xlim=(111,155),ylim=(-45,-9),xticks=[115,135,155],yticks=[-40,-30,-20,-10]);ax.set_xticklabels(['115°E','135°E','155°E']);ax.set_yticklabels(['40°S','30°S','20°S','10°S']);ax.set_aspect(1.1)
for k,r in REGIONS.items():
 x0,x1=r['lon'];y0,y1=r['lat'];ax.add_patch(Rectangle((x0,y0),x1-x0,y1-y0,fc=RC[k],ec='black',lw=.7));ax.annotate(k,((x0+x1)/2,(y0+y1)/2),xytext=(5,6),textcoords='offset points',weight='bold',fontsize=10)
ax.annotate('North',xy=(117,-14),xytext=(117,-23),ha='center',fontsize=8.5,arrowprops={'arrowstyle':'->','lw':1.1})
length=1000/(111.195*np.cos(np.deg2rad(-41)));ax.plot([116,116+length],[-41,-41],c='black',lw=2);ax.text(116+length/2,-43.7,'1000 km',ha='center',fontsize=8.5);panel(ax,'(a)');ax.set_title('Forecast domains',pad=17)
daily=pd.read_csv(ROOT/'data/processed/agcd_daily_regional_mm.csv',index_col=0,parse_dates=True).loc['2000':'2019'];monthly=daily.resample('MS').sum();cycle=monthly.groupby(monthly.index.month).mean();ax=axs[1]
for k in REGIONS:ax.plot(range(1,13),cycle[k],marker='o',mfc='white',ms=4.4,lw=1.2,color=RC[k],label=k)
ax.set(xticks=[1,4,7,10],xticklabels=['Jan','Apr','Jul','Oct'],xlim=(.7,12.3),ylabel='Monthly rainfall (mm)');panel(ax,'(b)');ax.set_title('Seasonal rainfall',pad=17);ax.legend(frameon=False,ncol=2,loc='upper right',fontsize=8.5)
save(fig,'Fig01_regions')

fig,axs=plt.subplots(2,1,figsize=(6.8,5.5));fig.subplots_adjust(left=.08,right=.97,bottom=.05,top=.88,hspace=.66)
ax=axs[0];panel(ax,'(a)');ax.set(xlim=(1999.5,2019.5),ylim=(-.25,1.9),yticks=[],xticks=[2000,2005,2010,2015,2019]);ax.set_title('One of twenty outer validation folds',pad=16)
for year in range(2000,2020):
 colour='#e69f00' if year==2010 else '#eeeeee' if year in [2009,2011] else '#a7c8e1';ax.add_patch(Rectangle((year-.45,.2),.9,.75,fc=colour,ec='white'))
ax.text(2010,1.16,'Held out',ha='center',fontsize=9);ax.text(2004,1.16,'Training years',ha='center',fontsize=9)
ax.annotate('Excluded neighbours',xy=(2011,.25),xytext=(2015.4,1.55),ha='center',fontsize=9,arrowprops={'arrowstyle':'->','lw':.8});ax.set_xlabel('Origin year')
ax=axs[1];ax.axis('off');panel(ax,'(b)')
for x,label,c in [(.0,'Calibrate five\nrainfall products','#d6e4ef'),(.355,'Link their ranks\ninto joint samples','#eadced'),(.71,'Reconcile samples\nwith nonnegative weeks','#f6dfc9')]:
 ax.add_patch(Rectangle((x,.56),.29,.36,fc=c,ec='#666',lw=.8));ax.text(x+.145,.74,label,ha='center',va='center',fontsize=9)
for x in [.29,.645]:ax.annotate('',xy=(x+.065,.74),xytext=(x,.74),arrowprops={'arrowstyle':'->','lw':1})
ax.text(.5,.31,'28-day total = Week 1 + Week 2 + Week 3 + Week 4',ha='center',weight='bold',fontsize=10)
ax.text(.5,.09,'Nested year blocks supply errors for the reconciliation weights',ha='center',fontsize=9)
save(fig,'Fig02_design')

fig,axs=four()
for ax,k in zip(axs.flat,REGIONS):
 for m in ['Raw','Quantile_mapping','Seasonal_EMOS','Direct_EMOS','MinT_NN']:
  d=S[(S.domain==k)&(S.method==m)].set_index('lead').reindex(['W1','W2','W3','W4']);line(ax,[1,2,3,4],d.crpss,m)
 ax.axhline(0,c='.5',lw=.8,ls=':');ax.set(xticks=[1,2,3,4],xlabel='Forecast week',ylabel='CRPSS',ylim=(-.18,.65))
legend(fig,axs[0,0],3);save(fig,'Fig03_skill')

fig,axs=four()
for ax,k in zip(axs.flat,REGIONS):
 for off,base,col,mark in [(-.10,'Direct_EMOS','#0072B2','o'),(.10,'Bottom_up','#D55E00','s')]:
  d=B[(B.domain==k)&(B.method=='MinT_NN')&(B.baseline==base)].set_index('lead').loc[['W1','W2','W3','W4','D28']]
  ax.errorbar(d.delta,np.arange(5)+off,xerr=[d.delta-d.lower,d.upper-d.delta],fmt=mark,mfc='white',mec=col,mew=1,ms=5,c=col,capsize=2.5,lw=1,label='vs '+LABEL[base])
 ax.axvline(0,c='.5',lw=.8,ls=':');ax.set(yticks=range(5),yticklabels=['Week 1','Week 2','Week 3','Week 4','28 days'],xlim=(-.27,.43),xlabel='CRPS change (mm)');ax.invert_yaxis()
legend(fig,axs[0,0],2);save(fig,'Fig04_reconciliation')

core=['Raw','Direct_EMOS','Bottom_up','MinT_NN'];fig,axs=four()
for ax,k in zip(axs.flat,REGIONS):
 ax.plot([0,1],[0,1],c='.6',ls=':',lw=.9)
 for m in ['Raw','Direct_EMOS','MinT_NN']:
  d=C[(C.domain==k)&(C.method==m)&C.lead.isin(['W2','W3','W4'])].copy();d['bin']=np.minimum((d.probability*10).astype(int),9);g=d.groupby('bin').agg(p=('probability','mean'),o=('event','mean'),n=('event','size'));g=g[g.n>=30];line(ax,g.p,g.o,m)
 ax.set(xlim=(0,1),ylim=(0,1),xticks=[0,.5,1],yticks=[0,.5,1],xlabel='Forecast probability',ylabel='Observed frequency')
legend(fig,axs[0,0],3);save(fig,'Fig05_reliability')

fig,axs=four()
for ax,k in zip(axs.flat,REGIONS):
 for m in core:
  d=S[(S.domain==k)&(S.method==m)].set_index('lead').loc[['W1','W2','W3','W4','D28']];line(ax,range(5),100*d.coverage80,m)
 ax.axhline(80,c='.5',ls=':',lw=.9);ax.set(xticks=range(5),xticklabels=['W1','W2','W3','W4','28 d'],ylim=(35,95),ylabel='80% interval coverage (%)',xlabel='Accumulation period')
legend(fig,axs[0,0],2);save(fig,'Fig06_coverage')

M=pd.read_csv(P/'mechanism_summary.csv');corr=json.loads((P/'mechanism_correlations.json').read_text());fig,axs=plt.subplots(1,2,figsize=(6.8,4.7));fig.subplots_adjust(left=.1,right=.98,bottom=.27,top=.78,wspace=.36)
symbols={'DJF':'o','MAM':'s','JJA':'^','SON':'D'}
for ax,kind,l,title in zip(axs,['linear','nn'],'ab',['Linear predictive means','Nonnegative sample means']):
 for _,row in M.iterrows():ax.scatter(100*row.gain_predicted,100*row['gain_real_'+kind],s=44,marker=symbols[row.season],facecolors='white',edgecolors=RC[row.domain],linewidths=1.2)
 ax.axhline(0,color='.6',ls=':',lw=.9);ax.set(xlim=(-.8,24),ylim=(-1.5,2.5),xlabel='Predicted variance gain (%)',ylabel='Realised MSE gain (%)');panel(ax,f'({l})');ax.set_title(title,pad=16);c=corr[kind];ax.text(.98,.96,f'ρ = {c["rho"]:.2f}\n95% CI {c["lower"]:.2f} to {c["upper"]:.2f}',transform=ax.transAxes,va='top',ha='right',fontsize=8.5)
h=[plt.Line2D([],[],ls='',marker='o',mfc='white',mec=RC[k],label=k) for k in REGIONS];fig.legend(handles=h,loc='upper center',ncol=4,frameon=False,bbox_to_anchor=(.52,.995))
h=[plt.Line2D([],[],ls='',marker=m,mfc='white',mec='.25',label=f'{s}  '+{'DJF':'summer','MAM':'autumn','JJA':'winter','SON':'spring'}[s]) for s,m in symbols.items()];fig.legend(handles=h,loc='lower center',ncol=2,frameon=False,bbox_to_anchor=(.52,.01));save(fig,'Fig07_mechanism')

fig,axs=plt.subplots(2,2,figsize=(6.8,6.7));fig.subplots_adjust(left=.12,right=.97,bottom=.10,top=.84,wspace=.45,hspace=.72)
for ax,l in zip(axs.flat,'abcd'):panel(ax,f'({l})')
n=C[(C.domain=='N')&(C.lead=='D28')].copy();n['wet']=pd.to_datetime(n.date).dt.month.isin([11,12,1,2,3,4])
ax=axs[0,0]
for off,m in zip([-.12,0,.12],['Raw','Seasonal_EMOS','Direct_EMOS']):
 v=n[n.method==m].groupby('wet').crps.mean();line(ax,np.array([0,1])+off,[v[True],v[False]],m)
ax.set(xticks=[0,1],xticklabels=['Nov–Apr','May–Oct'],ylabel='28-day CRPS (mm)',ylim=(0,43));ax.set_title('Northern wet and dry halves',pad=13)
ax=axs[0,1];wet=n[(n.method=='Direct_EMOS')&n.wet];alln=n[n.method=='Direct_EMOS'];share=wet.crps.sum()/alln.crps.sum()*100
ax.scatter([0,1],[100*len(wet)/len(alln),share],s=65,facecolors='white',edgecolors=['#0072B2','#D55E00'],linewidths=1.5)
for i,val in enumerate([100*len(wet)/len(alln),share]):ax.text(i,val+5,f'{val:.1f}%',ha='center',fontsize=10)
ax.set(xticks=[0,1],xticklabels=['Origins','CRPS total'],xlim=(-.4,1.4),ylim=(0,108),ylabel='Wet-season share (%)');ax.set_title('Rainfall magnitude weights CRPS',pad=13)
ax=axs[1,0];annual=n.groupby(['year','method']).crps.mean().unstack()
for m in ['Seasonal_EMOS','Direct_EMOS']:line(ax,annual.index,annual[m]-annual.Raw,m)
ax.axhline(0,color='.5',ls=':',lw=.9);ax.set(xticks=[2000,2005,2010,2015,2019],xlabel='Validation year',ylabel='EMOS minus raw CRPS (mm)');ax.tick_params(axis='x',labelsize=8);ax.set_title('Year-to-year performance',pad=13)
ax=axs[1,1]
for wetval,label,col in [(True,'Nov–Apr','#0072B2'),(False,'May–Oct','#D55E00')]:
 vals=n[(n.method=='Direct_EMOS')&(n.wet==wetval)].pit;counts,edges=np.histogram(vals,bins=np.linspace(0,1,11),density=True);ax.stairs(counts,edges,color=col,lw=1.4,label=label)
ax.axhline(1,color='.5',ls=':',lw=.9);ax.set(xlim=(0,1),xticks=[0,.5,1],xlabel='Randomized empirical PIT',ylabel='Density');ax.set_title('Distributional calibration',pad=13);ax.legend(frameon=False,fontsize=8,loc='upper center')
legend(fig,axs[0,0],3);save(fig,'Fig08_northern')

fig,axs=four()
for ax,k in zip(axs.flat,REGIONS):
 for off,method,base,col,marker,label in [(-.08,'ECC11_BU','Schaake11_BU','#0072B2','o','Bottom-up'),(.08,'ECC11_NN','Schaake11_NN','#D55E00','s','MinT-NN')]:
  d=B[(B.domain==k)&(B.method==method)&(B.baseline==base)].set_index('lead').loc[['W1','W2','W3','W4','D28']]
  ax.errorbar(d.delta,np.arange(5)+off,xerr=[d.delta-d.lower,d.upper-d.delta],fmt=marker,mfc='white',ms=5,c=col,capsize=2,lw=1,label=label)
 ax.axvline(0,c='.5',ls=':',lw=.8);ax.set(xlim=(-.4,.4),yticks=range(5),yticklabels=['W1','W2','W3','W4','28 d'],xlabel='ECC minus historical CRPS (mm)');ax.invert_yaxis()
legend(fig,axs[0,0],2);save(fig,'FigS01_ecc')

fig,ax=plt.subplots(figsize=(6.8,3.7));fig.subplots_adjust(left=.12,right=.97,bottom=.2,top=.76)
A=pd.read_csv(P/'primary_annual.csv')
for (label,df),col,marker in zip(A.groupby('comparison',sort=False),['#0072B2','#D55E00','#009E73'],['o','s','^']):ax.plot(df.year,df.delta_normalized_percent,marker=marker,mfc='white',ms=4.5,lw=1,color=col,label=label)
ax.axhline(0,color='.5',ls=':',lw=.8);ax.set(xlabel='Validation year',ylabel='Change / climatological CRPS (%)',xticks=[2000,2005,2010,2015,2019]);ax.legend(loc='upper center',bbox_to_anchor=(.5,1.37),frameon=False,ncol=1);save(fig,'FigS02_annual')
print('Created 8 main and 2 supplementary figures in PNG, PDF and SVG.',flush=True)
