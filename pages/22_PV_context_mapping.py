import streamlit as st
from components.pv_rules_engine import PVEngine
from datetime import datetime

st.set_page_config(
    page_title="PV Context Mapping",
    page_icon="🧩",
    layout="wide"
)

st.title("🧩 PV Context & Obligation Mapping")
st.caption(
    "This page determines whether a Product Responsible (PV) is required. "
    "If required, PV obligations are derived automatically."
)

# =========================================================
# GUARD: TICKET MUST EXIST
# =========================================================
if "latest_ticket" not in st.session_state or st.session_state.latest_ticket is None:
    st.error("No ticket available. Please access this page via a ticket.")
    st.stop()

ticket = st.session_state.latest_ticket

# =========================================================
# A. PRODUCT / SOFTWARE FACTS (AUTO-FILLED)
# =========================================================
st.header("A. Product / Software Facts")
st.caption("Pre-filled from Architecture & LUY. Read-only.")

col1, col2, col3 = st.columns(3)

with col1:
    application = st.text_input(
        "Application name",
        ticket.get("application", ""),
        disabled=True
    )
    vendor = st.text_input(
        "Vendor",
        ticket.get("vendor", "Unknown"),
        disabled=True
    )
    product_type = st.selectbox(
        "Product type",
        ["Fremdsoftware", "Eigenentwicklung", "Hardware"],
        index=["Fremdsoftware", "Eigenentwicklung", "Hardware"]
        .index(ticket.get("product_type", "Fremdsoftware")),
        disabled=True
    )

with col2:
    domain = st.text_input(
        "Domain",
        ticket.get("domain", ""),
        disabled=True
    )
    capabilities = st.multiselect(
        "Capabilities",
        ticket.get("capabilities", []),
        default=ticket.get("capabilities", []),
        disabled=True
    )
    license_type = st.selectbox(
        "License type",
        ["Commercial", "Open Source", "Internal"]
    )

with col3:
    deployment = st.selectbox(
        "Deployment type",
        ["SaaS", "On-Prem", "Hybrid"]
    )
    business_criticality = st.selectbox(
        "Business criticality",
        ["Low", "Medium", "High", "Mission Critical"]
    )
    urgency = st.selectbox(
        "Urgency",
        ["Niedrig", "Mittel", "Hoch", "Kritisch"],
        index=["Niedrig", "Mittel", "Hoch", "Kritisch"]
        .index(ticket.get("urgency", "Mittel"))
    )
    tool_type = st.selectbox(
        "Tool type",
        [
            "Enterprise application",
            "SaaS application",
            "Desktop application",
            "Developer tool / IDE extension",
            "System utility / runtime",
            "Script / automation",
        ]
    )

# =========================================================
# B. RISK & COMPLIANCE INDICATORS
# =========================================================
st.header("B. Risk & Compliance Indicators")

col1, col2, col3 = st.columns(3)

with col1:
    personal_data = st.checkbox("Processes personal data")
    authentication = st.checkbox("Authenticates users")

with col2:
    internet_exposed = st.checkbox("Internet exposed")
    regulatory_relevant = st.checkbox("Regulatory relevant")

with col3:
    availability = st.selectbox(
        "Availability requirement",
        ["Best effort", "Business hours", "24/7"]
    )
    data_classification = st.selectbox(
        "Data classification",
        ["Public", "Internal", "Confidential", "Restricted"]
    )

# =========================================================
# PV ELIGIBILITY DECISION
# =========================================================
st.divider()
st.header("PV Eligibility Decision")

def decide_pv_required(
    product_type,
    tool_type,
    business_criticality,
    personal_data,
    regulatory_relevant,
    internet_exposed,
    deployment,
):
    reasons = []

    # -------------------------------------------------
    # 1. Tool type baseline
    # -------------------------------------------------
    if tool_type in ["Enterprise application", "SaaS application", "Desktop application"]:
        reasons.append(f"Tool type: {tool_type}")

    elif tool_type in ["Developer tool / IDE extension", "System utility / runtime"]:
        if personal_data or regulatory_relevant:
            reasons.append(f"Regulated use of {tool_type}")

    elif tool_type == "Script / automation":
        if business_criticality in ["High", "Mission Critical"]:
            reasons.append("High business critical automation")

    # -------------------------------------------------
    # 2. Risk-based escalation
    # -------------------------------------------------
    if business_criticality in ["High", "Mission Critical"]:
        reasons.append("High business criticality")

    if personal_data:
        reasons.append("Processes personal data")

    if regulatory_relevant:
        reasons.append("Regulatory relevance")

    if internet_exposed:
        reasons.append("Internet exposed")

    if deployment == "SaaS":
        reasons.append("Externally operated (SaaS)")

    # -------------------------------------------------
    # 3. Internal low-risk shortcut
    # -------------------------------------------------
    if product_type == "Eigenentwicklung" and tool_type == "Script / automation" and not reasons:
        return False, ["Low-risk internal script"]

    return len(reasons) > 0, reasons

