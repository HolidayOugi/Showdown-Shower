import streamlit as st
import pandas as pd
import plotly.express as px
import os


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

selected_gen = st.selectbox('Choose a Gen', sorted(gens))

match_df = pd.read_csv(f'./output/matches/{selected_gen}_matches.csv')

months = sorted(match_df['year_month'].unique())
start_month = st.selectbox("Start Month", months, index=0)
end_months = [m for m in months if m >= start_month]
end_month = st.selectbox("End Month", end_months, index=len(end_months) - 1)

filtered_df = match_df[
    (match_df['year_month'] >= start_month) &
    (match_df['year_month'] <= end_month)]

fig = px.bar(
    filtered_df,
    x="year_month",
    y="count",
    color="format",
    labels={"year_month": "Month", "count": "Matches", "format": "Format"}
)

fig.update_layout(barmode='relative')
st.plotly_chart(fig, use_container_width=True)

selected_format = st.selectbox('Choose a Format', sorted(formats))

format_df = pd.read_csv(f'./output/tiers/{selected_format}.csv')

format_df_ratings = format_df.dropna(subset=['rating'])
format_df_ratings['rating'] = pd.to_numeric(format_df_ratings['rating'], errors='coerce')
format_df_ratings['Switches'] = format_df_ratings['# Switches 1']+format_df_ratings['# Switches 2']
format_df_ratings['Switch percent'] = (format_df_ratings['Switches']/format_df_ratings['Turns'])*100

fig = px.scatter(
    format_df_ratings,
    x='rating',
    y='Switch percent',
    hover_name='id',
    title='Probability of turn having a switch based on rating'
)

st.plotly_chart(fig, use_container_width=True)

max_rating = format_df_ratings['rating'].max()
min_rating = format_df_ratings['rating'].min()

format_df_ratings['rating_bin'] = pd.cut(format_df_ratings['rating'], bins=range(int(min_rating), int(max_rating), 20))

forfeit_stats = format_df_ratings.groupby('rating_bin').agg(
    total_matches=('Forfeit', 'count'),
    forfeit_count=('Forfeit', 'sum')
).reset_index()

forfeit_stats['forfeit_rate'] = (forfeit_stats['forfeit_count'] / forfeit_stats['total_matches']) * 100
forfeit_stats['rating_bin'] = forfeit_stats['rating_bin'].astype(str)

# 3. Grafico
fig = px.line(
    forfeit_stats,
    x='rating_bin',
    y='forfeit_rate',
    labels={
        'rating_bin': 'Rating',
        'forfeit_rate': 'Forfeit (%)'
    },
    title='Forfeit percentage based on rating (20 points increments)'
)

fig.update_traces(mode='lines+markers')
fig.update_layout(xaxis_showticklabels=False, yaxis_range=[0, 100])

st.plotly_chart(fig, use_container_width=True)
