# Session State Management

## Overview
This document describes how application state is initialized, stored, and managed across Streamlit sessions. State includes user authentication, tickets, LUY software catalog, EPM lists, requirements tracking, and domain/capability mappings.

---

## 👤 **User & Authentication State**

### Location
[`state/user.py`](../state/user.py) & [`state/core.py`](../state/core.py)

### Initialization
```python
from state.core import init_app_state
init_app_state()  # Called in home.py
```

### Session Variables
```python
st.session_state.user = {
    "username": "john.doe",
    "display_name": "John Doe",
    "role": "user",  # or "admin"
    "pv_roles": ["PV_TECHNISCH", "PV_FACHLICH"],  # if applicable
    "department": "IS-P",  # if applicable
    "active": True
}

st.session_state.is_admin = True  # Shortcut for role checks
```

### Login Pages
- **Device/User Login:** [`pages/19_user_device_login.py`](../pages/19_user_device_login.py)
- **EPM Admin Login:** [`pages/20_epm_login.py`](../pages/20_epm_login.py)

---

## 🎫 **Ticket Management**

### Location
[`state/tickets.py`](../state/tickets.py)

### Initialization
```python
from state.tickets import init_tickets, create_ticket, get_all_tickets

init_tickets()  # Creates empty `st.session_state.tickets` list
```

### Ticket Lifecycle Statuses
```python
TICKET_STATUSES = [
    "DRAFT",                          # Initial state
    "ARCH_REVIEW_IN_PROGRESS",        # (Legacy, may be replaced)
    "DOMAIN_CAPABILITY_FINALIZED",    # After IS-P classification
    "PV_CONTEXT_REQUIRED",            # If PV roles missing
    "PV_RESP_FINALIZATION",           # Derived obligations shown
    "PV_ASSIGNED",                    # Waiting for final approval
    "APPROVED",                       # Final approval granted
    "REJECTED",                       # Rejected by any stakeholder
]
```

### Ticket Structure
```json
{
  "ticket_id": "TICKET-A1B2C3D4",
  "source": "IT Service Direkt",
  "application": "Visual Studio Code",
  "vendor": "Microsoft",
  "reason": "Development IDE required",
  
  "status": "DRAFT",
  "journey": "it_service_direkt",
  "created_by": "john.doe",
  "date": "2025-12-23T10:30:00",
  
  "urgency": "Medium",
  "license_type": "Open Source",
  "infrastructure": null,
  
  "shop_artikel_decision": "Greylist",
  
  "final_domain": "Development Tools",
  "final_capabilities": ["Code Editing / IDE", "Debugging Tools"],
  "product_type": "Fremdsoftware",
  
  "department_reviews": {
    "IS-P": {
      "decision": "Approve",
      "comment": "Architecture approved",
      "timestamp": "2025-12-23T11:00:00",
      "actor": "architect.1",
      "domain": "Development Tools",
      "capabilities": ["Code Editing / IDE"]
    },
    "CSO-I": {
      "decision": "Approve",
      "comment": "Security check passed"
    },
    "IS-G": {
      "decision": "Need More Information",
      "comment": "Compliance clarification needed"
    },
    "IS-V": {
      "decision": "Approve",
      "comment": "License budget available"
    }
  },
  
  "departments_informed": ["IS-P", "CSO-I", "IS-G", "IS-V"],
  "approval_required": true,
  "approval_status": "APPROVED",
  
  "pv_context": {
    "deployment": "SaaS",
    "business_criticality": "High",
    "urgency": "Medium",
    "data_classification": "Internal",
    
    "personal_data": false,
    "internet_exposed": true,
    "authentication": true,
    "regulatory_relevant": false,
    
    "user_count": "500–5000",
    "support_model": "Defined SLA",
    "change_frequency": "Occasional",
    "release_frequency": "Planned",
    "integrations": "High",
    "customization": "Standard",
    
    "derived": {
      "min_level": "L2",
      "required_roles": ["PV_TECHNISCH"],
      "required_processes": ["Produktmanagement", "Change Management"]
    }
  },
  
  "derived_obligations": {
    "level": "L2",
    "scenario": "Neueinführung",
    "responsibilities": [
      {
        "pv": "PV_TECHNISCH",
        "aufgabe": "Dokumentiert den Betrieb des IT-Produkts",
        "häufigkeit": "bei Bedarf",
        "prozess": "Produktmanagement"
      }
    ],
    "responsibilities_by_process": {
      "Produktmanagement": [...],
      "Change Management": [...]
    },
    "calculated_at": "2025-12-23T12:00:00",
    "calculated_by": "PV_CONTEXT_MAPPING"
  },
  
  "pv_acceptance": {
    "decision": "ACCEPTED",
    "reason": "We can cover these responsibilities",
    "decided_by": "pv_manager",
    "decided_at": "2025-12-23T13:00:00"
  },
  
  "history": [
    {
      "timestamp": "2025-12-23T10:30:00",
      "actor": "john.doe",
      "action": "IT Service Direkt Request Submitted",
      "details": {
        "software_name": "VS Code",
        "vendor": "Microsoft",
        "urgency": "Medium"
      },
      "new_status": "DRAFT"
    },
    {
      "timestamp": "2025-12-23T11:00:00",
      "actor": "architect.1",
      "action": "IS-P Review Completed",
      "details": {
        "decision": "Approve",
        "domain": "Development Tools",
        "capabilities": ["Code Editing / IDE"]
      },
      "new_status": "DOMAIN_CAPABILITY_FINALIZED"
    }
  ]
}
```

