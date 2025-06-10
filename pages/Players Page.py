import streamlit as st
import pandas as pd
from PIL import Image
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
import os

sns.set(rc={'ytick.labelcolor': 'white', 'xtick.labelcolor': 'white'})
sns.set(rc={'axes.facecolor': '#0000FF', 'figure.facecolor': (0, 0, 0, 0)})

st.title("👤 Players")

if 'rows_shown' not in st.session_state:
    st.session_state.rows_shown = 5

formats = [
    os.path.splitext(df)[0]
    for df in os.listdir('./output/tiers')
    if df.endswith(".csv")
]

selected_format = st.selectbox('Choose a Format', sorted(formats))

players_df = pd.read_csv(f'./output/players/{selected_format}_players.csv')
players_df['rating_delta'] = players_df['highest_rating'] - players_df['lowest_rating']
players_df['pokemon_used'] = players_df['pokemon_used'].apply(eval)
players_df_filtered = players_df[players_df['played'] >= 10]
pokemon_df = pd.read_csv('./input/pokemon_stats.csv')
bigcol1, sep, bigcol2 = st.columns([10, 1, 10])

with bigcol1:

    st.subheader("Total Player Stats")

    col1, col2 = st.columns(2)

    with col1:
        players_df['first_played'] = pd.to_datetime(players_df['first_played'])
        players_df['last_played'] = pd.to_datetime(players_df['last_played'])

        players_df['time_difference'] = (players_df['last_played'] - players_df['first_played']).dt.days
        players_df = players_df.sort_values('time_difference', ascending=False)

        fig = px.scatter(
            players_df,
            x='rating_delta',
            y='time_difference',
            labels={
                'rating_delta': 'Rating Delta',
                'time_difference': 'Days between 1st and last match'
            },
            hover_name='name',
            title=f'Time difference between 1st and last match<br>based on rating delta in {selected_format}'
        )

        st.plotly_chart(fig, use_container_width=True)

        fig = px.scatter(
            players_df,
            x='highest_rating',
            y='played',
            labels={
                'highest_rating': 'Max Rating',
                'played': 'Matches Played',
            },
            hover_name='name',
            title=f'Correlation between Max Rating and<br>Matches Played in {selected_format}'
        )

        st.plotly_chart(fig, use_container_width=True)

    with col2:

        players_df_filtered['winrate'] = (players_df_filtered['wins'] / players_df_filtered['played'])*100
        fig = px.histogram(
            players_df_filtered,
            x='winrate',
            nbins=20,
            title=f'Winrate distribution in {selected_format}<br>'
                  f'with 10 or more matches played',
            labels={'winrate': 'Winrate'},
            opacity=0.75
        )

        fig.update_xaxes(range=[0, 100], tickmode='linear', dtick=10)

        fig.update_layout(yaxis_title='# Players')

        st.plotly_chart(fig, use_container_width=True, config={'staticPlot': True})

        fig = px.histogram(
            players_df_filtered,
            x='rating_delta',
            nbins=10,
            title=f'Rating Delta in {selected_format}<br>'
                  f'with 10 or more matches played',
            labels={'rating_delta': 'Rating Delta'},
            opacity=0.75
        )

        fig.update_layout(yaxis_title='# Players')

        fig.update_xaxes(tickmode='linear', dtick=100)

        st.plotly_chart(fig, use_container_width=True, config={'staticPlot': True})

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
        })

    with col2:
        st.markdown(f"First Played: {row['first_played']}")
        st.markdown(f"Last Played: {row['last_played']}")

    with col3:
        if row['lowest_rating'] > 0 and row['highest_rating'] > 0:
            st.markdown(f"Min Rating: {row['lowest_rating']}")
            st.markdown(f"Max Rating: {row['highest_rating']}")

    if isinstance(row['rating_list'], str):

        row['rating_list'] = eval(row['rating_list'])


        rating_list = row['rating_list']


        if rating_list:

            df_rating = pd.DataFrame({
                'Match': list(range(1, len(rating_list) + 1)),
                'Rating': rating_list
            })

            df_rating['Smoothed Rating'] = df_rating['Rating'].rolling(window=20, min_periods=1).mean()

            fig = px.line(df_rating, x='Match', y='Smoothed Rating',
                          title=f"Rating history for {selected_player} in {selected_format}",
                          markers=False)

            st.plotly_chart(fig, use_container_width=True)

    format_df = pd.read_csv(f'./output/tiers/{selected_format}.csv')
    format_df = format_df[(format_df['player1'] == row['name']) | (format_df['player2'] == row['name'])]
    format_df["uploadtime"] = pd.to_datetime(format_df["uploadtime"])
    format_df['weekday'] = format_df['uploadtime'].dt.weekday
    format_df['weekday'] = format_df['weekday'].map({
        0: 'Monday', 1: 'Tuesday', 2: 'Wednesday', 3: 'Thursday', 4: 'Friday', 5: 'Saturday', 6: 'Sunday'
    })
    format_df['hour'] = format_df['uploadtime'].dt.hour
    bins = list(range(0, 25, 2))
    labels = [f"{b}-{b + 2}" for b in bins[:-1]]
    format_df['hour_bin'] = pd.cut(format_df['hour'], bins=bins, right=False, labels=labels)

    selected_mode = st.selectbox('Choose a visualization mode', ['Separated', 'Combined'])
    if selected_mode == 'Separated':

        weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        format_df['weekday'] = pd.Categorical(format_df['weekday'], categories=weekday_order, ordered=True)

        col1, col2 = st.columns(2)

        with col1:


            hour_counts = format_df['hour_bin'].value_counts().sort_index().reset_index()
            hour_counts.columns = ['hour_bin', 'matches']
            hour_counts['hour_bin'] = hour_counts['hour_bin'].astype(str)

            fig = px.bar(hour_counts,
                         x='hour_bin', y='matches',
                         labels={'hour_bin': 'Hours', 'matches': '# Matches'},
                         title=f'Frequency of matches during certain hours (GMT)<br>by {row['name']} in {selected_format}')

            fig.update_xaxes(type='category')
            st.plotly_chart(fig, use_container_width=True)

        with col2:

            weekday_count = format_df.groupby('weekday').size().reset_index(name='count')

            weekday_count = weekday_count.sort_values('weekday')

            fig = px.bar(weekday_count,
                         x='weekday',
                         y='count',
                         labels={
                             'weekday': 'Weekday',
                             'count': '# Matches'
                         },
                         title=f'Frequency of matches during certain days (GMT)<br>by {row['name']} in {selected_format}')

            st.plotly_chart(fig, use_container_width=True)

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

        format_df = format_df.drop(columns=['format', 'hour', 'hour_bin', 'weekday', 'rating', 'player1', 'player2', 'Winner', 'Forfeit', 'Team 1', 'Team 2', 'Turns', '# Switches 1', '# Switches 2'])
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