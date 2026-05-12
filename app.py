import streamlit as st
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from google import genai

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Charisma RPG", page_icon="🎬", layout="centered")

# --- CAREER PATHS (The Skill Tree) ---
SKILL_MAP = {
    "Practice": [(0, "Basic Mirror Work"), (500, "Vocal Warmup Suite"), (2000, "Self-Tape Mastery"), (5000, "Script Deconstruction"), (10000, "Method Immersion")],
    "Acting": [(0, "Physical Neutrality"), (500, "Emotional Access"), (2000, "Dialect & Tone"), (5000, "Character Transformation"), (10000, "Master Class Presence")],
    "Charisma": [(0, "Eye Contact 101"), (500, "Active Listening"), (2000, "The Magnetic Hook"), (5000, "Public Persuasion"), (10000, "Natural Magnetism")],
    "Storytelling": [(0, "The Narrative Arc"), (500, "Humor & Timing"), (2000, "Suspense Building"), (5000, "The Vulnerable Monologue"), (10000, "Orator Mastery")]
}

# --- CLOUD VAULT LOGIC ---
def get_sheet():
    try:
        if "gcp_service_account" not in st.secrets:
            st.error("Vault Error: Streamlit Secrets missing.")
            return None
        creds_dict = st.secrets["gcp_service_account"]
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        return client.open("Charisma_RPG_Data").worksheet("Data")
    except Exception as e:
        st.error(f"Google Connection Error: {e}")
        return None

def load_game():
    sheet = get_sheet()
    if sheet:
        try:
            data = sheet.acell('B2').value 
            if data:
                return json.loads(data)
        except Exception as e:
            st.error(f"Error reading cell B2: {e}")
            
    # Default fallback if sheet is empty or fails
    return {"level": 1, "total_xp": 0, "mana": 100, "api_key": "", "branch_xp": {"Acting": 0, "Charisma": 0, "Storytelling": 0, "Practice": 0}, "directors_notes": {}}

def save_game():
    sheet = get_sheet()
    if sheet:
        data = {
            "level": st.session_state.level,
            "total_xp": st.session_state.total_xp,
            "mana": st.session_state.mana,
            "api_key": st.session_state.api_key,
            "branch_xp": st.session_state.branch_xp,
            "directors_notes": st.session_state.directors_notes
        }
        try:
            sheet.update_acell('B2', json.dumps(data))
        except Exception as e:
            st.error(f"Failed to save to cloud: {e}")

# --- INITIALIZATION ---
if 'level' not in st.session_state:
    save_data = load_game()
    for key, value in save_data.items():
        st.session_state[key] = value
    st.session_state.daily_ai_quest = None
    st.session_state.current_reward = 0
    st.session_state.current_branch = "Practice"

# --- RESTART LOGIC ---
def restart_game():
    # Reset local state
    st.session_state.level = 1
    st.session_state.total_xp = 0
    st.session_state.mana = 100
    st.session_state.branch_xp = {"Acting": 0, "Charisma": 0, "Storytelling": 0, "Practice": 0}
    st.session_state.directors_notes = {}
    st.session_state.daily_ai_quest = None
    # Overwrite cloud save
    save_game()
    st.rerun()

# --- AI LOGIC (Modern google-genai) ---
def generate_ai_quest(api_key, branch, difficulty):
    try:
        client = genai.Client(api_key=api_key)
        prompt = f"Act as a coach. Level {st.session_state.level} introvert. Branch: {branch}. Difficulty: {difficulty}. Give me one 2-sentence social quest. No advice, just the action."
        
        with st.spinner("Drafting your scene..."):
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
            )
            
            st.session_state.daily_ai_quest = response.text
            xp_map = {"Easy": 25, "Medium": 65, "Hard": 150}
            st.session_state.current_reward = xp_map[difficulty]
            return True
    except Exception as e:
        st.error(f"AI API Error: {e}")
        return False

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Studio Settings")
    key = st.text_input("Gemini API Key", value=st.session_state.api_key, type="password")
    if st.button("Save Key"):
        st.session_state.api_key = key
        save_game()
        st.success("Key Saved!")
    
    st.divider()
    st.write("### 🚨 Danger Zone")
    if st.button("Restart Career", type="secondary"):
        st.warning("This will erase all XP and Levels!")
        if st.button("Confirm Restart", type="primary"):
            restart_game()

