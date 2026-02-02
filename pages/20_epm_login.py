import streamlit as st
from state.user import USERS  # your central user dictionary

st.title("EPM Login")

username = st.text_input("Username")
password = st.text_input("Password", type="password")

col1, col2 = st.columns([1,1])

with col1:
    if st.button("Login"):
        user = USERS.get(username)
        if user and user["password"] == password:
            # Check if user has access to the "epm" system
            if "epm" not in user.get("systems", []):
                st.error("You do not have access to the EPM system.")
                st.stop()

            # Save unified user object in session state
            st.session_state.user = user.copy()
            st.session_state.user["username"] = username

            st.success(f"Logged in as {username} ({', '.join(user['roles'])})")

            # Redirect to EPM dashboard
            st.switch_page("pages/6_epm_scanner_dashboard.py")
            st.stop()
        else:
            st.error("Invalid username or password.")

with col2:
    if st.button("Cancel"):
        st.session_state.user = None
        st.stop()

# -------------------------
# Optional: show login info if already logged in
# -------------------------
if st.session_state.get("user"):
    user = st.session_state.user
    st.info(f"Already logged in as {user['username']} ({', '.join(user['roles'])})")
