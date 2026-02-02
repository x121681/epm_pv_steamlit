# User Journeys & Workflows

## Overview
This application manages software approval and Product Responsibility (PV) assignment through multiple stakeholder journeys, from end-user requests through architecture review, security evaluation, compliance checks, and PV obligation mapping.

---

## 🧑‍💻 **User Journey: Device/Endpoint Access**

**Entry Point:** [`pages/21_user_journey_selection.py`](pages/21_user_journey_selection.py)

**Actors:** End-users, employees requesting software access

### Scanner-Based Flows

| Step | Page | Trigger | Action | Output |
|------|------|---------|--------|--------|
| 1 | [`0_scanner_blacklist.py`](pages/0_scanner_blacklist.py) | Blacklisted app detected | View block reason | Acknowledgment only |
| 2 | [`0b_blocked_yellow.py`](pages/0b_blocked_yellow.py) | Greylist app detected | Submit justification | Create ticket for review |
| 3 | [`0c_blocked_red.py`](pages/0c_blocked_red.py) | Permanently blocked app | Email support or request whitelist | Support ticket |

### New Software Request Flow

| Step | Page | Trigger | Action | Output |
|------|------|---------|--------|--------|
| 1 | [`1_it_service_direkt.py`](pages/1_it_service_direkt.py) | User initiates request | Submit intake form (name, vendor, reason, urgency, infrastructure) | Ticket created in `DRAFT` status |
| 2 | [`17_ticket_history.py`](pages/17_ticket_history.py) | Anytime | View all tickets & decisions | Track progress across workflows |

**Key State Management:**
- User login: [`state/user.py`](state/user.py) → `st.session_state.user`
- Current app: [`state/luy.py`](state/luy.py) → `get_current_luy_app()`
- Active ticket: [`state/tickets.py`](state/tickets.py) → `get_latest_ticket()`

---

## 🛡️ **EPM Team Journey**

**Entry Point:** [`pages/6_epm_scanner_dashboard.py`](pages/6_epm_scanner_dashboard.py)

**Actors:** EPM administrators, security team, compliance officers

### Full EPM Approval Workflow

| Step | Page | Role | Input | Action | Output |
|------|------|------|-------|--------|--------|
| 1 | [`6_epm_scanner_dashboard.py`](pages/6_epm_scanner_dashboard.py) | Admin | Black/White/Greylist | Monitor & manage lists | Statistics, manual reclassification |
| 2 | [`5_shop_artikel.py`](pages/5_shop_artikel.py) | Admin | Latest ticket | Initial assessment (Ersteeinschätzung) | Whitelist/Blacklist/Greylist decision |
| 3 | [`8_approval_required.py`](pages/8_approval_required.py) | Multi-dept | Greylist decision | Parallel department reviews | Final APPROVED/REJECTED status |

**Ticket Status Flow:**
```
DRAFT
  ↓ [Shop Artikel Decision Made]
DOMAIN_CAPABILITY_FINALIZED
  ↓ [Check PV Coverage]
PV_CONTEXT_REQUIRED (if PV missing)
  ↓ [User Provides PV Context]
PV_RESP_FINALIZATION
  ↓ [All Reviews Complete]
APPROVED or REJECTED
```

---

## 🏛️ **Architecture Journey (IS-P / EAM)**

**Entry Point:** [`pages/14_is_p_architecture_flow.py`](pages/14_is_p_architecture_flow.py)

**Actors:** Solution architects, technical PVs, domain experts

| Step | Page | Input | Action | Output |
|------|------|-------|--------|--------|
| 1 | [`14_is_p_architecture_flow.py`](pages/14_is_p_architecture_flow.py) | Tickets needing review | Domain & capability AI classification | Suggest domains/capabilities |
| 2 | (same page) | Classification suggestions | Architect approves/adjusts classification | Update ticket with final domain/capabilities |
| 3 | (same page) | Final domain/capabilities | Check PV coverage via LUY | Detect missing PV roles |
| 4 | [`22_PV_context_mapping.py`](pages/22_PV_context_mapping.py) | PV context form | Architect collects operational details | Derive PV obligations & level |
| 5 | (same page) | Derived obligations | Save PV context & responsibilities | Store for user confirmation |

