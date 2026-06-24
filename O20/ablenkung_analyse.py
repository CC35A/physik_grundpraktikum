import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit

# spezi palette
YELLOW = "#fcc72d"
ORANGE = "#ea6d3d"
RED = "#e03a3c"
MAGENTA = "#cb1f73"
BLUE = "#383a6b"

DELTA_ANGLE = 0.1 # deg

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

def sellmeier(lambda_um, B, C):
    # lambda is expected to be in micrometers to prevent overflow
    return np.sqrt(1.0 + (B * lambda_um**2) / (lambda_um**2 - C))

df = pd.read_csv("data/ablenkung_prisma_1.csv",sep=";",decimal=",")

df = df[["Farbe", "GelbL", "GelbR", "Rot", "Violett"]]

lambdas_nm = np.array([404.7, 435.8, 491.6, 546.1, 577.0, 623.4])
lambdas_um = lambdas_nm / 1000.0 # convert to micrometer

PHI_DEG = 59.15 # (260.2 - 141.9)/2
phi_rad = np.radians(PHI_DEG)

delta_deg = np.abs(df["GelbR"] - df["GelbL"]) / 2.0 # minimum deflection
delta_rad = np.radians(delta_deg)

# refractive index using snell's law
n_measured = np.sin((delta_rad + phi_rad) / 2.0) / np.sin(phi_rad / 2.0)

delta_delta_rad = np.radians(DELTA_ANGLE)

dn_ddelta = np.cos((delta_rad + phi_rad) / 2.0) / (2.0 * np.sin(phi_rad / 2.0))
n_err = np.abs(dn_ddelta) * delta_delta_rad

popt, pcov = curve_fit(sellmeier, lambdas_um, n_measured, p0=[1.1, 0.01])
B_fit, C_fit = popt

n_NaD = sellmeier(0.589, B_fit, C_fit)

fig, ax = plt.subplots(figsize=(8, 5))

x_line_um = np.linspace(0.38, 0.65, 300)
x_line_nm = x_line_um * 1000.0
y_line_fit = sellmeier(x_line_um, B_fit, C_fit)

ax.plot(
    x_line_nm,
    y_line_fit,
    color=BLUE,
    linestyle="-",
    linewidth=1.5,
    label=f"Sellmeier-Fit ($B={B_fit:.4f}, C={C_fit:.5f}\\,\\mu\\mathrm{{m}}^2$)",
    zorder=2,
)

ax.errorbar(
    lambdas_nm,
    n_measured,
    yerr=n_err,
    fmt="o",
    color=RED,
    ecolor=RED,
    elinewidth=1.2,
    capsize=3,
    markersize=5.5,
    label="Messdaten Prisma 1 mit $\\Delta n$",
    zorder=3,
)

ax.scatter(
    [589],
    [n_NaD],
    color=YELLOW,
    edgecolors=ORANGE,
    s=50,
    zorder=4,
)

top_ticks = [404.7, 435.8, 491.6, 546.1, 577.0, 589.0, 623.4]
top_labels = [
    "violett",
    "blau",
    "grün",
    "hellgrün",
    "gelb",
    r"$n_d$",
    "rot",
]

ax_top = ax.secondary_xaxis("top")
ax_top.set_xticks(top_ticks)

ax_top.set_xticklabels(top_labels, fontsize=9.5, rotation=35)
ax_top.set_xlabel(
    r"Emissionslinien $(\mathrm{Hg})$ und Referenz $(n_d)$", labelpad=8
)

for i, tick_label in enumerate(ax_top.get_xticklabels()):
    if i == 5:
        tick_label.set_color(ORANGE)
        tick_label.set_fontweight("bold")
    else:
        tick_label.set_color(MAGENTA)
        tick_label.set_fontstyle("italic")

ax.set_xlabel(r"Wellenlänge $\lambda$ $(\mathrm{nm})$")
ax.set_ylabel(r"Brechungsindex $n$")

ax.grid(True, which="both", linestyle="--", alpha=0.4)

plt.tight_layout()
plt.savefig("data/out/ablenkung_prisma_1.pdf")
plt.savefig("data/out/ablenkung_prisma_1.png")
plt.show()

print("WERTE PRISMA 1")
print(f"fit_B = {B_fit:.5f}")
print(f"fit_C = {C_fit:.7f} um^2")
print(f"589 nm: n = {n_NaD:.4f}\n")
print("Wertetabelle:")
for f, l, n, dn in zip(df["Farbe"], lambdas_nm, n_measured, n_err):
    print(f"  {f:10s} ({l:.1f} nm): n = {n:.4f} +- {dn:.4f}")