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
from huggingface_hub import hf_hub_download

sns.set(rc={'ytick.labelcolor': 'white', 'xtick.labelcolor': 'white'})
sns.set(rc={'axes.facecolor': '#0000FF', 'figure.facecolor': (0, 0, 0, 0)})

st.title("👤 Players")

if 'rows_shown' not in st.session_state:
    st.session_state.rows_shown = 5

with open('./input/formats.txt', 'r') as f:
    formats = [line.strip() for line in f if line.strip()]


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
    path = f'./output/players/{selected_format}_players.parquet'
    if not os.path.exists(path):
        filename = f"{selected_format}_players.parquet"
        players_df = pd.read_parquet(hf_hub_download(
            repo_id="HolidayOugi/showdown-shower-resources",
            repo_type="dataset",
            filename=f"players/{filename}",
        ))
    else:
        players_df = pd.read_parquet(f'./output/players/{selected_format}_players.parquet')
    players_df = players_df.sort_values(by='played', ascending=False)
    players_df['list_name'] = players_df['name'] + ' - ' + players_df['played'].astype(str) + " matches"

    players_df["rating_list"] = players_df["rating_list"].apply(lambda x: str(x) if isinstance(x, (np.ndarray, list)) else x)
    players_df["pokemon_used"] = players_df["pokemon_used"].apply(lambda x: str(x) if isinstance(x, dict) else x)

    return players_df, players_df['list_name'].tolist()

@st.cache_data
def load_player(players_df, selected_player, selected_format):
    if 'list_name' in players_df.columns:
        row = players_df[players_df['list_name'] == selected_player].iloc[0]
    else:
        row = players_df[players_df['name'] == selected_player].iloc[0]

    df_path = f'./output/tiers/{selected_format}.parquet'
    if os.path.exists(df_path):
        format_df = pd.read_parquet(df_path)

    else:
       filename = f"{selected_format}.parquet"
       format_df = pd.read_parquet(hf_hub_download(
            repo_id="HolidayOugi/showdown-shower-resources",
            repo_type="dataset",
            filename=f"tiers/{filename}"))

    format_df['id'] = format_df['id'].apply(lambda x: f"[{x}](https://replay.pokemonshowdown.com/{x})")
    format_df = format_df.sort_values(by=['uploadtime'])
    format_df["uploadtime"] = pd.to_datetime(format_df["uploadtime"])
    format_df = format_df[(format_df['player1'] == row['name']) | (format_df['player2'] == row['name'])]
    format_df['weekday'] = format_df['uploadtime'].dt.weekday
    format_df['weekday'] = format_df['weekday'].map({
        0: 'Monday', 1: 'Tuesday', 2: 'Wednesday', 3: 'Thursday', 4: 'Friday', 5: 'Saturday', 6: 'Sunday'
    })
    format_df['hour'] = format_df['uploadtime'].dt.hour
    bins = list(range(0, 25, 2))
    labels = [f"{b}-{b + 2}" for b in bins[:-1]]
    format_df['hour_bin'] = pd.cut(format_df['hour'], bins=bins, right=False, labels=labels)
    return row, format_df



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

        st.plotly_chart(fig, use_container_width=True)

        path = f"./output/graphs/players/{selected_format}/fig2.json"

        if not os.path.exists(path):

            path = hf_hub_download(
                    repo_id="HolidayOugi/showdown-shower-resources",
                    repo_type="dataset",
                    filename=f"graphs/players/{selected_format}/fig2.json"
                )

        with open(path, 'r', encoding='utf-8') as f:
            fig = pio.from_json(f.read())

        st.plotly_chart(fig, use_container_width=True)

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

        row['rating_list'] = np.fromstring(row['rating_list'].strip("[]"), sep=' ')

    rating_list = row['rating_list']

    if rating_list is not None and not pd.isna(rating_list) and rating_list.size > 0:
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
                      title=f"Rating history for {selected_player} in {selected_format}",
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
                title=f'Frequency of matches during certain hours (GMT) in {selected_format}'
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
                title=f'Frequency of matches during certain days (GMT) in {selected_format}'
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

