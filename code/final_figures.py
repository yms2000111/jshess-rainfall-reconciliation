"""Readable original scientific figures for the final factorial manuscript."""
from common import ROOT,REGIONS
import numpy as np,pandas as pd,json,shutil
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle,Polygon
F=ROOT/'revision/final_figures';F.mkdir(exist_ok=True);E=ROOT/'revision/extension'
C=pd.read_csv(E/'case_scores.csv.gz');B=pd.read_csv(E/'comparisons.csv');S=pd.read_csv(E/'scores.csv');R=pd.read_csv(E/'recalibration/scores.csv');RB=pd.read_csv(E/'recalibration/comparisons.csv')
plt.rcParams.update({'font.family':'Arial','font.size':11,'axes.titlesize':11.5,'axes.labelsize':11,'xtick.labelsize':10.5,'ytick.labelsize':10.5,'legend.fontsize':10,'axes.linewidth':.8,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42,'svg.fonttype':'none'})
COL={'Raw':'#333333','Bottom_up':'#0072B2','H0_7_NN':'#009E73','H1_7_NN':'#D55E00','H1_Direct':'#AA4499'}
LAB={'Raw':'ECMWF (QC)','Bottom_up':'Bottom-up','H0_7_NN':'H0, seven nodes','H1_7_NN':'H1, seven nodes','H1_Direct':'H1 direct'}
MARK={'Raw':'o','Bottom_up':'s','H0_7_NN':'^','H1_7_NN':'D','H1_Direct':'v'}
RC=dict(zip(REGIONS,['#AA4499','#009E73','#4477AA','#CC6677']))
def save(fig,name):
 for ext in ['png','pdf','svg']:fig.savefig(F/f'{name}.{ext}',dpi=600)
 plt.close(fig)
def panel(ax,l):
 x=-.075 if ax.get_position().width>.7 else -.17
 ax.text(x,1.13,f'({l})',transform=ax.transAxes,fontsize=13,weight='bold',va='bottom',clip_on=False)
def four(h=6.8,top=.82):
 fig,axs=plt.subplots(2,2,figsize=(6.8,h));fig.subplots_adjust(left=.13,right=.97,bottom=.105,top=top,hspace=.68,wspace=.43)
 for ax,k,l in zip(axs.flat,REGIONS,'abcd'):panel(ax,l);ax.set_title(k+'  '+REGIONS[k]['name'].replace(' Australia',''),pad=13)
 return fig,axs
def legend(fig,ax,ncol=2):
 h,l=ax.get_legend_handles_labels();fig.legend(h,l,loc='upper center',bbox_to_anchor=(.52,.99),ncol=ncol,frameon=False,columnspacing=1.5)
def line(ax,x,y,m):ax.plot(x,y,c=COL[m],marker=MARK[m],mfc='white',mew=1.2,ms=6,lw=1.35,label=LAB[m])
rng=np.random.default_rng(20261040);draw=rng.integers(0,20,(10000,20))

# Geography and climatic scale, with separate north-arrow label.
fig,axs=plt.subplots(1,2,figsize=(6.8,4.5));fig.subplots_adjust(left=.09,right=.98,bottom=.18,top=.75,wspace=.45)
countries=json.loads((ROOT/'data/support/countries.geojson').read_text(encoding='utf-8'));aus=next(f['geometry'] for f in countries['features'] if f['properties'].get('ADMIN')=='Australia');ax=axs[0]
for poly in aus['coordinates']:ax.add_patch(Polygon(poly[0],fc='#f6f6f6',ec='#555',lw=.8))
ax.set(xlim=(111,155),ylim=(-45,-9),xticks=[115,135,155],yticks=[-40,-30,-20,-10]);ax.set_xticklabels(['115°E','135°E','155°E']);ax.set_yticklabels(['40°S','30°S','20°S','10°S']);ax.set_aspect(1.1)
for k,r in REGIONS.items():
 x0,x1=r['lon'];y0,y1=r['lat'];ax.add_patch(Rectangle((x0,y0),x1-x0,y1-y0,fc='none',ec=RC[k],lw=1.6));ax.annotate(k,((x0+x1)/2,(y0+y1)/2),xytext=(5,6),textcoords='offset points',fontsize=11,weight='bold')
