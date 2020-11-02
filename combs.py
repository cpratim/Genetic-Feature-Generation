from itertools import permutations, combinations
from scipy.optimize import differential_evolution
import numpy as np
from threading import Thread
from model import signalize
from math import floor
import warnings
from matplotlib import pyplot as plt
from math import log
from gplearn.genetic import SymbolicRegressor

warnings.filterwarnings("ignore")

def _normalize(a):
    if len(a) == 0:
        return None
    r = []
    for i in range(len(a)):
        r.append(a[i] / a[0])
    return r

scalar_functions = (
    np.average,
    np.median,
    np.arange,
    np.min,
    np.max,
)

array_functions = (
    np.max,
    np.min,
    np.average,
    np.median,
    np.arange,
    np.std,
    np.sum,
    lambda a: np.median(np.cumsum(a)),
    lambda a: np.median(np.nancumprod(a)),
)

array_func_bounds = (
    0, (len(array_functions)-1)/10
)
scalar_func_bounds = (
    0, (len(scalar_functions)-1)/10
)


class GeneticExtraction(object):

    def __init__(self, X, Y, workers=1):

        self.X = X
        self.Y = Y
        self.results = []
        self.workers = workers

    def _transform(self, params, chosen, X):
        array_settings = [
            floor(i * 10) for i in params[:-1]
        ]
        scalar_setting = floor(params[-1] * 10)
        newX = []
        for x in X:
            arrays = [_normalize(x[i]) for i in chosen]
            transformed = [
                array_functions[array_settings[i]](arrays[i]) 
                for i in range(len(arrays))
            ]
            feat = scalar_functions[scalar_setting](transformed)
            newX.append(feat)
        return newX

    def _fitness(self, params, chosen):
        try:
            transX = self._transform(params, chosen, self.X)
        except Exception as e:
            return 1
        dev = 1
        R = np.corrcoef(transX, self.Y)[0][1]/dev
        return abs(R) ** -1 / 10


    def _evolve(self, comb, maxiter=1, popsize=50):
        bounds = tuple(
            [array_func_bounds for i in range(len(comb))]
            + [scalar_func_bounds]
        ) 
        try:
            result = differential_evolution(
                func=self._fitness,
                bounds=bounds,
                popsize=popsize,
                workers=-1,
                args=(comb,),
                disp=False,
                maxiter=maxiter,
            )
            params = result.x
            transX = self._transform(params, comb, self.X)
            dev = np.std(transX) ** .5
            R = np.corrcoef(transX, self.Y)[0][1]
            print(R)
            result = (R/dev, params, comb)
            self.results.append(result)
            return params
        except Exception as e:
            pass
        return  

    def extract(self):
        ops = [i for i in range(len(self.X[0]))]
        combs = []
        for i in range(1, len(ops)+1):
            comb = list(combinations(ops, i))
            combs.extend(comb)

        for comb in combs:
            self._evolve(comb)

        top_comb = sorted(
            self.results, 
            key=lambda x: x[0], 
            reverse=True
        )[0][2]
        print(top_comb)
        top_params = self._evolve(
            comb=top_comb,
            maxiter=5, 
            popsize=100,
        )
        return top_comb, top_params


symbols = ['SBUX']
X, Y = signalize(
    symbols=symbols,
    offset=10,
    period=1,
)

gen_ext = GeneticExtraction(X=X, Y=Y)
comb, params = gen_ext.extract()
transX = gen_ext._transform(params, comb, X)

print(f'R: {np.corrcoef(transX, Y)}')
plt.scatter(transX, Y)
plt.show()



