import streamlit as st

st.set_page_config(page_title='Showdown Shower', initial_sidebar_state="collapsed", layout='centered')

st.title("🎮 Showdown Shower")
st.markdown("Welcome! To the Ultimate Pokémon Showdown replay analysis.")

col1, col2, col3 = st.columns(3)

with col1:
    st.page_link("pages/Battles Page.py", label="BATTLES", icon="📊")

with col2:
    st.page_link("pages/Players Page.py", label="PLAYERS", icon="👤")

with col3:
    st.page_link("pages/Pokémon Page.py", label="POKÉMON", icon="🧬")
