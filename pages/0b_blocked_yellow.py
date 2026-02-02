import streamlit as st
from components.requirements import show_requirements
from components.ticket_history import add_ticket_event
from state.permissions import require_system
from state.tickets import create_ticket
from state.luy import get_current_luy_app
from state.epm_lists import find_epm_entry



st.session_state["device_current_page"] = "0b_blocked_yellow"  # unique per page

# ------------------------
# Require login
# ------------------------
require_system("device")

# ------------------------
# LUY App (source of truth)
# ------------------------
if "scanner_yellow_app" not in st.session_state:
    st.session_state.scanner_yellow_app = get_current_luy_app()

app_name = st.session_state.scanner_yellow_app

# ------------------------
# Page header
# ------------------------
st.title("🟡 EPM Scanner – Program Blocked (Approval Required)")
st.write(f"**Software:** {app_name}")

st.warning(
    f"The program **{app_name}** is **not whitelisted** and requires approval."
)

# ------------------------
# Lookup EPM context
# ------------------------
epm_entry = find_epm_entry(app_name)

with st.expander("📘 Why is this software blocked? (System context)", expanded=True):
    if epm_entry:
        st.markdown(f"**Category:** {epm_entry.get('Category')}")
        st.markdown(f"**Policy:** {epm_entry.get('Policy')}")
        st.markdown(f"**Reason (IT / Policy):** {epm_entry.get('Reason')}")
        st.markdown(f"**Entry Date:** {epm_entry.get('EntryDate')}")
        st.markdown(f"**Decision Date:** {epm_entry.get('DecisionDate') or 'Not decided yet'}")
    else:
        st.info("No existing policy information found. This software is currently unclassified.")

    if st.button("🔎 View full details in EPM Dashboard"):
        st.switch_page("pages/6_epm_scanner_dashboard.py")

# ------------------------
# Current user
# ------------------------
user = st.session_state.get("user")
if not user:
    st.warning("Please login first.")
    st.stop()

username = user["username"]

# ------------------------
# User justification
# ------------------------
with st.form("yellow_whitelist_form"):
    st.subheader("📝 Request Whitelisting / Justify Usage")

    user_reason = st.text_area(
        "Why do you need this software?",
        placeholder="Describe business need, duration, impact if blocked…"
    )

    col1, col2 = st.columns(2)
    cancel = col1.form_submit_button("Cancel")
    submit = col2.form_submit_button("Send Request")

# ------------------------
# Cancel
# ------------------------
if cancel:
    st.info("Action cancelled. The program remains blocked.")

# ------------------------
# Submit ticket
# ------------------------
if submit:
    if not user_reason.strip():
        st.error("Please provide a justification.")
    else:
        ticket = create_ticket(
            source="EPM Scanner Yellow",
            application=app_name,
            reason=user_reason,
            journey="scanner_yellow",
            status="Created",
            created_by=username,
            metadata={
                "epm_category": epm_entry.get("Category") if epm_entry else None,
                "epm_policy": epm_entry.get("Policy") if epm_entry else None,
            }
        )

        # ✅ ADD HISTORY EVENT
        add_ticket_event(
            ticket,
            action="Whitelist Request Submitted",
            actor=username,
            details={
                "source": "EPM Scanner Yellow",
                "application": app_name,
                "justification": user_reason,
                "epm_category": epm_entry.get("Category") if epm_entry else None,
                "epm_policy": epm_entry.get("Policy") if epm_entry else None,
            },
            new_status="Submitted for Review",
        )

        st.session_state.latest_ticket = ticket
        st.success("✅ Whitelist request sent successfully.")


# ------------------------
# Ticket shortcut
# ------------------------
ticket = st.session_state.get("latest_ticket")
if ticket:
    if st.button(f"🎟 Ticket ID: {ticket['ticket_id']}"):
        st.switch_page("pages/17_ticket_history.py")

# ------------------------
# Questions / Todos
# ------------------------
show_requirements(
    "Scanner Yellow Popup",
    items=[
        {
            "id": "Granularity",
            "text": "Should users always see policy reasons or only high-level explanations?",
        },
        {
            "id": "Just_in_Time_Scenarios",
            "text": "Do we allow time-bound whitelisting?"
        },
        {
            "id": "popularity",
            "text": "Do repeated requests influence decision confidence?"
        }
    ],
    req_type="question"
)

show_requirements(
    "Scanner Yellow Popup",
    items=[
        {
            "id": "Severity",
            "text": "Add policy severity (Low / Medium / High).",
        },
        {
            "id": "Auto_approval",
            "text": "Add auto-approval for known business domains."
        },
        {
            "id": "interop.",
            "text": "Link LUY → CMDB → EPM decision trace."
        },
        {
            "id": "System context",
            "text": "system context data presently doesn't make much sense, need to improve it."
        }
    ],
    req_type="todo"
)

# ------------------------
# Original popup reference
# ------------------------
with st.expander("Popup that leads to EPM ticket"):
    st.image("images/blocked_yellow_1.png")

with st.expander("Popup that leads to EPM ticket"):
    st.image("images/blocked_yellow_2.png")    