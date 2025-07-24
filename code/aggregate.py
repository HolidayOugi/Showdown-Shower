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
import gc


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

    escaped_name_base = glob.escape(name_base)
    part_files = sorted(glob.glob(os.path.join(PARQUET_DIR, f"{escaped_name_base}_part*.parquet")))
    single_file_path = os.path.join(PARQUET_DIR, f"{name_base}.parquet")

    if not part_files and not os.path.exists(single_file_path):
        shutil.copy2(new_file_path, single_file_path)
        print(f"Copied file {name_base} to {new_file_path}")
    else:
        try:
            df_new = pd.read_parquet(new_file_path)

            latest_part = []

            if part_files:
                part_files.sort(
                    key=lambda p: int(re.search(r"_part(\d+)\.parquet$", p).group(1))
                )
                latest_part = part_files[-1]
                df_existing = pd.read_parquet(latest_part)
                print(f"Loaded the latest chunk: {os.path.basename(latest_part)} "
                      f"with {len(df_existing):,} rows.")
            else:
                df_existing = pd.read_parquet(single_file_path)
                print(f"Loaded single file: {name_base}.parquet, rows: {len(df_existing):,}")


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
            del df_new, df_existing
            gc.collect()
            base_path = os.path.join(PARQUET_DIR, name_base)
            escaped_base_path = glob.escape(base_path)
            if len(df_merged) > 200000:
                print(f"DataFrame has {len(df_merged)} rows, splitting into chunks.")
                chunk_size = 200000
                num_chunks = (len(df_merged) + chunk_size - 1) // chunk_size

                old_chunks = glob.glob(f"{escaped_base_path}_part*.parquet")
                print(old_chunks)
                if old_chunks:
                    old_chunks.sort(key=lambda p: int(re.search(r"_part(\d+)\.parquet$", p).group(1)))
                    last_file = old_chunks[-1]
                    last_part_num = int(re.search(r"_part(\d+)\.parquet$", last_file).group(1))
                    os.remove(last_file)
                    print(f"  → Removed old chunk: {os.path.basename(last_file)}")
                else:
                    last_part_num = 1
                start_index = last_part_num

                for i in range(num_chunks):
                    chunk = df_merged.iloc[i * chunk_size : (i + 1) * chunk_size]
                    chunk_file = f"{base_path}_part{start_index + i}.parquet"
                    chunk.to_parquet(chunk_file, index=False, engine='pyarrow', row_group_size=1000)
                    print(f"  → Saved chunk {start_index + i} to {os.path.basename(chunk_file)}")

                single_file = f"{base_path}.parquet"
                if os.path.exists(single_file):
                    os.remove(single_file)
                    print(f"  → Removed old single file: {os.path.basename(single_file)}")
            else:
                if part_files:
                    df_merged.to_parquet(latest_part, index=False, engine='pyarrow', row_group_size=1000)
                    print(f"Joined {filename} → {os.path.basename(latest_part)}")
                else:
                    df_merged.to_parquet(f"{base_path}.parquet", index=False, engine='pyarrow', row_group_size=1000)
                    print(f"Joined {filename} → {name_base}.parquet")
        except Exception as e:
            print(e)
            continue

os.makedirs(f"{OUTPUT_DIR}/tiers", exist_ok=True)

load_battle(NEW_DATA_DIR, f"{OUTPUT_DIR}/tiers")

part_files = glob.glob(os.path.join(f"{OUTPUT_DIR}/tiers", '*_part*.parquet'))

file_groups = {}
for f in part_files:
    base = os.path.basename(f).rsplit('_part', 1)[0]
    full_base = os.path.join(f"{OUTPUT_DIR}/tiers", base)
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

