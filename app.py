import streamlit as st
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from google import genai

st.set_page_config(page_title="Charisma RPG", layout="centered")

# --- CLOUD VAULT LOGIC ---
def get_sheet():
    # Use the 'secrets' from Streamlit Cloud
    creds_dict = st.secrets["gcp_service_account"]
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    return client.open("Charisma_RPG_Data").worksheet("Data")

# --- AI LOGIC (Updated for google-genai) ---
def generate_ai_quest(api_key, branch, difficulty):
    try:
        # Initialize the new Client
        client = genai.Client(api_key=api_key)
        
        prompt = f"Act as a coach. Level {st.session_state.level} introvert. Branch: {branch}. Difficulty: {difficulty}. Give me one 2-sentence social quest."
        
        # Use the updated generation method
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        
        st.session_state.daily_ai_quest = response.text
        xp_map = {"Easy": 25, "Medium": 65, "Hard": 150}
        st.session_state.current_reward = xp_map[difficulty]
        return True
    except Exception as e:
        st.error(f"API Error: {e}")
        return False

def load_game():
    try:
        sheet = get_sheet()
        data = sheet.acell('B2').value # Get the JSON string from cell B2
        if data:
            return json.loads(data)
    except: pass
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
