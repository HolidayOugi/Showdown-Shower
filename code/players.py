import pandas as pd
import os

formats = [
    os.path.splitext(f)[0]
    for f in os.listdir('../output/tiers')
    if f.endswith('.csv')
]

players = []

for f in formats:
    df = pd.read_csv(f'../output/tiers/{f}.csv', parse_dates=['uploadtime'])
    df['rating'] = pd.to_numeric(df['rating'], errors='coerce')
    df1 = df[['player1', 'uploadtime', 'rating']].rename(columns={'player1': 'name'})
    df2 = df[['player2', 'uploadtime', 'rating']].rename(columns={'player2': 'name'})
    all_players = pd.concat([df1, df2], ignore_index=True)

    stats = all_players.groupby('name').agg(
        played=('name', 'count'),
        first_played=('uploadtime', 'min'),
        last_played=('uploadtime', 'max'),
        lowest_rating=('rating', 'min'),
        highest_rating=('rating', 'max'),
    )

    wins1 = df[df['Winner'] == df['player1']]['player1'].value_counts()
    wins2 = df[df['Winner'] == df['player2']]['player2'].value_counts()
    wins = wins1.add(wins2, fill_value=0).astype(int)

    losses1 = df[df['Winner'] == df['player2']]['player1'].value_counts()
    losses2 = df[df['Winner'] == df['player1']]['player2'].value_counts()
    losses = losses1.add(losses2, fill_value=0).astype(int)

    stats['wins'] = stats.index.map(wins).fillna(0).astype(int)
    stats['losses'] = stats.index.map(losses).fillna(0).astype(int)

    stats['format'] = f

    stats = stats.reset_index()[
        ['name', 'format', 'played', 'wins', 'losses', 'first_played', 'last_played', 'lowest_rating', 'highest_rating']]

    players.append(stats)

players_df = pd.concat(players, ignore_index=True)

players_df.to_csv('../output/players.csv', index=False)