import pandas as pd
import os

df = pd.read_csv('../input/battles_PARSED.csv')

for value, df2 in df.groupby('format'):
    txt_file =  '../output/tiers/formats.txt'
    if not os.path.exists(txt_file):
        open(txt_file, 'w').close()
    path = f'../output/tiers/{value}.csv'
    df2.to_csv(path, index=False)
    with open(txt_file, 'r+') as f:
        existing_format = f.read().splitlines()
        if value not in existing_format:
            f.write(value + '\n')
    if os.path.getsize(path) >=  104857600 :
        chunksize = 350_000
        for i, chunk in enumerate(pd.read_csv(path, chunksize=chunksize)):
            out_path = f'../output/tiers/{value}_{i}.csv'
            chunk.to_csv(out_path, index=False)
        os.remove(path)
