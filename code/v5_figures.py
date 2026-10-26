"""Focused V5 figures from archived results; all data markers are open squares."""
from common import ROOT,REGIONS
import numpy as np,pandas as pd,json,shutil
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle,Polygon,FancyBboxPatch
R=ROOT/'revision/review_v5';F=R/'figures';F.mkdir(exist_ok=True)
for p in (ROOT/'revision/review_v4/figures').glob('*'):
 if p.is_file():shutil.copy2(p,F/p.name)
for old,new in [('Fig10_mixtures','FigS06_mixtures'),('Fig08_forward','FigS07_forward')]:
 for ext in ['png','pdf','svg']:shutil.copy2(F/(old+'.'+ext),F/(new+'.'+ext))
plt.rcParams.update({'font.family':'Arial','font.size':11,'axes.labelsize':11,'axes.titlesize':12,'xtick.labelsize':10.5,'ytick.labelsize':10.5,'legend.fontsize':10,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42,'svg.fonttype':'none'})
codes=['N','NE','SE','SW','NW','CA','EC','TAS'];blue='#2166AC';orange='#B35806';green='#00886A'
def save(fig,name):
 for ext in ['png','pdf','svg']:fig.savefig(F/(name+'.'+ext),dpi=450)
 plt.close(fig)
def panel(ax,s):ax.annotate('('+s+')',xy=(0,1),xycoords='axes fraction',xytext=(-20,13),textcoords='offset points',weight='bold',fontsize=14,va='bottom',annotation_clip=False)

# A single main question, with distinct information configurations and honest nesting.
fig=plt.figure(figsize=(6.8,7.1));gs=fig.add_gridspec(3,1,height_ratios=[1,1.35,.45],hspace=.64);a,b,c=[fig.add_subplot(gs[i]) for i in range(3)]
a.set_axis_off();a.set_xlim(0,10);a.set_ylim(0,3.1)
def box(ax,x,y,w,h,label,face='#EAF2F8',size=11):
 ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.06',facecolor=face,edgecolor='#345',linewidth=.9));ax.text(x+w/2,y+h/2,label,ha='center',va='center',fontsize=size)
for i in range(4):box(a,.5+i*2.35,.1,1.65,.48,'Week '+str(i+1))
for i in range(2):box(a,1.65+i*4.7,1.2,1.65,.48,'Fortnight '+str(i+1))
box(a,4,2.3,1.65,.48,'28 days')
for x1,x2 in [(1.325,2.475),(3.675,2.475),(6.025,7.175),(8.375,7.175)]:a.annotate('',xy=(x2,1.18),xytext=(x1,.62),arrowprops={'arrowstyle':'->','color':'#567'})
for x in [2.475,7.175]:a.annotate('',xy=(4.825,2.28),xytext=(x,1.72),arrowprops={'arrowstyle':'->','color':'#567'})
panel(a,'a');a.set_title('One rainfall sequence, consistent accumulation periods',pad=17)
b.set_axis_off();b.set_xlim(0,10);b.set_ylim(-.25,5.4);panel(b,'b')
box(b,.1,4.45,9.8,.7,'Outer year held out; adjacent years excluded','#FFF0D8')
box(b,.1,3.05,4.65,.9,'Permitted outer training data\nFive inner year blocks')
box(b,5.25,3.05,4.65,.9,'Inner validation errors\nEstimate covariance W')
b.annotate('',xy=(7.6,4.02),xytext=(5,4.4),arrowprops={'arrowstyle':'->','color':'#567'});b.annotate('',xy=(2.4,4.02),xytext=(5,4.4),arrowprops={'arrowstyle':'->','color':'#567'})
box(b,.1,1.35,9.8,1.0,'Climate adjustment: none | weeks | aggregates | all nodes\nRefit marginals and rank templates on permitted data',size=10.5)
for x in [2.4,7.6]:b.annotate('',xy=(x,2.42),xytext=(x,3),arrowprops={'arrowstyle':'->','color':'#567'})
box(b,.1,0,9.8,.7,'Weekly summation or nonnegative reconciliation\nScore the outer year',face='#E6F2EB',size=10.5)
b.annotate('',xy=(5,.77),xytext=(5,1.29),arrowprops={'arrowstyle':'->','color':'#567'})
c.set_ylim(0,1);c.set_xlim(1999.5,2019.5);c.set_yticks([])
for y in range(2000,2020):c.add_patch(Rectangle((y-.45,.18),.9,.54,facecolor=orange if y==2010 else '#CCCCCC' if y in [2009,2011] else '#C7DDEE',edgecolor='white'))
c.set_xticks([2000,2005,2010,2015,2019]);c.set_xlabel('Example outer fold: 2010 verified, 2009 and 2011 excluded');panel(c,'c')
fig.subplots_adjust(left=.12,right=.96,top=.94,bottom=.09);save(fig,'Fig02_design')

