import streamlit as st
import uuid
from datetime import datetime

# -------------------------
# TICKET LIFECYCLE STATUSES
# -------------------------
TICKET_STATUSES = [
    "DRAFT",
    "ARCH_REVIEW_IN_PROGRESS",
    "DOMAIN_CAPABILITY_FINALIZED",
    "PV_CONTEXT_REQUIRED",
    "PV_RESP_FINALIZATION",
    "PV_ASSIGNED",
    "APPROVED",
    "REJECTED",
]

# -------------------------
# PV CONTEXT TEMPLATE
# -------------------------
def default_pv_context():
    return {
        # Product / deployment
        "deployment": None,
        "business_criticality": None,
        "urgency": None,
        "data_classification": None,

        # Risk indicators
        "personal_data": False,
        "internet_exposed": False,
        "authentication": False,
        "regulatory_relevant": False,

        # Operations
        "user_count": None,
        "support_model": None,
        "change_frequency": None,
        "release_frequency": None,
        "integrations": None,
        "customization": None,

        # Derived later by PV engine
        "derived": {
            "min_level": None,
            "required_roles": [],
            "required_processes": []
        }
    }

# -------------------------
# INITIALIZATION
# -------------------------
def init_tickets():
    if "tickets" not in st.session_state:
        st.session_state.tickets = []
    if "latest_ticket" not in st.session_state:
        st.session_state.latest_ticket = None

# -------------------------
# CREATE TICKET
# -------------------------
def create_ticket(
    source,
    application,
    reason,
    status="DRAFT",
    journey=None,
    created_by=None,
    extra=None,
    metadata=None
):
    """
    Create a new ticket and store in session state.
    Backward compatible with older pages.
    """
    init_tickets()

    created_by = created_by or st.session_state.get(
        "epm_username",
        st.session_state.get("device_username", "unknown"),
    )

    ticket = {
        "ticket_id": f"TICKET-{uuid.uuid4().hex[:8].upper()}",
        "source": source,
        "application": application,
        "reason": reason,
        "status": status,
        "journey": journey,
        "created_by": created_by,
        "urgency": extra.get("urgency", "Normal") if extra else "Normal",
        "date": datetime.now().isoformat(),

        # Optional metadata
        "metadata": metadata or {},

        # Architecture outputs
        "final_domain": None,
        "final_capabilities": [],

        # PV Context (lazy initialized)
        "pv_context": None,

        # History
        "history": []
    }

    # Merge legacy extra fields (non-breaking)
    if extra:
        ticket.update(extra)

    st.session_state.tickets.append(ticket)
    st.session_state.latest_ticket = ticket
    return ticket

# -------------------------
# GETTERS
# -------------------------
def get_latest_ticket():
    init_tickets()
    return st.session_state.latest_ticket

def get_all_tickets():
    init_tickets()
    return st.session_state.tickets

def set_all_tickets(ticket_list):
    """
    Overwrite all tickets.
    Maintains latest_ticket pointer.
    """
    init_tickets()
    st.session_state.tickets = ticket_list
    st.session_state.latest_ticket = ticket_list[-1] if ticket_list else None

# -------------------------
# HISTORY & EVENTS
# -------------------------
def add_ticket_event(ticket, action, actor=None, details=None, status=None):
    """
    Adds a structured event to the ticket history.
    Optionally updates ticket status.
    """
    init_tickets()
    actor = actor or st.session_state.get("user", {}).get("username", "system")

    event = {
        "action": action,
        "actor": actor,
        "timestamp": datetime.now().isoformat(),
        "details": details or {}
    }

    ticket.setdefault("history", []).append(event)

    if status:
        if status not in TICKET_STATUSES:
            raise ValueError(
                f"Invalid status '{status}', must be one of {TICKET_STATUSES}"
            )
        ticket["status"] = status

# -------------------------
# PV CONTEXT HELPERS
# -------------------------
def ensure_pv_context(ticket):
    """
    Ensure the ticket has a PV context.
    Safe for old tickets.
    """
    if ticket.get("pv_context") is None:
        ticket["pv_context"] = default_pv_context()
    return ticket["pv_context"]

def require_pv_context(ticket, actor="system"):
    """
    Move ticket into PV_CONTEXT_REQUIRED and initialize PV context.
    """
    ensure_pv_context(ticket)
    add_ticket_event(
        ticket,
        action="PV Context Required",
        actor=actor,
        status="PV_CONTEXT_REQUIRED"
    )

# -------------------------
# UTILITY: FIND TICKET
# -------------------------
def find_ticket(ticket_id):
    init_tickets()
    for t in st.session_state.tickets:
        if t["ticket_id"] == ticket_id:
            return t
    return None
