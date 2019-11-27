# Etapa surtidor común con FET de acumulación canal N

import numpy as np
from feten import FETen
from resistor import best_rdiv, nearest_r, nearest_greater_r

class EtapaSE(object): 

    def __init__(self, fet, vdd, rd, rs, r1, r2, rg):
        self._fet = fet
        self._r1 = r1
        self._r2 = r2
        self._rd = rd
        self._rs = rs
        self._rg = rg
        self._zi = rg + r1 * r2 / (r1 + r2)
        self._zo = rd
        self._vdd = vdd
        self._gain = None
        self._gain_db = None
        self._mdo = None
        self._mdi = None
        self._calcula_pto_trabajo()

    @classmethod
    def from_gain_rd_rs_zi(cls, fet, vdd=12, gain_t=25, rd=100, rs=0, zi=1e5, odiv=4, isE96=False):
        rd = nearest_r(rd, isE96)
        rs = nearest_r(rs, isE96)
        gain_target = 10 ** (gain_t / 20)
        vgsq_target = gain_target / (2 * fet.k * rd) + fet.vt
        idq_target = FETen.idrain(vgsq_target, fet.k, fet.vt)
        vgq_target = vgsq_target + idq_target * rs

        r1, r2 = best_rdiv(vdd, vgq_target, isE96)
        r1 = int(r1 * 10 ** odiv)
        r2 = int(r2 * 10 ** odiv)
        rg = nearest_greater_r(zi - r1 * r2 / (r1 + r2), isE96)

        return cls(fet, vdd, rd, rs, r1, r2, rg)

    def _calcula_pto_trabajo(self):
        self._fet.vg = self.vdd * self.r2 / (self.r1 + self.r2)
        vgsq = [root for root in 
            np.poly1d([
                self.rs * self._fet.k, 
                1 - 2 * self.rs * self._fet.k * self._fet.vt, 
                self.rs * self._fet.k * self._fet.vt ** 2 - self._fet.vg]).r
            if root > self._fet.vt][0]
        self._fet.vs = FETen.idrain(vgsq, self._fet.k, self._fet.vt) * self.rs
        self._fet.vd = self.vdd - self._fet.idq * self.rd
        self._fet.on()
        self._gain_db = 20 * np.log10(self._fet.gm * self.rd)
        self._gain = 10 ** (self._gain_db / 20)
        self._mdo = min(self.idq * self.rd, self.vdsq - self.vgsq)
        self._mdi = self._mdo / self._gain

    @property
    def r1(self):
        return self._r1

    @r1.setter
    def r1(self, r1):
        self._r1 = r1
        self._zi = self.rg + self.r1 * self.r2 / (self.r1 + self.r2)
        self._calcula_pto_trabajo()

    @property
    def r2(self):
        return self._r2

    @r2.setter
    def r2(self, r2):
        self._r2 = r2
        self._zi = self.rg + self.r1 * self.r2 / (self.r1 + self.r2)
        self._calcula_pto_trabajo()

    @property
    def rd(self):
        return self._rd

    @rd.setter
    def rd(self, rd):
        self._rd = rd
        self._zo = rd
        self._calcula_pto_trabajo()

    @property
    def rs(self):
        return self._rs

    @rs.setter
    def rs(self, rs):
        self._rs = rs
        self._calcula_pto_trabajo()

    @property
    def rg(self):
        return self._rg

    @rg.setter
    def rg(self, rg):
        self._rg = rg
        self._zi = self.rg + self.r1 * self.r2 / (self.r1 + self.r2)

    @property
    def vdd(self):
        return self._vdd

    @vdd.setter
    def vdd(self, vdd):
        self._vdd = vdd
        self._calcula_pto_trabajo()

    @property
    def vgsq(self):
        return self._fet.vgs

    @property
    def vdsq(self):
        return self._fet.vds

    @property
    def vdq(self):
        return self._fet.vd

    @property
    def vgq(self):
        return self._fet.vg

    @property
    def vsq(self):
        return self._fet.vs

    @property
    def idq(self):
        return self._fet.idq

    @property
    def gain_db(self):
        return self._gain_db

    @property
    def zi(self):
        return self._zi

    @property
    def zo(self):
        return self._zo

    @property
    def k(self):
        return self._fet.k

    @property
    def vt(self):
        return self._fet.vt

    @property
    def mdi(self):
        return self._mdi

    @property
    def mdo(self):
        return self._mdo
