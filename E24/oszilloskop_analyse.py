import os
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
from matplotlib.colors import LogNorm

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
        "mathtext.fontset": "cm",
    }
)

datasets = [
    {"path": "./data/LED_ROT.csv", "label": "Kennlinie LED Rot", "export_name": "LED_ROT_plot", "cmap": "inferno"},
    {"path": "./data/LED_BLAU.csv", "label": "Kennlinie LED Blau", "export_name": "LED_BLAU_plot",  "cmap": "viridis"},
    {"path": "./data/Zener.csv", "label": "Kennlinie Zener Diode", "export_name": "Zener_plot",  "cmap": "ocean"}
]

R_MESS = 1000.0  # Ohm

for ds in datasets:
    file_path = ds["path"]
    if not os.path.exists(file_path):
        print(f"Fehler: Datei '{file_path}' nicht gefunden.")
        continue

    df = pd.read_csv(file_path, skiprows=12, names=["Zeit_s", "CH1_V", "CH2_V"], engine="c")

    window_time = 1000
    df["CH1_smooth"] = df["CH1_V"].rolling(window=window_time, center=True).mean()
    df["CH2_smooth"] = df["CH2_V"].rolling(window=window_time, center=True).mean()

    df_heatmap = df.dropna()
    U_heatmap = df_heatmap["CH1_smooth"]
    I_heatmap_mA = (df_heatmap["CH2_smooth"] / R_MESS) * 1000.0

    fig, ax = plt.subplots(figsize=(8, 5))

    h = ax.hist2d(
        U_heatmap,
        I_heatmap_mA,
        bins=[400, 300],
        cmap=ds["cmap"],
        norm=LogNorm(),
        rasterized=True,
        zorder=1
    )

    cbar = fig.colorbar(h[3], ax=ax, pad=0.02)
    cbar.set_label("Anzahl der Messpunkte (log)", rotation=270, labelpad=15)

    ax.axhline(0, color='white', linewidth=0.8, linestyle='-', alpha=0.5, zorder=2)
    ax.axvline(0, color='white', linewidth=0.8, linestyle='-', alpha=0.5, zorder=2)

    ax.xaxis.set_major_locator(MultipleLocator(2.0))
    ax.yaxis.set_major_locator(MultipleLocator(2.0))
    ax.xaxis.set_minor_locator(MultipleLocator(0.4))
    ax.yaxis.set_minor_locator(MultipleLocator(0.4))

    ax.grid(True, which="major", linestyle="-", alpha=0.4, color="grey", zorder=2)
    ax.grid(True, which="minor", linestyle=":", alpha=0.2, color="grey", zorder=2)

    ax.set_xlabel(r"Spannung $U$ (V)")
    ax.set_ylabel(r"Strom $I$ (mA)")

    u_min, u_max = U_heatmap.min(), U_heatmap.max()
    i_min, i_max = I_heatmap_mA.min(), I_heatmap_mA.max()

    u_pad = (u_max - u_min) * 0.1
    i_pad = (i_max - i_min) * 0.1

    ax.set_xlim(u_min - u_pad, u_max + u_pad)
    ax.set_ylim(i_min - i_pad, i_max + i_pad)

    fig.tight_layout()

    output_dir = "data/out"
    os.makedirs(output_dir, exist_ok=True)
    export_name = ds["export_name"]

    plt.savefig(f"{output_dir}/{export_name}.pdf", format="pdf", bbox_inches="tight", dpi=300)
    plt.savefig(f"{output_dir}/{export_name}.png", format="png", bbox_inches="tight", dpi=300)

    print(f"Gespeichert unter {output_dir}/{export_name}.png")
    plt.show()
