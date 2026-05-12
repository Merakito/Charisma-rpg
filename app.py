import streamlit as st
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials

st.set_page_config(page_title="Charisma RPG", layout="centered")

# --- CLOUD VAULT LOGIC ---
def get_sheet():
    # Use the 'secrets' from Streamlit Cloud
    creds_dict = st.secrets["gcp_service_account"]
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    return client.open("Charisma_RPG_Data").worksheet("Data")
def load_game():
    try:
        sheet = get_sheet()
        data = sheet.acell('B2').value 
        if data:
            return json.loads(data)
        return {"level": 1, "total_xp": 0, "mana": 100, "api_key": "", "branch_xp": {"Acting": 0, "Charisma": 0, "Storytelling": 0, "Practice": 0}, "directors_notes": {}}
    except Exception as e:
        st.error(f"Vault Loading Error: {e}") # This will force the error to show up on screen
        return {"level": 1, "total_xp": 0, "mana": 100, "api_key": "", "branch_xp": {"Acting": 0, "Charisma": 0, "Storytelling": 0, "Practice": 0}, "directors_notes": {}}

def save_game():
    sheet = get_sheet()
    data = {
        "level": st.session_state.level,
        "total_xp": st.session_state.total_xp,
        "mana": st.session_state.mana,
        "api_key": st.session_state.api_key,
        "branch_xp": st.session_state.branch_xp,
        "directors_notes": st.session_state.directors_notes
    }
    sheet.update_acell('B2', json.dumps(data)) # Write JSON to cell B2

# ... (Keep the rest of your UI and Logic code identical to v6.0) ...
