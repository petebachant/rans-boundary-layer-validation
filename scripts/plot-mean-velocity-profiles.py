"""Plot mean velocity profiles."""

import glob
import os

import h5py
import matplotlib.pyplot as plt
import pandas as pd

plt.style.use("seaborn-v0_8")


def read_profiles():
    """Read profile data from JHTDB HDF5 file, and assemble into a dictionary
    of NumPy arrays.
    """
    with h5py.File("data/jhtdb-profiles.h5", "r") as f:
        data = {}
        for k in f.keys():
            kn = k.split("_")[0]
            if kn.endswith("m"):
                kn = kn[:-1]
            data[kn] = f[k][()]
    # Correct fluctuation terms according to README
    # >uum is the time-averaged of u*u (not u'*u', where u'=u-um).
    # >So time-averaged of u'*u'=uum-um*um. Same for other quantities.
    for dim1 in ("u", "v", "w"):
        for dim2 in ("u", "v", "w"):
            if f"{dim1}{dim2}" in data:
                data[f"{dim1}{dim2}"] = (
                    data[f"{dim1}{dim2}"] - data[dim1] * data[dim2]
                )
    return data


if __name__ == "__main__":
    labels = {
        "laminar": "Laminar",
        "k-epsilon": r"$k$–$\epsilon$",
        "k-omega": r"$k$–$\omega$",
    }
    data = read_profiles()
    fig, ax = plt.subplots()
    ax.plot(data["u"][:, 1500], data["y"], linestyle="dashed", label="DNS")
    ax.legend()
    for turbulence_model in ["laminar", "k-epsilon", "k-omega"]:
        fpaths = glob.glob(
            f"cases/{turbulence_model}/postProcessing/sample/*/x906.8_U.csv"
        )
        assert len(fpaths) == 1
        df2 = pd.read_csv(fpaths[0])
        df2.plot(x="U_0", y="y", ax=ax, label=turbulence_model)
    ax.set_xlabel("$U$")
    ax.set_ylabel("$y$")
    os.makedirs("figures", exist_ok=True)
    fig.savefig("figures/mean-velocity-profiles.png")
