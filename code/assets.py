import pandas as pd
import os

df = pd.read_csv("../input/pokedex.csv")
output_dir = "../assets/Gen 9"

name_counts = {}

for _, row in df.iterrows():
    filename = os.path.basename(row['Image'])
    old_path = os.path.join(output_dir, filename)
    base_name = str(row['Index'])

    count = name_counts.get(base_name, 0)
    if count == 0:
        new_filename = f"{base_name}.png"
    else:
        new_filename = f"{base_name}_{count}.png"
    name_counts[base_name] = count + 1

    new_path = os.path.join(output_dir, new_filename)

    if os.path.exists(old_path):
        os.rename(old_path, new_path)
    else:
        print(f"File non trovato: {old_path}")