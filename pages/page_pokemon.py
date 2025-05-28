import streamlit as st
import pandas as pd
import ast
from PIL import Image

st.title("🧬 Pokémon")

if 'rows_shown' not in st.session_state:
    st.session_state.rows_shown = 5

df = pd.read_csv('./output/pokemon.csv')
df['moves'] = df['moves'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)

pokemon = st.selectbox('Choose a Pokémon', sorted(df['pokemon'].unique()))
df_filtered = df[df['pokemon'] == pokemon]
formats = df_filtered['format'].unique()
selected_format = st.selectbox('Choose a Format', sorted(formats))
row = df_filtered[df_filtered['format'] == selected_format].iloc[0]

st.subheader(f"{pokemon} in {selected_format}")
gen = selected_format.split(']')[0][1:]
image = Image.open(f"./assets/{gen}/{row['Pdex']}.png")
image = image.resize((128, 128))
st.image(image, width=128)

st.write(f"Wins: {row['won']}")
st.write(f"Losses: {row['lost']}")
st.write("Moves Used:")
for move, count in row['moves']:
    st.write(f"- {move}: {count}")

st.write(f"Replays in {selected_format}")
format_df = pd.read_csv(f'./output/tiers/{selected_format}.csv')
format_df = format_df[format_df['Team 1'].apply(lambda x: pokemon in x) | format_df['Team 2'].apply(lambda x: pokemon in x)]




format_df = format_df.drop(columns=['format', 'rating', 'player1', 'player2', 'Winner', 'Forfeit', 'Team 1', 'Team 2', 'Turns', '# Switches 1', '# Switches 2'])
format_df['id'] = format_df['id'].apply(lambda x: f"[{x}](https://replay.pokemonshowdown.com/{x})")
format_df = format_df.sort_values(by=['uploadtime'])
format_df = format_df.rename(columns={"id": "Replay", "uploadtime": "Upload Date"})
st.write(format_df.head(st.session_state.rows_shown).to_markdown(index=False), unsafe_allow_html=True)

if st.button("Load more", key="load_more_button"):
    st.session_state.rows_shown += 5
    st.rerun()

