# FET acumulación canal N

import numpy as np
from scipy.optimize import curve_fit
from resistor import best_rdiv, nearest_r, r_str

class FETen:

    def __init__(self, k, vt):
        self.k = k
        self.vt = vt

    @classmethod
    def fromdata(cls, vgs_data, id_data):
        popt, pcov = curve_fit(idrain, vgs_data, id_data)
        k, vt = tuple(popt)
        return cls(k, vt)

    @classmethod
    def fromparams(cls, k, vt):
        return cls(k, vt)

    @staticmethod
    def idrain(vgs, k, vt):
        return k * (vgs - vt) ** 2
