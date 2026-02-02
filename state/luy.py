import streamlit as st
import csv
import os
from datetime import datetime

# =====================================================
# Project Paths
# =====================================================
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
COMPONENTS_PATH = os.path.join(PROJECT_ROOT, "components", "domain_cap_map.csv")

# =====================================================
# Fixed LUY Products (Seed Data)
# =====================================================
FIXED_LUY_PRODUCTS = [
    {
        "id": "LUY-001",
        "name": "Adobe Photoshop",
        "vendor": "Adobe",
        "product": "Photoshop",
        "domain": "Media, Graphics & Document Processing",
        "capabilities": ["Image / Graphics Editing Tools", "Vector Graphics / Diagram Tools"],
        "active": True,
        "source": "seed",
        "blocked": True 
    },
    {
        "id": "LUY-002",
        "name": "Oracle Database",
        "vendor": "Oracle",
        "product": "Database",
        "domain": "Databases & Data Management",
        "capabilities": ["Database Clients & Admin Tools", "Data Modeling & Schema Design"],
        "active": True,
        "source": "seed",
        "blocked": True
    },
    {
        "id": "LUY-003",
        "name": "Atlassian Jira",
        "vendor": "Atlassian",
        "product": "Jira",
        "domain": "Office, Collaboration & Productivity",
        "capabilities": ["Project / Task / Workflow Collaboration Tools", "Documentation & Wiki Tools"],
        "active": True,
        "source": "seed",
        "blocked": False
    },
    {
        "id": "LUY-004",
        "name": "Bruno API Client",
        "vendor": "Bruno",
        "product": "API Lifecycle Tool",
        "domain": "API & Integration Tools",
        "capabilities": ["API Design & Modeling", "API Testing & Validation"],
        "active": True,
        "source": "seed",
        "blocked": False
    },
    {
        "id": "LUY-005",
        "name": "Jenkins CI/CD",
        "vendor": "CloudBees",
        "product": "Jenkins",
        "domain": "Build & CI/CD",
        "capabilities": ["Continuous Integration / Continuous Delivery", "Deployment Automation & Configuration"],
        "active": True,
        "source": "seed",
        "blocked": False
    },
    {
        "id": "LUY-006",
        "name": "Internal Data Manager",
        "vendor": "Internal",
        "product": "Custom Internal Tool",
        "domain": "Custom / Internal Applications",
        "capabilities": ["Internal Business Applications", "Automation / Integration Scripts"],
        "active": True,
        "source": "seed",
        "blocked": True
    }
]

# =====================================================
# LUY → PV mapping
# =====================================================
LUY_PV_MAP = {
    "LUY-001": ["john.doe"],
    "LUY-002": ["alice.admin"],
    "LUY-003": ["bob.epm", "max.mustermann"],
    "LUY-004": ["alice.admin", "max.mustermann"],
}

# =====================================================
# Initialization
# =====================================================
def init_luy_state():
    if "luy_entries" not in st.session_state:
        # Seed once, never overwrite again
        st.session_state.luy_entries = FIXED_LUY_PRODUCTS.copy()

    if "luy_discussions" not in st.session_state:
        st.session_state.luy_discussions = {}

    if "luy_vendors" not in st.session_state:
        st.session_state.luy_vendors = [
            "Adobe", "Oracle", "JetBrains", "Atlassian", "SAP", "MongoDB", "VMware"
        ]

    if "luy_products" not in st.session_state:
        st.session_state.luy_products = [
            "Client", "Studio", "Agent", "Workbench", "Connector", "Service", "Tool"
        ]

    if "luy_domain_caps" not in st.session_state:
        st.session_state.luy_domain_caps = load_domain_capabilities()

    if "luy_current_app" not in st.session_state:
        st.session_state.luy_current_app = None

# =====================================================
# Domain / Capability CSV
# =====================================================
def load_domain_capabilities():
    domain_caps = []
    if os.path.exists(COMPONENTS_PATH):
        with open(COMPONENTS_PATH, newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f, delimiter=";")
            current_domain = None
            for row in reader:
                name = row.get("Name", "").strip()
                if name.startswith("Domain –"):
                    current_domain = name.replace("Domain –", "").strip()
                elif name.startswith("Capability –") and current_domain:
                    capability = name.replace("Capability –", "").strip()
                    domain_caps.append({
                        "domain": current_domain,
                        "capability": capability
                    })
    return domain_caps

# =====================================================
# LUY Catalog (Source of Truth)
# =====================================================
def get_luy_entries():
    init_luy_state()
    return st.session_state.luy_entries


def get_luy_entry_by_name(name: str):
    init_luy_state()
    return next(
        (e for e in st.session_state.luy_entries if e.get("name") == name),
        None
    )


def add_luy_entry(entry: dict):
    """
    Add a LUY entry (manual or automatic).
    Prevents duplicate IDs.
    """
    init_luy_state()

    entry_id = entry.get("id")
    if not entry_id:
        raise ValueError("LUY entry must contain an 'id'")

    existing_ids = {e["id"] for e in st.session_state.luy_entries}
    if entry_id in existing_ids:
        return entry  # already exists

    entry.setdefault("active", True)
    entry.setdefault("created_at", datetime.utcnow().isoformat())
    entry.setdefault("source", "manual")

    st.session_state.luy_entries.append(entry)
    return entry


def get_pv_for_product(luy_id: str):
    init_luy_state()
    return LUY_PV_MAP.get(luy_id, [])

# =====================================================
# Vendors / Products
# =====================================================
def get_vendors():
    init_luy_state()
    return st.session_state.luy_vendors


def get_products():
    init_luy_state()
    return st.session_state.luy_products

# =====================================================
# Current App Helpers
# =====================================================
def get_current_luy_app():
    init_luy_state()
    if st.session_state.luy_current_app is None:
        st.session_state.luy_current_app = st.session_state.luy_entries[0]["name"]
    return st.session_state.luy_current_app


def set_current_luy_app(app_name: str):
    init_luy_state()
    st.session_state.luy_current_app = app_name

# =====================================================
# Discussions / Comments
# =====================================================
def add_luy_discussion(luy_id: str, comment: str):
    init_luy_state()
    if not comment:
        return
    st.session_state.luy_discussions.setdefault(luy_id, [])
    st.session_state.luy_discussions[luy_id].append(comment)


def get_luy_discussions(luy_id: str):
    init_luy_state()
    return st.session_state.luy_discussions.get(luy_id, [])
