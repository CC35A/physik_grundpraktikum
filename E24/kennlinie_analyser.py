import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit
from matplotlib.ticker import FuncFormatter
import os

# spezi palette
YELLOW = "#fcc72d"
ORANGE = "#ea6d3d"
RED = "#e03a3c"
MAGENTA = "#cb1f73"
BLUE = "#383a6b"

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

datasets = [
    {"path": "./data/germanium.csv", "label": "Germanium-Diode", "color": ORANGE, "color_fit": RED},
    {"path": "./data/silizium.csv", "label": "Silizium-Diode", "color": MAGENTA, "color_fit": BLUE},
]

def linear_log_diode(U, m, ln_I_s):
    """Linearisierte Shockley-Gleichung: ln(I) = m * V + ln(I_s)"""
    return m * U + ln_I_s


fig, ax = plt.subplots(figsize=(8, 5))

for ds in datasets:
    if not os.path.exists(ds['path']):
        print(f"Überspringe {ds['path']} - Datei nicht gefunden!")
        continue

    df = pd.read_csv(ds['path'], sep=";", decimal=",") # read german csv notation
    df = df[["Messung", "Strom", "Spannung"]]

    U_mes = df["Spannung"].values
    I_mes = df["Strom"].values
    ln_I_mes = np.log(I_mes)

    popt, pcov = curve_fit(linear_log_diode, U_mes, ln_I_mes)
    m_fit, ln_I_fit = popt

    U_line = np.linspace(df["Spannung"].min(), df["Spannung"].max(), 200)

    ln_I_fit_line = linear_log_diode(U_line, m_fit, ln_I_fit)
    I_fit_line = np.exp(ln_I_fit_line)

    ax.scatter(
        df["Spannung"],
        df["Strom"],
        color=ds["color"],
        marker="s",
        label=ds["label"]
    )

    ax.plot(
        U_line,
        I_fit_line,
        color=ds["color_fit"],
        linestyle="--",
        linewidth=2,
        label=f"{ds["label"]} - Linear Fit"
    )

ax.grid(True)
ax.set_xlabel("Spannung $U$ (mV)")
ax.set_ylabel("Stromstärke $I$ (µA)")

plt.yscale("log")

plt.legend(loc="best")
plt.tight_layout()

# output plot as file
output_path = f"data/out/Dioden_Kennlinie"

plt.savefig(f"{output_path}.pdf", format="pdf", bbox_inches="tight")
plt.savefig(f"{output_path}.png", format="png", bbox_inches="tight")

plt.show()

