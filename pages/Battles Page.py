import streamlit as st
import pandas as pd
import plotly.express as px
import os
from PIL import Image
import plotly.io as pio
from huggingface_hub import hf_hub_download


if 'barmode' not in st.session_state:
    st.session_state.barmode = "Total"
if 'last_range' not in st.session_state:
    st.session_state.last_range = (None, None)
if 'pokemon_shown_battles' not in st.session_state:
    st.session_state.pokemon_shown_battles = 6

def reset_pokemon_shown_battles():
    st.session_state.pokemon_shown_battles = 6


def format_quarter(q):
    year = q[:4]
    quarter = q[4:]
    return f"{year} {quarter}"

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

st.title("📊 Battles")



with open('./input/formats.txt', 'r') as f:
    formats = [line.strip() for line in f if line.strip()]

gens = sorted(
    set(f.split(']')[0].strip('[') for f in formats),
    key=lambda x: int(x.split()[1])
)

@st.cache_data
def load_graphs(selected_format):

        subcol1, subcol2 = st.columns(2)

        with subcol1:

            path = f"./output/graphs/battle/{selected_format}/fig1.json"

            if os.path.exists(path):

                fig = pio.read_json(path)
                st.plotly_chart(fig, use_container_width=True, config={"staticPlot": True},  key=f"{selected_format}_fig1")

            else:
                try:
                    fig = pio.read_json(hf_hub_download(
                        repo_id="HolidayOugi/showdown-shower-resources",
                        repo_type="dataset",
                        filename=f"graphs/battle/{selected_format}/fig1.json"
                    ))
                    st.plotly_chart(fig, use_container_width=True, config={"staticPlot": True},
                                    key=f"{selected_format}_fig1")
                except Exception as e:
                    pass

            path = f"./output/graphs/battle/{selected_format}/fig2.json"

            if os.path.exists(path):

                fig = pio.read_json(path)
                st.plotly_chart(fig, use_container_width=True, config={"staticPlot": True},
                                key=f"{selected_format}_fig2")

            else:
                try:
                    fig = pio.read_json(hf_hub_download(
                        repo_id="HolidayOugi/showdown-shower-resources",
                        repo_type="dataset",
                        filename=f"graphs/battle/{selected_format}/fig2.json"
                    ))
                    st.plotly_chart(fig, use_container_width=True, config={"staticPlot": True},
                                    key=f"{selected_format}_fig2")
                except Exception as e:
                    pass

        with subcol2:

            path = f"./output/graphs/battle/{selected_format}/fig3.json"

            if os.path.exists(path):

                fig = pio.read_json(path)
                st.plotly_chart(fig, use_container_width=True, config={"staticPlot": True},
                                key=f"{selected_format}_fig3")

            else:
                try:
                    fig = pio.read_json(hf_hub_download(
                        repo_id="HolidayOugi/showdown-shower-resources",
                        repo_type="dataset",
                        filename=f"graphs/battle/{selected_format}/fig3.json"
                    ))
                    st.plotly_chart(fig, use_container_width=True, config={"staticPlot": True},
                                    key=f"{selected_format}_fig3")
                except Exception as e:
                    pass

            path = f"./output/graphs/battle/{selected_format}/fig4.json"

            if os.path.exists(path):

                fig = pio.read_json(path)
                st.plotly_chart(fig, use_container_width=True, config={"staticPlot": True},
                                key=f"{selected_format}_fig4")

            else:
                try:
                    fig = pio.read_json(hf_hub_download(
                        repo_id="HolidayOugi/showdown-shower-resources",
                        repo_type="dataset",
                        filename=f"graphs/battle/{selected_format}/fig4.json"
                    ))
                    st.plotly_chart(fig, use_container_width=True, config={"staticPlot": True},
                                    key=f"{selected_format}_fig4")
                except Exception as e:
                    pass

@st.cache_data
def load_types(selected_format):

        st.markdown(f"### Most popular types in {selected_format}")

        path = f"./output/graphs/battle/{selected_format}/fig_types.json"

        if os.path.exists(path):
            fig = pio.read_json(path)
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
        else:
            try:
                fig = pio.read_json(hf_hub_download(
                    repo_id="HolidayOugi/showdown-shower-resources",
                    repo_type="dataset",
                    filename=f"graphs/battle/{selected_format}/fig_types.json"
                ))
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
            except Exception as e:
                pass

