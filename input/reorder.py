import pandas as pd
import os
import re
from collections import defaultdict
import gc

def repartition_all(folder, chunk_size=200000):
    groups = defaultdict(list)
    for filename in os.listdir(folder):
        if filename.endswith(".parquet"):
            match = re.match(r"^(.*)_part\d+\.parquet$", filename)
            if match:
                prefix = match.group(1)
            else:
                prefix = filename.replace(".parquet", "")
            groups[prefix].append(filename)
    
    for prefix, files in groups.items():
        files = sorted(
            files, 
            key=lambda x: int(re.search(r"_part(\d+)", x).group(1)) if "_part" in x else 0
        )
        print(f"Joining {len(files)} files for '{prefix}'")

        dfs = []
        for f in files:
            filepath = os.path.join(folder, f)
            dfs.append(pd.read_parquet(filepath))
        big_df = pd.concat(dfs, ignore_index=True)
        before = len(big_df)
        big_df = big_df.drop_duplicates(subset=["id"], ignore_index=True)
        after = len(big_df)
        if after < before:
            print(f"  -> Removed {before - after} duplicates")
        total = after
        print(f"Total rows {prefix}: {total}")

        num_parts = (total + chunk_size - 1) // chunk_size
        for i in range(num_parts):
            start = i * chunk_size
            end = min((i + 1) * chunk_size, total)
            part_df = big_df.iloc[start:end]
            if num_parts == 1:
                outname = f"{prefix}.parquet"
            else:
                outname = f"{prefix}_part{i+1}.parquet"
            outpath = os.path.join(folder, outname)
            part_df.to_parquet(outpath, index=False, engine='pyarrow', row_group_size=1000)
            print(f"  -> Saved {outname}: {len(part_df)} rows")
        del big_df, dfs, part_df
        gc.collect()


repartition_all("parquet", chunk_size=200000)