**Key Functions:**
- Domain/capability classification: [`components/luy_engine.py`](components/luy_engine.py) → `LuyEngine.classify_software()`
- PV obligation derivation: [`components/pv_rules_engine.py`](components/pv_rules_engine.py) → `PVEngine.get_pv_responsibilities()`
- PV task mapping: [`components/pv_journey.csv`](components/pv_journey.csv) (German PV responsibilities)

---

## 🔐 **Security & Compliance Flow (Parallel Reviews)**

**Invoked From:** [`pages/8_approval_required.py`](pages/8_approval_required.py)

**Parallel Stakeholders:**

| Department | Page | Review Type | Decision Options |
|------------|------|-------------|------------------|
| **CSO-I** (Security) | [`10_backend_eirma.py`](pages/10_backend_eirma.py) | Security risk assessment | Approve / Reject / Need Info |
| **IS-G** (Compliance) | [`11_backend_cmdb.py`](pages/11_backend_cmdb.py) | Configuration & compliance | Approve / Reject / Need Info |
| **IS-V** (Finance/License) | [`18_backend_spyder.py`](pages/18_backend_spyder.py) | License & budget review | Approve / Reject / Need Info |
| **MPI** (Ticketing) | [`12_backend_mpi.py`](pages/12_backend_mpi.py) | Lifecycle & ticketing status | Tracking only |

**Final Decision Logic:**
```
IF any dept Rejects → REJECTED
ELSE IF any dept "Need Info" → PENDING
ELSE IF all depts Approve → APPROVED
```

---

## 📊 **PV Responsibilities Flow**

**Entry Point:** [`pages/22_PV_context_mapping.py`](pages/22_PV_context_mapping.py)

**Purpose:** Map software domain/capabilities + business context to PV obligations

### Context Collection & Derivation

| Section | Input Fields | Engine/Source | Output |
|---------|-------------|-------------|--------|
| **A. Product Facts** | Application, Vendor, Domain, Capabilities | Prefilled (read-only) | N/A |
| **B. Deployment & Criticality** | Deployment (SaaS/On-Prem/Hybrid), Business Criticality | User input | Risk indicators |
| **C. Risk & Compliance** | Personal data, Authentication, Internet exposed, Regulatory relevant | User checkboxes | Compliance flags |
| **C. Operational** | User count, Support model, Change/Release frequency, Integrations, Customization | User dropdowns | Operational profile |
| **D. Derived Obligations** | (Calculated from A–C) | [`PVEngine`](components/pv_rules_engine.py) | PV level (L0–L4), Scenario, Task list |

**Key Data Source:**
- PV journeys: [`components/pv_journey.csv`](components/pv_journey.csv) — German responsibility matrix

---

## 💡 **Requirements & Decision Tracking**

**Entry Point:** [`pages/requirements_overview.py`](pages/requirements_overview.py)

**Types:**
- 🔶 **Questions:** Unresolved design decisions
- 🛠️ **Todos:** Implementation gaps or pending tasks
- 📝 **Notes:** Important context & assumptions

**Status Lifecycle:**
```
Proposed → In Progress → Completed → Reviewed
```

**Persistence:** [`requirement_store/`](requirement_store/) (JSON files per requirement)

**Key Functions:**
- Show requirements: [`components/requirements.show_requirements()`](components/requirements.py)
- Persist: [`state/requirements.save_requirement()`](state/requirements.py)
- Load: [`state/requirements.get_all_requirements()`](state/requirements.py)

---

## 🔄 **Ticket Lifecycle & Status Transitions**

### Creation Points
1. **User initiated:** [`1_it_service_direkt.py`](pages/1_it_service_direkt.py) (new software request)
2. **Scanner triggered:** [`0b_blocked_yellow.py`](pages/0b_blocked_yellow.py) or [`0c_blocked_red.py`](pages/0c_blocked_red.py) (greylist/blacklist challenge)
3. **System created:** Backend processes (EPM list updates)

### Full State Transition Map
```
DRAFT
  ↓ [Create via IT Service Direkt or Scanner]
  
DOMAIN_CAPABILITY_FINALIZED
  ↓ [IS-P Architecture Review + Classification (14_is_p_architecture_flow.py)]
  
PV_CONTEXT_REQUIRED
  ↓ [If PV roles missing; detected in 14_is_p_architektur_flow.py]
  ↓ [User fills context form in 22_PV_context_mapping.py]
  
PV_RESP_FINALIZATION
  ↓ [Derived obligations shown to user in 17_ticket_history.py]
  ↓ [User confirms acceptance]
  
PV_ASSIGNED
  ↓ [All department reviews from 8_approval_required.py complete]
  
APPROVED or REJECTED
  ↓ [Final decision applied via add_ticket_event()]
```