def load_pokemon(selected_format):

        if not os.path.exists('./output/pokemon.parquet'):
            usage_df =  pd.read_parquet(hf_hub_download(
            repo_id="HolidayOugi/showdown-shower-resources",
            repo_type="dataset",
            filename="pokemon.parquet"
        ))
        else:
            usage_df = pd.read_parquet('./output/pokemon.parquet')
        usage_df = usage_df[usage_df['format'] == selected_format]
        usage_df = usage_df.sort_values(by='usage', ascending=False)
        new_usage_df = usage_df.head(st.session_state.pokemon_shown_battles)

        num_pokemon = min(len(new_usage_df), st.session_state.pokemon_shown_battles)

        st.markdown(f"### Top {num_pokemon} Most Used Pokémon in {selected_format}")

        for row_start in range(0, len(new_usage_df), 6):
            cols = st.columns([3, 3, 3, 3, 3, 3])
            for i, col in enumerate(cols):
                idx = row_start + i
                if idx < len(new_usage_df):
                    row = new_usage_df.iloc[[idx]]
                    with col:
                        gen = selected_format.split(']')[0][1:]
                        gen_number = int(gen.split()[1])
                        if gen_number < 6:
                            gen_path = gen
                        else:
                            gen_path = 'HOME'
                        pdex = row['Pdex'].iloc[0]
                        image_path = get_image_path(gen_path, pdex)
                        st.image(image_path, width=300)
                        name = row['pokemon'].iloc[0]
                        st.markdown(name)
                        type1 = row['Type 1'].iloc[0]
                        type2 = row['Type 2'].iloc[0]
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
                        st.markdown(f'Usage: {'%.2f' % (row['usage'].iloc[0])}%')
                else:
                    with col:
                        st.empty()
        if st.session_state.pokemon_shown_battles < len(usage_df):
            if st.button("Load more", key="load_more_button"):
                st.session_state.pokemon_shown_battles += 6
                st.rerun()

@st.cache_data
def load_heatmap(selected_mode, selected_format):
    if selected_mode == 'Separated':

        subcol1, subcol2 = st.columns(2)

        with subcol1:

            path = f"./output/graphs/battle/{selected_format}/fig_hour.json"

            if os.path.exists(path):

                fig = pio.read_json(path)
                st.plotly_chart(fig, use_container_width=True,
                                key=f"{selected_format}_fig_hour")

            else:
                try:
                    fig = pio.read_json(hf_hub_download(
                        repo_id="HolidayOugi/showdown-shower-resources",
                        repo_type="dataset",
                        filename=f"graphs/battle/{selected_format}/fig_hour.json"
                    ))
                    st.plotly_chart(fig, use_container_width=True,
                                    key=f"{selected_format}_fig_hour")
                except Exception as e:
                    pass

        with subcol2:

            path = f"./output/graphs/battle/{selected_format}/fig_weekday.json"

            if os.path.exists(path):

                fig = pio.read_json(path)
                st.plotly_chart(fig, use_container_width=True,
                                key=f"{selected_format}_fig_weekday")

            else:
                try:
                    fig = pio.read_json(hf_hub_download(
                        repo_id="HolidayOugi/showdown-shower-resources",
                        repo_type="dataset",
                        filename=f"graphs/battle/{selected_format}/fig_weekday.json"
                    ))
                    st.plotly_chart(fig, use_container_width=True,
                                    key=f"{selected_format}_fig_weekday")
                except Exception as e:
                    pass

    else:

        path = f"./output/graphs/battle/{selected_format}/heatmap.png"

        if os.path.exists(path):
            st.image(path, use_container_width=True)

        else:
            try:
                path = hf_hub_download(
                    repo_id="HolidayOugi/showdown-shower-resources",
                    repo_type="dataset",
                    filename=f"graphs/battle/{selected_format}/heatmap.png"
                )
                st.image(path, use_container_width=True)
            except Exception as e:
                pass


col1, col2 = st.columns([3, 10])

with col1:

    selected_gen = st.selectbox('Choose a Gen', sorted(gens))

    if not os.path.exists(f'./output/matches/{selected_gen}_matches.parquet'):
        match_df = pd.read_parquet(hf_hub_download(
            repo_id="HolidayOugi/showdown-shower-resources",
            repo_type="dataset",
            filename=f"matches/{selected_gen}_matches.parquet"
        ))

    else:
        match_df = pd.read_parquet(f'./output/matches/{selected_gen}_matches.parquet')

    match_df['year_month'] = match_df['year_month'].dt.to_timestamp()
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

        if agg_df['format'].str.contains("ANYTHINGGOES").any():

            fig.add_bar(
                x=[None],
                y=[None],
                name="<span style='visibility:hidden'>Format ANYTHINGGOES</span>",
                marker=dict(color="rgba(0,0,0,0)"),
                showlegend=True
            )
        else:

            fig.add_bar(
                x=[None],
                y=[None],
                name="<span style='visibility:hidden'>Format UBERS</span>",
                marker=dict(color="rgba(0,0,0,0)"),
                showlegend=True
            )

    st.plotly_chart(fig, use_container_width=True)

selected_format = st.selectbox('Choose a Format', sorted(formats), on_change=reset_pokemon_shown_battles)

col1, col2 = st.columns([10, 7])

with col1:
    load_graphs(selected_format)
    selected_mode = st.selectbox('Choose a visualization mode', ['Separated', 'Combined'])
    load_heatmap(selected_mode, selected_format)

with col2:
    load_types(selected_format)
    load_pokemon(selected_format)