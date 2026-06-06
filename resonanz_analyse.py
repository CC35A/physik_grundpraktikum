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

# uncertainty guessing
DELTA_A = 0.1 # 0.5 * unit size
DELTA_f = 0.01 # Hz

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
    {"path": "./data/Resonanz_0_2A.csv", "label": "0,2 A", "color": MAGENTA},
    {"path": "./data/Resonanz_0_4A.csv", "label": "0,4 A", "color": ORANGE},
]


def resonanz_kurve(f, A, f0, gamma):
    return A / np.sqrt((f0 ** 2 - f ** 2) ** 2 + (gamma * f) ** 2)

fig, ax = plt.subplots(figsize=(6, 4))

for ds in datasets:
    # read data
    df = pd.read_csv(ds["path"], sep=";", decimal=",")
    f_data = df["Frequenz"]
    A_data = df["Amplitude"]

    # fit
    f0_guess = f_data[np.argmax(A_data)]
    p0_guess = [max(A_data), f0_guess, 0.1]

    popt, pcov = curve_fit(resonanz_kurve, f_data, A_data, p0=p0_guess, sigma=np.full_like(A_data, DELTA_A), absolute_sigma=True)

    perr = np.sqrt(np.diag(pcov))
    f0_fit, f0_err = popt[1], perr[1]

    print(f"Ergebnis für {ds['label']}: f0 = {f0_fit:.3f} +/- {f0_err:.3f} Hz")

    ax.errorbar(f_data, A_data, xerr=DELTA_f, yerr=DELTA_A, fmt='o', color=ds["color"], alpha=0.8, capsize=3, markersize=2, label=ds["label"])

    f_fit = np.linspace(min(f_data), max(f_data), 200)
    ax.plot(f_fit, resonanz_kurve(f_fit, *popt),
            color=ds["color"], linestyle="--", label=fr"Fit {ds['label']} ($\gamma={popt[2]:.2f}$)")


ax.set_title("Resonanzkurvenvergleich")
ax.set_xlabel("Frequenz $f$ [Hz]")
ax.set_ylabel(r"Amplitude $A$ [a.u.]")

ax.grid(True, linestyle=":", alpha=0.6) # grid lines for better visibility
ax.legend(loc="best")   # show legend
fig.tight_layout()  # optimize layout

output_path = "./data/out/Resonanzkurven_plot.pdf"
plt.savefig(output_path, format="pdf", bbox_inches="tight")
print(f"Grafik erfolgreich gespeichert unter: {output_path}")

plt.show()