@st.cache_data
def load_pokemon(row, selected_format):
    st.markdown(f"### Top 6 Most Used Pokémon by {row['name']} in {selected_format}")

    pokemon_df = pd.read_csv('./input/pokemon_stats.csv')

    if isinstance(row['pokemon_used'], str):
        row['pokemon_used'] = eval(row['pokemon_used'])

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
                gen_number = int(gen.split()[1])
                if gen_number < 6:
                    gen_path = gen
                else:
                    gen_path = 'HOME'
                pdex = row_p['Pdex'].iloc[0]
                image_path = f"./assets/{gen_path}/{pdex}.png"
                if not os.path.exists(image_path):
                    if not '-' in pdex:
                        image_path = hf_hub_download(
                            repo_id="HolidayOugi/showdown-shower-resources",
                            repo_type="dataset",
                            filename=f"assets/{gen_path}/{pdex}.png"
                        )
                    else:
                        pdex = pdex.split('-')[0]
                        new_image_path = f"./assets/{gen_path}/{pdex}.png"
                        if not os.path.exists(new_image_path):
                            image_path = hf_hub_download(
                                repo_id="HolidayOugi/showdown-shower-resources",
                                repo_type="dataset",
                                filename=f"assets/{gen_path}/{pdex}.png"
                            )
                        else:
                            image_path = new_image_path
                image = Image.open(image_path)
                image = image.resize((128, 128))
                st.image(image, width=128)
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
                    image1 = image1.resize((500, 120))
                    st.image(image1, width=120)
                    if not pd.isna(type2) and type2 != "":
                        type2_path = f"./assets/icons/new/{type2.lower()}.png"
                        if not os.path.exists(type2_path):
                            type2_path = hf_hub_download(
                                repo_id="HolidayOugi/showdown-shower-resources",
                                repo_type="dataset",
                                filename=f"assets/icons/new/{type2.lower()}.png"
                            )
                        image2 = Image.open(type2_path)
                        image2 = image2.resize((500, 120))
                        st.image(image2, width=120)
                st.markdown(f'Usage: {'%.2f' % (row_p['percent'].iloc[0])}%')
        else:
            with col:
                st.empty()

@st.cache_data
def load_replays(matches_df_raw, start_date, end_date):
    matches_df = matches_df_raw[['id', 'uploadtime']]
    filtered_df = matches_df[
        (matches_df["uploadtime"].dt.date >= start_date) &
        (matches_df["uploadtime"].dt.date <= end_date)
        ]

    filtered_df = filtered_df.rename(columns={"id": "Replay", "uploadtime": "Upload Date"})

    return filtered_df


parquet_dir = './output/players'

selected_format = st.selectbox('Choose a Format', sorted(formats))

bigcol1, sep, bigcol2 = st.columns([10, 1, 10])

with bigcol1:

    load_graphs(selected_format)

with sep:
    st.markdown("<div style='border-left: 1px solid #ccc; height: 100%;'></div>", unsafe_allow_html=True)

with bigcol2:

    st.subheader("Individual Player Stats by Format")
    players_df, player_list = load_parquet(selected_format)
    selected_player = st.selectbox('Choose a player', player_list)
    row, matches_df = load_player(players_df, selected_player, selected_format)
    load_player_graphs(row, selected_player, selected_format)

    key = f"{selected_player} ({selected_format})"

    selected_mode = st.selectbox('Choose a visualization mode', ['Separated', 'Combined'], key=f"{key}_mode")

    load_heatmap(row, matches_df, selected_mode, selected_format)

    load_pokemon(row, selected_format)

    st.subheader(f"Replays of {row['name']} in {selected_format}")

    col1, col2 = st.columns(2)
    with col2:

        min_date = matches_df["uploadtime"].min().date()
        max_date = matches_df["uploadtime"].max().date()

        selected_dates = st.date_input(
            "Dates",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
            label_visibility="collapsed",
            key="individual"
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

        replay_df = load_replays(matches_df, start_date, end_date)

        st.write(
            replay_df.head(st.session_state.rows_shown).to_markdown(index=False),
            unsafe_allow_html=True
        )

        if st.session_state.rows_shown < len(replay_df):
            if st.button("Load more", key=f"{key}_load"):
                st.session_state.rows_shown += 5
                st.rerun()