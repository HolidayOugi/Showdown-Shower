import pandas as pd
from collections import defaultdict
import re

def parse_log(log):
    lines = log.splitlines()

    winner = None
    team1 = set()
    team2 = set()
    moves_used = defaultdict(set)
    tier = None
    nickname_map = {}

    for line in lines:

        if line.startswith('|win|'):
            winner = line.split('|')[2]

        elif line.startswith('|tier|'):
            tier = line.split('|')[2].strip().title()

        elif line.startswith('|switch|p1a:') or line.startswith('|switch|p2a:'):
            match = re.match(r'\|switch\|(p[12]a): ([^|]+)\|([^|,]+)', line)

            if match:
                player_slot = match.group(1)
                nickname = match.group(2).strip()
                species = match.group(3).strip()
                nickname_map[nickname] = species
                if player_slot == 'p1a':
                    team1.add(species.title())
                else:
                    team2.add(species.title())


        elif line.startswith('|move|'):
            match = re.match(r'\|move\|p[12]a: ([^|]+)\|([^|]+)\|', line)

            if match:
                nickname = match.group(1).strip().title()
                move = match.group(2).strip().title()
                species = nickname_map.get(nickname, nickname)
                moves_used[species].add(move)


    return winner, tier, team1, team2, moves_used


def pokemon_dataframe(df_logs):
    rows = []

    for _, row in df_logs.iterrows():
        log = row['log']
        winner, tier, team1, team2, moves_used = parse_log(log)

        all_pokemon = team1.union(team2)

        if not tier:
            continue  # skip logs with no format info

        for mon in all_pokemon:
            rows.append({
                'pokemon': mon,
                'format': tier,
                'played': 1,
                'won': int(winner == row['player1'] and mon in team1) or int(winner == row['player2'] and mon in team2),
                'lost': int(winner == row['player2'] and mon in team1) or int(winner == row['player1'] and mon in team2),
                'moves': list(moves_used.get(mon, []))
            })

    df_help = pd.DataFrame(rows)

    df_help['pokemon'] = df_help['pokemon'].str.replace("’", "'", regex=False) #farfetch
    df_help['format'] = df_help['format'].apply(
        lambda x: x.split(']')[0] + ']' + ' ' + x.split(']')[1].strip().upper() if ']' in x else x.upper())

    df_new = df_help.groupby(['pokemon', 'format']).agg({
        'played': 'sum',
        'won': 'sum',
        'lost': 'sum',
        'moves': lambda x: list(set(m for sublist in x for m in sublist))
    }).reset_index()

    df_new = df_new.sort_values(by=['pokemon', 'format']).reset_index(drop=True)
    df_new['moves'] = df_new['moves'].apply(lambda x: sorted(x) if isinstance(x, list) else x)
    df_new['win_rate'] = (df_new['won']/(df_new['won']+df_new['lost']))*100
    df_battles = pd.read_csv('battles_PARSED.csv', index_col=[0])
    df_format = df_battles['format'].value_counts().rename_axis('format').reset_index(name='counts')
    print(df_format)
    df_new = pd.merge(df_new, df_format, on='format')
    df_new['usage'] = (df_new['played']/df_new['counts'])*100
    df_new = df_new.drop(columns='counts')

    return df_new

def filter_pokemon(pokemon_df):
    invalid_pokemon = pd.DataFrame()

    for gen in range(1, 5):
        gen_label = f'[Gen {gen}]'
        valid_file = f'./gen_filter/gen{gen}.txt'

        with open(valid_file, 'r', encoding='utf-8') as f:
            valid_pokemon = set(name.strip().lower() for name in f if name.strip())

        mask = pokemon_df['format'].str.startswith(gen_label, na=False)
        df_gen = pokemon_df[mask]

        is_valid = df_gen['pokemon'].str.lower().isin(valid_pokemon)
        invalid = df_gen[~is_valid]

        invalid_pokemon = pd.concat([invalid_pokemon, invalid], ignore_index=True)

        pokemon_df = pokemon_df.drop(invalid.index)

    return pokemon_df, invalid_pokemon

df= pd.read_csv("./data.csv", index_col=[0])
pd.set_option('display.max_columns', None)

df_summary = pokemon_dataframe(df)

pokemon_df, invalid_pokemon = filter_pokemon(df_summary)

print(pokemon_df)

pokemon_df.to_csv('pokemon.csv', index = False)
invalid_pokemon.to_csv('invalid_pokemon.csv', index = False)