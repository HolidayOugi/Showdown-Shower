import streamlit as st
import pandas as pd
from PIL import Image
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
import os
import plotly.io as pio
import numpy as np
from huggingface_hub import hf_hub_download, list_repo_files
import json
from datetime import date
import re

sns.set(rc={'ytick.labelcolor': 'white', 'xtick.labelcolor': 'white'})
sns.set(rc={'axes.facecolor': '#0000FF', 'figure.facecolor': (0, 0, 0, 0)})

st.title("👤 Players")

if 'rows_shown_players' not in st.session_state:
    st.session_state.rows_shown_players = 5

if 'pokemon_shown' not in st.session_state:
    st.session_state.pokemon_shown = 6

with open('./input/formats.txt', 'r') as f:
    formats = [line.strip() for line in f if line.strip()]

def reset_status():
    st.session_state.pokemon_shown = 6
    st.session_state.rows_shown_players = 5

def get_image_path(gen_path, pdex):
    for ext in ['png', 'gif']:
        image_path = f"./assets/{gen_path}/{pdex}.{ext}"
        if os.path.exists(image_path):
            return image_path
    if '-' in pdex:
        base_pdex = pdex.split('-')[0]
        for ext in ['png', 'gif']:
            image_path = f"./assets/{gen_path}/{base_pdex}.{ext}"
            if os.path.exists(image_path):
                return image_path

    for ext in ['png', 'gif']:
        try:
            image_path = hf_hub_download(
                repo_id="HolidayOugi/showdown-shower-resources",
                repo_type="dataset",
                filename=f"assets/{gen_path}/{pdex}.{ext}"
            )
            return image_path
        except:
            pass

    if '-' in pdex:
        base_pdex = pdex.split('-')[0]
        for ext in ['png', 'gif']:

            try:
                image_path = hf_hub_download(
                    repo_id="HolidayOugi/showdown-shower-resources",
                    repo_type="dataset",
                    filename=f"assets/{gen_path}/{base_pdex}.{ext}"
                )
                return image_path
            except:
                pass

    return None


@st.cache_data
def get_player_data(file_path, selected_player):
    if not os.path.exists(file_path):
        filename = os.path.basename(file_path)
        players_df = pd.read_parquet(hf_hub_download(
            repo_id="HolidayOugi/showdown-shower-resources",
            repo_type="dataset",
            filename=f"players/{filename}",
        ))
    else:
        players_df = pd.read_parquet(file_path)
    players_df["rating_list"] = players_df["rating_list"].apply(
        lambda x: str(x) if isinstance(x, (np.ndarray, list)) else x)
    players_df["pokemon_used"] = players_df["pokemon_used"].apply(lambda x: str(x) if isinstance(x, dict) else x)

    if "name" in players_df.columns and selected_player in players_df["name"].values:
        return players_df
    return None

@st.cache_data
def load_parquet(selected_format):
    path = f'./output/players/{selected_format}/{selected_format}_players_top100.parquet'
    if not os.path.exists(path):
        filename = f"{selected_format}_players_top100.parquet"
        players_df = pd.read_parquet(hf_hub_download(
            repo_id="HolidayOugi/showdown-shower-resources",
            repo_type="dataset",
            filename=f"players/{selected_format}/{filename}",
        ))
    else:
        players_df = pd.read_parquet(path)
    players_df = players_df.sort_values(by='played', ascending=False)
    players_df['list_name'] = players_df['name'] + ' - ' + players_df['played'].astype(str) + " matches"

    return players_df, players_df['list_name'].tolist()


