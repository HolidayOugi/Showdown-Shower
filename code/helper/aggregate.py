import os
import shutil
import pandas as pd
import numpy as np
import re

NEW_DATA_DIR = "../../input/new_data"
PARQUET_DIR = "../../input/parquet"

os.makedirs(PARQUET_DIR, exist_ok=True)

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