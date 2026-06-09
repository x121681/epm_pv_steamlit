import streamlit as st
from state.requirements import get_requirements_grouped_by_status, get_requirement_status_distribution, load_all_requirements

st.title("📋 Requirements Overview")

load_all_requirements()
requirements_by_status = get_requirements_grouped_by_status()
status_distribution = get_requirement_status_distribution()

if not status_distribution:
    st.info("No requirements have been added yet.")
    st.stop()

st.subheader("Requirement Status Distribution")
status_cols = st.columns(len(status_distribution))
for col, status in zip(status_cols, status_distribution):
    col.metric(status, status_distribution[status])

st.bar_chart(status_distribution)

selected_status = st.selectbox(
    "Show requirements for status:",
    options=["All"] + list(requirements_by_status.keys())
)

visible_statuses = (
    list(requirements_by_status.keys())
    if selected_status == "All"
    else [selected_status]
)

for status in visible_statuses:
    requirements = sorted(
        requirements_by_status.get(status, []),
        key=lambda r: (
            str(r.get("section", "")),
            str(r.get("title", "")),
            str(r.get("id", ""))
        )
    )
    if not requirements:
        continue

    st.markdown(f"## {status} — {len(requirements)}")

    for req in requirements:
        header = f"{req.get('title', 'Untitled Requirement')} — {req.get('id', '')}"
        with st.expander(header):
            left, right = st.columns([3, 2])
            with left:
                st.write(f"**Section:** {req.get('section', '')}")
                st.write(f"**Type:** {req.get('type', '')}")
                st.write(f"**Owner:** {req.get('actor', '')}")
            with right:
                st.write(f"**Status:** {req.get('status', '')}")
                st.write(f"**Events:** {len(req.get('history', []))}")

            st.write("---")
            history = sorted(req.get("history", []), key=lambda h: h.get("timestamp", ""), reverse=True)
            if not history:
                st.info("No history yet.")
                continue

            for h in history:
                details = h.get("details", {})
                from_s = details.get("from", "—")
                to_s = details.get("to", "—")
                entry_header = f"{h.get('timestamp')} | {h.get('actor')} | {from_s} → {to_s}"
                with st.expander(entry_header):
                    st.write("**Action:**", h.get("action"))
                    st.write("**Comment:**")
                    st.write(details.get("comment", "—"))
