import streamlit as st

def init_app_state():
    """
    Global session bootstrap.
    Safe to call from any page.
    """

    # -----------------------------
    # Unified Identity
    # -----------------------------
    if "user" not in st.session_state:
        st.session_state.user = None

    # -----------------------------
    # Global UI helpers
    # -----------------------------
    if "notifications" not in st.session_state:
        st.session_state.notifications = []

    if "initialized" not in st.session_state:
        st.session_state.initialized = True
