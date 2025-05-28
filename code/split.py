import pandas as pd

df = pd.read_csv('../input/battles_PARSED.csv')

for value, df2 in df.groupby('format'):
    df2.to_csv(f'../output/tiers/{value}.csv', index=False)