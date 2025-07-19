import pandas as pd
import re
import os
from tqdm import tqdm
import numpy as np

def load_battle(input_folder, output_folder):

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

            elif line.startswith('|player|p1|'):
                p1 = line.split('|')[3]

            elif line.startswith('|player|p2|'):
                p2 = line.split('|')[3]

            elif line.startswith('|teamsize|p1|'):
                tsize1 = int(line.split('|')[3])

            elif line.startswith('|teamsize|p2|'):
                tsize2 = int(line.split('|')[3])

            elif line.startswith('|win|'):
                winner = line.split('|')[2]

            elif line.startswith('|poke|p1|'):
                species = line.split('|')[3].split(',')[0].strip()
                species = species.replace('’', "'")
                team1.add(species.title())

            elif line.startswith('|poke|p2|'):
                species = line.split('|')[3].split(',')[0].strip()
                species = species.replace('’', "'")
                team2.add(species.title())

            elif line.startswith('|switch|p1a:'):
                switch1 += 1
                parts = line.split('|')
                if len(parts) > 3:
                    species = parts[3].split(',')[0].strip()
                    species = species.replace('’', "'")
                    team1.add(species.title())

            elif line.startswith('|switch|p2a:'):
                switch2 += 1
                parts = line.split('|')
                if len(parts) > 3:
                    species = parts[3].split(',')[0].strip()
                    species = species.replace('’', "'")
                    team2.add(species.title())

            elif line.startswith('|turn|'):
                max_turn += 1

            elif line.startswith('|faint|p1a'):
                faint1 += 1

            elif line.startswith('|faint|p2a'):
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

    INPUT_FOLDER = input_folder
    OUTPUT_FOLDER = output_folder
    tqdm.pandas()

    for filename in os.listdir(INPUT_FOLDER):
        if filename.endswith(".parquet"):
            input_path = os.path.join(INPUT_FOLDER, filename)
            output_path = os.path.join(OUTPUT_FOLDER, filename)

            try:
                df = pd.read_parquet(input_path)

                print(f"Elaborating {filename}")

                df['uploadtime'] = pd.to_datetime(df['uploadtime'], unit='s')

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

                df['players'] = df['players'].apply(normalize_players)
                df['player1'] = df['players'].apply(lambda x: x[0] if len(x) > 0 else None)
                df['player2'] = df['players'].apply(lambda x: x[1] if len(x) > 1 else None)

                parsed = df['log'].progress_map(parse_log)
                df_new = pd.DataFrame(parsed.tolist(),
                                      columns=['Winner', 'Forfeit', 'Team 1', 'Team 2', 'Turns', '# Switches 1',
                                               '# Switches 2'])

                df = df.drop(columns=['log', 'players', 'formatid', 'private', 'password'], errors='ignore')
                df['format'] = os.path.splitext(filename)[0].rsplit('_part', 1)[0]
                df = pd.concat([df, df_new], axis=1)
                df.to_parquet(output_path, index=False)

            except Exception as e:
                print(e)
                continue