ax.annotate('North',xy=(117,-14),xytext=(117,-23),ha='center',fontsize=10,arrowprops={'arrowstyle':'->','lw':1.1});length=1000/(111.195*np.cos(np.deg2rad(41)));ax.plot([116,116+length],[-41,-41],c='black',lw=2);ax.text(116+length/2,-44,'1000 km',ha='center',fontsize=10);panel(ax,'a');ax.set_title('Forecast domains',pad=16)
daily=pd.read_csv(ROOT/'data/processed/agcd_daily_regional_mm.csv',index_col=0,parse_dates=True).loc['2000':'2019'];monthly=daily.resample('MS').sum();cycle=monthly.groupby(monthly.index.month).mean();annual=daily.resample('YS').sum().mean();ax=axs[1]
for k in REGIONS:ax.plot(range(1,13),cycle[k],marker='o',mfc='white',ms=5.5,lw=1.2,color=RC[k],label=f'{k}  {annual[k]:.0f} mm yr$^{{-1}}$')
ax.set(xticks=[1,4,7,10],xticklabels=['Jan','Apr','Jul','Oct'],xlim=(.7,12.4),ylabel='Monthly rainfall (mm)');panel(ax,'b');ax.set_title('Seasonal rainfall',pad=16);fig.legend(*ax.get_legend_handles_labels(),loc='upper center',ncol=2,frameon=False,bbox_to_anchor=(.53,1.0));save(fig,'Fig01_domains')

# Hierarchy and experiment diagram, all texts original.
fig,axs=plt.subplots(3,1,figsize=(6.8,7.3),gridspec_kw={'height_ratios':[2.4,1.45,1.35]});fig.subplots_adjust(left=.10,right=.96,bottom=.08,top=.93,hspace=.62)
ax=axs[0];ax.set(xlim=(0,1),ylim=(0,1));ax.axis('off');panel(ax,'a')
def box(ax,x,y,w,h,txt,fc):
 ax.add_patch(Rectangle((x,y),w,h,facecolor=fc,edgecolor='#666',lw=.8));ax.text(x+w/2,y+h/2,txt,ha='center',va='center',fontsize=11)
for i in range(4):box(ax,.04+i*.22,.02,.18,.20,f'Week {i+1}','#e7eef4')
box(ax,.12,.42,.27,.20,'Days 1 to 14','#e4eee8');box(ax,.59,.42,.27,.20,'Days 15 to 28','#e4eee8');box(ax,.35,.80,.29,.20,'Days 1 to 28','#f8e6d7')
for a,b in [((.13,.22),(.255,.42)),((.35,.22),(.255,.42)),((.57,.22),(.725,.42)),((.79,.22),(.725,.42)),((.255,.62),(.495,.80)),((.725,.62),(.495,.80))]:ax.annotate('',xy=b,xytext=a,arrowprops={'arrowstyle':'->','lw':1})
ax.text(.99,.86,'Climate indices\nenter aggregates\nonly in H1',ha='right',va='top',fontsize=10,color='#9a4100')
ax=axs[1];ax.axis('off');panel(ax,'b');ax.text(.23,1.05,'Five nodes',ha='center',weight='bold');ax.text(.74,1.05,'Seven nodes',ha='center',weight='bold')
for x,y,label in [(.02,.53,'H0: rainfall only'),(.53,.53,'H0: rainfall only'),(.02,.04,'H1: climate at total'),(.53,.04,'H1: climate at aggregates')]:box(ax,x,y,.46,.36,label,'#f6f6f6')
ax=axs[2];panel(ax,'c');ax.set(xlim=(1999.5,2019.5),ylim=(-.1,1.65),yticks=[],xticks=[2000,2005,2010,2015,2019])
for yr in range(2000,2020):ax.add_patch(Rectangle((yr-.45,.25),.9,.65,fc='#e69f00' if yr==2010 else '#e8e8e8' if yr in [2009,2011] else '#a7c8e1',ec='white'))
ax.text(2004,1.14,'Permitted fitting years',ha='center',fontsize=10);ax.annotate('Held out',xy=(2010,.85),xytext=(2013.0,1.38),ha='center',fontsize=10,arrowprops={'arrowstyle':'->'});ax.set_xlabel('Origin year; adjacent years excluded');save(fig,'Fig02_design')

