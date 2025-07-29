import pandas as pd
import os
from tqdm import tqdm
import numpy as np
from rapidfuzz.fuzz import ratio

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
            if line.startswith('|tie') and not line.startswith('|tier'):
                winner = 'Tie'

            elif line.startswith('N') and len(lines) < 2:
                winner = 'DROP THIS ROW'
                return winner, forfeit, p1, p2, list(team1), list(team2), max_turn, switch1, switch2

            elif line.startswith('|player|p1|') and winner is None:
                name = line.split('|')[3]
                if len(name) >= 1:
                    p1 = name

            elif line.startswith('|player|p2|') and winner is None:
                name = line.split('|')[3]
                if len(name) >= 1:
                    p2 = name

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

            elif 'forfeited' in line and not line.startswith('|c|') and not line.startswith('|chat|'):
                forfeit = True
                if p1 is not None and p1 in line:
                    winner = p2
                elif p2 is not None and p2 in line:
                    winner = p1

        def remove_variants(name_set):
            base_forms = {name.split('-')[0] for name in name_set}
            return {name for name in name_set if '-' not in name and name in base_forms}

        team1_filtered = remove_variants(team1)
        team2_filtered = remove_variants(team2)

        if winner == 'Tie':
            forfeit = False

        if winner != p1 and winner != p2 and winner != 'Tie' and winner is not None:

            score1 = ratio(winner, p1)
            score2 = ratio(winner, p2)

            if score1 >= score2:
                winner = p1
            else:
                winner = p2

        if winner is None:
            winner = 'Unknown'


        if forfeit is None:

            if winner == p1:
                if faint2 < len(team2_filtered) or (tsize2 > 0 and faint2 < tsize2):
                    forfeit = True
                else:
                    forfeit = False

            elif winner == p2:
                if faint1 < len(team1_filtered) or (tsize1 > 0 and faint1 < tsize1):
                    forfeit = True
                else:
                    forfeit = False

            else:
                forfeit = False

        return winner, forfeit, p1, p2, list(team1), list(team2), max_turn, switch1, switch2

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

                parsed = df['log'].progress_map(parse_log)
                df_new = pd.DataFrame(parsed.tolist(),
                                      columns=['Winner', 'Forfeit', 'player1', 'player2', 'Team 1', 'Team 2', 'Turns', '# Switches 1',
                                               '# Switches 2'])

                df = df.drop(columns=['log', 'players', 'formatid', 'private', 'password'], errors='ignore')
                df['format'] = os.path.splitext(filename)[0].rsplit('_part', 1)[0]
                df = pd.concat([df, df_new], axis=1)
                df = df[df['Winner'] != 'DROP THIS ROW']
                df.to_parquet(output_path, index=False)

            except Exception as e:
                print(e)
                continue