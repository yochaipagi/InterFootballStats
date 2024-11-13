import streamlit as st
import plotly.graph_objects as go
from google.oauth2 import service_account
from googleapiclient.discovery import build
import pandas as pd

# Page config
st.set_page_config(page_title="Team Statistics", layout="wide")

# Google Sheets setup (same as main.py)
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# At the top of your file, after imports
SHEETS_CONFIG = {
    "Statistics vs Moldova 4 - 3": {
        "spreadsheet_id": "1yKtKwtmQheGPvIpBcus-BbkbTc5WcF_J91uVVXOe5Zk",
        "range": "Sheet1!A1:P1000"
    },
    # Add more teams as needed
}

@st.cache_data
def load_data(spreadsheet_id, range_name):
    """Modified load_data function to accept spreadsheet parameters"""
    credentials = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=SCOPES
    )
    service = build('sheets', 'v4', credentials=credentials)
    sheet = service.spreadsheets()
    result = sheet.values().get(
        spreadsheetId=spreadsheet_id,
        range=range_name
    ).execute()
    values = result.get('values', [])
    df = pd.DataFrame(values[1:], columns=values[0])
    
    # Convert numeric columns
    numeric_columns = [
        'Goals', 'Assists', 'Shots on target', 'Shots off target', 'Key Passes', 'Dribbles',
        'Ball lost', 'Crosses to box', 'Failed passes', 'Tackles Won', 
        'Clearances/Saves', 'Fouls Committed', 'Fouls Won'
    ]
    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    return df

def safe_int_convert(value):
    """Helper function to safely convert values to integers"""
    try:
        if pd.isna(value):
            return 0
        return int(value)
    except:
        return 0

