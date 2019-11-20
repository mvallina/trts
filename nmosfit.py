#!/usr/bin/env python3

import matplotlib.pyplot as plt
import numpy as np
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("file", type=str, help="data file")
parser.add_argument("-R", "--rd", type=float, default=1e3, help="resistor on drain")
parser.add_argument("-D", "--diagnose", action="store_true", help="plot aux polynomial")
parser.add_argument("-I", "--init", type=float, default=10, help="iterative seed")
parser.add_argument("-G", "--gain", type=float, default=25, help="gain desired (dB)")
parser.add_argument("-P", "--plot", action="store_true", help="plot fitted polynomial")

args = parser.parse_args()

try:
    data = np.genfromtxt(args.file)
except OSError:
    print("File {0:s} does not exist".format(args.file))
    exit()
    
vgs_data, id_data = data[:, 0], data[:, 1]

if args.diagnose:
    vx = np.linspace(0, 10, 1000)
    vy1 = [((vgs_data - v) @ id_data - 
        np.square(vgs_data - v) @ id_data * np.sum(np.power(vgs_data - v, 3)) / 
        np.sum(np.power(vgs_data - v, 4)))
        for v in vx]
    #vy2 = [((vgs_data @ id_data - 
    #    np.square(vgs_data - v) @ id_data * np.sum(np.power(vgs_data - v, 3)) / 
    #    np.sum(np.power(vgs_data - v, 4))) / np.sum(id_data))
    #    for v in vx]
    #vy3 = [(vgs_data @ id_data - np.sum(id_data) * v +
    #    np.square(vgs_data - v) @ id_data * np.sum(np.power(vgs_data - v, 3)) / 
    #    np.sum(np.power(vgs_data - v, 4)))]
        
    plt.plot(vx, vy1, color="r") 
    #plt.plot(vx, vy2, color="g") 
    #plt.plot(vx, vy3, color="b") 
    plt.xlabel(r"$v_t$")
    plt.ylabel(r"$p(v_t$)")
    plt.grid()
    plt.show()
    exit()
    
# Biseccion
va, vt = 0, 0
vb = args.init
while np.abs(va - vb) > 10 * np.finfo(float).eps * va:
    vt = (va + vb) / 2
    d = ((vgs_data - vt) @ id_data - 
        (np.square(vgs_data - vt) @ id_data / np.sum(np.power(vgs_data - vt, 4))) *
        np.sum(np.power(vgs_data - vt, 3))) 
    if d > 0:
        vb = vt
    elif d < 0:
        va = vt
    else:
        va = vb

k = id_data @ np.square(vgs_data - vt) / np.sum(np.power(vgs_data - vt, 4))
k2 = id_data @ (vgs_data - vt) / np.sum(np.power(vgs_data - vt, 3))

if np.abs(k - k2) > 10 * np.finfo(float).eps * k:
    print("fit invalid, try a different seed estimated from aux polynomial")
    exit()

gain_target = 10 ** (args.gain / 20)
vgsq = gain_target / (2 * k * args.rd) + vt
idq = k * (vgsq - vt) ** 2

print("k = {:3.3f} mA/V^2".format(k * 1000))
print("Vt = {:2.3f} V\n".format(vt))
print("Desired gain [{} dB]".format(args.gain))
print("Rd {}".format(args.rd))
print("Vgsq = {:3.3} V".format(vgsq))
print("Idq = {:2.4} mA".format(1000 * idq))

if args.plot:
    vgs = np.linspace(vgs_data[0], vgs_data[len(vgs_data) - 1], 1000)
    i_d = k * np.square(vgs - vt)
    
    plt.title(r"$K = {0:3.3f} mA/V^2, V_t = {1:2.3f}V$".format(k * 1000, vt))
    plt.xlabel(r"$v_t$")
    plt.ylabel(r"$i_d$")
    plt.grid()
    plt.plot(vgs_data, id_data, marker="o", linestyle=" ")
    plt.plot(vgs, i_d, linestyle="-")
    plt.show()
