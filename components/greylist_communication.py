import streamlit as st
from state.tickets import get_all_tickets, set_all_tickets
from components.ticket_history import add_ticket_event

def show_greylist_review(dept_name: str):
    """
    Display Greylist tickets for a given department and allow
    the department to submit decision, comments, domain, and capabilities.
    
    Parameters:
        dept_name (str): Department code, e.g., "IS-P", "IS-G", "CSO-I", "IS-V"
    """
    tickets = get_all_tickets()
    greylist_tickets = [t for t in tickets if t.get("approval_required")]

    if not greylist_tickets:
        st.info("No Greylist tickets available.")
        return

    user = st.session_state.get("user", {})
    actor = user.get("username", "Unknown")

    for t in greylist_tickets:
        t.setdefault("department_reviews", {})
        t["department_reviews"].setdefault(dept_name, {})

        with st.expander(f"{t['application']} – {t['ticket_id']}"):
            st.write(f"**Reason:** {t.get('reason','')}")
            st.write(f"**Created By:** {t.get('created_by','Unknown')}")
            st.write(f"**Urgency:** {t.get('urgency', 'Normal')}")
            st.write(f"**License Type:** {t.get('license_type','Unknown')}")
            st.write(f"**Vendor:** {t.get('vendor','N/A')}")
            st.write(f"**Infrastructure:** {t.get('infrastructure','N/A')}")

            current_review = t["department_reviews"][dept_name]
            current_decision = current_review.get("decision")
            current_comment = current_review.get("comment", "")


            # Department decision
            decision = st.radio(
                "Your decision:",
                ["Approve", "Reject", "Need More Information"],
                index=["Approve","Reject","Need More Information"].index(current_decision) if current_decision else 0,
                key=f"{t['ticket_id']}_{dept_name}"
            )

            # Comment
            comment = st.text_area(
                "Comment:",
                value=current_comment,
                key=f"{t['ticket_id']}_{dept_name}_comment"
            )


            if st.button("Submit", key=f"submit_{t['ticket_id']}_{dept_name}"):
                # Update department_reviews
                t["department_reviews"][dept_name]["decision"] = decision
                t["department_reviews"][dept_name]["comment"] = comment


                # Add history event
                add_ticket_event(
                    t,
                    action=f"{dept_name} review submitted",
                    actor=actor,
                    details={
                        "department": dept_name,
                        "decision": decision,
                        "comment": comment
                    }
                )

                set_all_tickets(tickets)
                st.success("✅ Decision & comment saved and history updated.")