def binary_search(selected_format, selected_player, online):
    if not online:
        folder = f'./output/players/{selected_format}'
        file_list = [
            f for f in os.listdir(folder)
            if "part" in f and f.endswith(".parquet") and os.path.isfile(os.path.join(folder, f))
        ]
        low = 0
        high = len(file_list) - 1
        while low <= high:
            mid = (low + high) // 2
            df = pd.read_parquet(f'{folder}/{file_list[mid]}')
            first_name = df['name'].iloc[0]
            last_name = df['name'].iloc[-1]

            if first_name <= selected_player <= last_name:
                result = df[df['name'] == selected_player]
                if not result.empty:
                    return df
                else:
                    return None
            elif selected_player < first_name:
                high = mid - 1
            else:
                low = mid + 1

        return None

    else:
        try:
            df = pd.read_parquet(hf_hub_download(
                repo_id="HolidayOugi/showdown-shower-resources",
                repo_type="dataset",
                filename=f"players/{selected_format}/{selected_format}_players.parquet",
            ))

            result = df[df['name'] == selected_player]
            if not result.empty:
                return df
            else:
                return None
        except:
            pass

        all_files = list_repo_files("HolidayOugi/showdown-shower-resources", repo_type="dataset")
        file_list = [f for f in all_files if f.startswith(f'players/{selected_format}/') and f.endswith('.parquet') and 'part' in f]
        low = 0
        high = len(file_list) - 1
        while low <= high:
            mid = (low + high) // 2
            try:
                df = pd.read_parquet(hf_hub_download(
                    repo_id="HolidayOugi/showdown-shower-resources",
                    repo_type="dataset",
                    filename=f"{file_list[mid]}",
                ))
                first_name = df['name'].iloc[0]
                last_name = df['name'].iloc[-1]
                if first_name <= selected_player <= last_name:
                    result = df[df['name'] == selected_player]
                    if not result.empty:
                        return df
                    else:
                        return None
                elif selected_player < first_name:
                    high = mid - 1
                else:
                    low = mid + 1

            except:
                return None
        return None


def load_player(selected_player, selected_format, players_df=None):
    if players_df is not None:
        row = players_df[players_df['list_name'] == selected_player].iloc[0]
    else:
        folder = f'./output/players/{selected_format}'
        if os.path.exists(folder):
            online = False
        else:
            online = True
        path = os.path.join(folder, f'{selected_format}_players.parquet')
        if os.path.exists(path):
            players_df = pd.read_parquet(path)
            players_df = players_df[players_df['name'] == selected_player]
            if players_df.empty:
                return None, None
            else:
                row = players_df[players_df['name'] == selected_player].iloc[0]

        else:
            players_df = binary_search(selected_format, selected_player, online)
            if players_df is not None:
                row = players_df[players_df['name'] == selected_player].iloc[0]



            else:
                return None, None

    row["rating_list"] = "[" + ", ".join(map(str, row["rating_list"])) + "]" if isinstance(row["rating_list"], (np.ndarray, list)) else row["rating_list"]
    row["pokemon_used"] = str(row["pokemon_used"]) if isinstance(row["pokemon_used"], dict) else row["pokemon_used"]
    if isinstance(row['replays'], str):
        row['replays'] = json.loads(row['replays'])
    else:
        row['replays'] = []
    replay_list = row['replays']
    replay_df = pd.DataFrame(replay_list, columns=['Replay', 'Upload Date'])
    replay_df['Replay'] = replay_df['Replay'].apply(lambda x: f"[{x}](https://replay.pokemonshowdown.com/{x})")
    replay_df = replay_df.sort_values(by=['Upload Date'])
    replay_df["Upload Date"] = pd.to_datetime(replay_df["Upload Date"])
    replay_df['weekday'] = replay_df["Upload Date"].dt.weekday
    replay_df['weekday'] = replay_df['weekday'].map({
        0: 'Monday', 1: 'Tuesday', 2: 'Wednesday', 3: 'Thursday', 4: 'Friday', 5: 'Saturday', 6: 'Sunday'
    })
    replay_df['hour'] = replay_df["Upload Date"].dt.hour
    bins = list(range(0, 25, 2))
    labels = [f"{b}-{b + 2}" for b in bins[:-1]]
    replay_df['hour_bin'] = pd.cut(replay_df['hour'], bins=bins, right=False, labels=labels)

    return row, replay_df






