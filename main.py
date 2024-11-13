import streamlit as st

st.set_page_config(page_title="Team Stats Home", page_icon="⚽", layout="wide")

# Add a header with custom styling
st.markdown("""
    <h1 style='text-align: center;'>Welcome to Team Statistics Dashboard</h1>
    """, unsafe_allow_html=True)

# Add some introductory content
st.markdown("""
    ### 📊 What you'll find here:
    - Team performance metrics
    - Player statistics
    - Match analysis
    - Historical data
    
    ### 🚀 Getting Started:
    1. Use the sidebar on the left to navigate between different pages
    2. Each page provides different insights about team performance
    3. Data is automatically updated from our Google Sheets database
    
    ### 📌 Need Help?
    Contact the administrator if you need access or have questions.
""")

# Add a footer
st.markdown("---")
st.markdown("*Data is updated regularly to ensure accuracy*") 