import pandas as pd
import os

def clean_parquet_folder(folder):
    for filename in os.listdir(folder):
        if filename.endswith(".parquet"):
            filepath = os.path.join(folder, filename)
            try:
                df = pd.read_parquet(filepath)
                
                if "log" in df.columns:
                    before = len(df)
                    df = df[df["log"] != "N"]
                    after = len(df)
                    print(f"{filename}: {before} -> {after} rows")
                    
                    # sovrascrive il file
                    df.to_parquet(filepath, index=False)
                else:
                    print(f"{filename}: 'log' column not found, skipped")
            
            except Exception as e:
                print(f"Error with {filename}: {e}")

clean_parquet_folder("parquet")