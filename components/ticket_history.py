from datetime import datetime

def add_ticket_event(
    ticket: dict,
    action: str,
    actor: str,
    details: dict | None = None,
    new_status: str | None = None,
):
    """
    Append a decision/event to a ticket's history.

    Parameters:
    - ticket: the ticket dict to update
    - action: short description (e.g. 'IS-P Review Completed')
    - actor: who performed the action (e.g. 'IS-P', 'IS-G', username)
    - details: optional dict with structured info
    - new_status: optional status update for the ticket
    """

    # Ensure history exists
    ticket.setdefault("history", [])

    # Create event
    event = {
        "timestamp": datetime.now().isoformat(),
        "actor": actor,
        "action": action,
        "details": details or {},
    }

    # Append event
    ticket["history"].append(event)

    # Optionally update ticket status
    if new_status:
        ticket["status"] = new_status


def sync_department_reviews_from_history(ticket: dict):
    """
    Populate ticket['department_reviews'] based on history events.
    Each department keeps a list of comment history.
    Last event per department wins for decision/comment display.
    """
    ticket.setdefault("department_reviews", {})

    for event in ticket.get("history", []):
        details = event.get("details", {})
        department = details.get("department")
        if not department:
            continue

        review = ticket["department_reviews"].setdefault(department, {})
        review.setdefault("history", [])

        # Append comment to history if exists
        if "comment" in details:
            review["history"].append({
                "timestamp": event.get("timestamp"),
                "actor": event.get("actor"),
                "comment": details["comment"],
                "decision": details.get("decision"),
                "domain": details.get("domain"),
                "capabilities": details.get("capabilities"),
                "source": details.get("source")
            })

        # Always update current decision for UI selectbox etc.
        if "decision" in details:
            review["decision"] = details["decision"]
        if "comment" in details:
            review["comment"] = details["comment"]

        # Add other enrichment
        review["actor"] = event.get("actor")
        review["timestamp"] = event.get("timestamp")
        if "domain" in details:
            review["domain"] = details["domain"]
        if "capabilities" in details:
            review["capabilities"] = details["capabilities"]
