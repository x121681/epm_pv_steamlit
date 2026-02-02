import streamlit as st
from streamlit_mermaid import st_mermaid
from components.requirements import show_requirements

# -------------------------------------------------
# Page config
# -------------------------------------------------
st.set_page_config(
    page_title="EPM Workflow Journey Map",
    page_icon="📊",
    layout="wide"
)

st.title("📊 EPM Workflow Journey Map")
st.caption(
    "Click the steps directly under the diagram to navigate. "
    "Buttons are aligned 1:1 with the workflow nodes."
)

# -------------------------------------------------
# 1️⃣ Mermaid diagram (VISUAL ONLY)
# -------------------------------------------------
st_mermaid("""
%%{init: {'flowchart': {'htmlLabels': true}, 'primaryColor': '#E8F4F8', 'primaryTextColor': '#000', 'primaryBorderColor': '#0066cc', 'lineColor': '#4A4A4A', 'secondBkgColor': '#FFF4E6', 'tertiaryColor': '#E8F5E9'}}%%
flowchart LR

%% =========================
%% LEGEND NODES
%% =========================
LEGEND["📌 LEGEND"]:::legend
LANE1["Extra"]:::extra
LANE2["Feature"]:::feature
LANE3["Implemented"]:::implemented         

%% =========================
%% End User Lane
%% =========================
subgraph ENDUSER["🧑‍💻 End User"]
    A["🚀 Device Login / SSO"]

    subgraph EPM_Blockmeldung["🚫 EPM Blockmeldung"]
        B1["🔴 Blacklisted App"]
        B2["⛔ EPM ticket method"]
        B3["🟡 Admin Permission"]
        B4["⛔ Outlook mail method"]
    end

    D["📝 IT Service Direkt"]
end

C["🛒 Bestellung auslösen"]

%% =========================
%% EPM Admin Lane
%% =========================
subgraph EPM_tool["🔧 EPM Management Tools"]
    H["🎟 My Tickets"]
    E["📊 EPM Scanner Dashboard"]
end           

subgraph EPM["📊 EPM Admin"]

    subgraph MPI["🛒 MPI Shop Artikel"]
        F["🛒 Shop Artikel Decision"]
        N1["ℹ️ EPM Admins Erst-Einschätzung"]
        N4["❓ Automatische Weitergabe?"]
    end
end

O["🔍 Freigabe nötig"]

%% =========================
%% Parallel Reviews
%% =========================
subgraph REVIEWS["🔍 Fachliche & Technische Prüfungen"]
    N5["ℹ️ Zurzeit im MPI geplant"]

    subgraph ARCH["🏛 Architect (IS-P / EAM)"]
        I["🏗 Architecture Review"]
        N2["ℹ️ LUY / Confluence"]
    end

    subgraph ISG["📋 IS-G (Compliance)"]
        J["✅ Compliance Review"]
        K["🧩 PV Context Mapping"]
        N3["ℹ️ Abteilungsfeedback"]
    end

    subgraph SEC["🔐 Security"]
        P["🔐 CSO-I Review"]
    end

    subgraph ISV["💰 IS-V (License / Finance)"]
        Q["💰 License Review"]
    end
    R["Final Decision"]       
end

%% =========================
%% Outcomes
%% =========================
R1["✅ APPROVED"]
R2["❌ REJECTED"]

%% =========================
%% Flow
%% =========================
A --> B1
A --> B3
A --> B4
A --> D
ENDUSER --> EPM_tool
EPM --> EPM_tool

B1 --> C
B3 --> C
B4 --> C
D --> C

C --> F
N1 -.-> F
N4 -.-> F

F -->|Whitelist| R1
F -->|Blacklist| R2
F -->|Greylist| O

O --> I
O --> J
O --> P
O --> Q
           
K --> R
J --> R
P --> R
Q --> R

I --> K
           
%% =========================
%% STYLING
%% =========================
classDef extra fill:#E3F2FD,stroke:#1976D2,stroke-width:2px,color:#000
classDef feature fill:#FFF3E0,stroke:#F57C00,stroke-width:2px,color:#000
classDef implemented fill:#E8F5E9,stroke:#388E3C,stroke-width:2px,color:#000
classDef legend fill:#F3E5F5,stroke:#7B1FA2,stroke-width:2px,color:#000

class B2,H,E,F,I,J,K,P,Q,R feature
class A,B1,B3,B4,D implemented
class LEGEND legend

""")



# Tight spacing so overlay feels attached
st.markdown("<div style='margin-top:-20px'></div>", unsafe_allow_html=True)

# -------------------------------------------------
# Navigation helper
# -------------------------------------------------
def go(page: str):
    st.switch_page(page)

