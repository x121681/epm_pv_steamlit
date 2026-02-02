import streamlit as st
from state.user import USERS  # your central user dictionary

st.title("User Device Login")

username = st.text_input("Username")
password = st.text_input("Password", type="password")

col1, col2 = st.columns(2)

with col1:
    if st.button("Cancel"):
        # Clear any temporary session info for device login
        st.session_state.user = None
        st.session_state.device_current_page = "User Journeys"
        st.stop()

with col2:
    if st.button("OK"):
        user = USERS.get(username)
        if user and user["password"] == password:
            # Check if user has access to the "device" system
            if "device" not in user.get("systems", []):
                st.error("You do not have access to the Device system.")
                st.stop()

            # Save the unified user object in session state
            st.session_state.user = user.copy()  # make a copy to store session-specific info
            st.session_state.user["username"] = username

            # Redirect to user journey page
            st.session_state.device_current_page = "21_user_journey_selection"
            st.success(f"Welcome, {username}!")
            st.switch_page("pages/21_user_journey_selection.py")
            st.stop()
        else:
            st.warning("Invalid username or password.")

# -------------------------
# Optional: show login info if already logged in
# -------------------------
if st.session_state.get("user"):
    user = st.session_state.user
    st.info(f"Already logged in as {user['username']} ({', '.join(user['roles'])})")