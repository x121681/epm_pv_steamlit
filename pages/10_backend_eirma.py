import streamlit as st
from components.greylist_communication import show_greylist_review

st.title("🔐 EIRMA – Security Repository")

st.info("""
Simulated security metadata: protection requirements, classification, 
risk assessments, findings, and remediation tasks.
""")

# Example: pass the ticket_id dynamically from selection
ticket_id = st.session_state.get("current_ticket_id")  # you can set this somewhere
show_greylist_review("CSO-I")
