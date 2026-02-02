import streamlit as st
import random
from state.tickets import get_latest_ticket
from components.requirements import show_requirements
from components.ticket_history import add_ticket_event


st.session_state["device_current_page"] = "5_shop_artikel"  # unique per page


user = st.session_state.get("user", {})
actor = user.get("username", "system")

def send_greylist_email(ticket):
    recipients = [
        "EAM-admins@bsh.com",
        "IS-G@bsh.com",
        "CSO-I@bsh.com",
        "IS-V@BSH.com"
    ]

    subject = f"[EPM Greylist Review] {ticket['application']} – Ticket {ticket['ticket_id']}"
    
    body = f"""
Hello Team,

A new Greylist software request has been submitted and requires your review.

Ticket ID: {ticket['ticket_id']}
Application: {ticket['application']}
Created By: {ticket['created_by']}
Reason: {ticket['reason']}
Urgency: {ticket.get('urgency', 'Normal')}
License Type: {ticket.get('license_type', 'Unknown')}
License Cost: {ticket.get('license_cost', 'N/A')}
Vendor: {ticket.get('vendor', 'N/A')}
Infrastructure: {ticket.get('infrastructure', 'N/A')}

Please provide your feedback and final decision: Whitelist / Blacklist / Need More Information.

Thank you.
"""

    # In prototype: just show as a message
    st.info(f"📧 Email would be sent to {', '.join(recipients)}")
    st.text_area("Email Body (Simulated)", body, height=300)


st.title("🛒 Shop Artikel MPI Process")

# -------------------------------------------------
# Load active ticket (REUSE existing mechanism)
# -------------------------------------------------
ticket = get_latest_ticket()

if ticket is None:
    st.error(
        "No active ticket found.\n\n"
        "Shop Artikel must be triggered from IT Service Direct "
        "or a Scanner decision page."
    )
    st.stop()

# -------------------------------------------------
# Show ticket context
# -------------------------------------------------
st.subheader(f"Ticket ID: {ticket.get('ticket_id')}")
st.write(f"**Application:** {ticket.get('application')}")
st.write(f"**Reason:** {ticket.get('reason')}")
st.write(f"**Created by:** {ticket.get('created_by', 'Unknown')}")

# -------------------------------------------------
# Validate required data
# -------------------------------------------------
if not ticket.get("application") or not ticket.get("reason"):
    st.warning("Ticket is missing required data. Cannot proceed.")
    st.stop()

# -------------------------------------------------
# Process step (NO creation, ONLY enrichment)
# -------------------------------------------------
if st.button("Submit for AI Check"):
   # decision = random.choice(["whitelist", "blacklist", "Greylist"])
    decision = "Greylist" #remove this only for testing
    ticket["status"] = "Shop Artikel Completed"
    ticket["decision"] = decision
    ticket["journey"] = "shop_artikel"

    add_ticket_event(
    ticket,
    action="Shop Artikel decision completed",
    actor=actor,
    details={
        "decision": decision,
        "application": ticket.get("application"),
    },
    new_status="Shop Artikel Completed"
)

    if decision == "Greylist":
        ticket["approval_required"] = True
        ticket["approval_type"] = "Freigabe"
        ticket["departments_informed"] = ["IS-P", "CSO-I", "IS-G", "IS-V"]
        # 🔁 Phase-based, parallel approval
        ticket["approval_status"] = "Pending"
        ticket["approval_step"] = "Department Review"

    # 🧩 Parallel department reviews (initialized once)
        ticket["department_reviews"] = {
        "CSO-I": {
            "decision": None,
            "comment": "",
            "contacted": True,
            "responded_at": None,
        },
        "IS-P": {
            "decision": None,
            "comment": "",
            "contacted": True,
            "responded_at": None,
        },
        "IS-G": {
            "decision": None,
            "comment": "",
            "contacted": True,
            "responded_at": None,
        },
        "IS-V": {
            "decision": None,
            "comment": "",
            "contacted": True,
            "responded_at": None,
        },
    }
    else:
        ticket["approval_required"] = False
        ticket["approval_type"] = None
        ticket["departments_informed"] = []

    add_ticket_event(
    ticket,
    action="Greylist review initiated",
    actor="system",
    details={
        "departments_notified": ticket.get("departments_informed", []),
        "approval_step": ticket.get("approval_step"),
    },
    new_status="Pending Department Review"
    )

    st.success(f"Decision made: {decision.upper()}")

    if decision == "Greylist":
        send_greylist_email(ticket)
        st.switch_page("pages/8_approval_required.py")
    else:
        st.switch_page("pages/13_summary.py")



with st.expander("Shop Artikel MPI Process Flowchart"):
    st.image("images/shop_artikel.png")

show_requirements(
    "shop article",
    items=[
        {
            "id": "stakeholder_contact",
            "text": "How the stakeholeders like CSO-I, IS-P are informed is not clear? Per E-Mail?",
        },
        {
            "id": "stakeholder_feedback",
            "text": "How there feedback is collected, also per e-mail and manual?",
        },
        {
            "id": "arch_criteria",
            "text": "Also it is not clear when a software needs to be evaluated by Architecture Board, what criteria are architectural?",
        },
        {
            "id": "decision_black/white/grey_criteria",
            "text": "Presently, a dummy AI check which randomly allocates in white / grey / blacklist allocates is done but eventually "
            "we need to understand how EPM-admin plan to do this? in this case it also is Freigabe possible , needed or not needed?",
        }
    ],
    req_type="question"
)

show_requirements(
    "shop article",
    items=[
        {
            "id": "grey_stackholders",
            "text": "Alignment with PF, MT regarding the departments to be informed in case of Greylist decision.",
        },
        {
            "id": "criteria_listing",
            "text": "Align with PF, LS how they do plan to decide on listing or what is the procedure..",
        },
        {
            "id": "collab_model",
            "text": "Alignment with MT how the collaboration model on decision between departments looks like.",
        }
    ],
    req_type="todo"
)

show_requirements(
    "shop article",
    items=[
        {
            "id": "paramerters",
            "text": "The admin evaluates the software based on:"
                "- Security risk (malware history, remote access ability, encryption bypass)"
                "- Data protection implications (GDPR relevance, telemetry, cloud connections)"
                "- License / legal concerns"
                "- Compliance guidelines"
                "- Technical stability impact"
                "- Business need vs risk",
        }
    ],
    req_type="note"
)