### Ticket CRUD Functions
```python
from state.tickets import (
    create_ticket,           # Create new ticket
    get_latest_ticket,       # Get currently active ticket
    get_all_tickets,         # Get all tickets
    set_all_tickets,         # Persist ticket list
    find_ticket,             # Find by ID
    add_ticket_event         # Log event to history
)

# Example: Create ticket
ticket = create_ticket(
    source="IT Service Direkt",
    application="VS Code",
    reason="Development IDE",
    status="DRAFT",
    journey="it_service_direkt",
    created_by="john.doe"
)

# Example: Add event
from components.ticket_history import add_ticket_event
add_ticket_event(
    ticket=ticket,
    action="Shop Artikel Decision Made",
    actor="admin.user",
    details={"decision": "Greylist", "reason": "Needs review"},
    new_status="DOMAIN_CAPABILITY_FINALIZED"
)
```

### Ticket Event History
**Location:** [`components/ticket_history.py`](../components/ticket_history.py)

```python
# Event structure (added to ticket.history)
{
  "timestamp": "2025-12-23T10:30:00",
  "actor": "john.doe",
  "action": "Action description",
  "details": {
    "field1": "value1",
    "decision": "Approve",
    "domain": "Development Tools",
    "capabilities": ["Code Editing / IDE"]
  },
  "new_status": "DOMAIN_CAPABILITY_FINALIZED"
}
```

---

## 📦 **LUY (Software Repository) State**

### Location
[`state/luy.py`](../state/luy.py)

### Initialization
```python
from state.luy import init_luy_state, get_luy_entries

init_luy_state()  # Loads fixed + runtime entries
entries = get_luy_entries()
```

### Fixed LUY Products

| ID | Name | Vendor | Domain | Capabilities |
|----|------|--------|--------|--------------|
| LUY-001 | Adobe Photoshop | Adobe | Media, Graphics & Document Processing | Image / Graphics Editing Tools |
| LUY-002 | Oracle Database | Oracle | Databases & Data Management | Database Clients & Admin Tools |
| LUY-003 | Atlassian Jira | Atlassian | Office, Collaboration & Productivity | Project / Task / Workflow Collaboration Tools |
| LUY-004 | Bruno API Client | Bruno | API & Integration Tools | API Design & Modeling, API Testing & Validation |
| LUY-005 | Jenkins CI/CD | CloudBees | Build & CI/CD | Continuous Integration / Continuous Delivery |
| LUY-006 | Internal Data Manager | Internal | Data Management | Internal Data & Metadata Management Tools |

### LUY Entry Structure
```python
{
    "id": "LUY-001",
    "name": "Adobe Photoshop",
    "vendor": "Adobe",
    "product": "Photoshop",
    "domain": "Media, Graphics & Document Processing",
    "capabilities": ["Image / Graphics Editing Tools", "Vector Graphics / Diagram Tools"],
    "active": True,
    "source": "seed"  # "seed" or "runtime"
}
```