# --- MAIN UI ---
st.title("🎬 Cinematic Charisma RPG")
st.progress(st.session_state.mana / 100, text=f"Social Battery (Mana): {st.session_state.mana}%")

tab1, tab2 = st.tabs(["📋 The Call Sheet", "🌳 Career Paths"])

with tab1:
    st.write("### 📽️ Today's Scene")
    col1, col2 = st.columns(2)
    with col1: branch_choice = st.selectbox("Department", ["Practice", "Acting", "Charisma", "Storytelling"])
    with col2: diff_choice = st.select_slider("Intensity", options=["Easy", "Medium", "Hard"])
    
    if st.session_state.api_key:
        if st.session_state.daily_ai_quest is None:
            if st.button("Generate Quest ✨", use_container_width=True):
                st.session_state.current_branch = branch_choice
                if generate_ai_quest(st.session_state.api_key, branch_choice, diff_choice):
                    st.rerun()
        else:
            st.info(f"**[{st.session_state.current_branch}]** {st.session_state.daily_ai_quest}")
            if st.button(f"Complete Scene (+{st.session_state.current_reward} XP) ✅", use_container_width=True):
                if st.session_state.mana >= 20:
                    st.session_state.branch_xp[st.session_state.current_branch] += st.session_state.current_reward
                    st.session_state.total_xp += st.session_state.current_reward
                    st.session_state.mana -= 20
                    
                    # Global Level Up Check
                    if st.session_state.total_xp >= 500:
                        st.session_state.level += 1
                        st.session_state.total_xp = 0
                        st.balloons()
                        st.success(f"Level Up! You are now Level {st.session_state.level}")
                    
                    st.session_state.daily_ai_quest = None
                    save_game()
                    st.rerun()
                else:
                    st.error("Not enough Social Battery! Rest at Craft Services.")
            
            if st.button("🔄 Reshoot (Generate Different Quest)", use_container_width=True):
                st.session_state.daily_ai_quest = None
                st.rerun()
    else:
        st.warning("Please enter your API Key in the sidebar to generate quests.")

    st.divider()
    if st.button("🔋 Rest at Craft Services (Restore Mana)", use_container_width=True):
        st.session_state.mana = 100
        save_game()
        st.toast('Mana Restored!')
        st.rerun()

with tab2:
    st.write("### 🌳 Career Progression")
    st.caption(f"Global Level: {st.session_state.level} | Global XP: {st.session_state.total_xp} / 500")
    st.divider()
    
    for branch_name, milestones in SKILL_MAP.items():
        xp = st.session_state.branch_xp[branch_name]
        
        # Calculate current title and next milestone
        current_title = "Novice"
        next_milestone = 10000 # Default max
        
        for req, title in milestones:
            if xp >= req:
                current_title = title
            else:
                next_milestone = req
                break
                
        with st.expander(f"{branch_name}: {current_title} ({xp} XP)"):
            progress_ratio = min(xp / next_milestone, 1.0) if next_milestone > 0 else 1.0
            st.progress(progress_ratio, text=f"Progress to next rank: {xp} / {next_milestone} XP")
            
            st.write("**Roadmap:**")
            for req, title in milestones:
                st.write(f"{'✅' if xp >= req else '🔒'} {title} ({req} XP)")

st.markdown("<br><center><small>Directed by You | Powered by Gemini & Streamlit</small></center>", unsafe_allow_html=True)
