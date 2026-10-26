from common import ROOT
import pandas as pd
p=ROOT/'revision/extension';b=pd.read_csv(p/'comparisons.csv')
print(b.query("lead=='D28' and score=='crps'").to_string(index=False))
c=pd.read_csv(p/'case_scores.csv.gz')
print(c.query("lead=='D28'").groupby(['domain','method','season']).crps.mean().unstack('method').round(3).to_string())
print(pd.read_csv(p/'decomposition.csv').query("lead=='D28'").to_string(index=False))
weekly=c[c.lead.isin(['W1','W2','W3','W4'])].groupby(['domain','method']).crps.mean().unstack('method');print('WEEKLY',weekly.to_string())
print('MECHANISM',pd.read_csv(p/'mechanism_summary.csv').to_string(index=False))