# -------------------------------------------------
# 2️⃣ Inline overlay buttons (ALIGNED TO DIAGRAM)
# -------------------------------------------------

st.divider()
st.subheader("🔗 Stakeholder Navigation")
st.caption(
    "Even if you want to try Arch or EPM Journey a ticket is required so please login as end user first."
    "and then use (New request) to create a ticket, then with proper credentials you can login as EPM admin or Arch team."
)

c1, c2, c3 = st.columns(3)

with c1:
    st.markdown("### 🧑‍💻 End User")
    if st.button("Device Login / SSO"):
        st.switch_page("pages/19_user_device_login.py")
    if st.button("Blacklisted App"):
        st.switch_page("pages/0_scanner_blacklist.py")
    if st.button("Admin Permission"):
        st.switch_page("pages/0a_admin_permission.py")
    if st.button("Outlook mail method"):
        st.switch_page("pages/0c_blocked_red.py")
    if st.button("EPM ticket method"):
        st.switch_page("pages/0b_blocked_yellow.py")
    if st.button("New Request/IT Service Direkt"):
        st.switch_page("pages/1_it_service_direkt.pyy")

with c2:
    st.markdown("### 🔧 EPM Management Tools")
    if st.button("My Tickets"):
        st.switch_page("pages/17_ticket_history.py")
    if st.button("EPM Scanner Dashboard"):
        st.switch_page("pages/6_epm_scanner_dashboard.py")
    st.markdown("### 📊 EPM Admin")
    if st.button("Shop Artikel"):
        st.switch_page("pages/5_shop_artikel.py")

with c3:
    st.markdown("### 🏛 Approval Required")
    if st.button("Approvals"):
        st.switch_page("pages/8_approval_required.py")
    st.markdown("### Feedback")
    if st.button("Architecture Review"):
        st.switch_page("pages/14_is_p_architecture_flow.py")
    if st.button("IS-G PV Context"):
        st.switch_page("pages/22_PV_context_mapping.py")
    if st.button("CSO-I Review"):
        st.switch_page("pages/10_backend_eirma.py")
    if st.button("License Review"):
        st.switch_page("pages/18_backend_spyder.py")

st_mermaid("""
flowchart TD

%% =========================
%% Entry Points
%% =========================
A["🚫 EPM-Blockmeldung"]
B["🛒 Shopartikel"]

%% =========================
%% Initial Assessment
%% =========================
C["🧠 Ersteinschätzung<br/>IBW2 / EPM-Admins"]

%% =========================
%% Immediate Decisions
%% =========================
D["⛔ Keine Freigabe möglich<br/>(Blacklist)"]
E["✅ Kein Freigabeprozess notwendig"]

%% =========================
%% Parallel Reviews
%% =========================
subgraph REVIEWS["🔍 Fachliche & Technische Prüfungen"]
    R["📥 Review"]
    F["🔐 CSO-I<br/>(Security)"]
    G["🏛 IS-P<br/>(Architecture)"]
    H["📋 IS-G<br/>(Compliance)"]
    I["💰 IS-V<br/>(License / Finance)"]

    R --> F
    R --> G
    R --> H
    R --> I
end

J["👥 IBW2 / EPM-Admins"]
M["Ergebnis"]

%% =========================
%% Final Decision
%% =========================
K["📜 White / Blacklist"]
L["📣 Rückmeldung an User"]

%% =========================
%% Flow
%% =========================
A -->|"Bestellung auslösen"| B
B -->|"Automatische Weitergabe"| C

C -->|Direkt ablehnen| D
C -->|Direkt freigeben| E
C -->|Freigabe nötig| R

I --> M
F --> M
G --> M
H --> M

M --> J

J --> K
D --> L
E --> L
K --> L
""")

show_requirements("High Level Questions",[
    "Are we following whitelist first or blacklist first strategy: means denying [everything] by default and allowing only what is in white "
    "or allowing everything by default and only blocking what is in black - if we are mixing both then how does it work?",
    "In both cases what is to be allowed and what [Everything] means needs to be clarified, IT-Product and its scope and its mapping to different"
    "Semantics model - Interop - EAM needs to be agreed and strategy how to implement it?"
],req_type="question")

show_requirements("High Level Questions",[
    "From our first collection strategy where we worked on initial blocked excel list and collection of developers in confluence, my assumption"
    "is that we have a whitelist first strategy, but as we have some scripts as well in the list what is exactly being blocked is not clear",
    "Meanwhile as it is more than 1 year may be we have shifted to a mixed strategy",
    "Whatever is whitelisted should be categorized already in these capability / domain - Which is presently not the case",
    "Whatever is block / grey list should also have domain and category, specially if they are popular tools"
],req_type="note")
show_requirements("High Level Questions",[
    "Include rest of the pages and journexs in home",
],req_type="todo")