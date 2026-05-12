import streamlit as st
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import google.generativeai as genai

st.set_page_config(page_title="Charisma RPG", layout="centered")

# --- CLOUD VAULT LOGIC (WITH DIAGNOSTICS) ---
def get_sheet():
    try:
        # 1. Look for the secrets
        if "gcp_service_account" not in st.secrets:
            st.error("Diagnostic: Streamlit Secrets are missing or named incorrectly!")
            return None
            
        creds_dict = st.secrets["gcp_service_account"]
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        
        # 2. Try to open the sheet
        try:
            return client.open("Charisma_RPG_Data").worksheet("Data")
        except gspread.exceptions.SpreadsheetNotFound:
            st.error("Diagnostic: The Sheet 'Charisma_RPG_Data' was not found! Check spelling or Sharing permissions.")
            return None
            
    except Exception as e:
        st.error(f"Diagnostic: Connection Error - {e}")
        return None

def load_game():
    sheet = get_sheet()
    if sheet:
        try:
            data = sheet.acell('B2').value 
            if data:
                return json.loads(data)
        except Exception as e:
            st.error(f"Diagnostic: Error reading cell B2 - {e}")
            
    # Default fallback if anything fails
    return {"level": 1, "total_xp": 0, "mana": 100, "api_key": "", "branch_xp": {"Acting": 0, "Charisma": 0, "Storytelling": 0, "Practice": 0}, "directors_notes": {}}

# ... [THE REST OF YOUR APP.PY CODE STAYS EXACTLY THE SAME] ...
