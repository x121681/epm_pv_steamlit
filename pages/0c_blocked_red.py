import streamlit as st
from datetime import datetime
from urllib.parse import quote
from state.permissions import require_system
from state.tickets import create_ticket
from components.requirements import show_requirements
from components.ticket_history import add_ticket_event
from state.luy import get_current_luy_app
from state.epm_lists import find_epm_entry




st.session_state["device_current_page"] = "0c_blocked_red"  # unique per page

require_system("device")

# ------------------------
# Helper: generate mailto link
# ------------------------
def generate_mailto_link(to, subject, body):
    return f"mailto:{to}?subject={quote(subject)}&body={quote(body)}"

# ------------------------
# LUY App
# ------------------------
if "scanner_red_app" not in st.session_state:
    st.session_state.scanner_red_app = get_current_luy_app()

app_name = st.session_state.scanner_red_app

# ------------------------
# Current user
# ------------------------
user = st.session_state.get("user")
if not user:
    st.warning("Please login first.")
    st.stop()

username = user["username"]

hostname = "LAPTOP-1234"  # optional: dynamically fetch if needed
dummy_path = r"C:\Program Files\BlockedApp\app.exe"
timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# ------------------------
# Page header
# ------------------------
st.title("🔴 EPM Scanner – Software Blocked (Red)")
st.subheader(f"🚫 Application: **{app_name}**")

st.warning(
    f"The program **{app_name}** is **blocked** by policy. Administrative approval is required."
)

# ------------------------
# System context (read-only)
# ------------------------
epm_entry = find_epm_entry(app_name)
with st.expander("📘 Blocked Software Context (from EPM Dashboard)", expanded=True):
   
    if epm_entry:
        st.markdown(f"**Category:** {epm_entry.get('Category')}")
        st.markdown(f"**Policy:** {epm_entry.get('Policy')}")
        st.markdown(f"**Reason (IT / Policy):** {epm_entry.get('Reason')}")
        st.markdown(f"**Entry Date:** {epm_entry.get('EntryDate')}")
        st.markdown(f"**Decision Date:** {epm_entry.get('DecisionDate') or 'Not decided yet'}")
    else:
        st.info("No EPM policy information found for this software.")

    if st.button("🔎 View full details in EPM Dashboard"):
        st.switch_page("pages/6_epm_scanner_dashboard.py")

# ------------------------
# User justification
# ------------------------
st.subheader("📝 Provide Business Justification / Request Whitelisting")
reason = st.text_area("Describe why you need this software:", placeholder="Explain business need, impact, etc.")

col1, col2 = st.columns(2)

# ------------------------
# Send request / create ticket
# ------------------------
with col1:
    if st.button("Send Request"):
        if not reason.strip():
            st.error("A justification is required.")
        else:
            ticket = create_ticket(
                source="EPM Scanner Red",
                application=app_name,
                reason=reason,
                journey="scanner_red",
                status="Created",
                extra={
                    "epm_category": epm_entry.get("Category") if epm_entry else None,
                    "epm_policy": epm_entry.get("Policy") if epm_entry else None,
                    "executable_path": dummy_path,
                    "hostname": hostname,
                },
                created_by=username
            )

            # ✅ ADD TICKET HISTORY EVENT
            add_ticket_event(
                ticket,
                action="Red Scanner Whitelist Request Submitted",
                actor=username,
                details={
                    "application": app_name,
                    "reason": reason,
                    "epm_category": epm_entry.get("Category") if epm_entry else None,
                    "epm_policy": epm_entry.get("Policy") if epm_entry else None,
                    "executable_path": dummy_path,
                    "hostname": hostname,
                },
                new_status="Pending EPM / IS Review",
            )

            st.session_state["latest_ticket"] = ticket
            st.success(f"Request prepared. Ticket ID: {ticket['ticket_id']}")

# ------------------------
# Cancel
# ------------------------
with col2:
    if st.button("Cancel"):
        st.warning("Operation canceled. The software remains blocked.")

# ------------------------
# Email section (optional, simulated)
# ------------------------
ticket = st.session_state.get("latest_ticket")
if ticket:
    email_body = f"""
EPM Whitelist Request (RED)

Ticket ID: {ticket['ticket_id']}
Application: {ticket['application']}

Reason:
{ticket['reason']}

Technical Context:
- Executable Path: {dummy_path}
- Username: {username}
- Hostname: {hostname}
- Time: {timestamp}

Generated automatically by EPM Scanner.
"""
    mailto_link = generate_mailto_link(
        to="epm-admin@shg.de",
        subject="PM - Whitelistanfrage",
        body=email_body
    )
    st.info("Email draft prepared for EPM Admin.")
    st.markdown(f"[📧 Open email draft in Outlook]({mailto_link})", unsafe_allow_html=True)
    if st.button("✅ Send Email (Simulated)"):
        st.success("Email successfully sent to **epm-admin@shg.de**")
        st.caption(f"Sent at: {timestamp}")

        add_ticket_event(
            ticket,
            action="Whitelist Request Email Sent",
            actor=username,
            details={
                "to": "epm-admin@shg.de",
                "subject": "PM - Whitelistanfrage",
                "time": timestamp,
            },
            new_status="Submitted to EPM",
        )

        st.session_state["email_sent"] = {
            "to": "epm-admin@shg.de",
            "subject": "PM - Whitelistanfrage",
            "ticket_id": ticket["ticket_id"],
            "time": timestamp
        }


# ------------------------
# Original popup reference
# ------------------------
with st.expander("Popup that leads to Outlook"):
    st.image("images/blocked_red.png")

# ------------------------
# Questions / Notes
# ------------------------
show_requirements(
    "blocked red",
    items=[
        {
            "id": "Shop_article_trigger",
            "text": "Does the Email trigger the Shop Artikel process automatically or is manual intervention needed?",
        }
    ],
    req_type="question"
)

show_requirements(
    "blocked red",
    items=[
        {
            "id": "assume_auto_trigger",
            "text": "Until clarified, we assume email to epm-admin@shg.de triggers Shop Artikel workflow.",
        }
    ],
    req_type="todo"
)