import numpy as np


def normalize(a):
    if len(a) == 0:
        return None
    r = []
    for i in range(len(a)):
        r.append(a[i] / a[0])
    return r
