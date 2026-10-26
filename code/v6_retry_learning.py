from v6_climate_learning import *
if __name__=='__main__':
    p=L/'ACCESS_NW_2014.npz'
    p.rename(L/'ACCESS_NW_2014.npz.before_retry')
    print(fit_learning(('ACCESS','NW',2014)),flush=True)
    score_learning()
