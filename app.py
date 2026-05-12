import streamlit as st
import json
import os
import google.generativeai as genai

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Charisma RPG", page_icon="🎬", layout="centered")

# --- THE VAULT (v7.0) ---
SAVE_FILE = "charisma_save_v7.json"

SKILL_MAP = {
    "Practice": [(0, "Basic Mirror Work"), (500, "Vocal Warmup Suite"), (2000, "Self-Tape Mastery"), (5000, "Script Deconstruction"), (10000, "Method Immersion")],
    "Acting": [(0, "Physical Neutrality"), (500, "Emotional Access"), (2000, "Dialect & Tone"), (5000, "Character Transformation"), (10000, "Master Class Presence")],
    "Charisma": [(0, "Eye Contact 101"), (500, "Active Listening"), (2000, "The Magnetic Hook"), (5000, "Public Persuasion"), (10000, "Natural Magnetism")],
    "Storytelling": [(0, "The Narrative Arc"), (500, "Humor & Timing"), (2000, "Suspense Building"), (5000, "The Vulnerable Monologue"), (10000, "Orator Mastery")]
}

def load_game():
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "r") as f:
            return json.load(f)
    return {"level": 1, "total_xp": 0, "mana": 100, "api_key": "", "branch_xp": {"Acting": 0, "Charisma": 0, "Storytelling": 0, "Practice": 0}, "directors_notes": {}}

def save_game():
    data_to_save = {
        "level": st.session_state.level,
        "total_xp": st.session_state.total_xp,
        "mana": st.session_state.mana,
        "api_key": st.session_state.api_key,
        "branch_xp": st.session_state.branch_xp,
        "directors_notes": st.session_state.directors_notes
    }
    with open(SAVE_FILE, "w") as f:
        json.dump(data_to_save, f)

# Initialize
if 'level' not in st.session_state:
    save_data = load_game()
    for key, value in save_data.items():
        st.session_state[key] = value
    st.session_state.daily_ai_quest = None

# --- RESTART LOGIC ---
def restart_game():
    if os.path.exists(SAVE_FILE):
        os.remove(SAVE_FILE)
    st.session_state.clear()
    st.rerun()

# --- AI LOGIC ---
def generate_ai_quest(api_key, branch, difficulty):
    genai.configure(api_key=api_key)
    try:
        model = genai.GenerativeModel('gemini-pro')
        prompt = f"Act as a coach. Level {st.session_state.level} introvert. Branch: {branch}. Difficulty: {difficulty}. Give me one 2-sentence social quest."
        response = model.generate_content(prompt)
        st.session_state.daily_ai_quest = response.text
        xp_map = {"Easy": 25, "Medium": 65, "Hard": 150}
        st.session_state.current_reward = xp_map[difficulty]
        return True
    except: return False

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
        if st.button("Confirm Restart"):
            restart_game()

# --- MAIN UI ---
st.title("🎬 Cinematic Charisma RPG")
st.progress(st.session_state.mana / 100, text=f"Social Battery: {st.session_state.mana}%")

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
            if st.button(f"Complete Scene (+{st.session_state.current_reward} XP)", use_container_width=True):
                st.session_state.branch_xp[st.session_state.current_branch] += st.session_state.current_reward
                st.session_state.mana -= 20
                st.session_state.daily_ai_quest = None
                save_game()
                st.rerun()
    
    if st.button("🔋 Rest & Recharge", use_container_width=True):
        st.session_state.mana = 100
        save_game()
        st.rerun()

with tab2:
    st.write("### 🌳 Career Progression")
    for branch_name, milestones in SKILL_MAP.items():
        xp = st.session_state.branch_xp[branch_name]
        current_title = next((t for x, t in reversed(milestones) if xp >= x), "Novice")
        next_milestone = next((x for x, t in milestones if x > xp), 10000)
        
        with st.expander(f"{branch_name}: {current_title}"):
            st.progress(min(xp / next_milestone, 1.0), text=f"{xp} / {next_milestone} XP to next rank")
            for req, title in milestones:
                st.write(f"{'✅' if xp >= req else '🔒'} {title} ({req} XP)")

st.markdown("<br><center><small>Directed by You</small></center>", unsafe_allow_html=True)
