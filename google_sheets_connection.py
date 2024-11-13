from google.oauth2 import service_account
from googleapiclient.discovery import build
import streamlit as st
import pandas as pd

def get_sheet_data(spreadsheet_id):
    # Create credentials from streamlit secrets
    credentials = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=['https://www.googleapis.com/auth/spreadsheets.readonly']
    )
    
    try:
        # Connect to Google Sheets
        service = build('sheets', 'v4', credentials=credentials)
        sheet = service.spreadsheets()
        
        # Read the data
        result = sheet.values().get(
            spreadsheetId=spreadsheet_id,
            range='A1:Z1000'  # Adjust range as needed
        ).execute()
        
        # Convert to DataFrame
        values = result.get('values', [])
        if not values:
            return pd.DataFrame()
        
        df = pd.DataFrame(values[1:], columns=values[0])
        return df
    
    except Exception as e:
        st.error(f"Error accessing Google Sheet: {str(e)}")
        return pd.DataFrame() 