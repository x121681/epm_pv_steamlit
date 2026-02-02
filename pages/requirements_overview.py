import streamlit as st
from state.requirements import get_all_requirements, load_all_requirements

st.title("📋 Requirements Overview")

# Load persisted data
load_all_requirements()

requirements = get_all_requirements()

if not requirements:
    st.info("No requirements have been added yet.")
    st.stop()

for r in requirements:
    header = f"{r.get('id')} – {r.get('title','')}"
    with st.expander(header):
        st.write(f"**Type:** {r.get('type','')}")
        st.write(f"**Section:** {r.get('section','')}")
        st.write(f"**Current Status:** {r.get('status','')}")
        st.write("---")

        history = r.get("history", [])
        if not history:
            st.info("No history yet.")
            continue

        for h in history:
            details = h.get("details", {})
            from_s = details.get("from", "—")
            to_s = details.get("to", "—")

            entry_header = (
                f"{h.get('timestamp')} | "
                f"{h.get('actor')} | "
                f"{from_s} → {to_s}"
            )

            with st.expander(entry_header):
                st.write("**Action:**", h.get("action"))
                st.write("**Comment:**")
                st.write(details.get("comment", "—"))
