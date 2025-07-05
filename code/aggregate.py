import os
import pandas as pd
from battles import load_battle
from pokemon import load_pokemon
from players import load_players
from tiers import load_matches
from precalculate import precalculate
import json
from collections import Counter
import glob
import shutil
import re
import numpy as np


NEW_DATA_DIR = "../input/new_data"
PARQUET_DIR = "../input/parquet"
OUTPUT_DIR = "../output/new_data"
EXISTING_TIER_DIR = "../output"

os.makedirs(OUTPUT_DIR, exist_ok=True)

for filename in os.listdir(NEW_DATA_DIR):
    if not filename.endswith(".parquet"):
        continue

    new_file_path = os.path.join(NEW_DATA_DIR, filename)
    name_base = filename.replace(".parquet", "")

    matches = [
        f for f in os.listdir(PARQUET_DIR)
        if f.endswith(".parquet") and f.startswith(name_base)
    ]

    if not matches:
        shutil.move(new_file_path, os.path.join(PARQUET_DIR, filename))
    else:
        target_file = matches[0]
        existing_file_path = os.path.join(PARQUET_DIR, target_file)
        try:
            df_new = pd.read_parquet(new_file_path)
            df_existing = pd.read_parquet(existing_file_path)


            def normalize_players(value):
                if isinstance(value, (list, np.ndarray)):
                    return [str(p).strip().strip('\'"').strip() for p in value]

                if isinstance(value, str):
                    value = value.strip().strip('[]').strip()
                    if not value:
                        return []
                    parts = re.split(r'\s*,\s*', value)
                    return [p.strip('\'" ').strip() for p in parts]

                return []


            df_new['players'] = df_new['players'].apply(normalize_players)
            df_new['format'] = os.path.splitext(filename)[0]
            df_existing['players'] = df_existing['players'].apply(normalize_players)
            df_merged = pd.concat([df_existing, df_new], ignore_index=True).drop_duplicates(subset='id')
            df_merged.to_parquet(existing_file_path, index=False)
            print(f"Joined {filename} → {target_file}")
        except Exception as e:
            print(e)
            continue

os.makedirs(f"{OUTPUT_DIR}/tiers", exist_ok=True)

load_battle(NEW_DATA_DIR, f"{OUTPUT_DIR}/tiers")


for filename in os.listdir(f"{OUTPUT_DIR}/tiers"):

    if not filename.endswith(".parquet"):
        continue

    new_file_path = os.path.join(f"{OUTPUT_DIR}/tiers", filename)
    existing_file_path = os.path.join(f"{EXISTING_TIER_DIR}/tiers", filename)

    try:
        new_df = pd.read_parquet(new_file_path)

        if os.path.exists(existing_file_path):
            existing_df = pd.read_parquet(existing_file_path)
            combined_df = pd.concat([existing_df, new_df], ignore_index=True)
        else:
            combined_df = new_df

        if "id" in combined_df.columns:
            combined_df = combined_df.drop_duplicates(subset="id")

        combined_df.to_parquet(existing_file_path, index=False)
        print(f"Saved: {existing_file_path}")

    except Exception as e:
        print(f"Error: {filename}: {e}")


load_pokemon(NEW_DATA_DIR, OUTPUT_DIR)

def combine_datasets(EXISTING_TIER_DIR, OUTPUT_DIR, PARQUET_DIR, parquet):

    if os.path.exists(f"{EXISTING_TIER_DIR}/{parquet}"):
        df_old = pd.read_parquet(f"{EXISTING_TIER_DIR}/{parquet}")
    else:
        df_old = pd.DataFrame()

    df_new = pd.read_parquet(f"{OUTPUT_DIR}/{parquet}")

    df = pd.concat([df_old, df_new], ignore_index=True)

    df['moves'] = df['moves'].apply(lambda x: json.loads(x) if isinstance(x, str) else x)

    def aggregate_moves(moves_list):
        total = Counter()
        for moves in moves_list:
            total.update(dict(moves))
        return list(total.items())

    agg_df = df.groupby(['pokemon', 'format'], as_index=False).agg({
        'played': 'sum',
        'won': 'sum',
        'lost': 'sum',
        'win_rate': 'mean',
        'usage': 'first',
        'moves': aggregate_moves,
        'Pdex': 'first',
        'Type 1': 'first',
        'Type 2': 'first',
        'Total': 'first',
        'HP': 'first',
        'Attack': 'first',
        'Defense': 'first',
        'Sp. Atk': 'first',
        'Sp. Def': 'first',
        'Speed': 'first'
    })

    agg_df["win_rate"] = agg_df["won"] / agg_df["played"] * 100

    usage_list = []

    for fmt in agg_df['format'].unique():
        df_path = f'{PARQUET_DIR}/{fmt}.parquet'
        if os.path.exists(df_path):
            df_replays = pd.read_parquet(df_path)
            total_played = len(df_replays)
        else:
            pattern = glob.escape(f'{PARQUET_DIR}/{fmt}.parquet') + "_*.parquet"
            parts = sorted(glob.glob(pattern))

            if parts:
                part_dfs = [pd.read_parquet(part) for part in parts]
                df_replays = pd.concat(part_dfs, ignore_index=True)
                total_played = len(df_replays)
            else:
                continue

        df_fmt = agg_df[agg_df['format'] == fmt].copy()
        df_fmt['total_format_played'] = total_played
        df_fmt['usage'] = (df_fmt['played'] / total_played) * 100
        usage_list.append(df_fmt)

    agg_df = pd.concat(usage_list, ignore_index=True)

    agg_df = agg_df.drop(columns='total_format_played')

    agg_df['moves'] = agg_df['moves'].apply(lambda x: sorted(x) if isinstance(x, list) else x)
    agg_df['moves'] = agg_df['moves'].apply(lambda x: json.dumps(x))

    agg_df.to_parquet(f"{EXISTING_TIER_DIR}/{parquet}", index=False)

combine_datasets(EXISTING_TIER_DIR, OUTPUT_DIR, PARQUET_DIR, "pokemon.parquet")
combine_datasets(EXISTING_TIER_DIR, OUTPUT_DIR, PARQUET_DIR, "invalid_pokemon.parquet")

os.makedirs(f"{EXISTING_TIER_DIR}/players", exist_ok=True)
os.makedirs(f"{EXISTING_TIER_DIR}/matches", exist_ok=True)

load_players(f"{EXISTING_TIER_DIR}/tiers", f"{EXISTING_TIER_DIR}/players")
load_matches(f"{EXISTING_TIER_DIR}/tiers", f"{EXISTING_TIER_DIR}/matches")
precalculate(EXISTING_TIER_DIR, "../graphs")

if os.path.exists(OUTPUT_DIR):
    shutil.rmtree(OUTPUT_DIR)
    print(f"Removed OUTPUT_DIR: {OUTPUT_DIR}")

for file_path in glob.glob(os.path.join(NEW_DATA_DIR, "*")):
    try:
        os.remove(file_path)
        print(f"Deleted: {file_path}")
    except Exception as e:
        print(f"Failed to delete {file_path}: {e}")