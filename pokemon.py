import pandas as pd
from collections import defaultdict
import re

def extract_info_from_log(log):
    lines = log.splitlines()

    winner = None
    team1 = set()
    team2 = set()
    moves_used = defaultdict(set)
    tier = None

    for line in lines:

        if line.startswith('|win|'):
            winner = line.split('|')[2]

        elif line.startswith('|tier|'):
            tier = line.split('|')[2].strip().title()

        elif line.startswith('|switch|p1a:'):
            parts = line.split('|')
            if len(parts) > 3:
                species = parts[3].split(',')[0].strip()
                team1.add(species.title())

        elif line.startswith('|switch|p2a:'):
            parts = line.split('|')
            if len(parts) > 3:
                species = parts[3].split(',')[0].strip()
                team2.add(species.title())

        elif line.startswith('|move|'):
            parts = line.split('|')
            if len(parts) > 3:
                match = re.match(r'\|move\|p[12]a: ([^|]+)\|([^|]+)\|', line)
                if match:
                    mon = match.group(1).split(',')[0].strip()
                    move = match.group(2).strip().title()
                    moves_used[mon].add(move)

    return winner, tier, team1, team2, moves_used


def build_stats_dataframe(df_logs):
    rows = []

    for _, row in df_logs.iterrows():
        log = row['log']
        winner, tier, team1, team2, moves_used = extract_info_from_log(log)

        if not tier:
            continue  # skip logs with no format info

        for mon in team1:
            rows.append({
                'pokemon': mon,
                'format': tier,
                'won': int(winner == row['player1']),
                'lost': int(winner == row['player2']),
                'moves': list(moves_used.get(mon, []))
            })

        for mon in team2:
            rows.append({
                'pokemon': mon,
                'format': tier,
                'won': int(winner == row['player2']),
                'lost': int(winner == row['player1']),
                'moves': list(moves_used.get(mon, []))
            })

    df_help = pd.DataFrame(rows)
    df_help['format'] = df_help['format'].apply(
        lambda x: x.split(']')[0] + ']' + ' ' + x.split(']')[1].strip().upper() if ']' in x else x.upper())

    df_new = df_help.groupby(['pokemon', 'format']).agg({
        'won': 'sum',
        'lost': 'sum',
        'moves': lambda x: list(set(m for sublist in x for m in sublist))
    }).reset_index()

    df_new = df_new.sort_values(by=['pokemon', 'format']).reset_index(drop=True)
    df_new['moves'] = df_new['moves'].apply(lambda x: sorted(x) if isinstance(x, list) else x)

    return df_new

df= pd.read_csv("./data.csv", index_col=[0])
pd.set_option('display.max_columns', None)

df_summary = build_stats_dataframe(df)

print(df_summary)

df_summary.to_csv('pokemon.csv', index = False)

