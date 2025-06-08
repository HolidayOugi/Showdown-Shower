import streamlit as st
import pandas as pd
from PIL import Image
import plotly.express as px
import plotly.graph_objects as go
import os

st.title("👤 Players")

if 'rows_shown' not in st.session_state:
    st.session_state.rows_shown = 5

players_df = pd.read_csv('./output/players.csv')
players_df['pokemon_used'] = players_df['pokemon_used'].apply(eval)
pokemon_df = pd.read_csv('./input/pokemon_stats.csv')

formats = [
    os.path.splitext(df)[0]
    for df in os.listdir('./output/tiers')
    if df.endswith(".csv")
]

selected_format = st.selectbox('Choose a Format', sorted(formats))

players_df = players_df[players_df['format'] == selected_format]

bigcol1, sep, bigcol2 = st.columns([20, 1, 20])

with bigcol1:

    st.subheader("Total Player Stats")

with sep:
    st.markdown("<div style='border-left: 1px solid #ccc; height: 100%;'></div>", unsafe_allow_html=True)

with bigcol2:

    st.subheader("Individual Player Stats")
    players_df = players_df.sort_values(by='played', ascending=False)
    players_df['list_name'] = players_df['name'] + ' - ' + players_df['played'].astype(str) + " matches"
    selected_player = st.selectbox('Choose a player', players_df['list_name'])
    row = players_df[players_df['list_name'] == selected_player].iloc[0]
    col1, col2, col3 = st.columns(3)
    with col1:
        fig = go.Figure(data=[go.Pie(
            values=[row['wins'], row['losses']],
            marker=dict(colors=['#238210', '#ff0e0e']),
            labels=['Wins', 'Losses'],
            hole=0.7,
            direction='clockwise',
            sort=False,
            hovertemplate='%{label}: %{value} (%{percent})<extra></extra>',
            textinfo='none'
        )])

        fig.update_layout(
            dragmode=False,
            showlegend=False,
            margin=dict(t=20, b=20, l=20, r=20),
            height=130,
            width=130,
            annotations=[dict(
                text="Win Rate",
                x=0.5,
                y=0.5,
                font=dict(size=14, color="white"),
                showarrow=False
            )]
        )

        st.plotly_chart(fig, use_container_width=True, config={
            'displayModeBar': False,
            'displaylogo': False,
            'scrollZoom': False,
            'doubleClick': False,
            'editable': False,
            'staticPlot': False,
            'responsive': True,
            'modeBarButtonsToRemove': [
                'zoom2d', 'pan2d', 'select2d', 'lasso2d',
                'zoomIn2d', 'zoomOut2d', 'autoScale2d', 'resetScale2d'
            ]
        })

    with col2:
        st.markdown(f"First Played: {row['first_played']}")
        st.markdown(f"Last Played: {row['last_played']}")

    with col3:
        if row['lowest_rating'] > 0 and row['highest_rating'] > 0:
            st.markdown(f"Min Rating: {row['lowest_rating']}")
            st.markdown(f"Max Rating: {row['highest_rating']}")

    st.markdown(f"### Top 6 Most Used Pokémon by {row['name']}")

    usage_df = pd.DataFrame(row['pokemon_used'].items(), columns=['pokemon', 'count'])
    usage_df['percent'] = usage_df['count'] / row['played'] * 100
    usage_df = usage_df.sort_values(by='percent', ascending=False)
    total_df = pd.merge(usage_df, pokemon_df, on='pokemon')
    total_df = total_df.head(6)

    col1, col2, col3, col4, col5, col6 = st.columns([3, 3, 3, 3, 3, 3])
    cols = [col1, col2, col3, col4, col5, col6]

    for i, col in enumerate(cols):
        if i < len(total_df):
            with col:
                row_p = total_df.take([i])
                gen = selected_format.split(']')[0][1:]
                pdex = row_p['Pdex'].iloc[0]
                image = Image.open(f"./assets/{gen}/{pdex}.png")
                image = image.resize((128, 128))
                st.image(image, width=128)
                st.markdown(row_p['pokemon'].iloc[0])
                type1 = row_p['Type1'].iloc[0]
                type2 = row_p['Type2'].iloc[0]
                image1 = Image.open(f"./assets/icons/{type1.lower()}.png")
                image1 = image1.resize((192, 64))
                st.image(image1, width=64)
                if not pd.isna(type2) and type2 != "":
                    image2 = Image.open(f"./assets/icons/{type2.lower()}.png")
                    image2 = image2.resize((192, 64))
                    st.image(image2, width=64)
                st.markdown(f'Usage: {'%.2f' % (row_p['percent'].iloc[0])}%')
        else:
            with col:
                st.empty()

    st.subheader(f"Replays of {row['name']} in {selected_format}")

    col1, col2 = st.columns(2)
    with col2:

        format_df = pd.read_csv(f'./output/tiers/{selected_format}.csv')
        format_df = format_df[(format_df['player1'] == row['name']) | (format_df['player2'] == row['name'])]




        format_df = format_df.drop(columns=['format', 'rating', 'player1', 'player2', 'Winner', 'Forfeit', 'Team 1', 'Team 2', 'Turns', '# Switches 1', '# Switches 2'])
        format_df['id'] = format_df['id'].apply(lambda x: f"[{x}](https://replay.pokemonshowdown.com/{x})")
        format_df = format_df.sort_values(by=['uploadtime'])
        format_df["uploadtime"] = pd.to_datetime(format_df["uploadtime"])


        min_date = format_df["uploadtime"].min().date()
        max_date = format_df["uploadtime"].max().date()

        selected_dates = st.date_input(
            "Dates",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
            label_visibility="collapsed"
        )

        if len(selected_dates) == 1:
            start_date = selected_dates[0]
            end_date = max_date
        elif len(selected_dates) == 0:
            start_date = min_date
            end_date = max_date
        else:
            start_date, end_date = selected_dates

    with col1:

        filtered_df = format_df[
            (format_df["uploadtime"].dt.date >= start_date) &
            (format_df["uploadtime"].dt.date <= end_date)
        ]

        filtered_df = filtered_df.rename(columns={"id": "Replay", "uploadtime": "Upload Date"})

        st.write(
            filtered_df.head(st.session_state.rows_shown).to_markdown(index=False),
            unsafe_allow_html=True
        )

        if st.session_state.rows_shown < len(filtered_df):
            if st.button("Load more", key="load_more_button"):
                st.session_state.rows_shown += 5
                st.rerun()