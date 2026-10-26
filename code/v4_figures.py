"""Large, original publication figures; all data markers are hollow squares."""
from common import ROOT,REGIONS
import numpy as np,pandas as pd,json,shutil
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon,Rectangle
from matplotlib.colors import TwoSlopeNorm
R=ROOT/'revision/review_v4';F=R/'figures';F.mkdir(exist_ok=True)
legacy=R/'legacy_figures';legacy.mkdir(exist_ok=True)
legacy_source=(ROOT/'code/review_figures.py').read_text(encoding='utf-8').replace("revision/review_v3/figures","revision/review_v4/legacy_figures")
# The original plotting script executes its transformed source at the end.
legacy_source=legacy_source.replace("H1 minus bottom-up", "H1 minus BU-rain")
legacy_source=legacy_source.replace("exec(compile(source", "source=source.replace('Bottom-up','BU-rain').replace('H0, seven nodes','H0').replace('H1, seven nodes','H1').replace('vs bottom-up','vs BU-rain').replace('H1 vs BU','H1 vs'+chr(92)+'nBU-rain')\nexec(compile(source")
exec(compile(legacy_source,'v4_legacy_figures','exec'),{})
for p in (ROOT/'revision/review_v3/figures').glob('*'):
 if p.is_file():shutil.copy2(p,F/p.name)
for p in legacy.glob('*'):
 if p.is_file():shutil.copy2(p,F/p.name)
plt.rcParams.update({'font.family':'Arial','font.size':11,'axes.labelsize':11,'axes.titlesize':12,'xtick.labelsize':10.5,'ytick.labelsize':10.5,'legend.fontsize':10,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42,'svg.fonttype':'none'})
domains=dict(REGIONS);domains.update(json.loads((R/'coverage/domains.json').read_text()));codes=list(domains)
col=dict(zip(codes,['#AA4499','#009E73','#4477AA','#CC6677','#D55E00','#666666','#0072B2','#886600']))
aus=next(f['geometry'] for f in json.loads((ROOT/'data/support/countries.geojson').read_text(encoding='utf-8'))['features'] if f['properties'].get('ADMIN')=='Australia')
def save(fig,name):
 for ext in ['png','pdf','svg']:fig.savefig(F/(name+'.'+ext),dpi=500)
 plt.close(fig)
def panel(ax,letter):
 ax.annotate('('+letter+')',xy=(0,1),xycoords='axes fraction',xytext=(-22,20),textcoords='offset points',fontsize=14,fontweight='bold',va='bottom',annotation_clip=False)
def mapbase(ax):
 for p in aus['coordinates']:ax.add_patch(Polygon(p[0],fc='#f5f5f5',ec='#777',lw=.65))
 ax.set(xlim=(111,155),ylim=(-45,-9),xticks=[115,135,155],yticks=[-40,-30,-20,-10]);ax.set_xticklabels(['115°E','135°E','155°E']);ax.set_yticklabels(['40°S','30°S','20°S','10°S']);ax.set_aspect(1.1);ax.set_anchor('N')
fig,axs=plt.subplots(1,2,figsize=(6.8,5.1));fig.subplots_adjust(left=.09,right=.97,bottom=.17,top=.70,wspace=.49);ax=axs[0];mapbase(ax)
for k,r in domains.items():
 x0,x1=r['lon'];y0,y1=r['lat'];ax.add_patch(Rectangle((x0,y0),x1-x0,y1-y0,fc='none',ec=col[k],lw=1.7));ax.annotate(k,((x0+x1)/2,(y0+y1)/2),xytext=(4,7),textcoords='offset points',weight='bold',fontsize=11)
ax.annotate('North',xy=(116,-15),xytext=(116,-24),ha='center',fontsize=10,arrowprops={'arrowstyle':'->'});panel(ax,'a');ax.set_title('Eight domains',pad=15)
daily=pd.read_csv(ROOT/'data/processed/agcd_daily_regional_mm.csv',index_col=0,parse_dates=True).join(pd.read_csv(R/'coverage/daily_observations.csv',index_col=0,parse_dates=True)).loc['2000':'2019'];cycle=daily.resample('MS').sum().groupby(lambda x:x.month).mean();ax=axs[1]
for k in codes:ax.plot(range(1,13),cycle[k],marker='s',mfc='white',ms=5,mew=1,lw=1.15,c=col[k],label=k)
ax.set(xlim=(.6,12.4),xticks=[1,4,7,10],xticklabels=['Jan','Apr','Jul','Oct'],ylabel='Monthly rainfall (mm)');ax.grid(axis='y',color='#e7e7e7',lw=.5);ax.set_axisbelow(True);panel(ax,'b');ax.set_title('Observed seasonality',pad=15);fig.legend(*ax.get_legend_handles_labels(),loc='upper center',ncol=4,frameon=False,bbox_to_anchor=(.55,.99));save(fig,'Fig01_domains')
# Full nested workflow, including the extra layer needed to learn weights.
fig,axs=plt.subplots(3,1,figsize=(6.8,7.4),gridspec_kw={'height_ratios':[1.3,2.5,1.0]});fig.subplots_adjust(left=.11,right=.97,bottom=.08,top=.94,hspace=.6)
def box(ax,x,y,w,h,txt,fc='#edf2f5'):
 ax.add_patch(Rectangle((x,y),w,h,fc=fc,ec='#777',lw=.8));ax.text(x+w/2,y+h/2,txt,ha='center',va='center',fontsize=11)
