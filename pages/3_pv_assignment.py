import streamlit as st
from state.tickets import get_all_tickets, set_all_tickets
from components.ticket_history import add_ticket_event
from datetime import datetime

st.session_state["device_current_page"] = "pv_context_request"

user = st.session_state.get("user", {})
username = user.get("username", "unknown")

st.title("🛠 PV Context Required")

# Load tickets
tickets = get_all_tickets()
pv_context_tickets = [t for t in tickets if t.get("status") == "PV_CONTEXT_REQUIRED"]

if not pv_context_tickets:
    st.info("No tickets pending PV context input.")
    st.stop()

selected_ticket_id = st.selectbox(
    "Select ticket to provide missing PV context",
    [t["ticket_id"] for t in pv_context_tickets]
)

ticket = next(t for t in pv_context_tickets if t["ticket_id"] == selected_ticket_id)

st.subheader(f"Ticket: {ticket.get('application')} ({ticket['ticket_id']})")
st.write(f"**Reason:** {ticket.get('reason', '')}")
st.write(f"**Created by:** {ticket.get('created_by', '')}")

# =========================================================
# A. Deployment & Business Criticality
# =========================================================
st.header("A. Deployment & Business Criticality")
col1, col2, col3 = st.columns(3)

with col3:
    deployment = st.selectbox(
        "Deployment type",
        ["SaaS", "On-Prem", "Hybrid"],
        index=["SaaS", "On-Prem", "Hybrid"].index(ticket.get("deployment", "SaaS"))
    )
    business_criticality = st.selectbox(
        "Business criticality",
        ["Low", "Medium", "High", "Mission Critical"],
        index=["Low", "Medium", "High", "Mission Critical"].index(ticket.get("business_criticality", "Medium"))
    )

# =========================================================
# B. Risk & Compliance Indicators
# =========================================================
st.header("B. Risk & Compliance Indicators")
col1, col2, col3 = st.columns(3)

with col1:
    personal_data = st.checkbox("Processes personal data", value=ticket.get("personal_data", False))
    authentication = st.checkbox("Authenticates users", value=ticket.get("authentication", False))

with col2:
    internet_exposed = st.checkbox("Internet exposed", value=ticket.get("internet_exposed", False))
    regulatory_relevant = st.checkbox("Regulatory relevant", value=ticket.get("regulatory_relevant", False))

with col3:
    availability = st.selectbox(
        "Availability requirement",
        ["Best effort", "Business hours", "24/7"],
        index=["Best effort", "Business hours", "24/7"].index(ticket.get("availability", "Business hours"))
    )
    data_classification = st.selectbox(
        "Data classification",
        ["Public", "Internal", "Confidential", "Restricted"],
        index=["Public", "Internal", "Confidential", "Restricted"].index(ticket.get("data_classification", "Internal"))
    )

# =========================================================
# C. Operational Characteristics
# =========================================================
st.header("C. Operational Characteristics")
col1, col2, col3 = st.columns(3)

with col1:
    user_count = st.selectbox(
        "Number of users",
        ["<50", "50–500", "500–5000", ">5000"],
        index=["<50", "50–500", "500–5000", ">5000"].index(ticket.get("user_count", "<50"))
    )
    support_model = st.selectbox(
        "Support model",
        ["None", "Best effort", "Defined SLA"],
        index=["None", "Best effort", "Defined SLA"].index(ticket.get("support_model", "Best effort"))
    )

with col2:
    change_frequency = st.selectbox(
        "Change frequency",
        ["Rare", "Occasional", "Frequent"],
        index=["Rare", "Occasional", "Frequent"].index(ticket.get("change_frequency", "Occasional"))
    )
    release_frequency = st.selectbox(
        "Release frequency",
        ["Ad-hoc", "Planned", "Continuous"],
        index=["Ad-hoc", "Planned", "Continuous"].index(ticket.get("release_frequency", "Planned"))
    )

with col3:
    integrations = st.selectbox(
        "Integration criticality",
        ["None", "Low", "High"],
        index=["None", "Low", "High"].index(ticket.get("integrations", "Low"))
    )
    customization = st.selectbox(
        "Customization level",
        ["Standard", "Configured", "Highly customized"],
        index=["Standard", "Configured", "Highly customized"].index(ticket.get("customization", "Standard"))
    )

# =========================================================
# Save PV Context
# =========================================================
if st.button("✅ Submit PV Context"):
    ticket.update({
        "deployment": deployment,
        "business_criticality": business_criticality,
        "personal_data": personal_data,
        "authentication": authentication,
        "internet_exposed": internet_exposed,
        "regulatory_relevant": regulatory_relevant,
        "availability": availability,
        "data_classification": data_classification,
        "user_count": user_count,
        "support_model": support_model,
        "change_frequency": change_frequency,
        "release_frequency": release_frequency,
        "integrations": integrations,
        "customization": customization,
        "status": "PV_CONTEXT_PROVIDED",
        "journey": "pv_context_request",
    })

    add_ticket_event(
        ticket,
        action="PV context provided by user",
        actor=username,
        details={
            "deployment": deployment,
            "business_criticality": business_criticality,
            "personal_data": personal_data,
            "authentication": authentication,
            "internet_exposed": internet_exposed,
            "regulatory_relevant": regulatory_relevant,
            "availability": availability,
            "data_classification": data_classification,
            "user_count": user_count,
            "support_model": support_model,
            "change_frequency": change_frequency,
            "release_frequency": release_frequency,
            "integrations": integrations,
            "customization": customization,
        },
        new_status="PV_CONTEXT_PROVIDED"
    )

    set_all_tickets(tickets)
    st.success("PV context submitted successfully! PV assignment can now proceed.")