@st.cache_data
def load_graphs(selected_format):
    st.subheader("Total Player Stats by Format")

    col1, col2 = st.columns(2)

    with col1:
        path = f"./output/graphs/players/{selected_format}/fig1.json"

        if not os.path.exists(path):

            path = hf_hub_download(
                    repo_id="HolidayOugi/showdown-shower-resources",
                    repo_type="dataset",
                    filename=f"graphs/players/{selected_format}/fig1.json"
                )

        with open(path, 'r', encoding='utf-8') as f:
            fig = pio.from_json(f.read())

        st.plotly_chart(fig, use_container_width=True, config={'staticPlot': True})

        path = f"./output/graphs/players/{selected_format}/fig2.json"

        if not os.path.exists(path):

            path = hf_hub_download(
                    repo_id="HolidayOugi/showdown-shower-resources",
                    repo_type="dataset",
                    filename=f"graphs/players/{selected_format}/fig2.json"
                )

        with open(path, 'r', encoding='utf-8') as f:
            fig = pio.from_json(f.read())

        st.plotly_chart(fig, use_container_width=True, config={'staticPlot': True})

    with col2:

        path = f"./output/graphs/players/{selected_format}/fig3.json"

        if not os.path.exists(path):

            path = hf_hub_download(
                    repo_id="HolidayOugi/showdown-shower-resources",
                    repo_type="dataset",
                    filename=f"graphs/players/{selected_format}/fig3.json"
                )
        with open(path, 'r', encoding='utf-8') as f:
            fig = pio.from_json(f.read())

        st.plotly_chart(fig, use_container_width=True, config={'staticPlot': True})

        path = f"./output/graphs/players/{selected_format}/fig4.json"

        if not os.path.exists(path):

            path = hf_hub_download(
                    repo_id="HolidayOugi/showdown-shower-resources",
                    repo_type="dataset",
                    filename=f"graphs/players/{selected_format}/fig4.json"
                )

        with open(path, 'r', encoding='utf-8') as f:
            fig = pio.from_json(f.read())

        st.plotly_chart(fig, use_container_width=True, config={'staticPlot': True})

@st.cache_data
def load_player_graphs(row, selected_player, selected_format):
    col1, col2, col3 = st.columns(3)
    key = f"{selected_player} ({selected_format})"
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
                text="Winrate",
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
        },
                        key=f"{key}_pie"                        )

    with col2:
        st.markdown(f"First Played: {row['first_played']}")
        st.markdown(f"Last Played: {row['last_played']}")

    with col3:
        if row['lowest_rating'] > 0 and row['highest_rating'] > 0:
            st.markdown(f"Min Rating: {row['lowest_rating']}")
            st.markdown(f"Max Rating: {row['highest_rating']}")

    if isinstance(row['rating_list'], str):
        s = row['rating_list'].strip("[]")
        numbers = re.findall(r"\d+(?:\.\d+)?", s)
        row['rating_list'] = np.array([float(n) for n in numbers])

    rating_list = row['rating_list']

    if rating_list is not None and rating_list.size > 0:
        if isinstance(rating_list, np.ndarray) and rating_list.ndim == 0:
            rating_list = np.atleast_1d(rating_list)
        if isinstance(rating_list, (list, np.ndarray)):
            match_range = list(range(1, len(rating_list) + 1))
        else:
            match_range = [1]
        df_rating = pd.DataFrame({
            'Match': match_range,
            'Rating': rating_list
        })

        df_rating['Smoothed Rating'] = df_rating['Rating'].rolling(window=20, min_periods=1).mean()

        fig = px.line(df_rating, x='Match', y='Smoothed Rating',
                      title=f"Rating history for {row['name']} in {selected_format}",
                      markers=False)

        st.plotly_chart(fig, use_container_width=True, key=f"{key}_rating")

    return row

