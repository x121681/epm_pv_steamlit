import os
import json
from datetime import datetime
import streamlit as st

STORE_DIR = "requirement_store"

# -----------------------------
# Init
# -----------------------------
def init_requirement_store():
    os.makedirs(STORE_DIR, exist_ok=True)
    if "requirements" not in st.session_state:
        st.session_state.requirements = {}

# -----------------------------
# Load ALL requirements
# -----------------------------
def load_all_requirements():
    init_requirement_store()

    for fname in os.listdir(STORE_DIR):
        if not fname.endswith(".json"):
            continue

        path = os.path.join(STORE_DIR, fname)
        try:
            with open(path, encoding="utf-8") as f:
                req = json.load(f)
                req_id = req["id"]

                if req_id not in st.session_state.requirements:
                    st.session_state.requirements[req_id] = req
        except Exception as e:
            print(f"Error loading {fname}: {e}")

# -----------------------------
# Save
# -----------------------------
def save_requirement(req):
    path = os.path.join(STORE_DIR, f"{req['id']}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(req, f, indent=2, ensure_ascii=False)

# -----------------------------
# History
# -----------------------------
def add_requirement_event(req_id, action, actor, details=None):
    req = st.session_state.requirements.get(req_id)
    if not req:
        return

    req["history"].append({
        "timestamp": datetime.now().isoformat(),
        "action": action,
        "actor": actor,
        "details": details or {}
    })

    save_requirement(req)

# -----------------------------
# Query
# -----------------------------
def get_all_requirements():
    init_requirement_store()
    return list(st.session_state.requirements.values())

# -----------------------------
# Status helpers
# -----------------------------

STATUS_ORDER = [
    "Proposed",
    "In Progress",
    "Todo",
    "Completed",
    "Reviewed",
    "Rejected",
    "Not Relevant"
]


def get_requirements_grouped_by_status():
    load_all_requirements()
    grouped = {status: [] for status in STATUS_ORDER}
    grouped["Other"] = []

    for req in get_all_requirements():
        status = req.get("status", "Unknown")
        if status in grouped:
            grouped[status].append(req)
        else:
            grouped["Other"].append(req)

    if not grouped["Other"]:
        grouped.pop("Other")

    return grouped


def get_requirement_status_distribution():
    grouped = get_requirements_grouped_by_status()
    return {status: len(items) for status, items in grouped.items()}
