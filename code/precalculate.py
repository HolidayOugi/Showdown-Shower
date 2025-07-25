import pandas as pd
import plotly.express as px
import plotly.io as pio
import seaborn as sns
import matplotlib.pyplot as plt
from collections import Counter
import plotly.graph_objects as go
import os
import glob
import numpy as np
import warnings
from tqdm import tqdm

warnings.simplefilter('ignore')

def precalculate(input_folder, output_folder, format_list=None):


    sns.set(rc={'ytick.labelcolor': 'white', 'xtick.labelcolor': 'white'})
    sns.set(rc={'axes.facecolor': '#0000FF', 'figure.facecolor': (0, 0, 0, 0)})

    def battle():
        if format_list is None:
            with open('../input/formats.txt', 'r') as f:
                formats = [line.strip() for line in f if line.strip()]
        else:
            formats = format_list

        for format in tqdm(formats, desc=f"Calculating battle graphs"):
            print(format)
            df_path = f'{input_folder}/tiers/{format}.parquet'
            path = f'{output_folder}/battle/{format}'
            os.makedirs(path, exist_ok=True)

            if os.path.exists(df_path):
                format_df = pd.read_parquet(df_path)

            else:
                pattern = glob.escape(f'{input_folder}/tiers/{format}') + "_*.parquet"
                parts = sorted(glob.glob(pattern))

                if parts:
                    part_dfs = [pd.read_parquet(part) for part in parts]
                    format_df = pd.concat(part_dfs, ignore_index=True)

                else:
                    continue

            format_df['rating'] = pd.to_numeric(format_df['rating'], errors='coerce')
            format_df_ratings = format_df.dropna(subset=['rating'])
            format_df_ratings['Switches'] = format_df_ratings['# Switches 1'] + format_df_ratings['# Switches 2']
            format_df_ratings['Switch percent'] = (format_df_ratings['Switches'] / format_df_ratings['Turns']) * 100
            format_df['Team 1'] = format_df['Team 1'].apply(lambda x: list(x) if isinstance(x, (list, np.ndarray)) else x)
            format_df['Team 2'] = format_df['Team 2'].apply(lambda x: list(x) if isinstance(x, (list, np.ndarray)) else x)

            fig = px.scatter(
                format_df_ratings,
                x='rating',
                y='Switch percent',
                labels={
                    'rating': 'Rating',
                    'Switch percent': 'Switch (%)'
                },
                hover_name='id',
                title=f'Probability of turn having a switch<br>based on rating in {format}'
            )

            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=0, r=0, t=100, b=0),
                font=dict(
                    color='white',
                    size=16
                ),
                title=dict(
                    text=fig.layout.title.text,
                    y=0.95,
                    x=0.5,
                    xanchor='center'
                ),
                title_font=dict(
                    size=20,
                    color='white'
                ),
                legend_font=dict(
                    size=14
                )
            )

            fig.update_xaxes(
                color='white',
                tickfont=dict(size=14),
                showgrid=False
            )

            fig.update_yaxes(
                color='white',
                tickfont=dict(size=14),
                gridcolor='rgba(255, 255, 255, 0.1)',
                zeroline=False
            )

            pio.write_image(
                fig,
                f'{output_folder}/battle/{format}/fig1.png',
                format='png',
                width=800,
                height=600
            )

            fig = px.scatter(
                format_df_ratings,
                x='rating',
                y='Turns',
                labels={
                    'rating': 'Rating',
                    'Turns': 'Turns'
                },
                hover_name='id',
                title=f'Number of turns based on rating in {format}'
            )

            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=0, r=0, t=100, b=0),
                font=dict(
                    color='white',
                    size=16
                ),
                title=dict(
                    text=fig.layout.title.text,
                    y=0.95,
                    x=0.5,
                    xanchor='center'
                ),
                title_font=dict(
                    size=20,
                    color='white'
                ),
                legend_font=dict(
                    size=14
                )
            )

            fig.update_xaxes(
                color='white',
                tickfont=dict(size=14),
                showgrid=False
            )

            fig.update_yaxes(
                color='white',
                tickfont=dict(size=14),
                gridcolor='rgba(255, 255, 255, 0.1)',
                zeroline=False
            )

            pio.write_image(
                fig,
                f'{output_folder}/battle/{format}/fig2.png',
                format='png',
                width=800,
                height=600
            )

            max_rating = format_df_ratings['rating'].max()
            min_rating = format_df_ratings['rating'].min()

            if not (pd.isna(min_rating) or pd.isna(max_rating)):

                format_df_ratings['rating_bin'] = pd.cut(format_df_ratings['rating'],
                                                         bins=range(int(min_rating) - 20, int(max_rating) + 20, 20))

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
                    title=f'Forfeit percentage based on rating<br>(20 points increments) in {format}'
                )

                fig.update_traces(mode='lines+markers')
                fig.update_layout(xaxis_showticklabels=False, yaxis_range=[0, 100])

                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    margin=dict(l=0, r=0, t=100, b=0),
                    font=dict(
                        color='white',
                        size=16
                    ),
                    title=dict(
                        text=fig.layout.title.text,
                        y=0.95,
                        x=0.5,
                        xanchor='center'
                    ),
                    title_font=dict(
                        size=20,
                        color='white'
                    ),
                    legend_font=dict(
                        size=14
                    )
                )

                fig.update_xaxes(
                    color='white',
                    tickfont=dict(size=14),
                    showgrid=False
                )

                fig.update_yaxes(
                    color='white',
                    tickfont=dict(size=14),
                    gridcolor='rgba(255, 255, 255, 0.1)',
                    zeroline=False
                )

                pio.write_image(
                    fig,
                    f'{output_folder}/battle/{format}/fig3.png',
                    format='png',
                    width=800,
                    height=600
                )

                def team_similarity(row):
                    team1 = row['Team 1']
                    team2 = row['Team 2']

                    if isinstance(team1, str):
                        team1 = [p.strip() for p in team1.split(',')]
                    if isinstance(team2, str):
                        team2 = [p.strip() for p in team2.split(',')]

                    if isinstance(team1, np.ndarray):
                        team1 = list(team1)
                    if isinstance(team2, np.ndarray):
                        team2 = list(team2)

                    if not isinstance(team1, list) or not isinstance(team2, list):
                        return np.nan

                    set1 = set(team1)
                    set2 = set(team2)

                    if not set1 or not set2:
                        return 0.0

                    intersection = len(set1.intersection(set2))
                    base = min(len(set1), len(set2))
                    return (intersection / base) * 100 if base > 0 else 0.0


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
                    title=f'Team Similarity percentage based on rating<br>(20 points increments) in {format}'
                )

                fig.update_traces(mode='lines+markers')
                fig.update_layout(xaxis_showticklabels=False, yaxis_range=[0, 100])

                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    margin=dict(l=0, r=0, t=100, b=0),
                    font=dict(
                        color='white',
                        size=16
                    ),
                    title=dict(
                        text=fig.layout.title.text,
                        y=0.95,
                        x=0.5,
                        xanchor='center'
                    ),
                    title_font=dict(
                        size=20,
                        color='white'
                    ),
                    legend_font=dict(
                        size=14
                    )
                )

                fig.update_xaxes(
                    color='white',
                    tickfont=dict(size=14),
                    showgrid=False
                )

                fig.update_yaxes(
                    color='white',
                    tickfont=dict(size=14),
                    gridcolor='rgba(255, 255, 255, 0.1)',
                    zeroline=False
                )

                pio.write_image(
                    fig,
                    f'{output_folder}/battle/{format}/fig4.png',
                    format='png',
                    width=800,
                    height=600
                )

            format_df["uploadtime"] = pd.to_datetime(format_df["uploadtime"])
            format_df['weekday'] = format_df['uploadtime'].dt.weekday
            format_df['weekday'] = format_df['weekday'].map({
                0: 'Monday', 1: 'Tuesday', 2: 'Wednesday', 3: 'Thursday', 4: 'Friday', 5: 'Saturday', 6: 'Sunday'
            })
            format_df['hour'] = format_df['uploadtime'].dt.hour
            bins = list(range(0, 25, 2))
            labels = [f"{b}-{b + 2}" for b in bins[:-1]]
            format_df['hour_bin'] = pd.cut(format_df['hour'], bins=bins, right=False, labels=labels)

            weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            ordered_hours = sorted(format_df['hour_bin'].unique(), key=lambda x: int(x.split('-')[0]))

            fig_hour = px.histogram(
                format_df,
                x='hour_bin',
                nbins=len(format_df['hour_bin'].unique()),
                category_orders={'hour_bin': ordered_hours},
                labels={'hour_bin': 'Hours'},
                title=f'Frequency of matches during certain hours (GMT) in {format}'
            )
            fig_hour.update_xaxes(type='category')
            fig_hour.update_layout(bargap=0)
            fig_hour.update_layout(yaxis_title='# Matches')

            fig_hour.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=0, r=0, t=100, b=0),
                font=dict(
                    color='white',
                    size=16
                ),
                title=dict(
                    text=fig_hour.layout.title.text,
                    y=0.95,
                    x=0.5,
                    xanchor='center'
                ),
                title_font=dict(
                    size=20,
                    color='white'
                ),
                legend_font=dict(
                    size=14
                )
            )

            fig_hour.update_xaxes(
                color='white',
                tickfont=dict(size=14),
                showgrid=False
            )

            fig_hour.update_yaxes(
                color='white',
                tickfont=dict(size=14),
                gridcolor='rgba(255, 255, 255, 0.1)',
                zeroline=False
            )

            pio.write_image(
                fig_hour,
                f'{output_folder}/battle/{format}/fig_hour.png',
                format='png',
                width=800,
                height=600
            )

            fig_weekday = px.histogram(
                format_df,
                x='weekday',
                nbins=7,
                category_orders={'weekday': weekday_order},
                labels={'weekday': 'Weekday', 'matches': '# Matches'},
                title=f'Frequency of matches during certain days (GMT) in {format}'
            )
            fig_weekday.update_xaxes(type='category')
            fig_weekday.update_layout(bargap=0)
            fig_weekday.update_layout(yaxis_title='# Matches')

            fig_weekday.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=0, r=0, t=100, b=0),
                font=dict(
                    color='white',
                    size=16
                ),
                title=dict(
                    text=fig_weekday.layout.title.text,
                    y=0.95,
                    x=0.5,
                    xanchor='center'
                ),
                title_font=dict(
                    size=20,
                    color='white'
                ),
                legend_font=dict(
                    size=14
                )
            )

            fig_weekday.update_xaxes(
                color='white',
                tickfont=dict(size=14),
                showgrid=False
            )

            fig_weekday.update_yaxes(
                color='white',
                tickfont=dict(size=14),
                gridcolor='rgba(255, 255, 255, 0.1)',
                zeroline=False
            )

            pio.write_image(
                fig_weekday,
                f'{output_folder}/battle/{format}/fig_weekday.png',
                format='png',
                width=800,
                height=600
            )

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
                fmt=".0f",
                cmap='YlOrRd',
                linewidths=.5,
                ax=ax,
            )

            fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
            ax.set_title(f'Distribution of Matches per Weekday and Hour Interval (GMT) in {format}', color='white')
            ax.set_xlabel('Hour Interval')
            ax.set_ylabel('Weekday')
            ax.xaxis.label.set_color('white')
            ax.yaxis.label.set_color('white')

            plt.tight_layout()
            fig.savefig(f'{output_folder}/battle/{format}/heatmap.png', bbox_inches='tight')
            plt.close(fig)

            format_df['full_team'] = format_df.apply(lambda row: list(set(row['Team 1'] + row['Team 2'])), axis=1)
            pokemon_df = pd.read_csv('../input/pokemon_stats.csv')
            types_df = pd.read_csv('../input/types.csv')
            types_df['count'] = 0

            poke_types = pokemon_df.set_index('pokemon')[['Type 1', 'Type 2']].to_dict(orient='index')

            type_counter = Counter()

            for team in format_df['full_team']:
                types_seen = set()
                for member in team:
                    if member not in poke_types:
                        continue
                    type1 = poke_types[member]['Type 1']
                    type2 = poke_types[member]['Type 2']

                    if type1 and type1 not in types_seen:
                        type_counter[type1] += 1
                        types_seen.add(type1)

                    if pd.notna(type2) and type2 != "" and type2 not in types_seen:
                        type_counter[type2] += 1
                        types_seen.add(type2)

            types_df['count'] = types_df['Type'].map(type_counter).fillna(0).astype(int)

            types_df = types_df[types_df['count'] > 0].sort_values(by='count', ascending=False)
            types_total = types_df['count'].sum()
            types_df['proportion'] = types_df['count'] / types_total

            fig = go.Figure()

            fig.add_trace(go.Bar(
                x=types_df['proportion'],
                y=['bar'] * len(types_df),
                orientation='h',
                marker=dict(color=types_df['color']),
                customdata=types_df[['Type', 'count']],
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

            pio.write_json(fig, f'{output_folder}/battle/{format}/fig_types.json')

    def players():

        if format_list is None:
            with open('../input/formats.txt', 'r') as f:
                formats = [line.strip() for line in f if line.strip()]
        else:
            formats = format_list

        for format in tqdm(formats, desc=f"Calculating player graphs"):
            print(format)
            players_path = f'{input_folder}/players/{format}_players.parquet'
            path = f'{output_folder}/players/{format}'
            os.makedirs(path, exist_ok=True)

            if os.path.exists(players_path):
                players_df = pd.read_parquet(players_path)
            else:
                continue


            players_df['rating_delta'] = players_df['highest_rating'] - players_df['lowest_rating']
            players_df['pokemon_used'] = players_df['pokemon_used'].apply(eval)
            players_df_filtered = players_df[players_df['played'] >= 10]

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
                title=f'Time difference between 1st and last match<br>based on rating delta in {format}'
            )

            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=0, r=0, t=100, b=0),
                font=dict(
                    color='white',
                    size=16
                ),
                title=dict(
                    text=fig.layout.title.text,
                    y=0.95,
                    x=0.5,
                    xanchor='center'
                ),
                title_font=dict(
                    size=20,
                    color='white'
                ),
                legend_font=dict(
                    size=14
                )
            )

            fig.update_xaxes(
                color='white',
                tickfont=dict(size=14),
                showgrid=False
            )

            fig.update_yaxes(
                color='white',
                tickfont=dict(size=14),
                gridcolor='rgba(255, 255, 255, 0.1)',
                zeroline=False
            )

            pio.write_image(
                fig,
                f'{output_folder}/players/{format}/fig1.png',
                format='png',
                width=800,
                height=600
            )

            fig = px.scatter(
                players_df,
                x='highest_rating',
                y='played',
                labels={
                    'highest_rating': 'Max Rating',
                    'played': 'Matches Played',
                },
                hover_name='name',
                title=f'Correlation between Max Rating and<br>Matches Played in {format}'
            )

            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=0, r=0, t=100, b=0),
                font=dict(
                    color='white',
                    size=16
                ),
                title=dict(
                    text=fig.layout.title.text,
                    y=0.95,
                    x=0.5,
                    xanchor='center'
                ),
                title_font=dict(
                    size=20,
                    color='white'
                ),
                legend_font=dict(
                    size=14
                )
            )

            fig.update_xaxes(
                color='white',
                tickfont=dict(size=14),
                showgrid=False
            )

            fig.update_yaxes(
                color='white',
                tickfont=dict(size=14),
                gridcolor='rgba(255, 255, 255, 0.1)',
                zeroline=False
            )

            pio.write_image(
                fig,
                f'{output_folder}/players/{format}/fig2.png',
                format='png',
                width=800,
                height=600
            )

            players_df_filtered['winrate'] = (players_df_filtered['wins'] / players_df_filtered['played']) * 100
            fig = px.histogram(
                players_df_filtered,
                x='winrate',
                nbins=20,
                title=f'Winrate distribution in {format}<br>'
                      f'with 10 or more matches played',
                labels={'winrate': 'Winrate'},
                opacity=0.75
            )

            fig.update_xaxes(range=[0, 100], tickmode='linear', dtick=10)

            fig.update_layout(yaxis_title='# Players')

            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=0, r=0, t=100, b=0),
                font=dict(
                    color='white',
                    size=16
                ),
                title=dict(
                    text=fig.layout.title.text,
                    y=0.95,
                    x=0.5,
                    xanchor='center'
                ),
                title_font=dict(
                    size=20,
                    color='white'
                ),
                legend_font=dict(
                    size=14
                )
            )

            fig.update_xaxes(
                color='white',
                tickfont=dict(size=14),
                showgrid=False
            )

            fig.update_yaxes(
                color='white',
                tickfont=dict(size=14),
                gridcolor='rgba(255, 255, 255, 0.1)',
                zeroline=False
            )

            pio.write_image(
                fig,
                f'{output_folder}/players/{format}/fig3.png',
                format='png',
                width=800,
                height=600
            )

            fig = px.histogram(
                players_df_filtered,
                x='rating_delta',
                nbins=10,
                title=f'Rating Delta in {format}<br>'
                      f'with 10 or more matches played',
                labels={'rating_delta': 'Rating Delta'},
                opacity=0.75
            )

            fig.update_layout(yaxis_title='# Players')

            fig.update_xaxes(tickmode='linear', dtick=100)

            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=0, r=0, t=100, b=0),
                font=dict(
                    color='white',
                    size=16
                ),
                title=dict(
                    text=fig.layout.title.text,
                    y=0.95,
                    x=0.5,
                    xanchor='center'
                ),
                title_font=dict(
                    size=20,
                    color='white'
                ),
                legend_font=dict(
                    size=14
                )
            )

            fig.update_xaxes(
                color='white',
                tickfont=dict(size=14),
                showgrid=False
            )

            fig.update_yaxes(
                color='white',
                tickfont=dict(size=14),
                gridcolor='rgba(255, 255, 255, 0.1)',
                zeroline=False
            )

            pio.write_image(
                fig,
                f'{output_folder}/players/{format}/fig4.png',
                format='png',
                width=800,
                height=600
            )



    battle()
    players()