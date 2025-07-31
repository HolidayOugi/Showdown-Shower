from battles import load_battle
from pokemon import load_pokemon
from players import load_players
from tiers import load_matches
from precalculate import precalculate
import os
import pandas as pd
import glob
import gc

load_battle("../input/parquet", "../output/tiers")

part_files = glob.glob(os.path.join("../output/tiers", '*_part*.parquet'))

file_groups = {}
for f in part_files:
    base = os.path.basename(f).rsplit('_part', 1)[0]
    full_base = os.path.join("../output/tiers", base)
    file_groups.setdefault(full_base, []).append(f)

for base_path, files in file_groups.items():
    files.sort()
    df_list = [pd.read_parquet(f) for f in files]
    df_merged = pd.concat(df_list, ignore_index=True)
    df_merged.to_parquet(f"{base_path}.parquet", index=False, engine='pyarrow', row_group_size=1000)

    for f in files:
        os.remove(f)

    del df_list, df_merged
    gc.collect()

file_parquet =  glob.glob(os.path.join("../output/tiers", '*.parquet'))
os.makedirs("../output/tiers/top", exist_ok=True)
for f in file_parquet:
    df = pd.read_parquet(f)
    path = os.path.join("../output/tiers/top", os.path.basename(f))
    top_df = df.sort_values(by="views", ascending=False).head(1000)
    top_df.to_parquet(path, index=False, engine='pyarrow', row_group_size=1000)

load_pokemon("../input/parquet", "../output")
load_players("../output/tiers", "../output/players")
load_matches("../output/tiers", "../output/matches")
precalculate("../output", "../output/graphs")