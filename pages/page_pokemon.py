import streamlit as st
import pandas as pd
import ast
from PIL import Image
import plotly.graph_objects as go
import base64

st.title("🧬 Pokémon")

if 'rows_shown' not in st.session_state:
    st.session_state.rows_shown = 5

if 'visible_moves' not in st.session_state:
    st.session_state.visible_moves = 5

def load_more():
    st.session_state.visible_moves += 5

df = pd.read_csv('./output/pokemon.csv')
df['moves'] = df['moves'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)
df['moves'] = df['moves'].apply(lambda x: sorted(x, key=lambda x: x[1], reverse=True))

pokemon = st.selectbox('Choose a Pokémon', sorted(df['pokemon'].unique()))
df_filtered = df[df['pokemon'] == pokemon]
formats = df_filtered['format'].unique()
selected_format = st.selectbox('Choose a Format', sorted(formats))
row = df_filtered[df_filtered['format'] == selected_format].iloc[0]

st.subheader(f"{pokemon} in {selected_format}")
gen = selected_format.split(']')[0][1:]

col1, col2, col3 = st.columns([3, 3, 10])

with col1:

    image = Image.open(f"./assets/{gen}/{row['Pdex']}.png")
    image = image.resize((128, 128))
    st.image(image, width=128)

with col2:
    type1 = row['Type1']
    type2 = row['Type2']
    image1 = Image.open(f"./assets/icons/{type1.lower()}.png")
    image1 = image1.resize((192, 64))
    print(type1, type2)
    st.image(image1, width=64)
    if not pd.isna(type2) and type2 != "":
        image2 = Image.open(f"./assets/icons/{type2.lower()}.png")
        image2 = image2.resize((192, 64))
        st.image(image2, width=64)
with col3:

    fig = go.Figure(data=[go.Pie(
        values=[row['won'], row['lost']],
        marker=dict(colors=['#4caf50', '#f44336']),
        labels=['Wins', 'Losses'],
        hole=0.7,
        direction='clockwise',
        sort=False,
        hovertemplate='%{label}: %{value} (%{percent})<extra></extra>',
        textinfo='none'
    )])

    fig.update_layout(
        showlegend=False,
        margin=dict(t=20, b=20, l=20, r=20),
        height=130,
        width=130,
    )

    st.plotly_chart(fig, use_container_width=False)

moves_df = pd.read_csv('./input/moves.csv')
moves_df = moves_df.map(lambda x: x.lstrip() if isinstance(x, str) else x)
types_df = pd.read_csv('./input/types.csv')
moves_df = pd.merge(moves_df, types_df, on='type')

visible_moves = st.session_state.visible_moves
moves_to_show = row['moves'][:visible_moves]

for move, count in moves_to_show:
    fig = go.Figure()
    move_row = moves_df[moves_df['move'].str.contains(move, case=False, na=False)]
    if move_row.empty:
        print(move)
    move_type = move_row['type'].iloc[0]
    color = move_row['color'].iloc[0]
    usage = count/(row['won']+row['lost'])

    col1, col2 = st.columns([10, 1])

    with col1:

        fig.add_trace(go.Bar(
            x=[1],
            y=[move],
            orientation='h',
            marker=dict(color='#e0e0e0'),
            hoverinfo='skip',
            showlegend=False
        ))

        fig.add_trace(go.Bar(
            x=[usage],
            y=[move],
            orientation='h',
            marker=dict(color=color),
            hovertemplate=(
                    f"<b>{move}</b><br>" +
                    f"Type: {move_type}<br>" +
                    f"Usage: {usage:.1%}<extra></extra>"
            ),
            showlegend=False
        ))

        fig.add_annotation(
            x=0.5,
            y=move,
            text=move,
            showarrow=False,
            font=dict(size=16, color='black'),
            xanchor='center',
            yanchor='middle'
        )

        fig.update_layout(
            height=60,
            margin=dict(l=20, r=20, t=5, b=5),
            barmode='overlay',
            xaxis=dict(range=[0, 1], showgrid=False, showticklabels=False, fixedrange=True),
            yaxis=dict(showticklabels=False),
            plot_bgcolor='white',
            paper_bgcolor='white'
        )

        st.plotly_chart(fig, use_container_width=True)

    with col2:
        move_key = move.replace(" ", "_")
        move_url = f"https://bulbapedia.bulbagarden.net/wiki/{move_key}_(move)"
        with open('./assets/icons/bulba.png', "rb") as f:
            img_bytes = f.read()
        img_b64 = base64.b64encode(img_bytes).decode()
        html_code = f'''
            <a href="{move_url}" target="_blank">
                <img src="data:image/png;base64,{img_b64}" width="24" style="vertical-align:middle;" />
            </a>
            '''
        st.markdown(html_code, unsafe_allow_html=True)

if visible_moves < len(row['moves']):
    st.button("Load more", on_click=load_more)

st.subheader(f"Replays of {pokemon} in {selected_format}")
format_df = pd.read_csv(f'./output/tiers/{selected_format}.csv')
format_df = format_df[format_df['Team 1'].apply(lambda x: pokemon in x) | format_df['Team 2'].apply(lambda x: pokemon in x)]




format_df = format_df.drop(columns=['format', 'rating', 'player1', 'player2', 'Winner', 'Forfeit', 'Team 1', 'Team 2', 'Turns', '# Switches 1', '# Switches 2'])
format_df['id'] = format_df['id'].apply(lambda x: f"[{x}](https://replay.pokemonshowdown.com/{x})")
format_df = format_df.sort_values(by=['uploadtime'])
format_df = format_df.rename(columns={"id": "Replay", "uploadtime": "Upload Date"})
st.write(format_df.head(st.session_state.rows_shown).to_markdown(index=False), unsafe_allow_html=True)

if st.session_state.rows_shown < len(format_df):
    if st.button("Load more", key="load_more_button"):
        st.session_state.rows_shown += 5
        st.rerun()

