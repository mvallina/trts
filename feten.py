# FET acumulación canal N

import numpy as np
from scipy.optimize import curve_fit

class Corte(Exception):
    pass
class Gradual(Exception):
    pass
class DemasiadaCorriente(Exception):
    pass

class FETen(object):

    def __init__(self, k, vt, vd=0, vg=0, vs=0, id_max=.1, error=None):
        self._ison = False
        self._k = k
        self._vt = vt
        self._vd = vd
        self._vg = vg
        self._vs = vs
        self._gm = 2 * self.k * (self.vg - self.vs + self.vt)
        self._id = FETen.idrain(self.vg - self.vs, self.k, self.vt)
        self._id_max = id_max
        self._error = None if error is None else error

    def _check(self):
        if self.vg - self.vs < self.vt:
            raise Corte
        elif self.vg > self.vd:
            raise Gradual
        elif self._id > self._id_max:
            raise DemasiadaCorriente
    
    def _refresh(self):
        self._gm = 2 * self.k * (self.vg - self.vs - self.vt)
        self._id = FETen.idrain(self.vg - self.vs, self.k, self.vt)
        if self._ison:
            self._check()

    @classmethod
    def fromdata(cls, vgs_data, id_data, id_max=.1):
        popt, pcov = curve_fit(FETen.idrain, vgs_data, id_data)
        k, vt = tuple(popt)
        return cls(k, vt, id_max=id_max, error=np.sqrt(np.diag(pcov)))

    @staticmethod
    def idrain(vgs, k, vt):
        return k * (vgs - vt) ** 2

    @property
    def k(self):
        return self._k

    @k.setter
    def k(self, k):
        self._error = None
        self._k = k
        self._refresh()

    @property
    def vt(self):
        return self._vt

    @vt.setter
    def vt(self, vt):
        self._error = None
        self._vt = vt
        self._refresh()

    @property
    def vd(self):
        return self._vd

    @vd.setter
    def vd(self, vd):
        self._vd = vd
        if self._ison:
            self._check()

    @property
    def vg(self):
        return self._vg

    @vg.setter
    def vg(self, vg):
        self._vg = vg
        self._refresh()

    @property
    def vs(self):
        return self._vs

    @vs.setter
    def vs(self, vs):
        self._vs = vs
        self._refresh()

    @property
    def vgs(self):
        return self.vg - self.vs

    @property
    def vds(self):
        return self.vd - self.vs

    @property
    def idq(self):
        return self._id

    @property
    def gm(self):
        return self._gm

    @property
    def error(self):
        return self._error

    def on(self):
        self._ison = True
        self._check()

    def off(self):
        self._ison = False