### Session Variables
```python
st.session_state.luy_entries          # List of all entries
st.session_state.luy_current_app      # Currently selected app name
st.session_state.luy_discussions      # Dict of discussions by LUY ID
st.session_state.luy_pv_map           # Mapping of LUY IDs to PV roles
```

### Key Functions
```python
from state.luy import (
    get_luy_entries,        # Get all entries
    get_current_luy_app,    # Get selected app
    set_current_luy_app,    # Set selected app
    add_luy_entry,          # Add runtime entry
    add_luy_discussion,      # Add discussion comment
    get_luy_discussions      # Get comments by ID
)
```

---

## 🌍 **Domain & Capability Classification**

### Location
[`components/domain_cap_map.csv`](../components/domain_cap_map.csv)

### Available Domains (15+)
- API & Integration Tools
- Build & CI/CD
- Databases & Data Management
- Development Tools & IDEs
- Endpoint & Application Security Tools
- File Management & System Utilities
- Infrastructure & Hosting
- Media, Graphics & Document Processing
- Monitoring & Observability
- Networking & Connectivity
- Office, Collaboration & Productivity
- Security & Compliance Tools
- System Utilities & OS Tools
- Testing & Quality Assurance
- Version Control & Documentation

### Classification Engine
**Location:** [`components/luy_engine.py`](../components/luy_engine.py)

```python
from components.luy_engine import LuyEngine

engine = LuyEngine("components/domain_cap_map.csv")

result = engine.classify_software(
    software_name="Visual Studio Code",
    description="Code editor for development",
    use_case="Software development"
)

# Returns:
{
    "domains": [
        ("Development Tools", 0.95),
        ("Development Tools & IDEs", 0.92)
    ],
    "capabilities": [
        ("Code Editing / IDE", 0.98),
        ("Debugging Tools", 0.85),
        ("Version Control Integration", 0.78)
    ],
    "confidence": 0.95
}
```

---

## 🛠 **PV (Product Responsibility) State**

### PV Journey Rules Engine
**Location:** [`components/pv_rules_engine.py`](../components/pv_rules_engine.py)

```python
from components.pv_rules_engine import PVEngine

pv_engine = PVEngine()

# Get PV responsibilities based on context
tasks = pv_engine.get_pv_responsibilities(
    product_type="Fremdsoftware",  # or "Eigenentwicklung", "Hardware"
    scenario="Neueinführung",       # or "Maintenance", "Release Upgrade", etc.
    level="L2"                      # L0–L4
)

# Returns list of task dicts
[
    {
        "pv": "PV_TECHNISCH",
        "aufgabe": "Dokumentiert den Betrieb des IT-Produkts",
        "häufigkeit": "bei Bedarf",
        "prozess": "Produktmanagement",
        "relevanz": ["Fremdsoftware"]
    },
    ...
]
```

### PV Journey CSV
**Location:** [`components/pv_journey.csv`](../components/pv_journey.csv)

Columns: `PV`, `Aufgabe`, `Häufigkeit`, `Prozess`, `Relevanz`, `Eigenentw. Software`, `Fremd-Software`, `Hardware`

**PV Types:**
- `PV_TECHNISCH` — Technical responsibilities
- `PV_FACHLICH` — Functional/business responsibilities

**Relevance Types:**
- `Eigenentwicklung` — Custom-built software
- `Fremdsoftware` — Commercial/third-party software
- `Hardware` — Hardware products

**Scenarios:**
- `Neueinführung` — Initial rollout
- `Maintenance` — Ongoing operations
- `Release Upgrade` — Version updates
- `Security relevant` — Security/compliance changes

**Levels:**
- `L0` — No responsibility
- `L1` — Support/consultation
- `L2` — Core responsibility
- `L3` — Extended responsibility
- `L4` — Strategic responsibility

---

## 📋 **EPM Lists State**

### Location
[`state/epm_lists.py`](../state/epm_lists.py)

### Initialization
```python
from state.epm_lists import init_epm_lists, get_epm_lists

init_epm_lists()  # Populates from LUY if empty
blacklist, whitelist, greylist = get_epm_lists()
```

