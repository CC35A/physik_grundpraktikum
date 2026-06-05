import os
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from scipy.signal import find_peaks
from scipy.optimize import curve_fit

# spezi palette
YELLOW = "#fcc72d"
ORANGE = "#ea6d3d"
RED = "#e03a3c"
MAGENTA = "#cb1f73"
BLUE = "#383a6b"

# camera calibration
PX_TO_CM = 1 / 32.0
DELTA_X = 2.8 * PX_TO_CM # = 0.04375 cm
DELTA_Y = 2.8 * PX_TO_CM # = 0.04375 cm

lookup_table = {
    "Schwingung.csv": {
        "title": "Schwingungsverlauf ungedämpft",
        "t1": 0.0, # 30.0,
        "t2": 0.0  # 60.0
    },
    "0.2ASchwingung.csv": {
        "title": "Schwingungsverlauf gedämpft ($I = 0,2\\,$A)",
        "t1": 0.0, # 15.0,
        "t2": 0.0  # 30.0
    },
    "0.4ASchwingung.csv": {
        "title": "Schwingungsverlauf gedämpft ($I = 0,4\\,$A)",
        "t1": 0.0, # 5.0,
        "t2": 0.0  # 15.0
    }
}

for filename, config in lookup_table.items():
    file_path = f"./data/{filename}"

    if not os.path.exists(file_path):
        print(f"Überspringe {filename} - Datei nicht gefunden!")
        continue

    plot_title = config["title"]
    t1 = config["t1"]
    t2 = config["t2"]

    df = pd.read_csv(file_path, sep=";", decimal=",") # read german csv notation
    df = df.dropna(how="all", axis=1) # fix german csv notation
    df.columns = df.columns.str.strip() # clean column titles

    if t2 == 0:
        t2 = df["Zeit [s]"].max()

    # calculate angle of deflection
    df["Winkel [Grad]"] = np.degrees(
        np.arctan(df["X Position [cm]"] / df["Y Position [cm]"])
    )

    # propagation of uncertainty using gaussian formula
    x = df["X Position [cm]"]
    y = df["Y Position [cm]"]
    delta_phi_rad = (1 / (x**2 + y**2)) * np.sqrt((y * DELTA_X)**2 + (x * DELTA_Y)**2)
    df["Fehler Winkel [Grad]"] = np.degrees(delta_phi_rad) # insert as new column in pd DataFrame

    # find peaks, 'prominence' filters noise
    peaks, _ = find_peaks(df["Winkel [Grad]"], prominence=3)

    t_peaks = df["Zeit [s]"].iloc[peaks].values
    phi_peaks = df["Winkel [Grad]"].iloc[peaks].values

    # calculate exponential envelope
    def exp_decay(t, phi_0, delta):
        """Exponentielle Abklingfunktion: phi(t) = phi_0 * e^(-delta * t)"""
        return phi_0 * np.exp(-delta * t)

    # curve_fit finds optimal parameters (popt) for phi_0 and delta and return uncertainty matrix (pcov)
    popt, pcov = curve_fit(exp_decay, t_peaks, phi_peaks, p0=[max(phi_peaks), 0.1])
    phi_0_fit, delta_fit = popt

    # root of diagonal of uncertainty matrix
    perr = np.sqrt(np.diag(pcov))
    phi_0_err = perr[0]
    delta_err = perr[1] # TODO: proper explanation

    # calculate logarithmic decrement
    T_mean = np.mean(np.diff(t_peaks))
    lambda_calc = delta_fit * T_mean

    # print results
    print(f"--- ERGEBNISSE FÜR {file_path} ---")
    print(f"Abklingkonstante (delta): {delta_fit:.4f} ± {delta_err:.4f} 1/s")
    print(f"Mittlere Periodendauer (T): {T_mean:.4f} s")
    print(f"Logarithmisches Dekrement (Lambda): {lambda_calc:.4f}")
    print("-" * 35)

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

    # make plot, define size in inches
    fig, ax = plt.subplots(figsize=(6, 4))

    # plot angle data
    ax.plot(
        df["Zeit [s]"],
        df["Winkel [Grad]"],
        label=r"$\varphi(t)$ (Auslenkwinkel)",
        color=BLUE,
        linewidth=0.5,
        marker=".",
        markersize=1,
    )

    # fill in range of uncertainty
    ax.fill_between(
        df["Zeit [s]"],
        df["Winkel [Grad]"] - df["Fehler Winkel [Grad]"],
        df["Winkel [Grad]"] + df["Fehler Winkel [Grad]"],
        color=YELLOW,
        alpha=0.5,
        label="Messunsicherheit"
    )

    # plot peaks
    ax.plot(
        t_peaks,
        phi_peaks,
        "x",
        color=RED,
        label="Extremwerte (Peaks)",
        markersize=6
    )

    # plot envelope
    t_fit = np.linspace(min(df["Zeit [s]"]), max(df["Zeit [s]"]), 500)
    ax.plot(
        t_fit,
        exp_decay(t_fit, phi_0_fit, delta_fit),
        label=r"Fit",
        color=MAGENTA,
        linestyle="--",
        linewidth=1.5
    )

    # axis labels
    ax.set_xlabel("Zeit $t$ [s]")
    ax.set_ylabel(r"Auslenkwinkel $\varphi$ [°]")
    ax.set_title(plot_title)

    # zoom
    ax.set_xlim(t1, t2)
    mask_zoom = (df["Zeit [s]"] >= t1) & (df["Zeit [s]"] <= t2)

    if mask_zoom.any():
        # find max and min angle in mask
        y_max = df.loc[mask_zoom, "Winkel [Grad]"].max()
        y_min = df.loc[mask_zoom, "Winkel [Grad]"].min()
        puffer = (y_max - y_min) * 0.1  # calculate 10% puffer to better see plot
        ax.set_ylim(y_min - puffer, y_max + puffer) # set new y limit

    ax.grid(True, linestyle=":", alpha=0.6) # grid lines for better visibility
    ax.legend(loc="best")   # show legend
    fig.tight_layout()  # optimize layout

    # output plot as file
    export_name = filename.replace(".csv", "_plot.pdf")
    output_path = f"./data/{export_name}"

    plt.savefig(output_path, format="pdf", bbox_inches="tight")

    print(f"Grafik erfolgreich gespeichert unter: {output_path}")
    plt.show()
    plt.close(fig)