@st.cache_data
def load_heatmap(row, format_df, selected_mode, selected_format):
    if selected_mode == 'Separated':

        weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        ordered_hours = sorted(format_df['hour_bin'].unique(), key=lambda x: int(x.split('-')[0]))

        subcol1, subcol2 = st.columns(2)

        with subcol1:
            fig_hour = px.histogram(
                format_df,
                x='hour_bin',
                nbins=len(format_df['hour_bin'].unique()),
                category_orders={'hour_bin': ordered_hours},
                labels={'hour_bin': 'Hours'},
                title=f'Frequency of matches during certain hours (GMT)<br>in {selected_format}'
            )
            fig_hour.update_xaxes(type='category')
            fig_hour.update_layout(bargap=0)
            fig_hour.update_layout(yaxis_title='# Matches')
            st.plotly_chart(fig_hour, use_container_width=True)

        with subcol2:
            fig_weekday = px.histogram(
                format_df,
                x='weekday',
                nbins=7,
                category_orders={'weekday': weekday_order},
                labels={'weekday': 'Weekday', 'matches': '# Matches'},
                title=f'Frequency of matches during certain days (GMT)<br>in {selected_format}'
            )
            fig_weekday.update_xaxes(type='category')
            fig_weekday.update_layout(bargap=0)
            fig_weekday.update_layout(yaxis_title='# Matches')
            st.plotly_chart(fig_weekday, use_container_width=True)

    else:

        count_df = format_df.groupby(['weekday', 'hour_bin']).size().reset_index(name='match_count')
        weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        hour_bin_order = ['0-2', '2-4', '4-6', '6-8', '8-10', '10-12', '12-14',
                          '14-16', '16-18', '18-20', '20-22', '22-24']

        pivot_df = count_df.pivot(
            index='weekday',
            columns='hour_bin',
            values='match_count'
        ).fillna(0)

        pivot_df = pivot_df.reindex(weekday_order)
        pivot_df = pivot_df[hour_bin_order]

        fig, ax = plt.subplots(figsize=(12, 6))

        sns.heatmap(
            pivot_df,
            annot=True,
            fmt="d",
            cmap='YlOrRd',
            linewidths=.5,
            ax=ax,
        )

        fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
        ax.set_title(f'Distribution of Matches per Weekday and Hour Interval (GMT) by {row['name']} in {selected_format}', color='white')
        ax.set_xlabel('Hour Interval')
        ax.set_ylabel('Weekday')
        ax.xaxis.label.set_color('white')
        ax.yaxis.label.set_color('white')

        plt.tight_layout()
        st.pyplot(fig, use_container_width=True)

def load_pokemon(row, selected_format):

    pokemon_df = pd.read_csv('./input/pokemon_stats.csv')

    if isinstance(row['pokemon_used'], str):
        row['pokemon_used'] = eval(row['pokemon_used'])

    usage_df = pd.DataFrame(row['pokemon_used'].items(), columns=['pokemon', 'count'])
    usage_df['percent'] = usage_df['count'] / row['played'] * 100
    usage_df = usage_df.sort_values(by='percent', ascending=False)
    total_df = pd.merge(usage_df, pokemon_df, on='pokemon')
    new_total_df = total_df.head(st.session_state.pokemon_shown)

    num_pokemon = min(len(new_total_df), st.session_state.pokemon_shown)

    st.markdown(f"### Top {num_pokemon} Most Used Pokémon by {row['name']} in {selected_format}")


    for row_start in range(0, len(new_total_df), 6):
        cols = st.columns([3, 3, 3, 3, 3, 3])
        for i, col in enumerate(cols):
            idx = row_start + i
            if idx < len(new_total_df):
                row_p = new_total_df.iloc[[idx]]
                with col:
                    gen = selected_format.split(']')[0][1:]
                    gen_number = int(gen.split()[1])
                    if gen_number < 6:
                        gen_path = gen
                    else:
                        gen_path = 'HOME'
                    pdex = row_p['Pdex'].iloc[0]
                    image_path = get_image_path(gen_path, pdex)
                    st.image(image_path, width=128)
                    name = row_p['pokemon'].iloc[0]
                    st.markdown(name)
                    type1 = row_p['Type 1'].iloc[0]
                    type2 = row_p['Type 2'].iloc[0]
                    if gen_number < 6:
                        if type1 == 'Fairy' or type2 == 'Fairy':
                            old_types = pd.read_csv('./input/old_types.csv')
                            old_row = old_types[old_types['pokemon'] == name]
                            type1 = old_row['Type 1'].iloc[0]
                            type2 = old_row['Type 2'].iloc[0]
                        type1_path = f"./assets/icons/old/{type1.lower()}.png"
                        if not os.path.exists(type1_path):
                            type1_path = hf_hub_download(
                                repo_id="HolidayOugi/showdown-shower-resources",
                                repo_type="dataset",
                                filename=f"assets/icons/old/{type1.lower()}.png"
                            )
                        image1 = Image.open(type1_path)
                        image1 = image1.resize((192, 64))
                        st.image(image1, width=64)
                        if not pd.isna(type2) and type2 != "":
                            type2_path = f"./assets/icons/old/{type2.lower()}.png"
                            if not os.path.exists(type2_path):
                                type2_path = hf_hub_download(
                                    repo_id="HolidayOugi/showdown-shower-resources",
                                    repo_type="dataset",
                                    filename=f"assets/icons/old/{type2.lower()}.png"
                                )
                            image2 = Image.open(type2_path)
                            image2 = image2.resize((192, 64))
                            st.image(image2, width=64)
                    else:
                        type1_path = f"./assets/icons/new/{type1.lower()}.png"
                        if not os.path.exists(type1_path):
                            type1_path = hf_hub_download(
                                repo_id="HolidayOugi/showdown-shower-resources",
                                repo_type="dataset",
                                filename=f"assets/icons/new/{type1.lower()}.png"
                            )
                        image1 = Image.open(type1_path)
                        image1 = image1.resize((400, 88))
                        st.image(image1, width=88)
                        if not pd.isna(type2) and type2 != "":
                            type2_path = f"./assets/icons/new/{type2.lower()}.png"
                            if not os.path.exists(type2_path):
                                type2_path = hf_hub_download(
                                    repo_id="HolidayOugi/showdown-shower-resources",
                                    repo_type="dataset",
                                    filename=f"assets/icons/new/{type2.lower()}.png"
                                )
                            image2 = Image.open(type2_path)
                            image2 = image2.resize((400, 88))
                            st.image(image2, width=88)
                    st.markdown(f'Usage: {'%.2f' % (row_p['percent'].iloc[0])}%')
            else:
                with col:
                    st.empty()
    if st.session_state.pokemon_shown < len(usage_df):
        if st.button("Load more", key="load_more_button"):
            st.session_state.pokemon_shown += 6
            st.rerun()


