import streamlit as st
import pandas as pd

st.title("🧬 Pokémon")

df = pd.read_csv('./output/pokemon.csv')

pokemon = st.selectbox('Choose a Pokémon', sorted(df['pokemon'].unique()))
df_filtered = df[df['pokemon'] == pokemon]
formats = df_filtered['format'].unique()
selected_format = st.selectbox('Choose a Format', sorted(formats))
row = df_filtered[df_filtered['format'] == selected_format].iloc[0]

st.subheader(f"{pokemon} in {selected_format}")
st.write(f"Wins: {row['won']}")
st.write(f"Losses: {row['lost']}")
st.write("Moves Used:")
moves = row['moves']
print(type(moves))