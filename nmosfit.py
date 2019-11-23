#!/usr/bin/env python3

import matplotlib.pyplot as plt
import numpy as np
import argparse
from scipy.optimize import curve_fit
from resistor import best_rdiv, nearest_r

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

d, R1, R2 = best_rdiv(args.vdd, vgq_target, args.e96)
R1 = int(R1 * 10 ** args.odiv)
R2 = int(R2 * 10 ** args.odiv)
vgq = args.vdd * R2 / (R1 + R2)
vgsq = [root for root in 
        np.poly1d([rs * k, 1 - 2 * rs * k * vt, rs * k * vt ** 2 - vgq]).r
        if root > vt][0]
idq = idrain(vgsq, k, vt)
gain = 20 * np.log10(2 * k * (vgsq - vt) * rd)

print("k = {:4.1f} mA/V²".format(k * 1000))
print("Vt = {:5.2f} V\n".format(vt))
print("R1 = {} ohm".format(R1))
print("R2 = {} ohm".format(R2))
print("Rd = {} ohm".format(rd))
print("Rs = {} ohm\n".format(rs))
print("Vgq = {:5.2f} V".format(vgq))
print("Vgsq = {:5.2f} V".format(vgsq))
print("Idq = {:4.1f} mA\n".format(1000 * idq))
print("Gain = {:3.0f} dB".format(gain))

if args.plot:
    vgs = np.linspace(vgs_data[0], vgs_data[len(vgs_data) - 1], 1000)
    i_d = k * np.square(vgs - vt)
    
    plt.title(r"$K = {0:6.1f} mA/V^2, V_t = {1:6.3f}V$".format(k * 1000, vt))
    plt.xlabel(r"$v_{gs}$")
    plt.ylabel(r"$i_d$")
    plt.grid()
    plt.plot(vgs_data, id_data, marker="o", linestyle=" ")
    plt.plot(vgs, i_d, linestyle="-")
    plt.show()
