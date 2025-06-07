import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
from collections import Counter
from PIL import Image

def format_quarter(q):
    year = q[:4]
    quarter = q[4:]
    return f"{year} {quarter}"


st.title("📊 Battles")

formats = [
    os.path.splitext(df)[0]
    for df in os.listdir('./output/tiers')
    if df.endswith(".csv")
]

gens = sorted(
    set(f.split(']')[0].strip('[') for f in formats),
    key=lambda x: int(x.split()[1])
)

col1, col2 = st.columns([3, 10])

with col1:

    selected_gen = st.selectbox('Choose a Gen', sorted(gens))

    match_df = pd.read_csv(f'./output/matches/{selected_gen}_matches.csv')

    match_df['year_month'] = pd.to_datetime(match_df['year_month'], format='%Y-%m')
    match_df['quarter'] = match_df['year_month'].dt.to_period('Q').astype(str)

    match_df['quarter'] = match_df['quarter'].apply(format_quarter)


    quarters = sorted(match_df['quarter'].unique())
    start_quarter = st.selectbox("Start Quarter", quarters, index=0)
    end_quarters = [q for q in quarters if q >= start_quarter]
    end_quarter = st.selectbox("End Quarter", end_quarters, index=len(end_quarters) - 1)

    filtered_df = match_df[
        (match_df['quarter'] >= start_quarter) &
        (match_df['quarter'] <= end_quarter)
    ]

    agg_df = filtered_df.groupby(['quarter', 'format']).agg({'count': 'sum'}).reset_index()
    barmode  = st.radio("Choose visualization type", ["Total", "Format"])

with col2:
    if barmode == "Format":
        agg_df = agg_df.sort_values(by=["quarter","format"])
        fig = px.bar(
            agg_df,
            x="quarter",
            y="count",
            color="format",
            labels={"quarter": "Quarter", "count": "Matches", "format": "Format"},
        )
        fig.update_layout(
            barmode="relative",
            legend=dict(
                x=1.02,
                y=1,
                bgcolor="rgba(0,0,0,0)",
                bordercolor="rgba(0,0,0,0)"
            )
        )

    else:
        total_df = agg_df.groupby("quarter", as_index=False).agg({"count": "sum"})

        fig = px.bar(
            total_df,
            x="quarter",
            y="count",
            color_discrete_sequence=["#8d8c95"],
            labels={"quarter": "Quarter", "count": "Matches", "format": "Format"},
        )
        fig.update_layout(
            barmode="relative",
            showlegend=True,
            legend=dict(
                x=1.02,
                y=1,
                bgcolor="rgba(0,0,0,0)",
                bordercolor="rgba(0,0,0,0)"
            )
        )

        fig.add_bar(
            x=[None],
            y=[None],
            name="<span style='visibility:hidden'>Format UBERS</span>",
            marker=dict(color="rgba(0,0,0,0)"),
            showlegend=True
        )

    st.plotly_chart(fig, use_container_width=True)

selected_format = st.selectbox('Choose a Format', sorted(formats))

col1, col2 = st.columns([10,7])

