import os
import pandas as pd
import gc
import glob

cartella = '../../input/parquet'
size = 1_000_000

file_parquet = [
    f for f in glob.glob(os.path.join(cartella, '*.parquet'))
    if not os.path.basename(f).endswith(tuple([f'_part{i}.parquet' for i in range(1, 100)]))
    and '_part' not in f
]

for file_path in file_parquet:
    try:
        df = pd.read_parquet(file_path)
        print(f"Read {file_path} with {len(df)} rows")

        if len(df) > size:
            print(f" → More than {size} rows, split...")
            num_chunks = (len(df) + size - 1) // size
            base_path = file_path.replace('.parquet', '')

            for i in range(num_chunks):
                chunk = df.iloc[i * size : (i + 1) * size]
                chunk_file = f"{base_path}_part{i+1}.parquet"
                chunk.to_parquet(chunk_file, index=False, engine='pyarrow', row_group_size=1000)
                print(f"    Saved {chunk_file} ({len(chunk)} rows)")

            os.remove(file_path)
            print(f"  ✅ Removed original file: {file_path}")
        else:
            print(f" → Don't need to split")

        del df
        gc.collect()

    except Exception as e:
        print(f"Error with file {file_path}: {e}")