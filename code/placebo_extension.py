"""Twenty full year-block predictor permutations, refitting all nested folds."""
from review_controls import *
P4=ROOT/'revision/review_v4/placebo';P4.mkdir(exist_ok=True)

def run(task):
 rep,year=task;path=P4/f'permutation_{rep:02d}_{year}.npz'
 if path.exists():return f'permutation {rep} year {year} cached'
 d,dates,r5,y5=load_data('N','primary');raw=expand(r5);y=expand(y5);z=lagged_climate(dates,d)
 donor=np.arange(2000,2020)
 if rep:
  rng=np.random.default_rng(SEED+90000+rep);rng.shuffle(donor);zz=z.copy();days=calendar_day(dates)
  for yy,dd in zip(range(2000,2020),donor):
   to=np.flatnonzero(dates.year==yy);fr=np.flatnonzero(dates.year==dd);source=fr[np.argmin(near_day(days[to,None],days[fr][None,:]),axis=1)];zz[to]=z[source]
  z=zz
 train=permitted(dates,[year-1,year,year+1]);test=np.flatnonzero(dates.year==year)
 out,_=evaluate_variant(raw,y,dates,z,train,test,'N',year,'H1');score=crps(out,y[test])
 np.savez_compressed(path,crps=score,dates=dates[test].values,donor=donor)
 return f'permutation {rep} year {year} complete'

def score():
 rows=[]
 for rep in range(21):
  yearly=[]
  for yr in range(2000,2020):yearly.append(np.load(P4/f'permutation_{rep:02d}_{yr}.npz')['crps'][:,6].mean())
  rows.append(dict(permutation=rep,crps=float(np.mean(yearly))))
 a=pd.DataFrame(rows);obs=a.iloc[0].crps;p=(1+int((a.iloc[1:].crps<=obs).sum()))/21
 a.to_csv(P4/'scores.csv',index=False);(P4/'summary.json').write_text(json.dumps(dict(observed=obs,null_min=float(a.iloc[1:].crps.min()),null_max=float(a.iloc[1:].crps.max()),permutations=20,monte_carlo_p=p,interpretation='Year-block exchangeability sensitivity; climate persistence makes this assumption approximate.'),indent=2));print((P4/'summary.json').read_text())

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--score',action='store_true');p.add_argument('--workers',type=int,default=8);a=p.parse_args()
 if a.score:score()
 else:
  with ProcessPoolExecutor(max_workers=a.workers) as pool:
   for f in as_completed([pool.submit(run,(r,y)) for r in range(21) for y in range(2000,2020)]):print(f.result(),flush=True)
