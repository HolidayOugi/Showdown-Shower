import pandas as pd
from collections import defaultdict, Counter
import re
import numpy as np
import os
from tqdm import tqdm
import json
def load_pokemon(input_folder, output_folder):

    def parse_log(log):
        lines = log.splitlines()

        winner = None
        team1 = set()
        team2 = set()
        moves_used = defaultdict(set)
        nickname_map = {}

        for line in lines:

            if line.startswith('|win|'):
                winner = line.split('|')[2]

            elif line.startswith('|poke|p1|'):
                species = line.split('|')[3].split(',')[0].strip()
                species = species.replace('’', "'")
                team1.add(species.title())

            elif line.startswith('|poke|p2|'):
                species = line.split('|')[3].split(',')[0].strip()
                species = species.replace('’', "'")
                team2.add(species.title())

            elif line.startswith('|switch|p1a:') or line.startswith('|switch|p2a:'):
                match = re.match(r'\|switch\|(p[12]a): ([^|]+)\|([^|,]+)', line)

                if match:
                    player_slot = match.group(1)
                    nickname = match.group(2).strip().lower()
                    species = match.group(3).strip()
                    nickname_map[nickname] = species.title()
                    if player_slot == 'p1a':
                        team1.add(species.title())
                    else:
                        team2.add(species.title())


            elif line.startswith('|move|'):
                match = re.match(r'\|move\|p[12]a: ([^|]+)\|([^|]+)\|', line)

                if match:
                    nickname = match.group(1).strip().lower()
                    move = match.group(2).strip().title()
                    species = nickname_map.get(nickname, nickname)
                    moves_used[species].add(move)


        return winner, team1, team2, moves_used


    def pokemon_dataframe(df_logs):
        rows = []

        def normalize_players(value):
            if isinstance(value, (list, np.ndarray)):
                return [str(p).strip().strip('\'"').strip() for p in value]

            if isinstance(value, str):
                value = value.strip().strip('[]').strip()
                if not value:
                    return []
                parts = re.split(r'\s*,\s*', value)
                return [p.strip('\'" ').strip() for p in parts]

            return []

        df_logs['players'] = df_logs['players'].apply(normalize_players)
        df_logs['player1'] = df_logs['players'].apply(lambda x: x[0] if len(x) > 0 else None)
        df_logs['player2'] = df_logs['players'].apply(lambda x: x[1] if len(x) > 1 else None)
        df_logs = df_logs.drop(columns=['players', 'formatid'])

        for _, row in tqdm(df_logs.iterrows(), total=len(df_logs), desc="Parsing logs"):
            log = row['log']
            winner, team1, team2, moves_used = parse_log(log)
            all_pokemon = team1.union(team2)
            for mon in all_pokemon:
                rows.append({
                    'pokemon': mon,
                    'format': row['format'],
                    'played': 1,
                    'won': int(winner == row['player1'] and mon in team1) or int(
                        winner == row['player2'] and mon in team2),
                    'lost': int(winner == row['player2'] and mon in team1) or int(
                        winner == row['player1'] and mon in team2),
                    'moves': Counter(moves_used.get(mon, [])),
                    'replays': (row['id'], row['uploadtime'])
                })

        df_help = pd.DataFrame(rows)
        df_help['pokemon'] = df_help['pokemon'].str.replace("’", "'", regex=False)

        def merge_counters(series):
            total_counters = Counter()
            for c in series:
                if isinstance(c, Counter):
                    total_counters.update(c)
            return sorted(total_counters.items(), key=lambda x: (-x[1], x[0]))

        def collect_replays(series):
            return list(series)

        df_new = df_help.groupby(['pokemon', 'format']).agg({
            'played': 'sum',
            'won': 'sum',
            'lost': 'sum',
            'moves': merge_counters,
            'replays': collect_replays
        }).reset_index()

        df_new['replays'] = df_new['replays'].apply(lambda lst: json.dumps([
            (rid, ts.isoformat() if hasattr(ts, 'isoformat') else str(ts)) for rid, ts in lst
        ]) if isinstance(lst, list) else '[]')
        df_new = df_new.sort_values(by=['pokemon', 'format']).reset_index(drop=True)
        df_new['moves'] = df_new['moves'].apply(lambda x: sorted(x) if isinstance(x, list) else x)
        df_new['moves'] = df_new['moves'].apply(lambda x: json.dumps(x))
        df_new['win_rate'] = (df_new['won']/(df_new['won']+df_new['lost']))*100
        df_stats = pd.read_csv('../input/pokemon_stats.csv', dtype={
            'Pdex': str,
            'Hp': int,
            'Attack': int,
            'Defense': int,
            'Sp. Atk': int,
            'Sp. Def': int,
            'Speed': int
        })
        df_new = pd.merge(df_new, df_stats, on='pokemon', how='left')

        return df_new


    def filter_pokemon(pokemon_df):
        invalid_pokemon = pd.DataFrame()

        for gen in range(1, 10):
            gen_label = f'[Gen {gen}]'
            valid_file = f'../input/gen_filter/gen{gen}.txt'

            if not os.path.exists(valid_file):
                continue

            with open(valid_file, 'r', encoding='utf-8') as f:
                valid_pokemon = set(name.strip().lower() for name in f if name.strip())

            mask = pokemon_df['format'].str.startswith(gen_label, na=False)
            df_gen = pokemon_df[mask]

            is_valid = df_gen['pokemon'].str.lower().isin(valid_pokemon)
            invalid = df_gen[~is_valid]

            invalid_pokemon = pd.concat([invalid_pokemon, invalid], ignore_index=True)

            pokemon_df = pokemon_df.drop(invalid.index)

        return pokemon_df, invalid_pokemon

    def calculate_usage(df):
        fmts = df['format'].unique()
        usage_list = []
        for fmt in tqdm(fmts, desc="Calculating usage stats"):
            df_path = f'{output_folder}/tiers/{fmt}.parquet'
            if os.path.exists(df_path):
                df_replays = pd.read_parquet(df_path)
                total_played = len(df_replays)
            else:
                return df
            df_fmt = df[df['format'] == fmt].copy()
            df_fmt['usage'] = (df_fmt['played'] / total_played) * 100
            usage_list.append(df_fmt)

        df = pd.concat(usage_list, ignore_index=True)

        return df

    def calculate_replay(df):
        os.makedirs(f"{output_folder}/replays", exist_ok=True)
        for pdex, group in tqdm(df.groupby('Pdex'), desc="Saving Pokémon replays"):
            df_out = group[['format', 'replays']].copy()
            path = os.path.join(f"{output_folder}/replays", f"{pdex}.parquet")
            df_out.to_parquet(path, index=False)
        df = df.drop(columns=['replays'])
        return df

    def aggregate_replays(replays_list):
        all_replays = []
        for lst in replays_list:
            if isinstance(lst, list):
                all_replays.extend([tuple(item) for item in lst])
        return all_replays

    def aggregate_moves(moves_list):
        total = Counter()
        for moves in moves_list:
            total.update(dict(moves))
        return list(total.items())


    input_dir = input_folder
    dfs = pd.DataFrame()
    file_list = os.listdir(input_dir)

    for file in file_list:

        full_path = os.path.join(input_dir, file)
        print(file)

        if file.endswith(".parquet"):
            df = pd.read_parquet(full_path)
            filename = os.path.splitext(file)[0]
            format_name = filename.split('_')[0]
            df['format'] = format_name
            df['uploadtime'] = pd.to_datetime(df['uploadtime'], unit='s')
            df_pokemon = pokemon_dataframe(df)
            if dfs.empty:
                dfs = df_pokemon
            else:
                dfs = pd.concat([dfs, df_pokemon], ignore_index=True)

    dfs['moves'] = dfs['moves'].apply(lambda x: json.loads(x) if isinstance(x, str) else x)
    dfs['replays'] = dfs['replays'].apply(lambda x: json.loads(x) if isinstance(x, str) else [])
    dfs = dfs.groupby(['pokemon', 'format'], as_index=False).agg({
        'played': 'sum',
        'won': 'sum',
        'lost': 'sum',
        'win_rate': 'mean',
        'moves': aggregate_moves,
        'replays': aggregate_replays,
        'Pdex': 'first',
        'Type 1': 'first',
        'Type 2': 'first',
        'Total': 'first',
        'HP': 'first',
        'Attack': 'first',
        'Defense': 'first',
        'Sp. Atk': 'first',
        'Sp. Def': 'first',
        'Speed': 'first'
    })

    dfs['win_rate'] = (dfs['won'] / (dfs['won'] + dfs['lost'])) * 100
    dfs['moves'] = dfs['moves'].apply(lambda x: json.dumps(x))
    dfs['replays'] = dfs['replays'].apply(lambda lst: json.dumps([
        (rid, ts.isoformat() if hasattr(ts, 'isoformat') else str(ts)) for rid, ts in lst
    ]) if isinstance(lst, list) else '[]')
    dfs = calculate_usage(dfs)
    dfs = calculate_replay(dfs)
    pokemon_df, invalid_pokemon = filter_pokemon(dfs)
    pokemon_df.to_parquet(f'{output_folder}/pokemon.parquet', index=False)
    invalid_pokemon.to_parquet(f'{output_folder}/invalid_pokemon.parquet', index=False)