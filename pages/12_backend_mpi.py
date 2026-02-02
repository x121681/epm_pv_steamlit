import streamlit as st
from components.greylist_communication import show_greylist_review

st.title("📘 MPI – Ticketing & Lifecycle Process")

st.info("""
This simulates MPI ticketing, lifecycle status, and approval routing information 
used in the EPM Freigabeprozess.
""")


show_greylist_review("IS-G")
