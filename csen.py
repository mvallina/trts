#!/usr/bin/env python3

import matplotlib.pyplot as plt
import numpy as np
import argparse
from resistor import r_str
from etapasen import EtapaSE
from feten import FETen, Corte, Gradual, DemasiadaCorriente

parser = argparse.ArgumentParser()
parser.add_argument("file", type=str, help="archivo de medidas")
parser.add_argument("-Rd", "--rd", type=int, default=100, help="resistencia drenador")
parser.add_argument("-Rs", "--rs", type=int, default=0, help="resistencia surtidor")
parser.add_argument("-Zi", "--zi", type=int, default=30, help="impedancia entrada Kohm")
parser.add_argument("-G", "--gain", type=float, default=25, help="ganancia (dB)")
parser.add_argument("-P", "--plot", action="store_true", help="pintar ajuste")
parser.add_argument("-I", "--idmax", type= float, default=.2, help="Id_max")
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

try:
    etapa = EtapaSE.from_gain_rd_rs_zi(FETen.fromdata(vgs_data, id_data, args.idmax), 
                args.vdd, args.gain, args.rd, args.rs, args.zi * 1000, 
                odiv=args.odiv, isE96=args.e96)
except Corte:
    print("Transistor en corte")
    exit()
except Gradual:
    print("Transistor en zona gradual")
    exit()
except DemasiadaCorriente:
    print("¡¡¡ Demasiada corriente !!!")
    exit()

print("\nParámetros estimados nFET\n")
print("{0:<4s} {1:>5.2f}".format("K =", etapa.k * 1000) + " mA/V²")
print("{0:<4s} {1:>5.2f}".format("Vt =", etapa.vt) + " V\n")
print("Red de polarización\tDisipación\n")
print("R1 = {0:>5s}{1:21.0f} mW".format(
    r_str(etapa.r1, args.e96), 1000 * ((etapa.vdd - etapa.vgq) ** 2 / etapa.r1)))
print("R2 = {0:>5s}{1:21.0f} mW".format(
    r_str(etapa.r2, args.e96), 1000 * etapa.vgq ** 2 / etapa.r2))
print("Rd = {0:>5s}{1:21.0f} mW".format(
    r_str(etapa.rd, args.e96), 1000 * etapa.rd * etapa.idq ** 2))
print("Rs = {0:>5s}{1:21.0f} mW".format(
    r_str(etapa.rs, args.e96), 1000 * etapa.rs * etapa.idq ** 2))
print("Rg ≥ {:>5s}\n".format(r_str(etapa.rg, args.e96)))
print("Punto de trabajo\n")
print("{0:<6s} {1:>6.2f}".format("Vdd =", etapa.vdd) + " V")
print("{0:<6s} {1:>6.2f}".format("Vdsq =", etapa.vdsq) + " V")
print("{0:<6s} {1:>6.2f}".format("Vgsq =", etapa.vgsq) + " V")
print("{0:<6s} {1:>6.2f}".format("Vrd =", etapa.vdd - etapa.vdq) + " V")
print("{0:<6s} {1:>6.2f}".format("Vdq =", etapa.vdq) + " V")
print("{0:<6s} {1:>6.2f}".format("Vgq =", etapa.vgq) + " V")
print("{0:<6s} {1:>6.2f}".format("Vsq =", etapa.vsq) + " V")
print("{0:<6s} {1:>6.2f}".format("MDₛ =", etapa.mdo) + " V")
print("{0:<6s} {1:>6.2f}".format("MDₑ =", 1000 * etapa.mdi) + " mV")
print("{0:<6s} {1:>6.2f}".format("Idq =", 1000 * etapa.idq) + " mA")
print("{0:<6s} {1:>6.2f}".format("Pₜ=", 1000 * etapa.idq * etapa.vdsq) + " mW\n")
print("Parámetros etapa\n")
print("{0:<3s} {1:>6.1f}".format("G =", etapa.gain_db) + " dB")
print("{0:<3s} {1:>5s}".format("Zi =", r_str(etapa.zi, args.e96)))
print("{0:<3s} {1:>5s}\n".format("Zo =", r_str(etapa.zo, args.e96)))

if args.plot:
    vgs = np.linspace(vgs_data[0], vgs_data[len(vgs_data) - 1], 1000)
    i_d = etapa.k * np.square(vgs - etapa.vt)
    
    plt.title(r"$K = {0:4.1f} mA/V^2, V_t = {1:5.2f}V$".format(etapa.k * 1000, etapa.vt))
    plt.xlabel(r"$v_{gs}$")
    plt.ylabel(r"$i_d$")
    plt.grid()
    plt.plot(vgs_data, id_data, marker="o", linestyle=" ")
    plt.plot(vgs, i_d, linestyle="-")
    plt.show()