fig,axs=four()
base=pd.read_csv(ROOT/'revision/primary/scores.csv')
for ax,k in zip(axs.flat,REGIONS):
 for method in ['Raw','Bottom_up','H0_7_NN','H1_7_NN']:
  d=S[(S.domain==k)&(S.method==method)].set_index('lead').loc[['W1','W2','W3','W4']];line(ax,[1,2,3,4],d.crpss,method)
 ax.axhline(0,c='.5',lw=.8,ls=':');ax.set(xticks=[1,2,3,4],xlabel='Forecast week',ylabel='CRPSS',ylim=(-.08,.62))
legend(fig,axs[0,0]);save(fig,'Fig03_weekly_skill')

fig,axs=four()
limits=[]
for k in REGIONS:
 ref=C.query("domain==@k and lead=='D28'").reference.mean()
 q=B.query("domain==@k and method=='H1_7_NN' and baseline in ['H0_7_NN','H1_5_NN','Bottom_up'] and lead=='D28' and score=='crps'")
 limits.extend((q[['lower','upper']].values/ref*100).ravel())
extent=max(abs(np.array(limits)));effect_xlim=(-extent*1.10,extent*1.10)
for ax,k in zip(axs.flat,REGIONS):
 for i,(base,label,col,mk) in enumerate([('H0_7_NN','Climate information','#009E73','o'),('H1_5_NN','Fortnight layer','#AA4499','s'),('Bottom_up','vs bottom-up','#D55E00','D')]):
  d=B.query("domain==@k and method=='H1_7_NN' and baseline==@base and lead=='D28' and score=='crps'").iloc[0];ref=C.query("domain==@k and lead=='D28'").reference.mean();val=d.delta/ref*100;lo=d.lower/ref*100;hi=d.upper/ref*100;ax.errorbar(val,i,xerr=[[val-lo],[hi-val]],fmt=mk,mfc='white',ms=6,mew=1.2,c=col,capsize=3,label=label)
 ax.axvline(0,c='.5',lw=.8,ls=':');ax.set(yticks=[0,1,2],yticklabels=['H1 vs H0','7 vs 5','H1 vs BU'],xlim=effect_xlim,xlabel='Change (% of climate CRPS)');ax.invert_yaxis()
legend(fig,axs[0,0],2);save(fig,'Fig04_factorial')

fig,axs=four(top=.87)
for ax,k in zip(axs.flat,REGIONS):
 for j,season in enumerate(['DJF','MAM','JJA','SON']):
  q=C.query("domain==@k and lead=='D28' and season==@season");a=q.groupby(['method','year']).crps.mean().unstack('method');diff=(a.H1_7_NN-a.H0_7_NN).values;lo,hi=np.quantile(diff[draw].mean(1),[.025,.975]);ax.errorbar(j,diff.mean(),yerr=[[diff.mean()-lo],[hi-diff.mean()]],fmt='o',mfc='white',ms=6,mew=1.3,c=RC[k],capsize=3)
 ax.axhline(0,c='.5',lw=.8,ls=':');ax.set(xticks=range(4),xticklabels=['DJF','MAM','JJA','SON'],ylabel='H1 minus H0 CRPS (mm)',xlabel='Origin season')
save(fig,'Fig05_seasons')

fig,axs=four()
cv=pd.read_csv(E/'coverage_curves.csv')
for ax,k in zip(axs.flat,REGIONS):
 for m in ['Raw','Bottom_up','H0_7_NN','H1_7_NN']:
  d=cv.query("domain==@k and lead=='D28' and method==@m");line(ax,d.nominal*100,d.coverage*100,m)
 ax.plot([15,100],[15,100],':',c='.5',lw=1);ax.set(xlim=(15,100),ylim=(15,100),xticks=[20,40,60,80,100],yticks=[20,40,60,80,100],xlabel='Nominal coverage (%)',ylabel='Observed coverage (%)')
legend(fig,axs[0,0]);save(fig,'Fig06_coverage')

fig,axs=plt.subplots(1,2,figsize=(6.8,4.6));fig.subplots_adjust(left=.12,right=.97,bottom=.17,top=.73,wspace=.38);g=pd.read_csv(E/'mechanism_summary.csv');symbols={'DJF':'o','MAM':'s','JJA':'^','SON':'D'}
for ax,col,title,l in zip(axs,['real_linear','real_nn'],['Linear mapping','Nonnegative samples'],'ab'):
 for _,r in g.iterrows():ax.scatter(r.predicted*100,r[col]*100,marker=symbols[r.season],s=52,facecolors='none',edgecolors=RC[r.domain],linewidths=1.2)
 ax.plot([-5,25],[-5,25],':',c='.6',lw=1);ax.axhline(0,c='.7',lw=.7);ax.set(xlim=(-5,25),ylim=(-7,25),xlabel='Predicted MSE gain (%)',ylabel='Observed MSE gain (%)',title=title);panel(ax,l)
