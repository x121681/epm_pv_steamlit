import streamlit as st
from components.greylist_communication import show_greylist_review

st.title("📦 CMDB / CMS – Configuration Items")

st.info("""
Simulated CMDB records including installed versions, environment, 
responsible teams, dependencies, and lifecycle states.
""")


show_greylist_review("IS-G")
