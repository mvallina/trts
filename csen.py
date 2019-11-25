#!/usr/bin/env python3

import matplotlib.pyplot as plt
import numpy as np
import argparse
from resistor import nearest_r, r_str
from etapasen import EtapaSE
from feten import FETen, Corte, Gradual, DemasiadaCorriente

parser = argparse.ArgumentParser()
parser.add_argument("file", type=str, help="archivo de medidas")
parser.add_argument("-Rd", "--rd", type=int, default=100, help="resistencia drenador")
parser.add_argument("-Rs", "--rs", type=int, default=0, help="resistencia surtidor")
parser.add_argument("-G", "--gain", type=float, default=25, help="ganancia (dB)")
parser.add_argument("-P", "--plot", action="store_true", help="pintar ajuste")
parser.add_argument("-E", "--e96", action="store_true", help="E96 en vez de E24")
parser.add_argument("-V", "--vdd", type=float, default=12, help="Vdd")
parser.add_argument("-O", "--odiv", type=int, default=4, help="orden del divisor de tensión")

args = parser.parse_args()

try:
    data = np.genfromtxt(args.file)
except OSError:
    print("No existe el archivo {0:s}".format(args.file))
    exit()
    
vgs_data, id_data = data[:, 0], data[:, 1]

rd = nearest_r(args.rd, args.e96)
rs = nearest_r(args.rs, args.e96)

trt = FETen.fromdata(vgs_data, id_data)

try:
    etapa = EtapaSE.from_gain_rd_rs(trt, args.vdd, args.gain, rd, rs, args.odiv, args.e96)
except Corte:
    print("Transistor en corte")
    exit()
except Gradual:
    print("Transistor en zona gradual")
    exit()
except DemasiadaCorriente:
    print("¡¡¡ Demasiada corriente !!!")
    exit()

print("\nParámetros estimados\n")
print("{0:<4s} {1:>5.2f}".format("K =", etapa.fet.k * 1000) + " mA/V²")
print("{0:<4s} {1:>5.2f}".format("Vt =", etapa.fet.vt) + " V\n")
print("Red de polarización\n")
print("R1 = {:>5s}".format(r_str(etapa.r1, args.e96)))
print("R2 = {:>5s}".format(r_str(etapa.r2, args.e96)))
print("Rd = {:>5s}".format(r_str(etapa.rd, args.e96)))
print("Rs = {:>5s}\n".format(r_str(etapa.rs, args.e96)))
print("Punto de trabajo\n")
print("{0:<6s} {1:>5.2f}".format("Vdd =", etapa.vdd) + " V")
print("{0:<6s} {1:>5.2f}".format("Vgsq =", etapa.get_vgsq()) + " V")
print("{0:<6s} {1:>5.2f}".format("Vdsq =", etapa.get_vdsq()) + " V")
print("{0:<6s} {1:>5.2f}".format("Vdq =", etapa.get_vdq()) + " V")
print("{0:<6s} {1:>5.2f}".format("Vgq =", etapa.get_vgq()) + " V")
print("{0:<6s} {1:>5.2f}".format("Vsq =", etapa.get_vsq()) + " V")
print("{0:<6s} {1:>5.2f}".format("Idq =", 1000 * etapa.get_idq()) + " mA\n")
print("Ganancia conseguida = {:.1f} dB\n".format(etapa.get_gain()))

if args.plot:
    vgs = np.linspace(vgs_data[0], vgs_data[len(vgs_data) - 1], 1000)
    i_d = etapa.fet.k * np.square(vgs - etapa.fet.vt)
    
    plt.title(r"$K = {0:4.1f} mA/V^2, V_t = {1:5.2f}V$".format(etapa.fet.k * 1000, etapa.fet.vt))
    plt.xlabel(r"$v_{gs}$")
    plt.ylabel(r"$i_d$")
    plt.grid()
    plt.plot(vgs_data, id_data, marker="o", linestyle=" ")
    plt.plot(vgs, i_d, linestyle="-")
    plt.show()
