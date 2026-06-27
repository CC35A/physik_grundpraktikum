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

def phasenverschiebung(f, f0, gamma):
    omega = 2 * np.pi * f
    omega0 = 2 * np.pi * f0

    phi = np.arctan2(gamma * omega, omega0**2 - omega**2) # formula for phase

    return np.degrees(phi)


fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(6, 6), sharex=True)

for ds in datasets:
    # read data
    df = pd.read_csv(ds["path"], sep=";", decimal=",")
    f_data = df["Frequenz"]
    A_data = df["Amplitude"]

    # fit
    f0_guess = f_data[np.argmax(A_data)]
    p0_guess = [max(A_data), f0_guess, 0.1]

    popt, pcov = curve_fit(
        resonanz_kurve,
        f_data,
        A_data,
        p0=p0_guess,
        sigma=np.full_like(A_data, DELTA_A),
        absolute_sigma=True,
        bounds=([0, 0, 0], [np.inf, np.inf, np.inf])
    )

    A_fit, f0_fit, gamma_fit = popt

    perr = np.sqrt(np.diag(pcov))
    A_err, f0_err, gamma_err = perr

    print(f"--- Ergebnisse für {ds['label']} ---")
    print(f"f0    = {f0_fit:.3f} +/- {f0_err:.3f} Hz")
    print(f"gamma = {gamma_fit:.3f} +/- {gamma_err:.3f}\n")

    # plot datapoints with errorbar
    ax1.errorbar(f_data, A_data, xerr=DELTA_f, yerr=DELTA_A, fmt='o', color=ds["color"], alpha=0.8, capsize=3, markersize=2, label=f"Messpunkt {ds["label"]}")

    # plot amplitude fit curve
    f_fit = np.linspace(min(f_data), max(f_data), 200)
    ax1.plot(f_fit, resonanz_kurve(f_fit, *popt),color=ds["color"], linestyle="--", label=f"Fit {ds['label']}")

    # plot phaseshift fit curve
    phi_fit = phasenverschiebung(f_fit, f0_fit, gamma_fit)
    ax2.plot(f_fit, phi_fit, color=ds["color"], linestyle="--", label=f"Fit {ds['label']}")

    # uncertainty propagation through sampling
    sample_params = np.random.multivariate_normal(popt, pcov, 1000)

    # params[1] is f0, params[2] is gamma
    phi_samples = np.array([phasenverschiebung(f_fit, params[1], params[2]) for params in sample_params])

    # one sigma rule
    phi_lower = np.percentile(phi_samples, 16, axis=0)
    phi_upper = np.percentile(phi_samples, 84, axis=0)

    ax2.fill_between(f_fit, phi_lower, phi_upper, color=ds["color"], alpha=0.4)

# styling for upper plot
#ax1.set_title("Resonanzkurvenvergleich")
ax1.set_xlabel("Frequenz $f$ (Hz)")
ax1.set_ylabel(r"Amplitude $A$ (LE)")
ax1.grid(True, linestyle=":", alpha=0.6) # grid lines for better visibility
ax1.legend(loc="best")   # show legend

# styling for lower plot
ax2.set_xlabel("Frequenz $f$ (Hz)")
ax2.set_ylabel(r"Phase $\phi$ (°)")
ax2.grid(True, linestyle=":", alpha=0.6) # grid lines for better visibility
ax2.axhline(90, color=BLUE, linestyle=":", alpha=0.8, label="Resonanz (90°)")
ax2.legend(loc="best")

fig.tight_layout()  # optimize layout

output_path = "data/out/Resonanzkurven_plot"

plt.savefig(f"{output_path}.pdf", format="pdf", bbox_inches="tight")
plt.savefig(f"{output_path}.png", format="png", bbox_inches="tight")

print(f"Grafik erfolgreich gespeichert unter: {output_path}")

plt.show()
