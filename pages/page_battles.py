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

selected_format = st.selectbox('Choose a Format', formats)

format_df = pd.read_csv(f'./output/tiers/{selected_format}.csv')

format_df_ratings = format_df.dropna(subset=['rating'])
format_df_ratings['Switches'] = format_df_ratings['# Switches 1']+format_df_ratings['# Switches 2']

fig = px.scatter(
    format_df_ratings,
    x='rating',
    y='Turns',
    hover_name='id',
)

st.plotly_chart(fig, use_container_width=True)

fig2 = px.scatter(
    format_df_ratings,
    x='rating',
    y='Switches',
    hover_name='id',
)

st.plotly_chart(fig2, use_container_width=True)
