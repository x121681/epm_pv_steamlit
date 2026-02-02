import streamlit as st
from datetime import datetime

from state.permissions import require_system
from state.tickets import get_all_tickets, find_ticket
from components.requirements import show_requirements

# -------------------------
# Guard: must be logged in
# -------------------------
require_system("device")

st.title("🎟 My Tickets")

# -------------------------
# Current logged-in user
# -------------------------
user = st.session_state.get("user")
if not user:
    st.warning("Please login first.")
    st.stop()

username = user["username"]
role = "Admin" if "admin" in user.get("roles", []) else "User"

st.caption(f"Logged in as: {username} ({role})")

# -------------------------
# Load tickets from state
# -------------------------
tickets = get_all_tickets()
if not tickets:
    st.info("No tickets have been created yet.")
    st.stop()

# -------------------------
# Role-based ticket display
# -------------------------
if role == "Admin":
    st.subheader("📋 All Tickets")
    normalized = []
    for t in tickets:
        normalized.append({
            "Ticket ID": t.get("ticket_id"),
            "Application": t.get("application"),
            "Status": t.get("status"),
            "Journey": t.get("journey"),
            "Created By": t.get("created_by"),
            "Source": t.get("source"),
            "Domain": t.get("final_domain"),
            "Capabilities": ", ".join(t.get("final_capabilities", [])),
        })
    st.dataframe(normalized, use_container_width=True)

else:
    st.subheader("👤 My Tickets")
    user_tickets = [t for t in tickets if t.get("created_by") == username]

    if not user_tickets:
        st.info("You have not created any tickets yet.")
    else:
        for t in user_tickets:
            with st.container():
                st.markdown(
                    f"**{t['ticket_id']} – {t['application']}**  \n"
                    f"Status: `{t['status']}`"
                )
                st.write(f"- Domain: {t.get('final_domain', 'N/A')}")
                st.write(f"- Capabilities: {', '.join(t.get('final_capabilities', []))}")

                if t.get("status") == "PV_CONTEXT_REQUIRED":
                    if st.button(
                        "Continue – Provide PV Context",
                        key=f"pv_{t['ticket_id']}"
                    ):
                        st.session_state["selected_ticket"] = t["ticket_id"]
                        st.switch_page("pages/22_PV_context_mapping.py")

# -------------------------
# Ticket history
# -------------------------
st.markdown("### 🕒 Ticket Decision History")

selected_ticket_id = st.selectbox(
    "Select a ticket to view history",
    [t["ticket_id"] for t in tickets]
)

ticket = find_ticket(selected_ticket_id)

if not ticket:
    st.warning("Ticket not found.")
    st.stop()

st.markdown(f"**Ticket Status:** `{ticket.get('status')}`")
st.markdown(f"**Final Domain:** {ticket.get('final_domain')}")
st.markdown(
    f"**Final Capabilities:** {', '.join(ticket.get('final_capabilities', []))}"
)

# =========================================================
# PV RESPONSIBILITY FINALIZATION (CUSTOMER VIEW)
# =========================================================

if ticket.get("status") == "PV_RESP_FINALIZATION":

    st.divider()
    st.header("🧾 PV Responsibility Finalization")

    derived = ticket.get("derived_obligations")
    if not derived:
        st.error("No derived PV obligations found for this ticket.")
        st.stop()

    st.info(
        "Based on the product context, the following PV responsibilities "
        "have been derived. Please confirm whether you are able to take over "
        "this responsibility."
    )

    # ---- Summary ----
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**Scenario:** {derived.get('scenario')}")
        st.markdown(f"**Minimum Level:** {derived.get('level')}")
    with col2:
        st.markdown(
            f"**Required PV Roles:** {', '.join(derived.get('pv_roles', []))}"
        )

    # ---- Responsibilities ----
    st.subheader("PV Responsibilities")

    grouped = derived.get("responsibilities_by_process", {})
    for process, tasks in grouped.items():
        st.markdown(f"### {process}")
        for t in tasks:
            st.markdown(
                f"- **{t['pv']}**: {t['aufgabe']} "
                f"(_{t['häufigkeit']}_)"
            )

    # ---- Decision ----
    st.subheader("Your Decision")

    decision = st.radio(
        "Do you accept the PV responsibility?",
        ["Accept", "Reject"],
        horizontal=True
    )

    reason = st.text_area(
        "Reason (mandatory)",
        placeholder="Please explain your decision…"
    )

    if st.button("Submit decision"):
        if not reason.strip():
            st.error("A reason is required.")
            st.stop()

        acceptance = {
            "decision": "ACCEPTED" if decision == "Accept" else "REJECTED",
            "reason": reason,
            "decided_by": username,
            "decided_at": datetime.now().isoformat(),
        }

        ticket["pv_acceptance"] = acceptance
        ticket["status"] = (
            "APPROVED" if decision == "Accept" else "REJECTED"
        )

        ticket.setdefault("history", []).append({
            "action": "PV_RESPONSIBILITY_DECISION",
            "actor": username,
            "timestamp": acceptance["decided_at"],
            "details": acceptance,
        })

        st.success(f"Decision recorded: {acceptance['decision']}")

# -------------------------
# History log
# -------------------------
history = ticket.get("history", [])
if not history:
    st.info("No decision history available.")
else:
    st.markdown("#### Event History")
    for h in reversed(history):
        st.markdown(
            f"""
            **{h.get('action', 'Update')}**  
            *By:* {h.get('actor', 'Unknown')}  
            *At:* {h.get('timestamp', 'Unknown')}  
            *Details:* `{h.get('details', {})}`  
            ---
            """
        )

show_requirements(
    "ticket History",
    items=[
        {
            "id": "improve log",
            "text": "log is difficult to understand, we need to improve it",
        }
    ],
    req_type="todo"
)
