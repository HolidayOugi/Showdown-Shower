import pandas as pd
from datetime import datetime
import re

def normalize_format(fmt):
    fmt = fmt.strip().lower().replace('\r', '')  # rimuovi spazi, newline
    match = re.search(r'gen\s*([1-5])', fmt)
    if not match:
        match = re.search(r'gen([1-5])', fmt)
    if match:
        gen = match.group(1)
    else:
        return None  # formato non valido

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

def parse_log(log_text):
    lines = log_text.splitlines()

    winner = None
    forfeit = None
    p1 = None
    p2 = None
    team1 = set()
    team2 = set()
    faint1 = 0
    faint2 = 0
    tsize1 = 0
    tsize2 = 0
    switch1 = -1 #always starts with switch
    switch2 = -1
    max_turn = 0

    for line in lines:
        if line.startswith('|tie'):
            winner = 'Tie'

        if line.startswith('|player|p1|'):
            p1 = line.split('|')[3]

        if line.startswith('|player|p2|'):
            p2 = line.split('|')[3]

        if line.startswith('|teamsize|p1|'):
            tsize1 = int(line.split('|')[3])

        if line.startswith('|teamsize|p2|'):
            tsize2 = int(line.split('|')[3])

        if line.startswith('|win|'):
            winner = line.split('|')[2]

        if line.startswith('|switch|p1a:'):
            switch1 += 1
            parts = line.split('|')
            if len(parts) > 3:
                species = parts[3].split(',')[0].strip()
                team1.add(species.title())

        if line.startswith('|switch|p2a:'):
            switch2 += 1
            parts = line.split('|')
            if len(parts) > 3:
                species = parts[3].split(',')[0].strip()
                team2.add(species.title())

        if line.startswith('|turn|'):
            max_turn += 1

        if line.startswith('|faint|p1a'):
            faint1 += 1

        if line.startswith('|faint|p2a'):
            faint2 += 1

    if winner == p1:
        if faint2 < len(team2) or (tsize2 > 0 and faint2 < tsize2):
            forfeit = True
        else:
            forfeit = False

    elif winner == p2:
        if faint1 < len(team1) or (tsize1 > 0 and faint1 < tsize1):
            forfeit = True
        else:
            forfeit = False

    else:
        forfeit = False

    return winner, forfeit, list(team1), list(team2), max_turn, switch1, switch2

df= pd.read_csv("../input/data.csv", index_col=[0])
pd.set_option('display.max_columns', None)
#df['uploadtime'] = pd.to_datetime(df['uploadtime'], unit='s')
#cleaned = df['players'].str.strip("[]")
#split_players = cleaned.str.extractall(r"'([^']+)'").unstack()
#split_players.columns = ['player1', 'player2']
#df = df.drop(columns=['players', 'Unnamed: 0', 'formatid']).join(split_players)
df['Winner'], df['Forfeit'], df['Team 1'], df['Team 2'], df['Turns'], df['# Switches 1'], df['# Switches 2']= zip(*df['log'].map(parse_log))
df = df.drop('log', axis=1)
df['format'] = df['format'].apply(normalize_format)
print(df)
df.to_csv('../input/battles_PARSED.csv', index=False)
