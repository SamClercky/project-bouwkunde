import re
import sys

import pandas as pd

if __name__ == "__main__":
    fileName = sys.argv[1]
    df = pd.read_csv(fileName)

    # Remove empty index column
    del df["1"]
    # Remove first row with units
    df.drop([0], inplace=True)

    # Convert to float
    df.replace(to_replace=r',', value=r'.', regex=True, inplace=True)
    df = df.astype({
        "Time": float,
        "Displacement": float,
        "Force": float,
        "Strain 1": float},
        copy=False)

    print(df)
    print(df.dtypes)

    # Write to cleaned data
    df.to_csv("clean_csv/" + fileName.split('/')[-1])
