# Etapa surtidor común con FET de acumulación canal N

from feten import FETen

class EtapaSE: 

    def __init__(self, Vdd, Rd, Rs, R1, R2, Rg):
        self.Vdd = Vdd
        self.R1 = R1
        self.R2 = R2
        self.Rd = Rd
        self.Rs = Rs
        self.Rg = Rg
        self.Zi = Rg + R1 * R2 / (R1 + R2)
        self.Zo = Rd
        self.gm = 2 * k * (vgs + vt

    @classmethod
    def from_gain_rd_rs(cls, gain, rd, rs):

