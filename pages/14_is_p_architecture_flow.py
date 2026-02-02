import streamlit as st
from datetime import datetime

from state.tickets import get_all_tickets, set_all_tickets
from state.luy import get_luy_entries, init_luy_state, LUY_PV_MAP
from components.luy_engine import LuyEngine
from components.ticket_history import add_ticket_event
from components.pv_rules_engine import PVEngine
from components.requirements import show_requirements

# -------------------------
# Page config and state
# -------------------------
st.session_state["device_current_page"] = "14_is_p_architecture_flow"
st.set_page_config(page_title="IS-P Arch Flow & Domain Review", page_icon="🧭")
st.title("🧭 IS-P Architecture Flow & Domain Capability Review")
st.caption("In case if we want to use EAM-tools (e.g. LUY, confluence) to send the feedback directly to Service manager" \
           "Shop article process, this page shows a prototype for it. Also by categorizing the software into domain and capability" \
           "we plan to manage the PV responsibilities more effectively.")

# -------------------------
# User guard
# -------------------------
user = st.session_state.get("user")
if not user:
    st.warning("Please login first.")
    st.stop()

username = user.get("username", "Unknown")
user_department = user.get("department", "IS-P")

# -------------------------
# Engines and data
# -------------------------
engine = LuyEngine("components/domain_cap_map.csv")
pv_engine = PVEngine()

tickets = get_all_tickets()
init_luy_state()

# -------------------------
# Filter IS-P tickets
# -------------------------
isp_tickets = []
for t in tickets:
    t.setdefault("department_reviews", {})
    if t.get("approval_required") and "IS-P" in t["department_reviews"]:
        isp_tickets.append(t)

if not isp_tickets:
    st.info("No IS-P tickets available.")
    st.stop()

# -------------------------
# Constants
# -------------------------
DECISIONS = ["Approve", "Reject", "Need More Information"]

# -------------------------
# Process tickets
# -------------------------
for t in isp_tickets:
    with st.expander(f"{t['application']} – {t['ticket_id']}", expanded=False):

        st.markdown("### 📄 Ticket Details")
        st.write(f"**Vendor:** {t.get('vendor', 'N/A')}")
        st.write(f"**Reason:** {t.get('reason', '')}")
        st.write(f"**Infrastructure:** {t.get('infrastructure', 'N/A')}")

        # ================= IS-P REVIEW =================
        st.markdown("### 🏗 IS-P Architecture Review")

        review = t["department_reviews"].setdefault("IS-P", {})
        review.setdefault("decision", "Approve")
        review.setdefault("comment", "")

        decision_value = review.get("decision")
        if decision_value not in DECISIONS:
            decision_value = "Approve"

        decision = st.radio(
            "Decision",
            DECISIONS,
            index=DECISIONS.index(decision_value),
            key=f"{t['ticket_id']}_isp_decision"
        )

        comment = st.text_area(
            "Architecture Comment",
            value=review.get("comment", ""),
            key=f"{t['ticket_id']}_isp_comment"
        )

        # ================= DOMAIN & CAPABILITY =================
        st.markdown("### 🧭 Domain & Capability Suggestions")

        if not t.get("domain_suggestions") or not t.get("capability_suggestions"):
            result = engine.classify_software(
                software_name=t.get("application", ""),
                description=t.get("reason", ""),
                use_case=t.get("use_case", "")
            )
            t["domain_suggestions"] = result.get("domains", [])
            t["capability_suggestions"] = result.get("capabilities", [])

        domains = [d for d, _ in t["domain_suggestions"]] or ["Other / New Domain"]
        caps = [c for c, _ in t["capability_suggestions"]]

        st.markdown("#### 🏛 Domains")
        for d, s in t["domain_suggestions"]:
            st.write(f"- **{d}** (score: {s})")

        final_domain = st.selectbox(
            "Final Domain",
            domains,
            index=0,
            key=f"{t['ticket_id']}_domain"
        )

        st.markdown("#### ⚙ Capabilities")
        for c, s in t["capability_suggestions"]:
            st.write(f"- **{c}** (score: {s})")

        final_caps = st.multiselect(
            "Final Capabilities",
            caps,
            default=t.get("final_capabilities", []),
            key=f"{t['ticket_id']}_caps"
        )

        # ================= SAVE =================
        if st.button("✅ Save IS-P Review & Classification", key=f"save_{t['ticket_id']}"):

            review["decision"] = decision
            review["comment"] = comment
            review["domain"] = final_domain
            review["capabilities"] = final_caps

            review.setdefault("history", []).append({
                "timestamp": datetime.now().isoformat(),
                "actor": username,
                "decision": decision,
                "comment": comment,
                "domain": final_domain,
                "capabilities": final_caps
            })

            t["final_domain"] = final_domain
            t["final_capabilities"] = final_caps
            t["classification_status"] = "Approved"

            add_ticket_event(
                t,
                action="IS-P Review Completed",
                actor=username,
                details={
                    "decision": decision,
                    "comment": comment,
                    "domain": final_domain,
                    "capabilities": final_caps
                }
            )

            # ================= PV CHECK =================
            st.markdown("### 🛠 PV Assignment Check")

            pv_missing = False

            for cap in final_caps:
                matching_pvs = []
                for entry in get_luy_entries():
                    if entry.get("domain") == final_domain and cap in entry.get("capabilities", []):
                        matching_pvs.extend(LUY_PV_MAP.get(entry["id"], []))

                if matching_pvs:
                    st.markdown(f"**Existing PVs for {final_domain} → {cap}:**")
                    for pv in set(matching_pvs):
                        st.write(f"- {pv}")
                else:
                    pv_missing = True

            if pv_missing:
                t["status"] = "PV_CONTEXT_REQUIRED"

                add_ticket_event(
                    t,
                    action="PV Context Required",
                    actor="system",
                    details={
                        "domain": final_domain,
                        "capabilities": final_caps
                    }
                )

                st.session_state["pv_forward_ticket"] = {
                    "ticket_id": t["ticket_id"],
                    "application": t["application"],
                    "domain": final_domain,
                    "capabilities": final_caps,
                    "product_type": t.get("product_type", "Eigenentwicklung"),
                    "level": t.get("pv_level", "L2"),
                    "scenario": t.get("pv_scenario", "Neueinführung")
                }

                st.warning("No PV assigned yet. User must provide PV context.")
            else:
                st.success("PV coverage found.")

            set_all_tickets(tickets)
            st.success("IS-P review saved successfully.")

# -----------------------------
# Notes / Todos
# -----------------------------
show_requirements(
    "Arch Flow Tools",
    items=[
        {
            "id": "Tools",
            "text": "We have to decide which kind of tools we are going to use LUY / Confluence , both etc",
        }
    ],
    req_type="todo"
)