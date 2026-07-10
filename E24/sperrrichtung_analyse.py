import pandas as pd
from matplotlib import pyplot as plt
import os
import numpy as np
from scipy.optimize import curve_fit
from matplotlib.ticker import FuncFormatter

# spezi palette
YELLOW = "#fcc72d"
ORANGE = "#ea6d3d"
RED = "#e03a3c"
MAGENTA = "#cb1f73"
BLUE = "#383a6b"

R_V = 10e6 # 10 megaohm resistance
U_accuracy_percent = 0.5 / 100
U_resolution = 0.01
U_digits = 2

I_accuracy_percent = 1.0 / 100
I_resolution = 0.01
I_digits = 3

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

    U_err = (np.abs(U_V) * U_accuracy_percent) + (U_digits * U_resolution)
    I_err = (np.abs(I_true) * I_accuracy_percent) + (I_digits * I_resolution)

    popt, pcov = curve_fit(
        real_diode_reverse,
        U_V,
        I_true,
        p0=[0.8, 10],
        sigma=I_err,
        absolute_sigma=True
    )

    I_s_fit, R_p_fit = popt

    perr = np.sqrt(np.diag(pcov))
    I_s_fit_err, R_p_fit_err = perr

    print(f"--- {ds['label']} ---")
    print(f"Sperrstrom I_s = {-I_s_fit:.3f} ± {I_s_fit_err:.3f} µA")
    print(f"Parallelwiderstand R_p = {R_p_fit:.2f} ± {R_p_fit_err:.2f} MΩ\n")

    U_line = np.linspace(U_V.min(), U_V.max(), 200)
    I_s_fit_line = real_diode_reverse(U_line, I_s_fit, R_p_fit)

    ax.errorbar(
        U_V,
        I_true,
        xerr=U_err,
        yerr=I_err,
        fmt="s",
        color=ds["color"],
        ecolor=ds["color"],
        elinewidth=1.2,
        capsize=3,
        markersize=5,
        label=f"{ds['label']} (Messdaten)",
        zorder=2
    )

    ax.plot(
        U_line,
        I_s_fit_line,
        color=ds["color_fit"],
        linestyle="--",
        linewidth=2,
        label=f"Fit ($I_S = {f'{I_s_fit:.2f}'.replace('.', ',')}\\,\\mu\\mathrm{{A}}$)"
    )

ax.set_xlabel(r"Spannung $U$ (V)")
ax.set_ylabel(r"Strom $I$ ($\mu$A)")

ax.yaxis.set_major_formatter(
    FuncFormatter(lambda y_val, _: f"{y_val:.2f}".replace(".", ","))
)

ax.grid(True, linestyle=":", alpha=0.6)
ax.legend(loc="best")
fig.tight_layout()

# output plot as file
output_path = f"data/out/Sperrrichtung-Kennlinie"

plt.savefig(f"{output_path}.pdf", format="pdf", bbox_inches="tight")
plt.savefig(f"{output_path}.png", format="png", bbox_inches="tight")

plt.show()
