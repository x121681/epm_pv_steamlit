import streamlit as st
from state.requirements import add_requirement_event, save_requirement

# -----------------------------
# Configuration
# -----------------------------
DEFAULT_STATUS = "Proposed"
LIFECYCLE_STATES = ["Proposed", "In Progress", "Completed", "Reviewed"]

# -----------------------------
# Ensure requirement exists
# -----------------------------

def ensure_requirement(req_id, title, section, req_type, actor):
    if "requirements" not in st.session_state:
        st.session_state.requirements = {}

    if req_id not in st.session_state.requirements:
        req = {
            "id": req_id,
            "title": title,
            "section": section,
            "type": req_type,
            "status": DEFAULT_STATUS,
            "actor": actor,
            "history": []
        }

        st.session_state.requirements[req_id] = req
        save_requirement(req)   # 🔥 persist immediately

# -----------------------------
# Main UI
# -----------------------------
def show_requirements(section_title, items, req_type="question", expanded=False):
    icons = {"question": "❓", "todo": "🛠️", "note": "📝"}
    captions = {
        "question": "These are unresolved details needed to complete the process logic.",
        "todo": "Pending tasks or missing implementation blocks.",
        "note": "Notices and remarks regarding the process."
    }

    page_name = st.session_state.get("device_current_page", "unknown_page")
    actor = (st.session_state.get("user") or {}).get("username", "Unknown")

    with st.expander(
        f"{icons.get(req_type,'❔')} {req_type.title()} – {section_title}",
        expanded=expanded
    ):
        st.caption(captions.get(req_type, ""))

        for idx, item in enumerate(items):
            req_id = f"{page_name}_{section_title.replace(' ','_')}_{req_type}_{idx+1}"

            ensure_requirement(
                req_id=req_id,
                title=item,
                section=section_title,
                req_type=req_type,
                actor=actor
            )

            req = st.session_state.requirements[req_id]

            # Initialize last-known status ONCE
            last_status_key = f"{req_id}_last_status"
            if last_status_key not in st.session_state:
                st.session_state[last_status_key] = req["status"]

            col1, col2 = st.columns([5, 2])

            with col1:
                st.info(f"{item} (ID: {req_id})")

            with col2:
                status = st.selectbox(
                    "Status",
                    options=LIFECYCLE_STATES,
                    index=LIFECYCLE_STATES.index(st.session_state[last_status_key]),
                    key=f"{req_id}_status"
                )

            # Status changed → require comment
            if status != req["status"]:
                comment_key = f"{req_id}_comment"

                comment = st.text_area(
                    "Comment (required)",
                    key=comment_key,
                    placeholder="Explain why this status change is needed..."
                )

                if st.button("Save status change", key=f"{req_id}_save"):
                    if not comment.strip():
                        st.warning("Comment is required to change status.")
                    else:
                        old_status = req["status"]

                        req["status"] = status
                        req["actor"] = actor

                        add_requirement_event(
                            req_id=req_id,
                            action="Status updated",
                            actor=actor,
                            details={
                                "from": old_status,
                                "to": status,
                                "comment": comment.strip()
                            }
                        )

                        save_requirement(req)

                        st.session_state[last_status_key] = status
                        st.session_state.pop(comment_key, None)

                        st.success("Status updated successfully.")