### List Structure
```python
{
    "Software": "Visual Studio Code",
    "Reason": "Security approved",
    "Policy": "Whitelisted",  # or "Blacklisted"
    "EntryDate": "2025-12-23",
    "DecisionDate": "2025-12-23"
}
```

### Session Variables
```python
st.session_state.epm_blacklist  # Permanently blocked
st.session_state.epm_whitelist  # Approved for use
st.session_state.epm_greylist   # Pending review
```

### Key Functions
```python
from state.epm_lists import (
    init_epm_lists,
    get_epm_lists,
    set_epm_lists,
    find_epm_entry
)
```

---

## 📊 **Department Review State**

### Review Structure (in Ticket)

```python
ticket["department_reviews"] = {
    "IS-P": {
        "decision": "Approve",  # or "Reject", "Need More Information"
        "comment": "Architecture approved",
        "timestamp": "2025-12-23T10:30:00",
        "actor": "architect.1",
        "domain": "Development Tools",
        "capabilities": ["Code Editing / IDE"]
    },
    "CSO-I": {
        "decision": "Approve",
        "comment": "Security check passed",
        ...
    },
    "IS-G": {
        "decision": "Approve",
        "comment": "Compliance verified",
        ...
    },
    "IS-V": {
        "decision": "Approve",
        "comment": "License budget available",
        ...
    }
}

ticket["departments_informed"] = ["IS-P", "CSO-I", "IS-G", "IS-V"]
```

### Final Decision Logic
**Location:** [`pages/8_approval_required.py`](../pages/8_approval_required.py)

```python
all_decisions = [
    ticket["department_reviews"][d]["decision"]
    for d in departments
]

if all(d == "Reject" for d in all_decisions):
    final_status = "REJECTED"
elif "Need More Information" in all_decisions:
    final_status = "PENDING"
elif all(d == "Approve" for d in all_decisions):
    final_status = "APPROVED"
else:
    final_status = "PENDING"
```

---

## 🧩 **PV Context Mapping State**

### Location
[`pages/22_PV_context_mapping.py`](../pages/22_PV_context_mapping.py)

### Context Collection Sections

**A. Product Facts (Pre-filled, read-only)**
- Application name
- Vendor
- Product type (Fremdsoftware / Eigenentwicklung / Hardware)
- Domain & Capabilities
- License type

**B. Deployment & Criticality**
- Deployment: SaaS / On-Prem / Hybrid
- Business Criticality: Low / Medium / High / Mission Critical
- Urgency: Niedrig / Mittel / Hoch / Kritisch

**C. Risk & Compliance**
- Processes personal data (boolean)
- Authenticates users (boolean)
- Internet exposed (boolean)
- Regulatory relevant (boolean)
- Data classification: Public / Internal / Confidential / Restricted
- Availability: Best effort / Business hours / 24/7

**D. Operational Characteristics**
- User count: <50 / 50–500 / 500–5000 / >5000
- Support model: None / Best effort / Defined SLA
- Change frequency: Rare / Occasional / Frequent
- Release frequency: Ad-hoc / Planned / Continuous
- Integration criticality: None / Low / High
- Customization level: Standard / Configured / Highly customized

### Derived Level Calculation
```python
# Base level from product type
level_order = ["L0", "L1", "L2", "L3", "L4"]
idx = 1 if product_type == "Eigenentwicklung" else 0

# Bump up for operational factors
if user_count in ["500–5000", ">5000"]:
    idx += 1
if business_criticality in ["High", "Mission Critical"]:
    idx += 1
if change_frequency == "Frequent":
    idx += 1
if regulatory_relevant or personal_data:
    idx += 1
if internet_exposed:
    idx += 1

level = level_order[min(idx, 4)]  # L0–L4
```

### Scenario Inference
```python
scenario = "Neueinführung"  # Default

if change_frequency == "Frequent":
    scenario = "Maintenance"
elif release_frequency in ["Planned", "Continuous"]:
    scenario = "Release Upgrade"
elif regulatory_relevant or personal_data:
    scenario = "Security relevant"
```

---

## 📋 **Requirements Tracking State**

### Location
[`state/requirements.py`](../state/requirements.py) & [`requirement_store/`](../requirement_store/)

### Initialization
```python
from state.requirements import init_requirements, get_all_requirements

init_requirements()  # Loads from disk
requirements = get_all_requirements()
```

