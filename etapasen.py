# Etapa surtidor común con FET de acumulación canal N

import numpy as np
from feten import FETen
from resistor import best_rdiv, nearest_r

class EtapaSE(object): 

    def __init__(self, fet, vdd, rd, rs, r1, r2, rg):
        self.__fet = fet
        self.__r1 = r1
        self.__r2 = r2
        self.__rd = rd
        self.__rs = rs
        self.__rg = rg
        self.__zi = rg + r1 * r2 / (r1 + r2)
        self.__zo = rd
        self.__vdd = vdd
        self.__gain = None
        self.__calcula_pto_trabajo()

    @classmethod
    def from_gain_rd_rs_zi(cls, fet, vdd=12, gain_t=25, rd=100, rs=0, zi=1e5, odiv=4, isE96=False):
        gain_target = 10 ** (gain_t / 20)
        vgsq_target = gain_target / (2 * fet.k * rd) + fet.vt
        idq_target = FETen.idrain(vgsq_target, fet.k, fet.vt)
        vgq_target = vgsq_target + idq_target * rs

        r1, r2 = best_rdiv(vdd, vgq_target, isE96)
        r1 = int(r1 * 10 ** odiv)
        r2 = int(r2 * 10 ** odiv)
        rg = nearest_r(zi - r1 * r2 / (r1 + r2), isE96)

        return cls(fet, vdd, rd, rs, r1, r2, rg)

    def __calcula_pto_trabajo(self):
        self.__fet.vg = self.vdd * self.r2 / (self.r1 + self.r2)
        vgsq = [root for root in 
            np.poly1d([
                self.rs * self.__fet.k, 
                1 - 2 * self.rs * self.__fet.k * self.__fet.vt, 
                self.rs * self.__fet.k * self.__fet.vt ** 2 - self.__fet.vg]).r
            if root > self.__fet.vt][0]
        self.__fet.vs = FETen.idrain(vgsq, self.__fet.k, self.__fet.vt) * self.rs
        self.__fet.vd = self.vdd - self.__fet.get_id() * self.rd
        self.__fet.on()
        self.__gain = 20 * np.log10(self.__fet.get_gm() * self.rd)

    @property
    def r1(self):
        return self.__r1

    @r1.setter
    def r1(self, r1):
        self.__r1 = r1
        self.__zi = self.rg + self.r1 * self.r2 / (self.r1 + self.r2)
        self.__calcula_pto_trabajo()

    @property
    def r2(self):
        return self.__r2

    @r2.setter
    def r2(self, r2):
        self.__r2 = r2
        self.__zi = self.rg + self.r1 * self.r2 / (self.r1 + self.r2)
        self.__calcula_pto_trabajo()

    @property
    def rd(self):
        return self.__rd

    @rd.setter
    def rd(self, rd):
        self.__rd = rd
        self.__zo = rd
        self.__calcula_pto_trabajo()

    @property
    def rs(self):
        return self.__rs

    @rs.setter
    def rs(self, rs):
        self.__rs = rs
        self.__calcula_pto_trabajo()

    @property
    def rg(self):
        return self.__rg

    @rg.setter
    def rg(self, rg):
        self.__rg = rg
        self.__zi = self.rg + self.r1 * self.r2 / (self.r1 + self.r2)

    @property
    def vdd(self):
        return self.__vdd

    @vdd.setter
    def vdd(self, vdd):
        self.__vdd = vdd
        self.__calcula_pto_trabajo()

    def get_vgsq(self):
        return self.__fet.get_vgs()

    def get_vdsq(self):
        return self.__fet.get_vds()

    def get_vdq(self):
        return self.__fet.vd

    def get_vgq(self):
        return self.__fet.vg

    def get_vsq(self):
        return self.__fet.vs

    def get_idq(self):
        return self.__fet.get_id()

    def get_gain(self):
        return self.__gain

    def get_zi(self):
        return self.__zi

    def get_zo(self):
        return self.__zo

    def get_k(self):
        return self.__fet.k

    def get_vt(self):
        return self.__fet.vt