def main():
    st.title("⚽ Team Statistics Dashboard")
    
    # Add team selector at the top
    selected_team = st.sidebar.selectbox(
        "Select Team",
        options=list(SHEETS_CONFIG.keys()),
        key="team_selector"
    )
    
    try:
        # Load data for selected team
        sheet_config = SHEETS_CONFIG[selected_team]
        df = load_data(sheet_config["spreadsheet_id"], sheet_config["range"])
        
        # Display current team
        st.sidebar.info(f"Currently viewing: {selected_team}")
        
        # Create tabs for main and team stats
        main_tab, team_tab = st.tabs(["Player Statistics", "Team Statistics"])
        
        with main_tab:
            # Player selector
            selected_player = st.selectbox("Select Player", df['Player'].unique())
            
            # Get player stats
            player_stats = df[df['Player'] == selected_player].iloc[0]
            
            # Player Overview
            st.header(f"📊 {selected_player}'s Statistics")
            
            # Display stats in columns
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.subheader("⚽ Scoring")
                st.metric("Goals", safe_int_convert(player_stats['Goals']))
                st.metric("Assists", safe_int_convert(player_stats['Assists']))
            
            with col2:
                st.subheader("🎯 Shooting")
                player_shots_on = safe_int_convert(player_stats['Shots on target'])
                player_shots_off = safe_int_convert(player_stats['Shots off target'])
                total_player_shots = player_shots_on + player_shots_off
                
                # Calculate shooting accuracy with proper error handling
                if total_player_shots > 0:
                    player_accuracy = (player_shots_on / total_player_shots) * 100
                else:
                    player_accuracy = 0
                
                # Display shooting metrics
                st.metric("Shot Accuracy", f"{player_accuracy:.1f}%")
                st.metric("Total Shots", total_player_shots)
                st.metric("Shots on Target", player_shots_on)
                st.metric("Shots off Target", player_shots_off)
            
            with col3:
                st.subheader("⚡ Performance")
                st.metric("Key Passes", safe_int_convert(player_stats['Key Passes']))
                st.metric("Dribbles", safe_int_convert(player_stats['Dribbles']))
            
            # Add new row of columns for defensive stats
            st.header("🛡️ Defensive Actions")
            col4, col5, col6 = st.columns(3)
            
            with col4:
                st.subheader("👊 Tackles & Fouls")
                st.metric("Tackles Won", safe_int_convert(player_stats['Tackles Won']))
                st.metric("Fouls Committed", safe_int_convert(player_stats['Fouls Committed']))
                st.metric("Fouls Won", safe_int_convert(player_stats['Fouls Won']))
            
            with col5:
                st.subheader("🛑 Defensive Actions")
                st.metric("Clearances/Saves", safe_int_convert(player_stats['Clearances/Saves']))
            
            # Add new row of columns for possession stats
            st.header("⚡ Possession Stats")
            col7, col8, col9 = st.columns(3)
            
            with col7:
                st.subheader("❌ Lost Possession")
                st.metric("Ball Lost", safe_int_convert(player_stats['Ball lost']))
                st.metric("Failed Passes", safe_int_convert(player_stats['Failed passes']))
            
            with col8:
                st.subheader("🎯 Crossing")
                st.metric("Crosses to Box", safe_int_convert(player_stats['Crosses to box']))
            
            # Add new performance chart
            st.header("📊 Detailed Performance Analysis")
            
            # Create radar chart for defensive and possession stats
            categories = ['Tackles Won', 'Clearances/Saves', 'Crosses to box', 
                         'Ball lost', 'Failed passes', 'Fouls Won']
            values = [safe_int_convert(player_stats[cat]) for cat in categories]
            
            fig3 = go.Figure(data=go.Scatterpolar(
                r=values,
                theta=categories,
                fill='toself'
            ))
            
            fig3.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, max(values) + 5]
                    )),
                showlegend=False,
                title="Player Performance Radar"
            )
            st.plotly_chart(fig3, use_container_width=True)
        
        with team_tab:
            # Team Overview
            st.header("📊 Team Overview")
            
            # Team totals
            team_totals = df.sum(numeric_only=True)
            
            # Display stats in columns
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.subheader("⚽ Goals & Assists")
                st.metric("Total Team Goals", safe_int_convert(team_totals['Goals']))
                st.metric("Total Team Assists", safe_int_convert(team_totals['Assists']))
            
            with col2:
                st.subheader("🎯 Shooting")
                total_shots_on = safe_int_convert(team_totals['Shots on target'])
                total_shots_off = safe_int_convert(team_totals['Shots off target'])
                total_shots = total_shots_on + total_shots_off
                
                # Calculate team shooting accuracy with proper error handling
                if total_shots > 0:
                    team_accuracy = (total_shots_on / total_shots) * 100
                else:
                    team_accuracy = 0
                
                st.metric("Team Shot Accuracy", f"{team_accuracy:.1f}%")
                st.metric("Total Shots", total_shots)
            
            with col3:
                st.subheader("⚡ Performance")
                st.metric("Total Key Passes", int(team_totals['Key Passes']))
                st.metric("Total Dribbles", int(team_totals['Dribbles']))
            
            # Top Performers
            st.header("🌟 Top Performers")
            
            col4, col5 = st.columns(2)
            
            with col4:
                # Top Scorers Chart
                top_scorers = df.nlargest(5, 'Goals')[['Player', 'Goals']]
                fig1 = go.Figure(go.Bar(
                    x=top_scorers['Goals'],
                    y=top_scorers['Player'],
                    orientation='h',
                    text=top_scorers['Goals'],
                    textposition='auto',
                ))
                fig1.update_layout(
                    title="Top Goalscorers",
                    xaxis_title="Goals",
                    height=300
                )
                st.plotly_chart(fig1, use_container_width=True)
            
            with col5:
                # Top Assisters Chart
                top_assisters = df.nlargest(5, 'Assists')[['Player', 'Assists']]
                fig2 = go.Figure(go.Bar(
                    x=top_assisters['Assists'],
                    y=top_assisters['Player'],
                    orientation='h',
                    text=top_assisters['Assists'],
                    textposition='auto',
                ))
                fig2.update_layout(
                    title="Top Assisters",
                    xaxis_title="Assists",
                    height=300
                )
                st.plotly_chart(fig2, use_container_width=True)
            
            st.header("🛡️ Team Defensive Stats")
            col10, col11, col12 = st.columns(3)
            
            with col10:
                st.subheader("👊 Team Tackles & Fouls")
                st.metric("Total Tackles Won", safe_int_convert(team_totals['Tackles Won']))
                st.metric("Total Fouls Committed", safe_int_convert(team_totals['Fouls Committed']))
                st.metric("Total Fouls Won", safe_int_convert(team_totals['Fouls Won']))
            
            with col11:
                st.subheader("🛑 Team Defensive Actions")
                st.metric("Total Clearances/Saves", safe_int_convert(team_totals['Clearances/Saves']))
            
            with col12:
                st.subheader("⚡ Team Possession")
                st.metric("Total Ball Lost", safe_int_convert(team_totals['Ball lost']))
                st.metric("Total Failed Passes", safe_int_convert(team_totals['Failed passes']))
                st.metric("Total Crosses to Box", safe_int_convert(team_totals['Crosses to box']))

    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        st.info("Please make sure your Google Sheets credentials are properly set up.")

    # Add new sheet form in sidebar
    with st.sidebar.expander("Add New Game Sheet"):
        new_team_name = st.text_input("Game Name")
        new_sheet_id = st.text_input("Spreadsheet ID")
        if st.button("Add Game"):
            if new_team_name and new_sheet_id:
                # Store in session state
                if 'additional_sheets' not in st.session_state:
                    st.session_state.additional_sheets = {}
                st.session_state.additional_sheets[new_team_name] = {
                    "spreadsheet_id": new_sheet_id,
                    "range": "Sheet1!A1:P1000"
                }
                st.success(f"Added {new_team_name}!")
                st.rerun()

if __name__ == "__main__":
    main()
