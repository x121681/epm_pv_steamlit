from datetime import datetime, timezone
import streamlit as st

def populate_epm_lists_from_luy():
    """
    Populate blacklist, whitelist, and greylist from LUY entries.
    Handles both string entries and dict entries with a 'Software' key.
    Adds EntryDate (now UTC) and DecisionDate (None by default).
    """
    # Initialize lists if not present
    if "epm_blacklist" not in st.session_state:
        st.session_state.epm_blacklist = []
    if "epm_whitelist" not in st.session_state:
        st.session_state.epm_whitelist = []
    if "epm_greylist" not in st.session_state:
        st.session_state.epm_greylist = []

    # Get LUY entries
    luy_entries = st.session_state.get("luy_entries", [])

    if not luy_entries:
        return  # nothing to populate

    # For demo purposes, just take first N entries
    num_entries = min(len(luy_entries), 3)

    blacklist = []
    whitelist = []
    greylist = []

    for i, app in enumerate(luy_entries[:num_entries]):
        software_name = app["Software"] if isinstance(app, dict) else str(app)

        # Alternate placing entries in black/white/grey for demonstration
        if i % 3 == 0:
            target_list = blacklist
            policy = "Blacklisted"
        elif i % 3 == 1:
            target_list = whitelist
            policy = "Whitelisted"
        else:
            target_list = greylist
            policy = "Greylist"

        target_list.append({
            "Software": software_name,
            "Reason": "Automatically populated from LUY",
            "Policy": policy,
            "EntryDate": datetime.now(timezone.utc),
            "DecisionDate": None
        })

    # Save back to session state
    st.session_state.epm_blacklist = blacklist
    st.session_state.epm_whitelist = whitelist
    st.session_state.epm_greylist = greylist
