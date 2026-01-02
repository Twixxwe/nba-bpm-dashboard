import streamlit as st
import pandas as pd

st.title("NBA BPM Matchup Dashboard (Beginner-Friendly)")

# Load NBA stats (from Basketball-Reference)
@st.cache_data
def load_data():
    url = "https://www.basketball-reference.com/leagues/NBA_2026_totals.html"
    tables = pd.read_html(url)
    nba = tables[0][['Player','Tm','MP','BPM']].dropna()
    nba['MP'] = pd.to_numeric(nba['MP'])
    nba['BPM'] = pd.to_numeric(nba['BPM'])
    nba['Impact'] = (nba['BPM']/100) * nba['MP'] * 2.083
    # Add Injury column
    nba['Injured'] = False
    return nba

nba = load_data()

# Sidebar: select injured players
st.sidebar.header("Injuries")
for i, row in nba.iterrows():
    if st.sidebar.checkbox(f"{row['Player']} Injured?", key=row['Player']):
        nba.at[i,'Impact'] = 0
        nba.at[i,'Injured'] = True

# Team selection
teams = nba['Tm'].unique()
team1 = st.selectbox("Team 1", teams)
team2 = st.selectbox("Team 2", teams)

# Calculate team totals
team1_total = nba[nba['Tm'] == team1]['Impact'].sum()
team2_total = nba[nba['Tm'] == team2]['Impact'].sum()
advantage = team1_total - team2_total

st.subheader("Projected Matchup")
st.write(f"{team1} Total Impact: {team1_total:.2f}")
st.write(f"{team2} Total Impact: {team2_total:.2f}")
st.write("Projected Advantage:", round(advantage, 2))

# Show sortable player table
st.subheader("Player Contributions")
st.dataframe(nba[nba['Tm'].isin([team1, team2])].sort_values('Impact', ascending=False))

# Optional: bar chart
st.subheader("Team Impact Comparison")
st.bar_chart({
    team1: team1_total,
    team2: team2_total
})
