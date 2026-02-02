import streamlit as st

def init_epm_lists():
    """
    Initialize EPM policy lists in session state.
    No software entries are added here; they come from business logic elsewhere.
    """
    if "epm_blacklist" not in st.session_state:
        st.session_state.epm_blacklist = []

    if "epm_whitelist" not in st.session_state:
        st.session_state.epm_whitelist = []

    if "epm_greylist" not in st.session_state:
        st.session_state.epm_greylist = []


def get_epm_lists():
    return (
        st.session_state.epm_blacklist,
        st.session_state.epm_whitelist,
        st.session_state.epm_greylist,
    )


def set_epm_lists(black, white, grey):
    st.session_state.epm_blacklist = black
    st.session_state.epm_whitelist = white
    st.session_state.epm_greylist = grey

def find_epm_entry(app_name):
    blacklist = st.session_state.get("epm_blacklist", [])
    whitelist = st.session_state.get("epm_whitelist", [])
    greylist = st.session_state.get("epm_greylist", [])

    for entry in blacklist:
        if entry.get("Software") == app_name:
            return entry | {"Category": "Blacklist"}

    for entry in whitelist:
        if entry.get("Software") == app_name:
            return entry | {"Category": "Whitelist"}

    for entry in greylist:
        if entry.get("Software") == app_name:
            return entry | {"Category": "Greylist"}

    return None
