import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import linregress

plt.style.use("classic")

def import_data(url: str) -> pd.DataFrame:
    df = pd.read_csv(url)

    # Clean data / normilize data
    del df["Unnamed: 0"]
    df["Displacement"] = df["Displacement"]/1000
    df["Force"] = df["Force"]*1000

    return df

def calc_E(df: pd.DataFrame, doorsnede: float, cut_off_point: int):
    x = df["Displacement"]
    y = df["Force"]/doorsnede

    plt.figure()
    plt.plot(x,y)

    x = x[:cut_off_point]
    y = y[:cut_off_point]
    plt.figure()
    plt.plot(x,y)

    slope, intercept, r, p, stderr = linregress(x,y)

    plt.figure()
    plt.plot(x,y)
    plt.plot(x, slope*x+intercept, "r-", label="gefitte lijn")
    plt.legend()

    return {
        "E-modulus": slope,
        "stderr": stderr
    }

