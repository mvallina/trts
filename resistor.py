import numpy as np

E24 = ([1.0, 1.1, 1.2, 1.3, 1.5, 1.6, 
        1.8, 2.0, 2.2, 2.4, 2.7, 3.0, 
        3.3, 3.6, 3.9, 4.3, 4.7, 5.1, 
        5.6, 6.2, 6.8, 7.5, 8.2, 9.1])
E96 = ([1.00, 1.02, 1.05, 1.07, 1.10, 1.13, 1.15, 1.18, 1.21, 
        1.24, 1.27, 1.30, 1.33, 1.37, 1.40, 1.43, 1.47, 1.50, 
        1.54, 1.58, 1.62, 1.65, 1.69, 1.74, 1.78, 1.82, 1.87, 
        1.91, 1.96, 2.00, 2.05, 2.10, 2.16, 2.21, 2.26, 2.32, 
        2.37, 2.43, 2.49, 2.55, 2.61, 2.67, 2.74, 2.80, 2.87, 
        2.94, 3.01, 3.09, 3.16, 3.24, 3.32, 3.40, 3.48, 3.57, 
        3.65, 3.74, 3.83, 3.92, 4.02, 4.12, 4.22, 4.32, 4.42, 
        4.53, 4.64, 4.75, 4.87, 4.99, 5.11, 5.23, 5.36, 5.49, 
        5.62, 5.76, 5.90, 6.04, 6.19, 6.34, 6.49, 6.65, 6.81,
        6.98, 7.15, 7.32, 7.50, 7.68, 7.87, 8.06, 8.25, 8.45, 
        8.66, 8.87, 9.09, 9.31, 9.53, 9.76])

def best_rdiv(vdd, vrel, ise96):
    eserie = E96 if ise96 else E24
    divd = sorted([(np.abs(vrel - vdd * R2 / (R1 + R2)), R1, R2) 
        for R1 in eserie for R2 in eserie], key = lambda x:x[0])
    return (divd[0][1], divd[0][2])

def nearest_r(resistor, ise96):
    if resistor <= 0:
        return 0
    eserie = E96 if ise96 else E24
    order = 10 ** np.floor(np.log10(resistor))
    resistors = sorted([(np.abs(resistor / order - R), R * order) 
        for R in eserie], key = lambda x:x[0])
    return int(resistors[0][1])

def r_str(resistor, ise96):
    if resistor >= 1e6:
        if ise96:
            return "{:.2f}".format(resistor / 1e6).rstrip("0").replace(".", "M")
        else:
            return "{:.1f}".format(resistor / 1e6).rstrip("0").replace(".", "M")
    elif resistor >= 1e3:
        if ise96:
            return "{:.2f}".format(resistor / 1e3).rstrip("0").replace(".", "K")
        else:
            return "{:.1f}".format(resistor / 1e3).rstrip("0").replace(".", "K")
    else:
        return "{:}R".format(resistor)