with col1:

    format_df = pd.read_csv(f'./output/tiers/{selected_format}.csv')

    subcol1, subcol2 = st.columns(2)

    with subcol1:

        format_df['rating'] = pd.to_numeric(format_df['rating'], errors='coerce')
        format_df_ratings = format_df.dropna(subset=['rating'])
        print(format_df_ratings['rating'].isna().sum())
        format_df_ratings['Switches'] = format_df_ratings['# Switches 1']+format_df_ratings['# Switches 2']
        format_df_ratings['Switch percent'] = (format_df_ratings['Switches']/format_df_ratings['Turns'])*100

        fig = px.scatter(
            format_df_ratings,
            x='rating',
            y='Switch percent',
            labels={
                'rating': 'Rating',
                'Switch percent': 'Switch (%)'
            },
            hover_name='id',
            title=f'Probability of turn having a switch<br>based on rating in {selected_format}'
        )

        st.plotly_chart(fig, use_container_width=True)

        fig = px.scatter(
            format_df_ratings,
            x='rating',
            y='Turns',
            labels={
                'rating': 'Rating',
                'Turns': 'Turns'
            },
            hover_name='id',
            title=f'Number of turns based on rating in {selected_format}'
        )

        st.plotly_chart(fig, use_container_width=True)

        format_df["uploadtime"] = pd.to_datetime(format_df["uploadtime"])
        format_df['hour'] = format_df['uploadtime'].dt.hour
        bins = list(range(0, 25, 2))
        labels = [f"{b}-{b + 2}" for b in bins[:-1]]
        format_df['hour_bin'] = pd.cut(format_df['hour'], bins=bins, right=False, labels=labels)
        hour_counts = format_df['hour_bin'].value_counts().sort_index().reset_index()
        hour_counts.columns = ['hour_bin', 'matches']
        hour_counts['hour_bin'] = hour_counts['hour_bin'].astype(str)


        fig = px.bar(hour_counts,
                      x='hour_bin', y='matches',
                      labels={'hour_bin': 'Hours', 'matches': '# Matches'},
                      title=f'Frequency of matches during certain hours (GMT) in {selected_format}')

        fig.update_xaxes(type='category')
        st.plotly_chart(fig, use_container_width=True)

    with subcol2:

        max_rating = format_df_ratings['rating'].max()
        min_rating = format_df_ratings['rating'].min()

        format_df_ratings['rating_bin'] = pd.cut(format_df_ratings['rating'], bins=range(int(min_rating)-20, int(max_rating)+20, 20))

        forfeit_stats = format_df_ratings.groupby('rating_bin').agg(
            total_matches=('Forfeit', 'count'),
            forfeit_count=('Forfeit', 'sum')
        ).reset_index()

        forfeit_stats['forfeit_rate'] = (forfeit_stats['forfeit_count'] / forfeit_stats['total_matches']) * 100
        forfeit_stats['rating_bin'] = forfeit_stats['rating_bin'].astype(str)

        fig = px.line(
            forfeit_stats,
            x='rating_bin',
            y='forfeit_rate',
            labels={
                'rating_bin': 'Rating',
                'forfeit_rate': 'Forfeit (%)'
            },
            title=f'Forfeit percentage based on rating<br>(20 points increments) in {selected_format}'
        )

        fig.update_traces(mode='lines+markers')
        fig.update_layout(xaxis_showticklabels=False, yaxis_range=[0, 100])

        st.plotly_chart(fig, use_container_width=True)


        def team_similarity(row):
            team1 = set([p.strip() for p in row['Team 1'].split(",")])
            team2 = set([p.strip() for p in row['Team 2'].split(",")])
            intersection = len(team1.intersection(team2))
            if len(team2) < len(team1):
                sim_percent = intersection / len(team2)
            else:
                sim_percent = intersection / len(team1)
            return sim_percent*100


        format_df_ratings['team_similarity'] = format_df_ratings.apply(team_similarity, axis=1)
        agg = format_df_ratings.groupby('rating_bin')['team_similarity'].mean().reset_index()

        agg['rating_bin'] = agg['rating_bin'].astype(str)

        fig = px.line(
            agg,
            x='rating_bin',
            y='team_similarity',
            labels={
                'rating_bin': 'Rating',
                'team_similarity': 'Mean Team Similarity (%)'
            },
            title=f'Team Similarity percentage based on rating<br>(20 points increments) in {selected_format}'
        )

        fig.update_traces(mode='lines+markers')
        fig.update_layout(xaxis_showticklabels=False, yaxis_range=[0, 100])
        st.plotly_chart(fig, use_container_width=True)

        format_df['weekday'] = format_df['uploadtime'].dt.weekday
        weekday_count = format_df.groupby('weekday').size().reset_index(name='count')
        weekday_count['weekday_name'] = weekday_count['weekday'].map({
            0: 'Monday', 1: 'Tuesday', 2: 'Wednesday', 3: 'Thursday', 4: 'Friday', 5: 'Saturday', 6: 'Sunday'
        })

        weekday_count = weekday_count.sort_values('weekday')

        fig = px.bar(weekday_count,
                     x='weekday_name',
                     y='count',
                     labels={
                         'weekday_name': 'Weekday',
                         'count': '# Matches'
                     },
                     title=f'Frequency of matches during certain days (GMT) in {selected_format}')

        st.plotly_chart(fig, use_container_width=True)

