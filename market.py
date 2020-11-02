from controls import *
from math import floor
import os

dates = sorted(os.listdir('../data/minute/AAPL'))
data_dir = '../data/minute'

class Market(object):

    def __init__(self, date, symbols):

        self.date = date
        self.symbols = symbols
        self.prev = dates[dates.index(date)-1]
        self.barsets, self.prev_barsets, self.changes = {}, {}, {}
        for sym in [s[0] for s in self.symbols]:
            try:
                self.barsets[sym] = read_bin(f'{data_dir}/{sym}/{self.date}')
                self.prev_barsets[sym] = read_bin(f'{data_dir}/{sym}/{self.prev}')
                self.changes[sym] = get_change(self.prev, sym)

            except:
                if sym in self.symbols:
                    self.symbols.remove(sym)

    def porfolio(self, disp=False, offset=0):

        max_p = len(self.symbols)
        funds = 5000
        active = {}
        min_t, take_p = 0, .20
        profit = 0
        tsp = []

        for m in range(offset, 390):

            curr_p = 0
            for sym, tp in self.symbols:

                try:
                    v, o, c, h, l = self.barsets[sym][m]
                    if sym not in active:
                        qty = floor(funds/max_p/c)
                        active[sym] = [tp, qty, c]
                    else:
                        tp, qty, lim = active[sym]
                        if tp == 0:
                            curr_p += qty * (lim - c)
                        elif tp == 1:
                            curr_p += qty * (c - lim)

                except Exception as e:
                    pass
            tsp.append(curr_p/funds)

        end_p = 0
        for sym in active:
            tp, qty, lim = active[sym]
            close = self.barsets[sym][-1][2]
            if tp == 0:
                end_p += qty * (lim - close)
            elif tp == 1:
                end_p += qty * (close - lim)

        tsp.append(end_p/funds)

        return max(tsp), min(tsp), tsp[-1]