def combine_datasets(EXISTING_TIER_DIR, OUTPUT_DIR, parquet):

    if os.path.exists(f"{EXISTING_TIER_DIR}/{parquet}"):
        df_old = pd.read_parquet(f"{EXISTING_TIER_DIR}/{parquet}")
    else:
        df_old = pd.DataFrame()

    df_new = pd.read_parquet(f"{OUTPUT_DIR}/{parquet}")

    fmts = df_new['format'].unique()

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

    agg_df['win_rate'] = (agg_df['won']/(agg_df['won']+agg_df['lost']))*100

    usage_list = []

    for fmt in fmts:
        df_path = f'{EXISTING_TIER_DIR}/tiers/{fmt}.parquet'
        if os.path.exists(df_path):
            df_replays = pd.read_parquet(df_path)
            total_played = len(df_replays)
        else:
            pattern = glob.escape(f'{EXISTING_TIER_DIR}/tiers/{fmt}') + "_*.parquet"
            parts = sorted(glob.glob(pattern))

            if parts:
                part_dfs = [pd.read_parquet(part) for part in parts]
                df_replays = pd.concat(part_dfs, ignore_index=True)
                total_played = len(df_replays)
            else:
                continue

        df_fmt = agg_df[agg_df['format'] == fmt].copy()
        df_fmt['usage'] = (df_fmt['played'] / total_played) * 100
        usage_list.append(df_fmt)

    updated_formats = {df['format'].iloc[0] for df in usage_list if not df.empty}

    agg_df = agg_df[~agg_df['format'].isin(updated_formats)]

    agg_df = pd.concat([agg_df] + usage_list, ignore_index=True)

    agg_df['moves'] = agg_df['moves'].apply(lambda x: sorted(x) if isinstance(x, list) else x)
    agg_df['moves'] = agg_df['moves'].apply(lambda x: json.dumps(x))

    agg_df.to_parquet(f"{EXISTING_TIER_DIR}/{parquet}", index=False)

def combine_replays(EXISTING_TIER_DIR, OUTPUT_DIR):

    def aggregate_replays(replays_list):
        all_replays = []
        for lst in replays_list:
            if isinstance(lst, list):
                all_replays.extend([tuple(item) for item in lst])
        return all_replays

    for file in os.listdir(f'{OUTPUT_DIR}/replays'):
        if not os.path.exists(os.path.join(f'{EXISTING_TIER_DIR}/replays/{file}')):
            shutil.copy2(f'{OUTPUT_DIR}/replays/{file}', f'{EXISTING_TIER_DIR}/replays/{file}')
        else:
            if file.endswith(".parquet"):
                df_old = pd.read_parquet(f'{EXISTING_TIER_DIR}/replays/{file}')
                df_new = pd.read_parquet(f'{OUTPUT_DIR}/replays/{file}')
                df_old['replays'] = df_old['replays'].apply(lambda x: json.loads(x) if isinstance(x, str) else [])

                df_new['replays'] = df_new['replays'].apply(lambda x: json.loads(x) if isinstance(x, str) else [])
                dfs = pd.concat([df_old, df_new])
                dfs = dfs.groupby(['format'], as_index=False).agg({
                    'replays': aggregate_replays,
                })
                dfs['replays'] = dfs['replays'].apply(lambda lst: json.dumps([
                    (rid, ts.isoformat() if hasattr(ts, 'isoformat') else str(ts)) for rid, ts in lst
                ]) if isinstance(lst, list) else '[]')
                dfs.to_parquet(f'{EXISTING_TIER_DIR}/replays/{file}', index=False)


combine_datasets(EXISTING_TIER_DIR, OUTPUT_DIR, "pokemon.parquet")
combine_datasets(EXISTING_TIER_DIR, OUTPUT_DIR, "invalid_pokemon.parquet")
combine_replays(EXISTING_TIER_DIR, OUTPUT_DIR)

os.makedirs(f"{EXISTING_TIER_DIR}/players", exist_ok=True)
os.makedirs(f"{EXISTING_TIER_DIR}/matches", exist_ok=True)

format_list = [os.path.splitext(f)[0] for f in os.listdir(f"{OUTPUT_DIR}/tiers") if os.path.isfile(f"{OUTPUT_DIR}/tiers/{f}")]

load_players(f"{EXISTING_TIER_DIR}/tiers", f"{EXISTING_TIER_DIR}/players", format_list)
load_matches(f"{EXISTING_TIER_DIR}/tiers", f"{EXISTING_TIER_DIR}/matches", format_list)
precalculate(EXISTING_TIER_DIR, "../output/graphs", format_list)

if os.path.exists(OUTPUT_DIR):
    shutil.rmtree(OUTPUT_DIR)
    print(f"Removed OUTPUT_DIR: {OUTPUT_DIR}")

for file_path in glob.glob(os.path.join(NEW_DATA_DIR, "*")):
    try:
        os.remove(file_path)
        print(f"Deleted: {file_path}")
    except Exception as e:
        print(f"Failed to delete {file_path}: {e}")