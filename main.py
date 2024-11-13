# Required libraries
import pandas as pd
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
from googleapiclient.discovery import build
import streamlit as st
import plotly.graph_objects as go

# Page config
st.set_page_config(page_title="Football Stats Dashboard", layout="wide")

# Google Sheets setup
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
SAMPLE_SPREADSHEET_ID = '1yKtKwtmQheGPvIpBcus-BbkbTc5WcF_J91uVVXOe5Zk'
SAMPLE_RANGE_NAME = 'Sheet1!A1:P1000'

@st.cache_data
def load_data():
    # Create credentials
    credentials = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],  # We'll set this up in Streamlit
        scopes=SCOPES
    )

    # Create service
    service = build('sheets', 'v4', credentials=credentials)
    sheet = service.spreadsheets()
    
    # Get data
    result = sheet.values().get(
        spreadsheetId=SAMPLE_SPREADSHEET_ID,
        range=SAMPLE_RANGE_NAME
    ).execute()
    
    # Convert to DataFrame
    values = result.get('values', [])
    df = pd.DataFrame(values[1:], columns=values[0])
    
    # Convert numeric columns
    numeric_columns = ['Goals', 'Assists', 'Played', 'Yellow C.', 
                      'Shots on target', 'Shots off target', 'Failed passes',
                      'Ball lost', 'Dribbles', 'Clearances/Saves',
                      'Fouls Committed', 'Fouls Won', 'Tackles Won',
                      'Crosses to box', 'Key Passes']
    
    for col in numeric_columns:
        # Convert to numeric and fill NaN with 0
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    return df

def main():
    st.title("⚽ Player Statistics Dashboard")
    
    try:
        # Load data
        df = load_data()
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return
        
    # Sidebar filters
    st.sidebar.header("Player Filters")
    selected_player = st.sidebar.selectbox("Select Player", df['Player'].unique())
    
    # Main content
    col1, col2, col3 = st.columns(3)
    
    # Player stats in first column
    with col1:
        st.subheader(f"📊 {selected_player}'s Key Stats")
        player_data = df[df['Player'] == selected_player].iloc[0]
        
        st.metric("Goals", player_data['Goals'])
        st.metric("Assists", player_data['Assists'])
        
        # Rest of your player stats code...
        # ... (keep the same code)

if __name__ == "__main__":
    main()
