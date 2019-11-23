# FET acumulación canal N

import numpy as np
from scipy.optimize import curve_fit
from resistor import best_rdiv, nearest_r, r_str

class nFETen:

    def __init__(self, vgs_data, id_data):
        popt, pcov = curve_fit(idrain, vgs_data, id_data)
        self.k, self.vt = tuple(popt)

    @staticmethod
    def idrain(vgs, k, vt):
        return k * (vgs - vt) ** 2
