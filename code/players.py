import pandas as pd
import os
from collections import defaultdict, Counter
import json
import numpy as np
import glob
from tqdm import tqdm


def load_players(input_folder, output_folder, format_list=None):
    if format_list is None:
        with open('../input/formats.txt', 'r') as f:
            formats = [line.strip() for line in f if line.strip()]
    else:
        formats = format_list

    for f in formats:
        df_path = f'{input_folder}/{f}.parquet'
        if os.path.exists(df_path):
            df = pd.read_parquet(df_path)

        else:
            pattern = glob.escape(f'{input_folder}/{f}') + "_*.parquet"
            parts = sorted(glob.glob(pattern))

            if parts:
                part_dfs = [pd.read_parquet(part) for part in parts]
                df = pd.concat(part_dfs, ignore_index=True)
            else:
                continue
        df['rating'] = pd.to_numeric(df['rating'], errors='coerce')
        df['Team 1'] = df['Team 1'].apply(lambda x: list(x) if isinstance(x, (list, np.ndarray)) else x)
        df['Team 2'] = df['Team 2'].apply(lambda x: list(x) if isinstance(x, (list, np.ndarray)) else x)
        df['id_upload'] = list(zip(df['id'], df['uploadtime']))
        df1 = df[['player1', 'uploadtime', 'rating', 'id_upload']].rename(columns={'player1': 'name'})
        df2 = df[['player2', 'uploadtime', 'rating', 'id_upload']].rename(columns={'player2': 'name'})
        all_players = pd.concat([df1, df2], ignore_index=True)

        stats = all_players.groupby('name').agg(
            played=('name', 'count'),
            first_played=('uploadtime', 'min'),
            last_played=('uploadtime', 'max'),
            lowest_rating=('rating', 'min'),
            highest_rating=('rating', 'max'),
            replays=('id_upload', list)
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



        for _, row in tqdm(df.iterrows(), total=len(df), desc=f"Processing players for {f}"):
            for player_col, team_col in [('player1', 'Team 1'), ('player2', 'Team 2')]:
                player = row[player_col]
                team = row[team_col]
                if isinstance(team, list):
                    pokemon_counts[player].update(team)

        stats['pokemon_used'] = stats.index.map(lambda name: dict(pokemon_counts[name]))
        stats['pokemon_used'] = stats['pokemon_used'].apply(lambda x: json.dumps(x) if isinstance(x, dict) else '{}')
        stats['replays'] = stats['replays'].apply(lambda lst: json.dumps([
            (rid, ts.isoformat() if hasattr(ts, 'isoformat') else str(ts)) for rid, ts in lst
        ]) if isinstance(lst, list) else '[]')

        stats['format'] = f

        stats = stats.reset_index()[
            ['name', 'format', 'played', 'wins', 'losses', 'first_played', 'last_played', 'lowest_rating', 'highest_rating', 'rating_list', 'pokemon_used', 'replays']]


        os.makedirs(f'{output_folder}/{f}', exist_ok=True)
        base_path = f'{output_folder}/{f}/{f}_players'

        if len(stats) > 20000:

            chunk_size = 20000
            num_chunks = (len(stats) + chunk_size - 1) // chunk_size
            for i in range(num_chunks):
                chunk = stats.iloc[i * chunk_size: (i + 1) * chunk_size]
                chunk_file = f"{base_path}_part{1 + i:02}.parquet"
                chunk.to_parquet(chunk_file, index=False, engine='pyarrow', row_group_size=1000)

            single_file = f"{base_path}.parquet"
            if os.path.exists(single_file):
                os.remove(single_file)

        else:
            stats.to_parquet(f'{base_path}.parquet', index=False)

        stats_sorted = stats.sort_values(by='played', ascending=False)
        top100 = stats_sorted.head(100)
        top100.to_parquet(f'{base_path}_top100.parquet', index=False)