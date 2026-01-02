import streamlit as st
import pandas as pd

st.title("NBA BPM Impact Dashboard (Fixed Version)")

@st.cache_data
def load_data():
    url = "https://www.basketball-reference.com/leagues/NBA_2026_advanced.html"
    
    # Read all tables
    tables = pd.read_html(url)
    nba = tables[0]
    
    # Remove repeated header rows
    nba = nba[nba['Rk'] != 'Rk']
    
    # Strip whitespace from column names
    nba.columns = nba.columns.str.strip()
    
    # Print column names for debugging (optional)
    # st.write("Available columns:", nba.columns.tolist())
    
    # Find the exact BPM column
    bpm_col = [c for c in nba.columns if 'BPM' in c]
    if not bpm_col:
        st.error("No BPM column found!")
        return pd.DataFrame()
    bpm_col = bpm_col[0]
    
    # Find the exact Team column (could be 'Team' or 'Tm')
    team_col = [c for c in nba.columns if c in ['Team', 'Tm']]
    if team_col:
        team_col = team_col[0]
    else:
        st.error("No Team column found!")
        return pd.DataFrame()
    
    # Keep needed columns
    nba = nba[['Player', team_col, 'G', 'MP', bpm_col]].dropna()
    
    # Rename team column to 'Team' for consistency
    nba = nba.rename(columns={team_col: 'Team'})
    
    # Convert to numeric
    nba['G'] = pd.to_numeric(nba['G'], errors='coerce')
    nba['MP'] = pd.to_numeric(nba['MP'], errors='coerce')
    nba[bpm_col] = pd.to_numeric(nba[bpm_col], errors='coerce')
    
    # Remove any rows with missing values
    nba = nba.dropna()
    
    # Compute MPG
    nba['MPG'] = nba['MP'] / nba['G']
    
    # Compute Impact
    nba['Impact'] = (nba[bpm_col] / 100) * nba['MPG'] * 2.083
    
    # Rename BPM column for consistency
    nba = nba.rename(columns={bpm_col: 'BPM'})
    
    # Injury column
    nba['Injured'] = False
    
    return nba

nba = load_data()

if nba.empty:
    st.error("Failed to load NBA data. Please check the Basketball-Reference page.")
    st.stop()

# Show data preview
st.sidebar.header("Data Preview")
st.sidebar.write(f"Loaded {len(nba)} players")
st.sidebar.write(f"Teams: {len(nba['Team'].unique())}")

# Sidebar: mark injured players
st.sidebar.header("Injuries")
for i, row in nba.iterrows():
    if st.sidebar.checkbox(f"{row['Player']} Injured?", key=row['Player']):
        nba.at[i, 'Impact'] = 0
        nba.at[i, 'Injured'] = True

# Team selection
teams = sorted(nba['Team'].unique())
team1 = st.selectbox("Team 1", teams, index=teams.index('TOR') if 'TOR' in teams else 0)
team2 = st.selectbox("Team 2", teams, index=teams.index('MIA') if 'MIA' in teams else 1)

# Team totals
team1_total = nba[nba['Team'] == team1]['Impact'].sum()
team2_total = nba[nba['Team'] == team2]['Impact'].sum()
advantage = team1_total - team2_total

st.subheader("Projected Matchup (BPM-based)")
col1, col2, col3 = st.columns(3)
col1.metric(f"{team1} Total Impact", f"{team1_total:.2f}")
col2.metric(f"{team2} Total Impact", f"{team2_total:.2f}")
col3.metric("Projected Advantage", f"{advantage:.2f}")

# Player table with sorting
st.subheader("Player Contributions")
player_table = nba[nba['Team'].isin([team1, team2])]

# Sorting options
col1, col2 = st.columns(2)
with col1:
    sort_column = st.selectbox(
        "Sort by:",
        options=['Team', 'Player', 'Impact', 'MPG', 'BPM']
    )
with col2:
    sort_order = st.radio("Order:", options=['Descending', 'Ascending'])

# Apply sorting
player_table = player_table.sort_values(
    by=sort_column,
    ascending=(sort_order == 'Ascending')
)

# Display table
st.dataframe(
    player_table[['Team', 'Player', 'MPG', 'BPM', 'Impact', 'Injured']].reset_index(drop=True),
    use_container_width=True
)

# Bar chart
st.subheader("Team Impact Comparison")
chart_data = pd.DataFrame({
    'Team': [team1, team2],
    'Impact': [team1_total, team2_total]
})
st.bar_chart(chart_data.set_index('Team'))
