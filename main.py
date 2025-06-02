import streamlit as st

st.set_page_config(page_title='Showdown Shower', initial_sidebar_state="collapsed", layout='centered')

st.title("🎮 Showdown Shower")
st.markdown("Welcome! To the Ultimate Pokémon Showdown replay analysis.")

with st.expander("About this project"):
    st.markdown("[Pokémon Showdown](https://pokemonshowdown.com/) is a battle simulator for the videogame series Pokémon. It has a thriving competitive scene, and Showdown is often used to simulate competitive battles between players from all around the world, both casual and professional.")
    st.markdown("A Pokémon battle consists of two players using a team of 6 different Pokémon taking turns. Each Pokémon has up to 4 pre-determined moves it can use to attack an opposing Pokémon. When a Pokémon life bar goes to 0, the Pokémon faints. The player who defeats all of the other team's Pokémon wins.")
    st.markdown("This website contains the results of over 500k competitive battle replays from Pokémon Showdown or other earlier simulators, ranging from 2005 to 2025. These replays are divided by generation and format. A replay may also have a rating, which shows the skill level of the two players, starting from 1000 for a new player.")
    st.markdown("A **generation** indicates which specific game the battle is simulating (i.e. Generation 1 represents the first games from 1996, Generation 2 the sequels from 1999 etc.). Each generation brings new moves and Pokémon, so each one has different strategies from the other ones.")
    st.markdown("Each generation is subdivided in **formats**, which are based on a specific Pokémon usage. Strong Pokémon get used the most, so they end up in the OverUsed format (OU). Less used Pokémon end up in the lower tiers, where they play with similarly less used Pokémon. This ensures that even weaker strategies see play at a competitive level.")
    st.markdown("Each Pokémon is differentiated by their stats (Attack, Defence, Speed etc.), their move pool and their types (i.e. Fire, Grass, Water etc.).")
    st.markdown("During their turn, a player may either use a move or switch out their Pokémon with another one from their team. Each move also has a type, which may increase, decrease or nullify the amount of damage an opposing Pokémon takes (Ex. a Water type move does more damage to a Fire type Pokémon).")
    st.markdown("All of these variables show the amount of data that can be extracted from battle replays, and how it can be used to track patterns, visualize strategies, single out outliers and analyze players' behaviour.")


col1, col2, col3, col4 = st.columns(4)

with col1:
    st.page_link("pages/Battles Page.py", label="BATTLES", icon="📊")

with col2:
    st.page_link("pages/Players Page.py", label="PLAYERS", icon="👤")

with col3:
    st.page_link("pages/Pokémon Page.py", label="POKÉMON", icon="🧬")

with col4:
    st.page_link("pages/Info Page.py", label="INFO", icon="ℹ️")
