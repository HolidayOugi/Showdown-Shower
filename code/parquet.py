import pandas as pd
import glob

file_paths = sorted(glob.glob("../train-*-of-00011*"))

dfs = [pd.read_parquet(path) for path in file_paths]
df_full = pd.concat(dfs, ignore_index=True)

df_full.to_csv("../input/data.csv", index=False)