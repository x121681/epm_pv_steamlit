import streamlit as st
import pandas as pd
from state.permissions import require_system
from state.tickets import (
    get_all_tickets,
    set_all_tickets,
)
from components.ticket_history import add_ticket_event, sync_department_reviews_from_history
from components.requirements import show_requirements

st.session_state["device_current_page"] = "8_approval_required"  # unique per page

# -----------------------------
# Page config
# -----------------------------
st.set_page_config(page_title="MPI – Greylist Approvals", layout="wide")
st.title("🔐 MPI – Greylist Approval Dashboard")
st.caption("View and manage Greylist software approval requests (parallel departmental reviews)")

# -----------------------------
# Access control
# -----------------------------
require_system("epm")

user = st.session_state.get("user")
if not user:
    st.error("Please log in to continue.")
    st.stop()

roles = user.get("roles", [])
username = user.get("username", "Unknown")
actor = username
is_admin = "admin" in roles

# -----------------------------
# Load all tickets
# -----------------------------
tickets = get_all_tickets()
if not tickets:
    st.info("No tickets available.")
    st.stop()

# -----------------------------
# Filter greylist tickets
# -----------------------------
greylist = [t for t in tickets if t.get("decision", "").lower() == "greylist"]

if not greylist:
    st.info("No Greylist tickets found.")
    st.stop()

# -----------------------------
# Table of all Greylist tickets
# -----------------------------
st.subheader("All Greylist Tickets")

df = pd.DataFrame([
    {
        "TicketID": t["ticket_id"],
        "Application": t["application"],
        "Reason": t.get("reason",""),
        "Status": t.get("approval_status","Pending"),
        "Step": t.get("approval_step","Department Review"),
        "Created By": t.get("created_by","Unknown"),
        "Date": t.get("date","")
    }
    for t in greylist
])

options = [f"{row['Application']} – {row['TicketID']}" for _, row in df.iterrows()]

selected_option = st.selectbox(
    "Select a ticket to view / edit",
    options=options
)

selected_ticket_id = selected_option.split(" – ")[1]
ticket = next((t for t in greylist if t["ticket_id"] == selected_ticket_id), None)
sync_department_reviews_from_history(ticket)