### Page-to-Status Mapping

| Page | Trigger | New Status | Condition |
|------|---------|-----------|-----------|
| [`1_it_service_direkt.py`](pages/1_it_service_direkt.py) | Form submit | `DRAFT` | New request created |
| [`5_shop_artikel.py`](pages/5_shop_artikel.py) | Decision made | `DOMAIN_CAPABILITY_FINALIZED` | If greylist decision |
| [`14_is_p_architecture_flow.py`](pages/14_is_p_architektur_flow.py) | Classification approved | `PV_CONTEXT_REQUIRED` | If PV missing; else stays at current |
| [`22_PV_context_mapping.py`](pages/22_PV_context_mapping.py) | Context submitted | `PV_RESP_FINALIZATION` | Architect saves derived obligations |
| [`17_ticket_history.py`](pages/17_ticket_history.py) | User decision | `APPROVED` or `REJECTED` | User confirms PV responsibility acceptance |
| [`8_approval_required.py`](pages/8_approval_required.py) | Final decision applied | `APPROVED` or `REJECTED` | Multi-dept review complete |

---

## 🔗 **Key Integration Points**

| System | Page | Function |
|--------|------|----------|
| **Beyond Trust (EPM)** | [`6_epm_scanner_dashboard.py`](pages/6_epm_scanner_dashboard.py) | EPM lists (Black/White/Greylist) |
| **EIRMA** | [`10_backend_eirma.py`](pages/10_backend_eirma.py) | Security metadata & protection requirements |
| **CMDB/CMS** | [`11_backend_cmdb.py`](pages/11_backend_cmdb.py) | Configuration items & compliance lifecycle |
| **MPI** | [`12_backend_mpi.py`](pages/12_backend_mpi.py) | Ticketing & approval routing |
| **SPYDER** | [`18_backend_spyder.py`](pages/18_backend_spyder.py) | License management & budget tracking |
| **LUY Repository** | [`state/luy.py`](state/luy.py) + [`22_PV_context_mapping.py`](pages/22_PV_context_mapping.py) | Software catalog & PV intelligence |

---

## 📦 **Data Model References**

### Ticket Structure
- **Location:** [`state/tickets.py`](state/tickets.py)
- **Key Fields:** `ticket_id`, `application`, `reason`, `status`, `journey`, `created_by`, `department_reviews`, `derived_obligations`, `history`
- **See:** [STATE_MANAGEMENT.md](state/STATE_MANAGEMENT.md#-ticket-management)

### LUY Entry Structure
- **Location:** [`state/luy.py`](state/luy.py)
- **Fields:** `id`, `name`, `vendor`, `product`, `domain`, `capabilities`, `active`, `source`
- **Fixed Products:** Adobe Photoshop (LUY-001), Oracle Database (LUY-002), Jira (LUY-003), Bruno API (LUY-004), Jenkins (LUY-005), Internal Data Manager (LUY-006)

### Domain & Capability Map
- **Location:** [`components/domain_cap_map.csv`](components/domain_cap_map.csv)
- **Domains:** 15+ categories (API & Integration, Build & CI/CD, Databases, Development Tools, Infrastructure, Media/Graphics, Monitoring, Networking, Office/Collaboration, Security, System Utilities, Testing & QA, etc.)
- **Capabilities:** 100+ mappings (e.g., "Code Editing / IDE", "Database Clients", "API Testing & Validation", etc.)

### User/Role Structure
- **Location:** [`state/user.py`](state/user.py)
- **Fields:** `username`, `password`, `display_name`, `role` (user/admin), `pv_roles` (PV_TECHNISCH, PV_FACHLICH), `domains`, `active`

---

## 🎯 **High-Level Questions & Strategy**

See [`pages/requirements_overview.py`](pages/requirements_overview.py) and home page [`home.py`](home.py) for open design questions:

1. **Whitelist vs. Blacklist Strategy:** Are we denying everything by default (whitelist-first) or allowing everything and blocking (blacklist-first)? Currently mixed; needs clarification.
2. **Semantic Interoperability:** How do domains, capabilities, and scopes map across EAM, CMDB, LUY, and EPM?
3. **Categorization Completeness:** All whitelisted/blacklisted items should have domain/capability tags (presently incomplete).

---

EOF