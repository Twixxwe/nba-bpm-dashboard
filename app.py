import streamlit as st
import pandas as pd

st.title("NBA BPM Impact Dashboard (Advanced Stats)")

# Load NBA Advanced stats
@st.cache_data
def load_data():
    url = "https://www.basketball-reference.com/leagues/NBA_2026_advanced.html"
    tables = pd.read_html(url)
    nba = tables[0]

    # Remove repeated header rows
    nba = nba[nba['Rk'] != 'Rk']

    # Keep needed columns
    nba = nba[['Player','Tm','G','MP','BPM']].dropna()
    
    # Convert to numeric
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
teams = nba['Tm'].unique()
team1 = st.selectbox("Team 1", teams)
team2 = st.selectbox("Team 2", teams)

# Team totals
team1_total = nba[nba['Tm'] == team1]['Impact'].sum()
team2_total = nba[nba['Tm'] == team2]['Impact'].sum()
advantage = team1_total - team2_total

st.subheader("Projected Matchup (BPM-based)")
st.write(f"{team1} Total Impact: {team1_total:.2f}")
st.write(f"{team2} Total Impact: {team2_total:.2f}")
st.write("Projected Advantage:", round(advantage, 2))

# Player table with fully sortable options
st.subheader("Player Contributions (Impact)")

# Filter for selected teams
player_table = nba[nba['Tm'].isin([team1, team2])]

# Let user choose column to sort by (include Team)
sort_column = st.selectbox(
    "Sort players by:",
    options=['Team', 'Player', 'Impact', 'MPG', 'BPM']
)

sort_order = st.radio("Sort order:", options=['Descending', 'Ascending'])

# Apply sorting
player_table = player_table.sort_values(
    by=sort_column,
    ascending=(sort_order == 'Ascending')
)

# Show sortable table
st.dataframe(player_table.reset_index(drop=True))

# Bar chart for team comparison
st.subheader("Team Impact Comparison")
st.bar_chart({
    team1: team1_total,
    team2: team2_total
})