# -----------------------------
# Display selected ticket details
# -----------------------------
if ticket:
    st.markdown("---")
    st.header(f"Ticket Details: {ticket['application']} ({ticket['ticket_id']})")

    st.subheader("Basic Information")
    st.write(f"**Application:** {ticket['application']}")
    st.write(f"**Reason:** {ticket.get('reason','')}")
    st.write(f"**Requested by:** {ticket.get('created_by','Unknown')}")
    st.write(f"**Decision:** {ticket.get('decision','')}")
    st.write(f"**Approval Status:** {ticket.get('approval_status','Pending')}")
    st.write(f"**Departments Informed:** {', '.join(ticket.get('departments_informed',[]))}")

    st.markdown("---")
    st.subheader("Department Reviews (Parallel)")

    departments = ticket.get("departments_informed", [])
    updates_made = False

    for dept in departments:
        review = ticket["department_reviews"].get(dept, {})
        decision = review.get("decision")
        comment = review.get("comment", "")

        # =======================
        # Admin editing
        # =======================
        if is_admin:
            with st.expander(f"{dept} Review", expanded=True):
                new_decision = st.radio(
                    f"{dept} decision",
                    ["Approve", "Reject", "Need More Information"],
                    index=["Approve","Reject","Need More Information"].index(decision) if decision else 0,
                    key=f"{ticket['ticket_id']}_{dept}_decision"
                )
                new_comment = st.text_area(
                    f"{dept} comment",
                    value=comment,
                    key=f"{ticket['ticket_id']}_{dept}_comment"
                )

                if new_decision != decision or new_comment != comment:
                    ticket["department_reviews"][dept]["decision"] = new_decision
                    ticket["department_reviews"][dept]["comment"] = new_comment
                    updates_made = True

                    # ✅ HISTORY EVENT
                    add_ticket_event(
                        ticket,
                        action=f"{dept} review updated",
                        actor=actor,
                        details={
                            "department": dept,
                            "decision": new_decision,
                            "comment": new_comment,
                            "domain": review.get("domain"),
                            "capabilities": review.get("capabilities", [])
                        }
                    )
        else:
            st.write(f"**{dept} Decision:** {decision or 'Pending'}")
            st.write(f"**{dept} Comment:** {comment or '—'}")

        # =======================
        # Review History
        # =======================
        history_entries = [
            h for h in ticket.get("history", [])
            if h.get("details", {}).get("department") == dept
        ]
        if history_entries:
            with st.expander(f"{dept} Review History ({len(history_entries)} entries)", expanded=False):
                for h in reversed(history_entries):  # newest first
                    st.write(f"**{h['timestamp']} | {h['actor']} | {h['details'].get('decision', '')}**")
                    st.write(f"Comment: {h['details'].get('comment','')}")
                    if h["details"].get("domain"):
                        st.write(f"Domain: {h['details'].get('domain')}")
                    if h["details"].get("capabilities"):
                        st.write(f"Capabilities: {', '.join(h['details'].get('capabilities',[]))}")
                    st.markdown("---")

    # -----------------------------
    # Detect all reviews completed (once)
    # -----------------------------
    all_decisions = [
        ticket["department_reviews"][d]["decision"]
        for d in departments
    ]

    if all(all_decisions) and not ticket.get("_all_reviews_logged"):
        add_ticket_event(
            ticket,
            action="All departmental reviews completed",
            actor="system",
            details={
                "departments": departments,
                "decisions": {
                    d: ticket["department_reviews"][d]["decision"]
                    for d in departments
                }
            }
        )
        ticket["_all_reviews_logged"] = True

    if is_admin and updates_made:
        set_all_tickets(tickets)
        st.success("✅ Department reviews updated")

    # -----------------------------
    # Final Decision Summary
    # -----------------------------
    st.markdown("---")
    st.subheader("Final Decision Summary")

    if "Reject" in all_decisions:
        final_status = "REJECTED"
        st.error("❌ Final Decision: REJECTED")
    elif "Need More Information" in all_decisions:
        final_status = "PENDING"
        st.warning("⚠ Final Decision: ON HOLD / MORE INFORMATION REQUIRED")
    elif all(d == "Approve" for d in all_decisions):
        final_status = "APPROVED"
        st.success("✅ Final Decision: APPROVED")
    else:
        final_status = "PENDING"
        st.info("ℹ Waiting for departmental input...")

    # -----------------------------
    # Apply final decision
    # -----------------------------
    if is_admin:
        if st.button("Apply Final Decision & Update Ticket"):
            ticket["approval_status"] = final_status

            # ✅ HISTORY EVENT
            add_ticket_event(
                ticket,
                action="Final Greylist decision applied",
                actor=actor,
                details={
                    "final_status": final_status,
                    "department_decisions": {
                        d: ticket["department_reviews"][d]["decision"]
                        for d in departments
                    }
                },
                new_status=final_status
            )

            set_all_tickets(tickets)
            st.success(f"Ticket updated. Final status: {final_status}")

# -----------------------------
# Notes / Todos
# -----------------------------
show_requirements(
    "approval required",
    items=[
        {
            "id": "grey_align_notifications",
            "text": "How deadlines are being aligned between departments and notifications on following schedule we have to think about it",
        }
    ],
    req_type="question"
)

show_requirements(
    "approval required",
    items=[
        {
            "id": "responsiblity",
            "text": "Each department is responsible for their own internal process.",
        },
         {
            "id": "deadlines",
            "text": "Deadlines should be obliged to",
        },
        {
            "id": "api_mpi_luy",
            "text": "We are assuming that we can trigger directly from shop article an architectural flow process",
        }
    ],
    req_type="note"
)