fig,axes=plt.subplots(1,2,figsize=(6.8,5.3),sharey=True)
for ax,system,file in zip(axes,['ECMWF','ACCESS-S2'],[R/'domain_comparisons.csv',R/'access_s2/domain_comparisons.csv']):
 d=pd.read_csv(file)
 for off,base,color,label in [(-.13,'H0',blue,'H1 minus H0'),(.13,'Weekly_climate_BU',orange,'H1 minus BU-clim')]:
  z=d.query('baseline==@base').set_index('domain').loc[codes]
  ax.errorbar(z.delta,np.arange(8)+off,xerr=np.vstack([z.delta-z.lower,z.upper-z.delta]),fmt='s',mfc='white',mec=color,ecolor=color,ms=6,mew=1.3,lw=1.15,capsize=2,label=label)
 ax.axvline(0,color='.4',lw=.9,ls=':');ax.set_title(system,pad=13);ax.set_xlabel('CRPS difference (mm)');ax.grid(axis='x',alpha=.15);ax.set_ylim(7.6,-.6)
axes[0].set_yticks(range(8),codes);panel(axes[0],'a');panel(axes[1],'b')
fig.legend(*axes[0].get_legend_handles_labels(),loc='lower center',ncol=2,bbox_to_anchor=(.5,.01));fig.subplots_adjust(left=.12,right=.97,top=.88,bottom=.2,wspace=.18);save(fig,'Fig05_transfer')

o=pd.read_csv(R/'operational/scores.csv');print('operational score columns',o.columns.tolist())
if 'method' in o.columns:o=o.query('lead=="D28"') if 'lead' in o.columns else o;o=o.pivot(index='domain',columns='method',values='crps')
else:o=o.set_index('domain')
fig,axes=plt.subplots(2,1,figsize=(6.8,6.7),gridspec_kw={'height_ratios':[1.35,1]})
ax=axes[0]
for i,(m,label,color) in enumerate([('Raw','ECMWF (QC)','#666666'),('Weekly_climate_BU','BU-clim',blue),('H1','H1',orange)]):
 ax.plot(range(8),o.loc[codes,m],marker='s',mfc='white',mec=color,mew=1.3,color=color,lw=1,ms=6,label=label)
ax.set_xticks(range(8),codes);ax.set_ylabel('28-day CRPS (mm)');ax.set_title('Previously unused 2020 issued forecasts',pad=15);ax.legend(ncol=3,loc='upper center',bbox_to_anchor=(.5,-.12));ax.grid(axis='y',alpha=.15);panel(ax,'a')
z=pd.read_csv(R/'operational/confirmatory_contrast.csv');ax=axes[1]
ax.errorbar(z.delta,[0,1,2],xerr=np.vstack([z.delta-z.lower,z.upper-z.delta]),fmt='s',mfc='white',mec=orange,ecolor=orange,mew=1.4,ms=7,lw=1.3,capsize=3)
ax.set_yticks([0,1,2],['4-origin blocks','6-origin blocks','8-origin blocks']);ax.set_ylim(2.5,-.5);ax.axvline(0,color='.4',ls=':',lw=1);ax.set_xlabel('H1 minus BU-clim (% of training raw CRPS)');ax.set_title('Equal-domain contrast and 95% intervals',pad=15);panel(ax,'b');ax.grid(axis='x',alpha=.15)
fig.subplots_adjust(left=.24,right=.97,top=.91,bottom=.1,hspace=.86);save(fig,'Fig08_holdout')