with col2:


    format_df['Team 1'] = format_df['Team 1'].apply(eval)
    format_df['Team 2'] = format_df['Team 2'].apply(eval)
    format_df['full_team'] = format_df.apply(lambda row: list(set(row['Team 1'] + row['Team 2'])), axis=1)
    pokemon_df = pd.read_csv('./input/pokemon_stats.csv')
    types_df =  pd.read_csv('./input/types.csv')
    types_df['count'] = 0

    poke_types = pokemon_df.set_index('pokemon')[['Type1', 'Type2']].to_dict(orient='index')

    type_counter = Counter()

    for team in format_df['full_team']:
        types_seen = set()
        for member in team:
            if member not in poke_types:
                continue
            type1 = poke_types[member]['Type1']
            type2 = poke_types[member]['Type2']

            if type1 and type1 not in types_seen:
                type_counter[type1] += 1
                types_seen.add(type1)

            if pd.notna(type2) and type2 != "" and type2 not in types_seen:
                type_counter[type2] += 1
                types_seen.add(type2)

    types_df['count'] = types_df['type'].map(type_counter).fillna(0).astype(int)

    types_df = types_df[types_df['count'] > 0].sort_values(by='count', ascending=False)
    types_total = types_df['count'].sum()
    types_df['proportion'] = types_df['count'] / types_total

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=types_df['proportion'],
        y=['bar'] * len(types_df),
        orientation='h',
        marker=dict(color=types_df['color']),
        customdata=types_df[['type', 'count']],
        hovertemplate='%{customdata[0]}: %{customdata[1]} (%{x:.1%})<extra></extra>'
    ))

    fig.update_layout(
        height=50,
        margin=dict(l=0, r=0, t=10, b=10),
        xaxis=dict(visible=False, fixedrange=True),
        yaxis=dict(visible=False, fixedrange=True),
        showlegend=False,
        barmode='stack',
    )

    st.markdown(f"### Most popular types in {selected_format}")
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

    st.markdown(f"### Top 5 Most Used Pokémon in {selected_format}")

    usage_df = pd.read_csv('./output/pokemon.csv')
    usage_df = usage_df[usage_df['format'] == selected_format]
    usage_df = usage_df.sort_values(by='usage', ascending=False)
    usage_df = usage_df.head(5)

    col1, col2, col3, col4, col5 = st.columns([3, 3, 3, 3, 3])
    cols = [col1, col2, col3, col4, col5]

    for i, col in enumerate(cols):
        if i < len(usage_df):
            with col:
                row = usage_df.take([i])
                gen = selected_format.split(']')[0][1:]
                pdex = row['Pdex'].iloc[0]
                image = Image.open(f"./assets/{gen}/{pdex}.png")
                image = image.resize((128, 128))
                st.image(image, width=128)
                st.markdown(row['pokemon'].iloc[0])
                type1 = row['Type1'].iloc[0]
                type2 = row['Type2'].iloc[0]
                image1 = Image.open(f"./assets/icons/{type1.lower()}.png")
                image1 = image1.resize((192, 64))
                st.image(image1, width=64)
                if not pd.isna(type2) and type2 != "":
                    image2 = Image.open(f"./assets/icons/{type2.lower()}.png")
                    image2 = image2.resize((192, 64))
                    st.image(image2, width=64)
                st.markdown(f'Usage: {'%.2f'%(row['usage'].iloc[0])}%')
        else:
            with col:
                st.empty()