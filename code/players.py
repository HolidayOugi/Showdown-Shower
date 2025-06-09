import pandas as pd
import os
from collections import defaultdict, Counter

formats = [
    os.path.splitext(f)[0]
    for f in os.listdir('../output/tiers')
    if f.endswith('.csv')
]

for f in formats:
    df = pd.read_csv(f'../output/tiers/{f}.csv', parse_dates=['uploadtime'])
    df['rating'] = pd.to_numeric(df['rating'], errors='coerce')
    df['Team 1'] = df['Team 1'].apply(eval)
    df['Team 2'] = df['Team 2'].apply(eval)
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

    valid_ratings = all_players.dropna(subset=['rating'])
    rating_lists = valid_ratings.sort_values('uploadtime').groupby('name')['rating'].apply(list)

    stats['rating_list'] = stats.index.map(rating_lists)

    wins1 = df[df['Winner'] == df['player1']]['player1'].value_counts()
    wins2 = df[df['Winner'] == df['player2']]['player2'].value_counts()
    wins = wins1.add(wins2, fill_value=0).astype(int)

    losses1 = df[df['Winner'] == df['player2']]['player1'].value_counts()
    losses2 = df[df['Winner'] == df['player1']]['player2'].value_counts()
    losses = losses1.add(losses2, fill_value=0).astype(int)

    stats['wins'] = stats.index.map(wins).fillna(0).astype(int)
    stats['losses'] = stats.index.map(losses).fillna(0).astype(int)

    pokemon_counts = defaultdict(Counter)

    for _, row in df.iterrows():
        for player_col, team_col in [('player1', 'Team 1'), ('player2', 'Team 2')]:
            player = row[player_col]
            team = row[team_col]
            if isinstance(team, list):
                pokemon_counts[player].update(team)

    stats['pokemon_used'] = stats.index.map(lambda name: dict(pokemon_counts[name]))

    stats['format'] = f

    stats = stats.reset_index()[
        ['name', 'format', 'played', 'wins', 'losses', 'first_played', 'last_played', 'lowest_rating', 'highest_rating', 'rating_list', 'pokemon_used']]

    stats.to_csv(f'../output/players/{f}_players.csv', index=False)