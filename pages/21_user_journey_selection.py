import streamlit as st
from state.core import init_app_state

# Ensure device login state exists
init_app_state()

st.title("Choose your next step")

st.write("Select the action that best matches what you need to do right now.")
st.info("If you are unsure, start with the blacklisted app flow or the software installation flow.")

col1, col2 = st.columns(2)
col3, col4 = st.columns(2)
col5, col6 = st.columns(2)

with col1:
    if st.button("� Open a blacklisted app"):
        st.session_state.device_current_page = "0_scanner_blacklist"
        st.switch_page("pages/0_scanner_blacklist.py")

with col2:
    if st.button("🛠️ Request software installation"):
        st.session_state.device_current_page = "0a_admin_permission"
        st.switch_page("pages/0a_admin_permission.py")

with col3:
    if st.button("📝 Create an EPM ticket"):
        st.session_state.device_current_page = "0b_blocked_yellow"
        st.switch_page("pages/0b_blocked_yellow.py")

with col4:
    if st.button("📧 Send follow-up mail"):
        st.session_state.device_current_page = "0c_blocked_red"
        st.switch_page("pages/0c_blocked_red.py")

with col5:
    if st.button("➕ Request a new whitelist entry"):
        st.session_state.device_current_page = "1_it_service_direkt"
        st.switch_page("pages/1_it_service_direkt.py")