### Requirement Structure
```json
{
  "id": "5_shop_artikel_shop_article_todo_1",
  "title": {
    "id": "grey_stackholders",
    "text": "Alignment with PF, MT regarding departments to be informed for Greylist decision"
  },
  "section": "shop article",
  "type": "todo",
  "status": "In Progress",
  "actor": "alice.admin",
  "history": [
    {
      "timestamp": "2025-12-23T09:35:40",
      "action": "Status updated",
      "actor": "alice.admin",
      "details": {
        "from": "Proposed",
        "to": "In Progress",
        "comment": "Starting implementation"
      }
    }
  ]
}
```

### Requirement Types
- **question:** Unresolved design decision
- **todo:** Implementation gap or pending task
- **note:** Important context or assumption

### Status Lifecycle
```
Proposed → In Progress → Completed → Reviewed
```

### Key Functions
```python
from state.requirements import (
    save_requirement,      # Persist to disk
    get_requirement,       # Load by ID
    get_all_requirements,  # Load all
    add_requirement_event  # Log status change
)
```

### File Structure
```
requirement_store/
├── 5_shop_artikel_shop_article_todo_1.json
├── 5_shop_artikel_shop_article_question_1.json
├── 8_approval_required_approval_required_note_1.json
├── ...
```

---

## 🎯 **Page-Level Context State**

### EPM Journey Context

| Variable | Set By | Purpose |
|----------|--------|---------|
| `st.session_state.selected_ticket` | [`8_approval_required.py`](../pages/8_approval_required.py) | Currently selected ticket ID |
| `st.session_state.pv_forward_ticket` | [`14_is_p_architektur_flow.py`](../pages/14_is_p_architektur_flow.py) | Forward ticket to PV context page |
| `st.session_state.latest_ticket` | Multiple pages | Most recently accessed/created ticket |

### Device/Scanner Journey Context

| Variable | Set By | Purpose |
|----------|--------|---------|
| `st.session_state.device_current_page` | All pages | Track current page in device flow |
| `st.session_state.scanner_red_app` | [`0c_blocked_red.py`](../pages/0c_blocked_red.py) | Currently viewed blocked app |

### LUY Context

| Variable | Set By | Purpose |
|----------|--------|---------|
| `st.session_state.luy_current_app` | [`state/luy.py`](../state/luy.py) | Selected LUY app |
| `st.session_state.luy_discussions` | Various pages | Comments on LUY entries |

---

## 🏗 **Initialization Flow**

### Application Startup (in `home.py`)
```python
import streamlit as st
from state.core import init_app_state

st.set_page_config(page_title="EPM Control Center", ...)
init_app_state()  # Master initialization
```

### `init_app_state()` Details (in `state/core.py`)
```python
def init_app_state():
    # User & permissions
    if "user" not in st.session_state:
        st.session_state.user = None
    
    # Tickets
    from state.tickets import init_tickets
    init_tickets()
    
    # LUY
    from state.luy import init_luy_state
    init_luy_state()
    
    # EPM lists
    from state.epm_lists import init_epm_lists
    init_epm_lists()
    
    # Requirements
    from state.requirements import init_requirements
    init_requirements()
```

---

## ⚙️ **Performance Considerations**

- **Tickets:** Stored in memory; no automatic persistence ⚠️ (lost on restart)
- **LUY:** 6 fixed entries + runtime additions (fast in-memory lookup)
- **Requirements:** Persisted to disk (faster than rebuilding from CSV)
- **EPM Lists:** Stored in memory; populated from LUY on init

### Recommendation
For production deployment, migrate ticket storage to a database (PostgreSQL, MongoDB) instead of session state.

---

## 📚 **Related Documentation**

- [`JOURNEYS.md`](../JOURNEYS.md) — Detailed user workflow descriptions
- [`navigation.py`](../navigation.py) — Page structure & sidebar routing
- [`components/ticket_history.py`](../components/ticket_history.py) — Event logging utilities
- [`components/pv_rules_engine.py`](../components/pv_rules_engine.py) — PV obligation derivation
- [`components/luy_engine.py`](../components/luy_engine.py) — Domain/capability classification
- [`components/requirements.py`](../components/requirements.py) — Requirement UI helpers

---

EOF