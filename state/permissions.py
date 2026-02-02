import streamlit as st


def require_system(system_name):
    """
    Ensure the logged-in user has access to the given system.
    Stops execution if access denied.
    """
    user = st.session_state.get("user")
    if not user:
        st.warning("Please login first.")
        st.stop()

    if system_name not in user.get("systems", []):
        st.warning(f"Access denied: you do not have access to {system_name}.")
        st.stop()

def require_role(role):
    """
    Stops execution if the logged-in user does not have the required role.
    """
    user = st.session_state.get("user")
    if not user or role not in user.get("roles", []):
        st.error("Insufficient permissions.")
        st.stop()