z=np.load(R/'circulation/verified_fields.npz');months=pd.DatetimeIndex(z['dates']).month;lon=z['lon'];lat=z['lat']
geo=json.loads((ROOT/'data/support/countries.geojson').read_text(encoding='utf-8'))['features']
fig=plt.figure(figsize=(6.8,7.4));gs=fig.add_gridspec(2,2,height_ratios=[1,1.05],hspace=.72,wspace=.15);axs=[fig.add_subplot(gs[0,i]) for i in range(2)];sc=fig.add_subplot(gs[1,:])
for ax,season,ms in zip(axs,['Summer (DJF)','Winter (JJA)'],[[12,1,2],[6,7,8]]):
 mask=np.isin(months,ms);q=z['shum'][mask].mean(0)*1000;u=z['uwnd'][mask].mean(0);v=z['vwnd'][mask].mean(0)
 im=ax.pcolormesh(lon,lat,q,cmap='YlGnBu',vmin=2,vmax=15,shading='nearest',rasterized=True)
 for ft in geo:
  g=ft['geometry'];polys=g['coordinates'] if g['type']=='MultiPolygon' else [g['coordinates']] if g['type']=='Polygon' else []
  for poly in polys:ax.add_patch(Polygon(poly[0],fill=False,edgecolor='.3',linewidth=.55))
 qu=ax.quiver(lon[::2],lat[::2],u[::2,::2],v[::2,::2],scale=100,width=.005,color='#303030')
 ax.add_patch(Rectangle((120,-15),20,10,fill=False,ec='#B2182B',lw=1.3,ls='--'))
 ax.add_patch(Rectangle((131.25,-15.75),3,3,fill=False,ec='black',lw=1.5));ax.set_xlim(100,155);ax.set_ylim(-25,5);ax.set_aspect('equal');ax.set_xticks([110,130,150],['110°E','130°E','150°E']);ax.set_yticks([-20,-10,0],['20°S','10°S','0°']);ax.set_title(season,pad=12)
axs[1].tick_params(labelleft=False);panel(axs[0],'a');panel(axs[1],'b');axs[1].quiverkey(qu,.82,-.38,10,'10 m s$^{-1}$',labelpos='W',coordinates='axes',fontproperties={'size':10})
cax=fig.add_axes([.25,.535,.54,.018]);cb=fig.colorbar(im,cax=cax,orientation='horizontal');cb.set_label('850 hPa specific humidity (g kg$^{-1}$)',labelpad=3)
d=pd.read_csv(R/'circulation/annual_djf_diagnostic.csv');sc.scatter(d.u850,d.h1_minus_h0_crps,marker='s',s=55,facecolors='none',edgecolors=blue,linewidths=1.4);sc.axhline(0,lw=.9,ls=':',color='.4');sc.set_xlabel('DJF zonal wind, 120–140°E and 15–5°S (m s$^{-1}$)');sc.set_ylabel('H1 minus H0 CRPS (mm)');sc.grid(alpha=.12);panel(sc,'c');sc.set_title('Twenty annual summer pairs',pad=14);sc.text(.02,.96,'Spearman $r_s$ = −0.25\n95% interval: −0.66 to 0.23',transform=sc.transAxes,ha='left',va='top',fontsize=10,bbox={'facecolor':'white','edgecolor':'none','alpha':.85,'pad':2})
fig.subplots_adjust(left=.13,right=.96,top=.92,bottom=.10);save(fig,'Fig10_circulation')

d=pd.read_csv(R/'all_five_year_omissions.csv');print('omission cols',d.columns.tolist())
fig,axes=plt.subplots(3,1,figsize=(6.8,7.2),sharex=True)
for ax,base,label in zip(axes,['Bottom_up','H0','Weekly_climate_BU'],['BU-rain','H0','BU-clim']):
 vals=d.query('baseline==@base').delta;ax.hist(vals,bins=40,color='#C7DDEE',edgecolor='white',linewidth=.4);ax.axvline(0,color='.4',ls=':',lw=1);ax.set_ylabel('Combinations');ax.set_title('H1 minus '+label,pad=9);ax.grid(axis='y',alpha=.12)
for ax,l in zip(axes,'abc'):panel(ax,l)
axes[-1].set_xlabel('Mean CRPS difference after omitting five years (mm)');fig.subplots_adjust(left=.15,right=.97,top=.93,bottom=.09,hspace=.55);save(fig,'FigS08_omissions')
print('V5 figures complete')
