import pandas as pd
import os
import glob

from tqdm import tqdm

def load_matches(input_folder, output_folder):

    formats = [
        os.path.splitext(f)[0]
        for f in os.listdir('../output/tiers')
        if f.endswith('.parquet')
    ]

    gens = sorted(
        set(f.split(']')[0].strip('[') for f in formats),
        key=lambda x: int(x.split()[1])
    )


    for gen in gens:
        match_series = []
        gen_formats = [g for g in formats if gen in g]
        for tier in tqdm(gen_formats, desc=f"Calculating matches of {gen}"):
            df_path = f'{input_folder}/{tier}.parquet'
            if os.path.exists(df_path):
                df = pd.read_parquet(df_path)

            else:
                pattern = glob.escape(f'{input_folder}/{tier}') + "_*.parquet"
                parts = sorted(glob.glob(pattern))

                if parts:
                    part_dfs = [pd.read_parquet(part) for part in parts]
                    df = pd.concat(part_dfs, ignore_index=True)
                else:
                    continue

            df['year_month'] = df['uploadtime'].dt.to_period('M')

            monthly_counts = df.groupby(['year_month']).size().reset_index(name='count')
            monthly_counts['format'] = tier

            match_series.append(monthly_counts)

        if match_series:
            df_agg = pd.concat(match_series)
            total_matches = df_agg.groupby(['year_month'])['count'].sum().reset_index(name='total')
            df_agg = df_agg.merge(total_matches, on=['year_month'])
            df_agg['percentage'] = (df_agg['count'] / df_agg['total']) * 100
            df_agg = df_agg.sort_values('year_month')
            df_agg.to_parquet(f'{output_folder}/{gen}_matches.parquet', index=False)