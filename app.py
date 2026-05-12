import streamlit as st

st.title("🎬 Test Screen")
st.write("If you can see this, the server is alive and the issue is with the Google Sheets connection!")
st.write("My Secrets:", st.secrets.get("gcp_service_account", "No secrets found!"))