for ax in axs[:2]:ax.set(xlim=(0,1),ylim=(0,1));ax.axis('off')
ax=axs[0];panel(ax,'a');box(ax,.03,.03,.94,.29,'Four weekly totals', '#eaf2f7');box(ax,.03,.48,.43,.32,'Two fortnights','#ecf4ec');box(ax,.54,.48,.43,.32,'28-day total','#f9e9dc');ax.annotate('',xy=(.23,.48),xytext=(.23,.32),arrowprops={'arrowstyle':'->'});ax.annotate('',xy=(.75,.48),xytext=(.75,.32),arrowprops={'arrowstyle':'->'})
ax=axs[1];panel(ax,'b')
for y,txt in [(.78,'Outer training years\nExclude verification year and neighbours'),(.52,'Inner held-out components\nFit marginals, ranks and W inside inner training'),(.26,'Learn weights or select a method\nUse only inner held-out CRPS'),(0,'Refit components on outer training years\nApply frozen rule to the outer year')]:box(ax,.07,y,.86,.19,txt)
for y in [.78,.52,.26]:ax.annotate('',xy=(.5,y-.07),xytext=(.5,y),arrowprops={'arrowstyle':'->'})
ax=axs[2];panel(ax,'c');ax.set(xlim=(1999.5,2019.5),ylim=(0,1.5),yticks=[],xticks=[2000,2005,2010,2015,2019])
for yr in range(2000,2020):ax.add_patch(Rectangle((yr-.45,.1),.9,.5,fc='#e69f00' if yr==2010 else '#ddd' if yr in [2009,2011] else '#a7c8e1',ec='white'))
ax.text(2004,1.05,'Fitting years',ha='center');ax.annotate('Held out',xy=(2010,.6),xytext=(2013,1.05),ha='center',arrowprops={'arrowstyle':'->'});ax.set_xlabel('Example outer fold');save(fig,'Fig02_design')
orig=pd.read_csv(ROOT/'revision/extension/comparisons.csv');new=pd.read_csv(R/'coverage/comparisons.csv');ac=pd.read_csv(R/'access_s2/comparisons.csv');cc=pd.read_csv(ROOT/'revision/review_v3/control_comparisons.csv')
def contrast(k,b):
 if k=='ACCESS_N':return ac.query('lead=="D28" and baseline==@b').iloc[0][['delta','lower','upper']].to_numpy(float)
 if k in codes[4:]:return new.query('domain==@k and lead=="D28" and baseline==@b').iloc[0][['delta','lower','upper']].to_numpy(float)
 if b=='H0':return orig.query('domain==@k and method=="H1_7_NN" and baseline=="H0_7_NN" and lead=="D28" and score=="crps"').iloc[0][['delta','lower','upper']].to_numpy(float)
 v=cc.query('domain==@k and method=="Weekly_climate_BU" and baseline=="H1_7_NN" and lead=="D28" and score=="crps"').iloc[0];return np.array([-v.delta,-v.upper,-v.lower])
fig,axs=plt.subplots(1,2,figsize=(6.8,5.9),gridspec_kw={'width_ratios':[1,1.1]});fig.subplots_adjust(left=.09,right=.98,bottom=.19,top=.84,wspace=.48);ax=axs[0];mapbase(ax);norm=TwoSlopeNorm(vmin=-.4,vcenter=0,vmax=.4);cmap=plt.get_cmap('RdBu_r')
for k,r in domains.items():
 x=np.mean(r['lon']);yy=np.mean(r['lat']);v=contrast(k,'H0')[0];ax.plot(x,yy,marker='s',mfc='white',mec='#666666',mew=.7,ms=12);ax.plot(x,yy,marker='s',mfc='white',mec=cmap(norm(v)),mew=2.4,ms=10);ax.annotate(k,(x,yy),xytext=(4,7),textcoords='offset points',fontsize=10.5)
panel(ax,'a');ax.set_title('Climate contrast',pad=17);fig.canvas.draw();pos=ax.get_position();cax=fig.add_axes([pos.x0,pos.y0-.11,pos.width,.025]);fig.colorbar(plt.cm.ScalarMappable(norm=norm,cmap=cmap),cax=cax,orientation='horizontal',label='H1 minus H0 CRPS (mm)')
ax=axs[1];keys=codes+['ACCESS_N']
for j,(b,lab,c) in enumerate([('H0','H1 minus H0','#0072B2'),('Weekly_climate_BU','H1 minus BU-clim','#D55E00')]):
 for i,k in enumerate(keys):
  v,lo,hi=contrast(k,b);ax.errorbar(v,i+(j-.5)*.24,xerr=[[v-lo],[hi-v]],fmt='s',mfc='white',mec=c,color=c,ms=5.5,lw=1,label=lab if i==0 else None)
