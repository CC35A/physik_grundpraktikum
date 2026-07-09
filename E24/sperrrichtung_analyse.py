import pandas as pd
from matplotlib import pyplot as plt
import os
import numpy as np
from scipy.optimize import curve_fit

# spezi palette
YELLOW = "#fcc72d"
ORANGE = "#ea6d3d"
RED = "#e03a3c"
MAGENTA = "#cb1f73"
BLUE = "#383a6b"

R_V = 10e6 # 10 megaohm resistance

# LaTeX config for matplotlib
plt.rcParams.update(
    {
        "font.family": "serif",
        "font.size": 11,
        "axes.labelsize": 11,
        "axes.titlesize": 12,
        "xtick.labelsize": 9,
        "ytick.labelsize": 9,
        "legend.fontsize": 9,
        "mathtext.fontset": "cm",  # 'computer modern' font for math
    }
)

def shockley_equation(U, m, I_s):
    return I_s * (np.exp(U * m) - 1)

def real_diode_reverse(U, I_s, R_p):
    return -I_s + (U / R_p)

datasets = [
    {"path": "./data/germanium_sperrrichtung.csv", "label": "Germanium-Diode", "color": ORANGE, "color_fit": RED},
    {"path": "./data/silizium_sperrrichtung.csv", "label": "Silizium-Diode", "color": MAGENTA, "color_fit": BLUE},
]

fig, ax = plt.subplots(figsize=(8, 5))

for ds in datasets:
    if not os.path.exists(ds['path']):
        print(f"Überspringe {ds['path']} - Datei nicht gefunden!")
        continue

    df = pd.read_csv(ds['path'], sep=";", decimal=",")  # read german csv notation
    df = df[["Messung", "Strom", "Spannung"]]

    U_mes = df["Spannung"].values
    I_mes = df["Strom"].values

    U_V = U_mes / 1000
    I_err_A = U_V / R_V

    I_err_uA = I_err_A * 1e6

    I_true = I_mes - I_err_uA

    popt, pcov = curve_fit(real_diode_reverse, U_mes, I_true, p0=[0.8, 5000])

    I_s_fit, R_p_fit = popt
    U_line = np.linspace(df["Spannung"].min(), df["Spannung"].max(), 200)
    I_s_fit_line = real_diode_reverse(U_line, I_s_fit, R_p_fit)

    ax.scatter(
        U_mes,
        I_true,
        color=ds["color"],
        marker="s",
        label=ds["label"],
    )

    ax.plot(
        U_line,
        I_s_fit_line,
        color=ds["color_fit"],
        linestyle="--",
        linewidth=2,
        label=f"{ds["label"]} - Linear Fit"
    )

ax.grid(True)
ax.legend(loc="best")
fig.tight_layout()
plt.show()
