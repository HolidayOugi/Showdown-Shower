import pandas as pd
from collections import defaultdict, Counter
import re
from pathlib import Path

def normalize_format(fmt):
    fmt = fmt.strip().lower().replace('\r', '')
    match = re.search(r'gen\s*([1-5])', fmt)
    if not match:
        match = re.search(r'gen([1-5])', fmt)
    if match:
        gen = match.group(1)
    else:
        return None

    if 'ou' in fmt:
        return f"[Gen {gen}] OU"
    elif 'uu' in fmt and 'uubl' not in fmt:
        return f"[Gen {gen}] UU"
    elif 'nu' in fmt:
        return f"[Gen {gen}] NU"
    elif 'uubl' in fmt:
        return f"[Gen {gen}] UUBL"
    elif 'uber' in fmt:
        return f"[Gen {gen}] UBERS"
    else:
        return f"[Gen {gen}] Other"

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


    return winner, tier, team1, team2, moves_used


def pokemon_dataframe(df_logs):
    rows = []

    total = len(df_logs)

    cleaned = df_logs['players'].str.strip("[]")
    split_players = cleaned.str.extractall(r"'([^']+)'").unstack()
    split_players.columns = ['player1', 'player2']
    df_logs = df_logs.drop(columns=['players', 'formatid']).join(split_players)
    counter = 1

    for _, row in df_logs.iterrows():
        print("Elaborating: " + str(counter) + " of " + str(total))
        log = row['log']
        winner, tier, team1, team2, moves_used = parse_log(log)

        all_pokemon = team1.union(team2)

        if not tier:
            continue

        for mon in all_pokemon:
            rows.append({
                'pokemon': mon,
                'format': tier,
                'played': 1,
                'won': int(winner == row['player1'] and mon in team1) or int(winner == row['player2'] and mon in team2),
                'lost': int(winner == row['player2'] and mon in team1) or int(winner == row['player1'] and mon in team2),
                'moves': Counter(moves_used.get(mon, []))
            })

        counter += 1

    df_help = pd.DataFrame(rows)

    df_help['pokemon'] = df_help['pokemon'].str.replace("’", "'", regex=False) #farfetch
    df_help['format'] = df_help['format'].apply(normalize_format)

    def merge_counters(series):
        total_counters = Counter()
        for c in series:
            if isinstance(c, Counter):
                total_counters.update(c)
        return sorted(total_counters.items(), key=lambda x: (-x[1], x[0]))

    df_new = df_help.groupby(['pokemon', 'format']).agg({
        'played': 'sum',
        'won': 'sum',
        'lost': 'sum',
        'moves': merge_counters
    }).reset_index()

    df_new = df_new.sort_values(by=['pokemon', 'format']).reset_index(drop=True)
    df_new['moves'] = df_new['moves'].apply(lambda x: sorted(x) if isinstance(x, list) else x)
    df_new['win_rate'] = (df_new['won']/(df_new['won']+df_new['lost']))*100
    df_battles = pd.read_csv('../input/battles_PARSED.csv')
    df_format = df_battles['format'].value_counts().rename_axis('format').reset_index(name='counts')
    df_new = pd.merge(df_new, df_format, on='format')
    df_new['usage'] = (df_new['played']/df_new['counts'])*100
    df_new = df_new.drop(columns='counts')
    df_stats = pd.read_csv('../input/pokemon_stats.csv')
    df_new = pd.merge(df_new, df_stats, on='pokemon', how='left')

    return df_new

def filter_pokemon(pokemon_df):
    invalid_pokemon = pd.DataFrame()

    for gen in range(1, 5):
        gen_label = f'[Gen {gen}]'
        valid_file = f'../input/gen_filter/gen{gen}.txt'

        with open(valid_file, 'r', encoding='utf-8') as f:
            valid_pokemon = set(name.strip().lower() for name in f if name.strip())

        mask = pokemon_df['format'].str.startswith(gen_label, na=False)
        df_gen = pokemon_df[mask]

        is_valid = df_gen['pokemon'].str.lower().isin(valid_pokemon)
        invalid = df_gen[~is_valid]

        invalid_pokemon = pd.concat([invalid_pokemon, invalid], ignore_index=True)

        pokemon_df = pokemon_df.drop(invalid.index)

    return pokemon_df, invalid_pokemon


if Path('../output/pokemon_completetest.csv').exists():
    df_summary=pd.read_csv('../output/pokemon_completetest.csv')

else:
    df= pd.read_csv("../input/data.csv")
    pd.set_option('display.max_columns', None)

    df_summary = pokemon_dataframe(df)
    df_summary.to_csv('../output/pokemon_completetest.csv', index = False)

pokemon_df, invalid_pokemon = filter_pokemon(df_summary)

print(pokemon_df)

pokemon_df.to_csv('../output/pokemon.csv', index = False)
invalid_pokemon.to_csv('../output/invalid_pokemon.csv', index = False)