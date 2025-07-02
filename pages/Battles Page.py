import streamlit as st
import pandas as pd
import plotly.express as px
import os
from PIL import Image
import plotly.io as pio

if 'barmode' not in st.session_state:
    st.session_state.barmode = "Total"
if 'last_range' not in st.session_state:
    st.session_state.last_range = (None, None)


def format_quarter(q):
    year = q[:4]
    quarter = q[4:]
    return f"{year} {quarter}"


st.title("📊 Battles")



with open('./output/tiers/formats.txt', 'r') as f:
    formats = [line.strip() for line in f if line.strip()]

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

    start_index = quarters.index(start_quarter)
    end_index = quarters.index(end_quarter)
    current_range = (start_index, end_index)

    if current_range != st.session_state.last_range:
        if end_index - start_index <= 8:
            st.session_state.barmode = "Format"
        else:
            st.session_state.barmode = "Total"
        st.session_state.last_range = current_range

    barmode = st.radio("Choose visualization type", ["Total", "Format"], key="barmode")

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

    subcol1, subcol2 = st.columns(2)

    with subcol1:

        fig = pio.read_json(f"./graphs/battle/{selected_format}/fig1.json")

        st.plotly_chart(fig, use_container_width=True, config={"staticPlot": True})

        fig = pio.read_json(f"./graphs/battle/{selected_format}/fig2.json")

        st.plotly_chart(fig, use_container_width=True, config={"staticPlot": True})


    with subcol2:

        fig = pio.read_json(f"./graphs/battle/{selected_format}/fig3.json")

        st.plotly_chart(fig, use_container_width=True)

        fig = pio.read_json(f"./graphs/battle/{selected_format}/fig4.json")

        st.plotly_chart(fig, use_container_width=True)


    selected_mode = st.selectbox('Choose a visualization mode', ['Separated', 'Combined'])
    if selected_mode == 'Separated':

        subcol1, subcol2 = st.columns(2)

        with subcol1:

            fig = pio.read_json(f"./graphs/battle/{selected_format}/fig_hour.json")
            st.plotly_chart(fig, use_container_width=True)

        with subcol2:

            fig = pio.read_json(f"./graphs/battle/{selected_format}/fig_weekday.json")

            st.plotly_chart(fig, use_container_width=True)

    else:

        st.image(f"./graphs/battle/{selected_format}/heatmap.png", use_container_width=True)

with col2:

    st.markdown(f"### Most popular types in {selected_format}")

    fig = pio.read_json(f"./graphs/battle/{selected_format}/fig_types.json")

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

    st.markdown(f"### Top 6 Most Used Pokémon in {selected_format}")

    usage_df = pd.read_csv('./output/pokemon.csv', dtype={'Pdex': str})
    usage_df = usage_df[usage_df['format'] == selected_format]
    usage_df = usage_df.sort_values(by='usage', ascending=False)
    usage_df = usage_df.head(6)

    col1, col2, col3, col4, col5, col6 = st.columns([3, 3, 3, 3, 3, 3])
    cols = [col1, col2, col3, col4, col5, col6]

    for i, col in enumerate(cols):
        if i < len(usage_df):
            with col:
                row = usage_df.take([i])
                gen = selected_format.split(']')[0][1:]
                pdex = row['Pdex'].iloc[0]
                image_path = f"./assets/{gen}/{pdex}.png"
                if not os.path.exists(image_path) and '-' in pdex:
                    pdex = pdex.split('-')[0]
                    image_path = f"./assets/{gen}/{pdex}.png"
                image = Image.open(image_path)
                image = image.resize((128, 128))
                st.image(image, width=128)
                name = row['pokemon'].iloc[0]
                st.markdown(name)
                type1 = row['Type 1'].iloc[0]
                type2 = row['Type 2'].iloc[0]
                if gen != 'Gen 9':
                    if type1 == 'Fairy' or type2 == 'Fairy':
                        old_types = pd.read_csv('./input/old_types.csv')
                        old_row = old_types[old_types['pokemon'] == name]
                        type1 = old_row['Type 1'].iloc[0]
                        type2 = old_row['Type 2'].iloc[0]
                    image1 = Image.open(f"./assets/icons/old/{type1.lower()}.png")
                    image1 = image1.resize((192, 64))
                    st.image(image1, width=64)
                    if not pd.isna(type2) and type2 != "":
                        image2 = Image.open(f"./assets/icons/old/{type2.lower()}.png")
                        image2 = image2.resize((192, 64))
                        st.image(image2, width=64)
                else:
                    image1 = Image.open(f"./assets/icons/new/{type1.lower()}.png")
                    image1 = image1.resize((500, 120))
                    st.image(image1, width=120)
                    if not pd.isna(type2) and type2 != "":
                        image2 = Image.open(f"./assets/icons/new/{type2.lower()}.png")
                        image2 = image2.resize((500, 120))
                        st.image(image2, width=120)
                st.markdown(f'Usage: {'%.2f'%(row['usage'].iloc[0])}%')
        else:
            with col:
                st.empty()