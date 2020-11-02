from controls import *
import os
from features import FeatureExtraction

dates = sorted(os.listdir('../data/minute/AAPL'))
data_dir = '../data/minute'

def signalize(symbols, offset, period):

    X, Y = [], []
    for i in range(period, len(dates)):
        dt = dates[i-period:i]
        curr = dt[-1]
        for sym in symbols:
            inp = []
            try:
                for d in dt:
                    _bars = read_bin(f'{data_dir}/{sym}/{d}')
                    (_o, _v) = (
                        [b[1] for b in _bars],
                        [b[0] for b in _bars],
                    )
                    if d == curr:
                        (_open, _close) = (
                            _bars[offset+1][1],
                            _bars[-1][2],
                        )
                        change = 1 + (_close - _open)/_open 
                        Y.append(change)
                        (_o, _v) = _o[:offset], _v[:offset]

                    inp.append(_o)
                    inp.append(_v)
                X.append(inp)
            except Exception as e:
                print(e)
                continue

    return X, Y 


'''
symbols = ['AAL']
X, Y = signalize(symbols, 90, period=5)

extraction = FeatureExtraction(workers=8)

settings, scores = extraction.extract(
    X=X,
    Y=Y,
    feat_count=1,
    max_time=1200,
    end_tol=1
)


newX = extraction.extract_features(
    X=X,
    settings=settings,
)

d = {'X': newX, 'Y': Y}

dump_json('data/data.json', d)
'''