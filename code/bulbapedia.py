import pandas as pd

url = "https://bulbapedia.bulbagarden.net/wiki/List_of_moves"

tables = pd.read_html(url)

moves = tables[0]

moves.columns = moves.iloc[1]

moves = moves.iloc[2:]

moves.to_csv("../input/moves_all.csv", index=False)