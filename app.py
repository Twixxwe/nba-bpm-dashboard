import streamlit as st
import pandas as pd

st.title("NBA BPM Impact Dashboard (Fixed Column Names)")

@st.cache_data
def load_data():
    url = "https://www.basketball-reference.com/leagues/NBA_2026_advanced.html"
    tables = pd.read_html(url)
    nba = tables[0]

    # Remove repeated header rows
    nba = nba[nba['Rk'] != 'Rk']

    # Strip whitespace from columns
    nba.columns = nba.columns.str.strip()

    # Use exact column names
    needed_cols = ['Player','Team','G','MP','BPM']
    nba = nba[needed_cols].dropna()

    # Convert numeric
    nba['G'] = pd.to_numeric(nba['G'])
    nba['MP'] = pd.to_numeric(nba['MP'])
    nba['BPM'] = pd.to_numeric(nba['BPM'])

    # Compute MPG
    nba['MPG'] = nba['MP'] / nba['G']

    # Compute Impact
    nba['Impact'] = (nba['BPM'] / 100) * nba['MPG'] * 2.083

    # Injury column
    nba['Injured'] = False

    return nba

nba = load_data()

# Sidebar: mark injured players
st.sidebar.header("Injuries")
for i, row in nba.iterrows():
    if st.sidebar.checkbox(f"{row['Player']} Injured?", key=row['Player']):
        nba.at[i,'Impact'] = 0
        nba.at[i,'Injured'] = True

# Team selection
teams = nba['Team'].unique()
team1 = st.selectbox("Team 1", teams)
team2 = st.selectbox("Team 2", teams)

# Team totals
team1_total = nba[nba['Team'] == team1]['Impact'].sum()
team2_total = nba[nba['Team'] == team2]['Impact'].sum()
advantage = team1_total - team2_total

st.subheader("Projected Matchup (BPM-based)")
st.write(f"{team1} Total Impact: {team1_total:.2f}")
st.write(f"{team2} Total Impact: {team2_total:.2f}")
st.write("Projected Advantage:", round(advantage, 2))

# Player table with sorting by multiple columns
st.subheader("Player Contributions (Impact)")

player_table = nba[nba['Team'].isin([team1, team2])]
sort_column = st.selectbox(
    "Sort players by:",
    options=['Team', 'Player', 'Impact', 'MPG', 'BPM']
)
sort_order = st.radio("Sort order:", options=['Descending', 'Ascending'])

player_table = player_table.sort_values(
    by=sort_column,
    ascending=(sort_order == 'Ascending')
)

st.dataframe(player_table.reset_index(drop=True))

# Bar chart
st.subheader("Team Impact Comparison")
st.bar_chart({
    team1: team1_total,
    team2: team2_total
})
