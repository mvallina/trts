#!/usr/bin/env python3

import matplotlib.pyplot as plt
import numpy as np
import argparse
from scipy.optimize import curve_fit
from resistor import best_rdiv, nearest_r, r_str

parser = argparse.ArgumentParser()
parser.add_argument("file", type=str, help="data file")
parser.add_argument("-Rd", "--rd", type=int, default=100, help="drain resistor")
parser.add_argument("-Rs", "--rs", type=int, default=0, help="source resistor")
parser.add_argument("-G", "--gain", type=float, default=25, help="gain (dB)")
parser.add_argument("-P", "--plot", action="store_true", help="plot fit")
parser.add_argument("-E", "--e96", action="store_true", help="E96 instead E24")
parser.add_argument("-V", "--vdd", type=float, default=12, help="Vdd")
parser.add_argument("-O", "--odiv", type=int, default=4, help="voltage divider order")

args = parser.parse_args()

try:
    data = np.genfromtxt(args.file)
except OSError:
    print("File {0:s} does not exist".format(args.file))
    exit()
    
vgs_data, id_data = data[:, 0], data[:, 1]

rd = nearest_r(args.rd, args.e96)
rs = nearest_r(args.rs, args.e96)

def idrain(vgs, k, vt):
    return k * (vgs - vt) ** 2

popt, pcov = curve_fit(idrain, vgs_data, id_data)
k, vt = tuple(popt)

gain_target = 10 ** (args.gain / 20)
vgsq_target = gain_target / (2 * k * rd) + vt
idq_target = idrain(vgsq_target, k, vt)
vgq_target = vgsq_target + idq_target * rs

R1, R2 = best_rdiv(args.vdd, vgq_target, args.e96)
R1 = int(R1 * 10 ** args.odiv)
R2 = int(R2 * 10 ** args.odiv)
vgq = args.vdd * R2 / (R1 + R2)
vgsq = [root for root in 
        np.poly1d([rs * k, 1 - 2 * rs * k * vt, rs * k * vt ** 2 - vgq]).r
        if root > vt][0]
idq = idrain(vgsq, k, vt)
vsq = idq * rs
vdq = args.vdd - idq * rd
vdsq = vdq - vsq
if vdsq < vgsq:
    print("No saturation")
    exit()
gain = 20 * np.log10(2 * k * (vgsq - vt) * rd)

print("\nEstimated transistor parameters")
print("-------------------------------")
print("K = {:>6.1f}".format(k * 1000).rstrip("0").rstrip(".") + " mA/V²")
print("Vt = {:>5.2f}".format(vt).rstrip("0").rstrip(".") + " V\n")
print("Best polarization network found for desired gain")
print("------------------------------------------------")
print("R1 = {:>5s}".format(r_str(R1, args.e96)))
print("R2 = {:>5s}".format(r_str(R2, args.e96)))
print("Rd = {:>5s}".format(r_str(rd, args.e96)))
print("Rs = {:>5s}\n".format(r_str(rs, args.e96)))
print("Quiescent point")
print("---------------")
print("{0:<6s} {1:>5.2f}".format("Vgsq =", vgsq).rstrip("0").rstrip(".") + " V")
print("{0:<6s} {1:>5.2f}".format("Vdsq =", vdsq).rstrip("0").rstrip(".") + " V")
print("{0:<6s} {1:>5.2f}".format("Vdq =", vdq).rstrip("0").rstrip(".") + " V")
print("{0:<6s} {1:>5.2f}".format("Vgq =", vgq).rstrip("0").rstrip(".") + " V")
print("{0:<6s} {1:>5.2f}".format("Vsq =", vsq).rstrip("0").rstrip(".") + " V")
print("{0:<6s} {1:>5.1f}".format("Idq =", 1000 * idq).rstrip("0").rstrip(".") + " mA\n")
print("Achieved gain")
print("-------------")
print("Gain = {:.1f} dB\n".format(gain))

if args.plot:
    vgs = np.linspace(vgs_data[0], vgs_data[len(vgs_data) - 1], 1000)
    i_d = k * np.square(vgs - vt)
    
    plt.title(r"$K = {0:4.1f} mA/V^2, V_t = {1:5.2f}V$".format(k * 1000, vt))
    plt.xlabel(r"$v_{gs}$")
    plt.ylabel(r"$i_d$")
    plt.grid()
    plt.plot(vgs_data, id_data, marker="o", linestyle=" ")
    plt.plot(vgs, i_d, linestyle="-")
    plt.show()
