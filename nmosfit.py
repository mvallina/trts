#!/usr/bin/env python3

import matplotlib.pyplot as plt
import numpy as np
import argparse
from scipy.optimize import curve_fit

parser = argparse.ArgumentParser()
parser.add_argument("file", type=str, help="data file")
parser.add_argument("-Rd", "--rd", type=int, default=100, help="drain resistor")
parser.add_argument("-Rs", "--rs", type=int, default=0, help="source resistor")
parser.add_argument("-G", "--gain", type=float, default=25, help="gain (dB)")
parser.add_argument("-P", "--plot", action="store_true", help="plot fitted polynomial")

args = parser.parse_args()

try:
    data = np.genfromtxt(args.file)
except OSError:
    print("File {0:s} does not exist".format(args.file))
    exit()
    
vgs_data, id_data = data[:, 0], data[:, 1]

def idrain(vgs, k, vt):
    return k * (vgs - vt) ** 2

popt, pcov = curve_fit(idrain, vgs_data, id_data)
k, vt = tuple(popt)

gain_target = 10 ** (args.gain / 20)
vgsq = gain_target / (2 * k * args.rd) + vt
idq = idrain(vgsq, k, vt)
vgq = vgsq + idq * args.rs

print("k = {:6.1f} mA/V^2".format(k * 1000))
print("Vt = {:6.3f} V\n".format(vt))
print("Gain = {:5.1f} dB".format(args.gain))
print("Rd = {} ohm".format(args.rd))
print("Rs = {} ohm".format(args.rs))
print("Vgq = {:6.3f} V".format(vgq))
print("Vgsq = {:6.3f} V".format(vgsq))
print("Idq = {:6.1f} mA".format(1000 * idq))

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
