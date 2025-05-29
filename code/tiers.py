import pandas as pd
import os

formats = [
    os.path.splitext(f)[0]
    for f in os.listdir('../output/tiers')
    if f.endswith('.csv')
]

gens = sorted(
    set(f.split(']')[0].strip('[') for f in formats),
    key=lambda x: int(x.split()[1])
)


for gen in gens:
    match_series = []
    gen_formats = [g for g in formats if gen in g]
    print(gen_formats)
    for tier in gen_formats:
        df = pd.read_csv(f'../output/tiers/{tier}.csv', parse_dates=['uploadtime'])

        df['year_month'] = df['uploadtime'].dt.to_period('M')

        monthly_counts = df.groupby(['year_month']).size().reset_index(name='count')
        monthly_counts['format'] = tier

        match_series.append(monthly_counts)

    df_agg = pd.concat(match_series)
    total_matches = df_agg.groupby(['year_month'])['count'].sum().reset_index(name='total')
    df_agg = df_agg.merge(total_matches, on=['year_month'])
    df_agg['percentage'] = (df_agg['count'] / df_agg['total']) * 100
    df_agg = df_agg.sort_values('year_month')
    df_agg.to_csv(f'../output/matches/{gen}_matches.csv', index=False)