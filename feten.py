# FET acumulación canal N

import numpy as np
from scipy.optimize import curve_fit

class Corte(Exception):
    pass
class Gradual(Exception):
    pass
class DemasiadaCorriente(Exception):
    pass

class FETen:

    def __init__(self, k, vt, vd=0, vg=0, vs=0, id_max=.1, error=None):
        self.__ison = False
        self.__k = k
        self.__vt = vt
        self.__vd = vd
        self.__vg = vg
        self.__vs = vs
        self.__gm = 2 * self.k * (self.vg - self.vs + self.vt)
        self.__id = FETen.idrain(self.vg - self.vs, self.k, self.vt)
        self.__id_max = id_max
        self.__error = None if error is None else error

    def __check(self):
        if self.vg - self.vs < self.vt:
            raise Corte
        elif self.vg > self.vd:
            raise Gradual
        elif self.__id > self.__id_max:
            raise DemasiadaCorriente
    
    def __refresh(self):
        self.__gm = 2 * self.k * (self.vg - self.vs - self.vt)
        self.__id = FETen.idrain(self.vg - self.vs, self.k, self.vt)
        if self.__ison:
            self.__check()

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
        return self.__k

    @k.setter
    def k(self, k):
        self.__error = None
        self.__k = k
        self.__refresh()

    @property
    def vt(self):
        return self.__vt

    @vt.setter
    def vt(self, vt):
        self.__error = None
        self.__vt = vt
        self.__refresh()

    @property
    def vd(self):
        return self.__vd

    @vd.setter
    def vd(self, vd):
        self.__vd = vd
        if self.__ison:
            self.__check()

    @property
    def vg(self):
        return self.__vg

    @vg.setter
    def vg(self, vg):
        self.__vg = vg
        self.__refresh()

    @property
    def vs(self):
        return self.__vs

    @vs.setter
    def vs(self, vs):
        self.__vs = vs
        self.__refresh()

    def get_vgs(self):
        return self.vg - self.vs

    def get_vds(self):
        return self.vd - self.vs

    def get_id(self):
        return self.__id

    def get_gm(self):
        return self.__gm

    def get_error(self):
        return self.__error

    def on(self):
        self.__ison = True
        self.__check()

    def off(self):
        self.__ison = False
