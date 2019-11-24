# FET acumulación canal N

import numpy as np
from scipy.optimize import curve_fit

class FETen:

    def __init__(self, k, vt, pcov):
        self.k = k
        self.vt = vt
        self.dk, self.dvt = None, None if pcov == None else np.sqrt(np.diag(pcov))

    @classmethod
    def fromdata(cls, vgs_data, id_data):
        popt, pcov = curve_fit(idrain, vgs_data, id_data)
        k, vt = tuple(popt)
        return cls(k, vt, pcov)

    @classmethod
    def fromparams(cls, k, vt):
        return cls(k, vt, None)

    @staticmethod
    def idrain(vgs, k, vt):
        return k * (vgs - vt) ** 2