pv_required, pv_reasons = decide_pv_required(
    product_type=product_type,
    tool_type=tool_type,
    business_criticality=business_criticality,
    personal_data=personal_data,
    regulatory_relevant=regulatory_relevant,
    internet_exposed=internet_exposed,
    deployment=deployment,
)

ticket["pv_eligibility"] = {
    "pv_required": pv_required,
    "reasons": pv_reasons,
    "decided_at": datetime.now().isoformat(),
    "decided_by": "PV_ELIGIBILITY_ENGINE",
}

if pv_required:
    st.warning("🟡 Product Responsible (PV) is REQUIRED")
    st.markdown("**Reason(s):**")
    for r in pv_reasons:
        st.markdown(f"- {r}")
else:
    st.success("🟢 No Product Responsible (PV) required")
    st.caption("No further PV responsibilities are necessary.")
    ticket["status"] = "PV_NOT_REQUIRED"
    st.json(ticket["pv_eligibility"])
    st.stop()

# =========================================================
# C. OPERATIONAL CHARACTERISTICS (ONLY IF PV REQUIRED)
# =========================================================
st.header("C. Operational Characteristics")

col1, col2, col3 = st.columns(3)

with col1:
    user_count = st.selectbox(
        "Number of users",
        ["<50", "50–500", "500–5000", ">5000"]
    )
    support_model = st.selectbox(
        "Support model",
        ["None", "Best effort", "Defined SLA"]
    )

with col2:
    change_frequency = st.selectbox(
        "Change frequency",
        ["Rare", "Occasional", "Frequent"]
    )
    release_frequency = st.selectbox(
        "Release frequency",
        ["Ad-hoc", "Planned", "Continuous"]
    )

with col3:
    integrations = st.selectbox(
        "Integration criticality",
        ["None", "Low", "High"]
    )
    customization = st.selectbox(
        "Customization level",
        ["Standard", "Configured", "Highly customized"]
    )

# =========================================================
# LEVEL INFERENCE (L0–L4) CAPPED BY TOOL TYPE
# =========================================================
level_order = ["L0", "L1", "L2", "L3", "L4"]

base_level_map = {
    "Low": "L1",
    "Medium": "L2",
    "High": "L3",
    "Mission Critical": "L4",
}

level = base_level_map.get(business_criticality, "L2")
idx = level_order.index(level)

def bump(idx, steps=1):
    return min(idx + steps, len(level_order) - 1)

if user_count == "500–5000":
    idx = bump(idx, 1)
elif user_count == ">5000":
    idx = bump(idx, 2)

if deployment == "SaaS":
    idx = bump(idx, 1)

if regulatory_relevant:
    idx = bump(idx, 1)

if personal_data:
    idx = bump(idx, 1)

if internet_exposed:
    idx = bump(idx, 1)

level = level_order[idx]

# Cap level by tool type
TOOL_TYPE_MAX_LEVEL = {
    "Script / automation": "L1",
    "Developer tool / IDE extension": "L2",
    "System utility / runtime": "L2",
    "Desktop application": "L3",
    "Enterprise application": "L4",
    "SaaS application": "L4",
}
max_level = TOOL_TYPE_MAX_LEVEL.get(tool_type, "L4")
if level_order.index(level) > level_order.index(max_level):
    level = max_level

# =========================================================
# SCENARIO INFERENCE
# =========================================================
scenario = "Neueinführung"

if change_frequency == "Frequent":
    scenario = "Maintenance"
elif release_frequency in ["Planned", "Continuous"]:
    scenario = "Release Upgrade"
elif regulatory_relevant or personal_data:
    scenario = "Security relevant"

# =========================================================
# D. DERIVED PV OBLIGATIONS
# =========================================================
st.header("D. Derived Obligations (Calculated)")

pv_engine = PVEngine()
derived_tasks = pv_engine.get_pv_responsibilities(
    product_type=product_type,
    scenario=scenario,
    level=level
)

grouped_tasks = pv_engine.group_by_process(derived_tasks)

for process, tasks in grouped_tasks.items():
    st.subheader(process)
    for t in tasks:
        st.markdown(
            f"- **{t['pv']}**: {t['aufgabe']} "
            f"(Frequency: {t['häufigkeit']})"
        )

# =========================================================
# SAVE RESULT
# =========================================================
st.divider()
st.header("E. Persist Derived PV Obligations")

if st.button("💾 Save PV decision & obligations"):
    ticket["derived_obligations"] = {
        "pv_required": True,
        "eligibility_reasons": pv_reasons,
        "level": level,
        "scenario": scenario,
        "responsibilities": derived_tasks,
        "processes": sorted({t["prozess"] for t in derived_tasks}),
        "pv_roles": sorted({t["pv"] for t in derived_tasks}),
        "calculated_at": datetime.now().isoformat(),
        "calculated_by": "PV_CONTEXT_MAPPING",
    }

    ticket["status"] = "PV_RESP_FINALIZATION"

    st.success("PV obligations saved successfully.")
    st.json(ticket["derived_obligations"])


