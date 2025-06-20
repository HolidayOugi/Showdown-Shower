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



bigcol1, sep, bigcol2, sep2, bigcol3 = st.columns([20, 1, 12, 1, 12])

with bigcol1:

    pokemon = st.selectbox('Choose a Pokémon', sorted(df['pokemon'].unique()))
    df_filtered = df[df['pokemon'] == pokemon]
    formats = df_filtered['format'].unique()
    selected_format = st.selectbox('Choose a Format', sorted(formats))
    row = df_filtered[df_filtered['format'] == selected_format].iloc[0]

    st.subheader(f"{pokemon} in {selected_format}")
    gen = selected_format.split(']')[0][1:]


    col1, col2, col3, col4 = st.columns([5, 3, 10, 10])

    with col1:

        image = Image.open(f"./assets/{gen}/{row['Pdex']}.png")
        image = image.resize((128, 128))
        st.image(image, width=128)

    with col2:
        type1 = row['Type1']
        type2 = row['Type2']
        image1 = Image.open(f"./assets/icons/{type1.lower()}.png")
        image1 = image1.resize((192, 64))
        st.image(image1, width=64)
        if not pd.isna(type2) and type2 != "":
            image2 = Image.open(f"./assets/icons/{type2.lower()}.png")
            image2 = image2.resize((192, 64))
            st.image(image2, width=64)

        gen_id = None
        if gen == 'Gen 1':
            gen_id = 'rb'
        elif gen == 'Gen 2':
            gen_id = 'gs'
        elif gen == 'Gen 3':
            gen_id = 'rs'
        elif gen == 'Gen 4':
            gen_id = 'dp'

        smogon_url = f"https://www.smogon.com/dex/{gen_id}/pokemon/{pokemon.lower()}/"
        with open('./assets/icons/smogon.png', "rb") as f:
            img_bytes = f.read()
        img_b64 = base64.b64encode(img_bytes).decode()
        html_code = f'''
                    <a href="{smogon_url}" target="_blank">
                        <img src="data:image/png;base64,{img_b64}" width="24" style="vertical-align:middle;" />
                    </a>
                    '''
        st.markdown(html_code, unsafe_allow_html=True)

    with col3:

        fig = go.Figure(data=[go.Pie(
            values=[row['won'], row['lost']],
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

    with col4:
        usage = row['usage']

        fig = go.Figure()

        fig.add_trace(go.Bar(
            x=[100],
            y=["Usage"],
            orientation='h',
            marker=dict(color="#e0e0e0"),
            hoverinfo='skip',
            showlegend=False
        ))

        fig.add_trace(go.Bar(
            x=[usage],
            y=["Usage"],
            orientation='h',
            marker=dict(color="#679afa"),
            hovertemplate='Usage: %{x}%<extra></extra>',
            showlegend=False
        ))

        fig.add_annotation(
            x=50,
            y="Usage",
            text="Usage",
            showarrow=False,
            font=dict(size=16, color='black'),
            xanchor='center',
            yanchor='middle'
        )

        fig.update_layout(
            dragmode=False,
            barmode='overlay',
            margin=dict(l=20, r=20, t=10, b=10),
            height=60,
            xaxis=dict(
                range=[0, 100],
                showticklabels=False,
                showgrid=False,
                zeroline=False
            ),
            yaxis=dict(
                showticklabels=False,
                showgrid=False,
                zeroline=False
            ),
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



    st.subheader("Stats")

    col1, col2 = st.columns([10, 1])

    with col1:


        stats = {
            'HP': row['HP'],
            'Attack': row['Attack'],
            'Defense': row['Defense'],
            'Sp. Atk': row['Sp. Atk'],
            'Sp. Def': row['Sp. Def'],
            'Speed': row['Speed']
        }

        labels = list(stats.keys())[::-1]
        values = list(stats.values())[::-1]
        max_stat = max(values)
        max_x = max(150, max_stat + 10)

        fig = go.Figure()

        fig.add_trace(go.Bar(
            x=values,
            y=labels,
            orientation='h',
            marker=dict(
                color=[
                    '#ff6969' if val < 70 else '#fffb70' if val < 100 else '#aafa9a'
                    for val in values
                ],
                line=dict(width=0)
            ),
            text=values,
            textposition='auto',
            hovertemplate='%{y}: %{x}<extra></extra>',
        ))

        fig.update_xaxes(tickfont=dict(color='white'))
        fig.update_yaxes(tickfont=dict(color='white'))

        fig.update_layout(
            xaxis=dict(range=[0, max_x]),
            dragmode=False,
            margin=dict(t=20, b=20, l=50, r=20),
            height=300,
            showlegend=False
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

        move_url = f"https://bulbapedia.bulbagarden.net/wiki/{pokemon}_(Pok%C3%A9mon)#Stats"
        with open('./assets/icons/bulba.png', "rb") as f:
            img_bytes = f.read()
        img_b64 = base64.b64encode(img_bytes).decode()
        html_code = f'''
                    <a href="{move_url}" target="_blank">
                        <img src="data:image/png;base64,{img_b64}" width="24" style="vertical-align:middle;" />
                    </a>
                    '''
        st.markdown(html_code, unsafe_allow_html=True)


    types_df = pd.read_csv('./input/types.csv')

    weak = set()
    resistant = set()
    immunity = set()
    quad_weak = set()
    quad_resistant = set()

    type1_weak = set(eval(types_df[types_df['type']  == type1]['weak'].iloc[0]))
    type1_resistant = set(eval(types_df[types_df['type']  == type1]['resistant'].iloc[0]))
    type1_immunity = set(eval(types_df[types_df['type']  == type1]['immunity'].iloc[0]))
    if not pd.isna(type2) and type2 != "":
        type2_weak = set(eval(types_df[types_df['type'] == type2]['weak'].iloc[0]))
        type2_resistant = set(eval(types_df[types_df['type'] == type2]['resistant'].iloc[0]))
        type2_immunity = set(eval(types_df[types_df['type'] == type2]['immunity'].iloc[0]))
        for t in type1_weak:
            if t in type2_weak:
                quad_weak.add(t)
            elif t in type2_resistant:
                continue
            elif t in type2_immunity:
                immunity.add(t)
            else:
                weak.add(t)
        for t in type1_resistant:
            if t in type2_weak:
                continue
            elif t in type2_resistant:
                quad_resistant.add(t)
            elif t in type2_immunity:
                immunity.add(t)
            else:
                resistant.add(t)
        for t in type1_immunity:
            immunity.add(t)

        for t in type2_weak:
            if t in type1_weak:
                quad_weak.add(t)
            elif t in type1_resistant:
                continue
            elif t in type1_immunity:
                immunity.add(t)
            else:
                weak.add(t)
        for t in type2_resistant:
            if t in type1_weak:
                continue
            elif t in type1_resistant:
                quad_resistant.add(t)
            elif t in type1_immunity:
                immunity.add(t)
            else:
                resistant.add(t)
        for t in type2_immunity:
            immunity.add(t)
    else:
        weak = type1_weak
        resistant = type1_resistant
        immunity = type1_immunity

    def render_type_row(label, types):
        if types:
            cols = st.columns(len(types) + 1)
            cols[0].markdown(f"**{label}:**")
            for i, t in enumerate(types):
                img = Image.open(f"./assets/icons/{t.lower()}.png").resize((192, 64))
                cols[i + 1].image(img, width=64)

    render_type_row("Quad weak", quad_weak)
    render_type_row("Weak", weak)
    render_type_row("Resistant", resistant)
    render_type_row("Quad resistant", quad_resistant)
    render_type_row("Immune", immunity)

with sep:
    st.markdown("<div style='border-left: 1px solid #ccc; height: 100%;'></div>", unsafe_allow_html=True)

with bigcol2:

    st.subheader(f"Most used moves by {pokemon} in {selected_format}")


    moves_df = pd.read_csv('./input/moves.csv')
    moves_df = moves_df.map(lambda x: x.lstrip() if isinstance(x, str) else x)
    moves_df = pd.merge(moves_df, types_df, on='type')

    visible_moves = st.session_state.visible_moves
    moves_to_show = row['moves'][:visible_moves]

    def hex_to_rgba(hex_color, factor):

        hex_color = hex_color.lstrip('#')
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)

        r_new = int(r + (255 - r) * factor)
        g_new = int(g + (255 - g) * factor)
        b_new = int(b + (255 - b) * factor)
        return f'rgb({r_new}, {g_new}, {b_new})'

    for move, count in moves_to_show:
        fig = go.Figure()
        move_row = moves_df[moves_df['move'].str.contains(move, case=False, na=False)]
        move_type = move_row['type'].iloc[0]
        color = move_row['color'].iloc[0]
        usage = count/(row['won']+row['lost'])

        col1, col2 = st.columns([10, 1])

        with col1:

            fig.add_trace(go.Bar(
                x=[1],
                y=[move],
                orientation='h',
                marker=dict(color=hex_to_rgba(color, 0.7)),
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

            if move_type == type1 or move_type == type2:

                fig.add_annotation(
                    x=0.5,
                    y=move,
                    text=f"<b>{move}</b>",
                    showarrow=False,
                    font=dict(size=16, color='black'),
                    xanchor='center',
                    yanchor='middle'
                )

            else:

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
                dragmode=False,
                height=60,
                margin=dict(l=20, r=20, t=5, b=5),
                barmode='overlay',
                xaxis=dict(range=[0, 1], showgrid=False, showticklabels=False, fixedrange=True),
                yaxis=dict(showticklabels=False),
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

with sep2:
    st.markdown("<div style='border-left: 1px solid #ccc; height: 100%;'></div>", unsafe_allow_html=True)

with bigcol3:

    st.subheader(f"Replays of {pokemon} in {selected_format}")
    format_df = pd.read_csv(f'./output/tiers/{selected_format}.csv')
    format_df = format_df[format_df['Team 1'].apply(lambda x: pokemon in x) | format_df['Team 2'].apply(lambda x: pokemon in x)]




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