ax.axvline(0,c='.5',ls=':',lw=1);ax.axhline(7.5,c='#cccccc',ls='--',lw=.6);ax.set(yticks=range(9),yticklabels=codes+['ACCESS N'],xlabel='CRPS difference (mm)',ylim=(8.65,-.65));panel(ax,'b');ax.set_title('Paired differences',pad=17);fig.legend(*ax.get_legend_handles_labels(),loc='upper center',ncol=2,frameon=False,bbox_to_anchor=(.54,.99));save(fig,'Fig05_transfer')
fa=pd.read_csv(ROOT/'revision/review_v3/forward_annual.csv');mm=pd.read_csv(R/'matched_validation_summary.csv');lab={'Raw':'Raw','Bottom_up':'BU-rain','H0':'H0','H1':'H1','Weekly_climate_BU':'BU-clim'};cols=['#333333','#0072B2','#009E73','#D55E00','#AA4499']
fig,axs=plt.subplots(2,1,figsize=(6.8,6.7));fig.subplots_adjust(left=.14,right=.97,bottom=.1,top=.85,hspace=.67)
for m,c in zip(lab,cols):
 a=fa.query('domain=="N" and lead=="D28" and method==@m').sort_values('year');axs[0].plot(a.year,a.crps,marker='s',mfc='white',c=c,ms=6,label=lab[m]);v=mm.query('domain=="N" and method==@m').iloc[0];axs[1].plot([0,1],[v.loyo_crps,v.forward_crps],marker='s',mfc='white',c=c,ms=6)
axs[0].set(xticks=range(2015,2020),ylabel='Annual CRPS (mm)',title='Northern forward scores');axs[1].set(xticks=[0,1],xticklabels=['LOYO, 2015–2019','Forward, 2015–2019'],ylabel='Mean CRPS (mm)',xlim=(-.3,1.3),title='Matched evaluation years');panel(axs[0],'a');panel(axs[1],'b');fig.legend(*axs[0].get_legend_handles_labels(),loc='upper center',ncol=3,frameon=False,bbox_to_anchor=(.55,1));save(fig,'Fig08_forward')
comp=pd.read_csv(R/'adaptive/comparisons.csv');fig,axs=plt.subplots(1,2,figsize=(6.8,4.8));fig.subplots_adjust(left=.13,right=.97,bottom=.2,top=.8,wspace=.4)
for ax,mode,letter in zip(axs,['LOYO','Forward'],'ab'):
 for j,(m,c) in enumerate([('State','#D55E00'),('Select_season','#0072B2')]):
  for i,k in enumerate(['N','NE','SE','SW']):
   a=comp.query('domain==@k and validation==@mode and lead=="D28" and method==@m and baseline=="Constant"').iloc[0];ax.errorbar(a.delta,i+(j-.5)*.23,xerr=[[a.delta-a.lower],[a.upper-a.delta]],fmt='s',mfc='white',c=c,ms=6,label=('State weights' if m=='State' else 'Seasonal selection') if i==0 else None)
 ax.axvline(0,c='.5',ls=':');ax.set(yticks=range(4),yticklabels=['N','NE','SE','SW'],ylim=(3.6,-.6),xlabel='CRPS change from\nconstant mixture (mm)',title='Year-block validation' if mode=='LOYO' else 'Forward 2015–2019');panel(ax,letter)
fig.legend(*axs[0].get_legend_handles_labels(),loc='upper center',ncol=2,frameon=False,bbox_to_anchor=(.55,.99));save(fig,'Fig10_mixtures')
# Preserve the two displaced figures as labelled supplementary figures.
for old,newname in [('Fig08_recalibration','FigS03_power_map'),('Fig05_seasons','FigS04_seasons')]:
 for ext in ['png','pdf','svg']:shutil.copy2(F/(old+'.'+ext),F/(newname+'.'+ext))
de=pd.read_csv(R/'adaptive/decision_summary.csv');fig,axs=plt.subplots(2,2,figsize=(6.8,7.0));fig.subplots_adjust(left=.13,right=.97,bottom=.1,top=.85,hspace=.65,wspace=.4)
for ax,k,letter in zip(axs.flat,['N','NE','SE','SW'],'abcd'):
 for m,c in [('Raw','#333333'),('Weekly_climate_BU','#AA4499'),('Constant','#0072B2'),('State','#D55E00')]:
  a=de.query('domain==@k and validation=="LOYO" and metric=="Expense" and threshold==100 and method==@m').sort_values('ratio');ax.plot(a.ratio,a.skill,c=c,marker='s',mfc='white',ms=3.8,lw=1.1,label=lab.get(m,m));ax.fill_between(a.ratio,a.lower,a.upper,color=c,alpha=.07)
 ax.axhline(0,c='.6',ls=':');ax.set(xlabel='Cost / loss',ylabel='Relative value',title=k);panel(ax,letter)
fig.legend(*axs[0,0].get_legend_handles_labels(),loc='upper center',ncol=2,frameon=False,bbox_to_anchor=(.55,1));save(fig,'FigS05_decision')
print('V4 figures generated with hollow square data markers.')