handles=[plt.Line2D([],[],c=c,marker='o',mfc='white',ls='',label=k) for k,c in RC.items()]+[plt.Line2D([],[],c='black',marker=mk,mfc='white',ls='',label=ss) for ss,mk in symbols.items()];fig.legend(handles=handles,loc='upper center',ncol=4,frameon=False,bbox_to_anchor=(.53,1));save(fig,'Fig07_mechanism')

fig,axs=four(top=.85)
for ax,k in zip(axs.flat,REGIONS):
 d=RB.query("domain==@k and measure=='crps'").set_index('lead').loc[['W1','W2','W3','W4','D28']];ax.errorbar(range(5),d.delta,yerr=[d.delta-d.lower,d.upper-d.delta],fmt='o',mfc='white',c=RC[k],ms=6,mew=1.3,capsize=3);ax.axhline(0,c='.5',ls=':',lw=1);ax.set(xticks=range(5),xticklabels=['W1','W2','W3','W4','28 d'],ylabel='Recalibration CRPS change (mm)',xlabel='Accumulation scale');r=R.query("domain==@k and lead=='D28'").set_index('method');ax.text(.03,.94,f'80% coverage: {100*r.loc["Original","coverage80"]:.1f}% to\n{100*r.loc["Coherent_recalibration","coverage80"]:.1f}%',transform=ax.transAxes,va='top',fontsize=10)
save(fig,'Fig08_recalibration')

# Supplementary probability diagnostics, with year-block reliability intervals.
fig,axs=four()
reliability=[]
for ax,k in zip(axs.flat,REGIONS):
 for method in ['Raw','Bottom_up','H0_7_NN','H1_7_NN']:
  q=C.query("domain==@k and method==@method and lead=='D28'");xx=[];yy=[]
  bins=np.minimum((q.prob90.values*10).astype(int),9)
  for b in range(10):
   mask=bins==b
   if mask.sum()<20:continue
   num=np.array([q.event90.values[mask&(q.year.values==yr)].sum() for yr in range(2000,2020)]);den=np.array([(mask&(q.year.values==yr)).sum() for yr in range(2000,2020)]);denboot=den[draw].sum(1);valid=denboot>0;boot=num[draw].sum(1)[valid]/denboot[valid];lo,hi=np.quantile(boot,[.025,.975]);x=q.prob90.values[mask].mean();y=q.event90.values[mask].mean();xx.append(x);yy.append(y);ax.errorbar(x,y,yerr=[[max(0,y-lo)],[max(0,hi-y)]],fmt='none',c=COL[method],alpha=.5,lw=.7);reliability.append(dict(domain=k,method=method,bin=b,n=int(mask.sum()),probability=x,event_frequency=y,lower=lo,upper=hi))
  line(ax,xx,yy,method)
 ax.plot([0,1],[0,1],':',c='.5');ax.set(xlim=(0,1),ylim=(0,1),xticks=[0,.5,1],yticks=[0,.5,1],xlabel='Predicted exceedance probability',ylabel='Observed frequency')
legend(fig,axs[0,0]);save(fig,'FigS01_tail_reliability');pd.DataFrame(reliability).to_csv(E/'reliability_bins.csv',index=False)
fig,axs=four()
for ax,k in zip(axs.flat,REGIONS):
 for m in ['Bottom_up','H0_7_NN','H1_7_NN']:
  q=C.query("domain==@k and lead=='D28' and method==@m");hist,edges=np.histogram(q.pit,bins=np.linspace(0,1,11));ax.step((edges[:-1]+edges[1:])/2,hist/hist.sum(),where='mid',label=LAB[m],color=COL[m],lw=1.5)
 ax.axhline(.1,c='.5',ls=':',lw=1);ax.set(xlim=(0,1),ylim=(0,.23),xlabel='Randomised PIT',ylabel='Proportion')
legend(fig,axs[0,0]);save(fig,'FigS02_pit')
print('Saved 8 main and 2 supplementary figures.',flush=True)