@st.cache_data
def load_replays(matches_df_raw, start_date, end_date):
    matches_df = matches_df_raw[["Replay", "Upload Date"]]
    filtered_df = matches_df[
        (matches_df["Upload Date"].dt.date >= start_date) &
        (matches_df["Upload Date"].dt.date <= end_date)
        ]

    return filtered_df


parquet_dir = './output/players'

selected_format = st.selectbox('Choose a Format', sorted(formats), on_change=reset_status)

bigcol1, sep, bigcol2 = st.columns([10, 1, 10])

with bigcol1:

    load_graphs(selected_format)

with sep:
    st.markdown("<div style='border-left: 1px solid #ccc; height: 100%;'></div>", unsafe_allow_html=True)

with bigcol2:

    st.subheader("Individual Player Stats by Format")

    selected_player_search = st.text_input("Search for a player", value="", placeholder="Enter player name",
                                    on_change=reset_status)


    players_df, player_list = load_parquet(selected_format)

    selected_player_list = st.selectbox(f"Or choose from the list below of the Top 100 players in {selected_format}.", player_list, on_change=reset_status, placeholder="Choose player name")

    if selected_player_search == "":
        selected_player = selected_player_list
        row, replay_df = load_player(selected_player, selected_format, players_df)

    else:
        selected_player = selected_player_search
        row, replay_df = load_player(selected_player, selected_format, None)
        if row is None:
            st.error(f"Player '{selected_player}' not found in the selected format '{selected_format}'. Please try another player.")
            selected_player = selected_player_list
            row, replay_df = load_player(selected_player, selected_format, players_df)

    if row is not None:


        st.markdown(f"### Player: {row['name']}")


        load_player_graphs(row, selected_player, selected_format)

        key = f"{selected_player} ({selected_format})"

        selected_mode = st.selectbox('Choose a visualization mode', ['Separated', 'Combined'], key=f"{key}_mode")

        load_heatmap(row, replay_df, selected_mode, selected_format)

        load_pokemon(row, selected_format)

        st.subheader(f"Replays of {row['name']} in {selected_format}")

        col1, col2 = st.columns(2)
        with col2:

            min_date = replay_df["Upload Date"].min().date()
            max_date = replay_df["Upload Date"].max().date()
            today = date.today()

            selected_dates = st.date_input(
                "Dates",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=today,
                label_visibility="collapsed",
                key="individual"
            )

            if len(selected_dates) == 1:
                start_date = selected_dates[0]
                end_date = today
            elif len(selected_dates) == 0:
                start_date = min_date
                end_date = max_date
            else:
                start_date, end_date = selected_dates

        with col1:

            replay_df = load_replays(replay_df, start_date, end_date)

            st.write(
                replay_df.head(st.session_state.rows_shown_players).to_markdown(index=False),
                unsafe_allow_html=True
            )

            if st.session_state.rows_shown_players < len(replay_df):
                if st.button("Load more", key=f"{key}_load"):
                    st.session_state.rows_shown_players += 5
                    st.rerun()