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

DELTA_ANGLE = 0.1 # deg

lookup_table = {
    "ablenkung_prisma_1": {
        "phi_deg": 59.15, # (260.2 - 141.9)/2
        "lambdas_nm": np.array([404.7, 435.8, 491.6, 546.1, 577.0, 623.4]),
        "top_ticks": [404.7, 435.8, 491.6, 546.1, 577.0, 589.0, 623.4],
        "top_labels": ["violett", "blau", "grün", "hellgrün", "gelb", r"$n_d$", "rot"],
    },
    "ablenkung_prisma_2": {
        "phi_deg": 60.55, # (261.7 - 140.6)/2
        "lambdas_nm": None,
        "top_ticks": [404.75, 435.8, 493.8, 546.1, 578.05, 589.0, 612.0, 671.0],
        "top_labels": ["violett", "blau", "grün", "hellgrün", "gelb", r"$n_d$", "rot", "rot"],
    },
}

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

for filename, config in lookup_table.items():
    file_path = f"data/{filename}.csv"

    if not os.path.exists(file_path):
        print(f"Überspringe {filename} - Datei nicht gefunden!")
        continue

    df = pd.read_csv(file_path, sep=";", decimal=",")  # read german csv notation
    df = df[["Farbe", "GelbL", "GelbR", "Rot", "Violett"]]

    if config["lambdas_nm"] is not None:
        lambdas_nm = config["lambdas_nm"]
    else:
        lambdas_nm = df["Farbe"].astype(float).values

    lambdas_um = lambdas_nm / 1000.0 # convert to micrometer

    PHI_DEG = config["phi_deg"]
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

    x_min_um = (lambdas_nm.min() - 15) / 1000.0
    x_max_um = (lambdas_nm.max() + 15) / 1000.0
    x_line_um = np.linspace(x_min_um, x_max_um, 300)
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

    x_pad = (lambdas_nm.max() - lambdas_nm.min()) * 0.05
    y_pad = (n_measured.max() - n_measured.min()) * 0.10

    ax.set_xlim(lambdas_nm.min() - x_pad, lambdas_nm.max() + x_pad)
    ax.set_ylim(n_measured.min() - y_pad, n_measured.max() + y_pad)

    left_limit, _ = ax.get_xlim()
    lower_limit, _ = ax.get_ylim()

    ax.vlines(
        589,
        ymin=lower_limit,
        ymax=n_NaD,
        color=ORANGE,
        linestyle=":",
        linewidth=1.2,
        alpha=0.9,
    )

    ax.hlines(
        n_NaD,
        xmin=left_limit,
        xmax=589,
        color=ORANGE,
        linestyle=":",
        linewidth=1.2,
        alpha=0.9,
    )

    n_NaD_str = f"{n_NaD:.4f}".replace(".", "{,}")
    ax.scatter(
        [589],
        [n_NaD],
        color=YELLOW,
        edgecolors=ORANGE,
        s=50,
        zorder=4,
        label=f"Na-D-Linie ($589\\,\\mathrm{{nm}} \\rightarrow n={n_NaD_str}$)",
    )

    y_span = n_measured.max() - n_measured.min()
    ax.text(
        591,
        lower_limit + y_span * 0.02,
        r"$\lambda = 589\,\mathrm{nm}$",
        color=ORANGE,
        fontsize=9.5,
        ha="left",
        va="bottom",
        zorder=5,
    )

    x_span = lambdas_nm.max() - lambdas_nm.min()
    ax.text(
        left_limit + x_span * 0.015,
        n_NaD + y_span * 0.01,
        f"$n = {n_NaD_str}$",
        color=ORANGE,
        fontsize=9.5,
        ha="left",
        va="bottom",
        fontweight="bold",
        zorder=5,
    )

    ax.yaxis.set_major_formatter(
        FuncFormatter(lambda y_val, _: f"{y_val:.3f}".replace(".", ","))
    )

    # top axis
    ax_top = ax.secondary_xaxis("top")
    ax_top.set_xticks(config["top_ticks"])
    ax_top.set_xticklabels(config["top_labels"], fontsize=9.5, rotation=35)
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
    plt.savefig(f"data/out/{filename}.pdf")
    plt.savefig(f"data/out/{filename}.png")
    plt.show()

    print(f"WERTE {filename.upper()}")
    print(f"fit_B = {B_fit:.5f}")
    print(f"fit_C = {C_fit:.7f} um^2")
    print(f"589 nm: n = {n_NaD:.4f}\n")
    print("Wertetabelle:")
    for f_raw, l, n_val, dn_val in zip(
            df["Farbe"], lambdas_nm, n_measured, n_err
    ):
        print(
            f"  {str(f_raw):10s} ({l:5.1f} nm): n = {n_val:.4f} +- {dn_val:.4f}"
        )