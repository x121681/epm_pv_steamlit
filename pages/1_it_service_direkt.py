import streamlit as st
from state.permissions import  require_system
from state.tickets import create_ticket
from components.ticket_history import add_ticket_event
from components.requirements import show_requirements

st.session_state["device_current_page"] = "1_it_service_direkt"  # unique per page

# Require login
require_system("device")
# removed explicit uuid usage for ticket id (create_ticket will generate one)

# ------------------------
# Current logged-in user
# ------------------------
user = st.session_state.get("user")
if not user:
    st.warning("Please login first.")
    st.stop()

username = user["username"]


st.title("🧾 IT-Service Direkt – Software Intake")
st.write("Bitte geben Sie die Informationen zu Ihrer Softwareanfrage ein.")

# Initialize session_state for storing request data
if "intake_submitted" not in st.session_state:
    st.session_state.intake_submitted = False

with st.form("software_intake_form"):
    st.header("🔍 Software Details")

    software_name = st.text_input("Name der Software", placeholder="z. B. Visual Studio Code")
    vendor = st.text_input("Name der Hersteller", placeholder="z.B. Microsoft")
    Funktionsweise = st.text_area("Wie Funtioniert dieses tool", placeholder="Visual Studio Code (commonly referred to as VS Code) is an integrated development " \
    "environment developed by Microsoft for Windows, Linux, macOS and web browsers. Features include support for debugging, syntax highlighting, intelligent code " \
    "completion, snippets, code refactoring, and embedded version control with Git.")
    
    st.header("💼 Lizenztyp")
    license_type = st.radio("Lizenzart", ["Open Source", "Kommerziell"], horizontal=True)

    if license_type == "Kommerziell":
        license_cost = st.text_input("Falls bekannt: Kosten / Lizenzmodell", placeholder="Optional")
    luyid= st.text_area("EAM Repository ID", placeholder="74534")
    workstation = st.text_area("Device on which it must be installed", placeholder="WS503702")
    weitereansprechpartner = st.text_area("Other stakeholders that require this software", placeholder="Lukas Pöhler")
    reason = st.text_area("Bedarf", placeholder="Warum wird die Software benötigt?")
    st.header("📁 Zusätzliche Informationen")
    urgency = st.selectbox("Dringlichkeit", ["Niedrig", "Mittel", "Hoch", "Kritisch"])
    documentation = st.file_uploader("Dokumentation oder technische Beschreibung (optional)")
    vendor_known = st.checkbox("Ich kenne den Hersteller / Vendor")

    if vendor_known:
        vendor_name = st.text_input("Name des Herstellers")

    infra_needed = st.checkbox("Hat das Produkt Hardware- / Infrastrukturabhängigkeiten?")

    if infra_needed:
        infra_desc = st.text_area(
            "Beschreibung der Infrastrukturabhängigkeiten",
            placeholder="z. B. benötigt spezielle Server, GPU, Container, etc."
        )

    submitted = st.form_submit_button("✓ Anfrage abschicken")

# -------------------------------------------------
# SUBMIT HANDLER
# -------------------------------------------------
if submitted:
    st.session_state.intake_submitted = True

    # ✅ BASIC VALIDATION (non-breaking)
    if not software_name or not reason:
        st.error("Bitte geben Sie mindestens Software-Name und Grund an.")
        st.stop()

    # -------------------------------------------------
    # CREATE TICKET (use create_ticket helper)
    # -------------------------------------------------
    ticket = create_ticket(
        source="IT Service Direkt",
        application=software_name,
        reason=reason,
        journey="it_service_direkt",
        status="Created",
        created_by= username,
        extra={
            "urgency": urgency,
            "license_type": license_type,
            "license_cost": license_cost if license_type == "Kommerziell" else None,
            "vendor": vendor_name if vendor_known else None,
            "infrastructure": infra_desc if infra_needed else None,
        }
    )
    add_ticket_event(
    ticket,
    action="IT Service Direkt Request Submitted",
    actor=username,
    details={
        "software_name": software_name,
        "vendor": vendor_name if vendor_known else vendor,
        "urgency": urgency,
        "license_type": license_type,
        "license_cost": license_cost if license_type == "Kommerziell" else None,
        "infrastructure_required": infra_needed,
        "infrastructure_details": infra_desc if infra_needed else None,
        "workstation": workstation,
        "eam_repository_id": luyid,
        "stakeholders": weitereansprechpartner,
    },
    new_status="Pending IS-P Review",
)


    # -------------------------------------------------
    # EXISTING UX (UNCHANGED)
    # -------------------------------------------------
    st.success("Ihre Anfrage wurde erfolgreich erfasst!")

    st.subheader("📬 Zusammenfassung Ihrer Eingaben:")
    st.write(f"**Software:** {software_name}")
    st.write(f"**Grund:** {reason}")
    st.write(f"**Dringlichkeit:** {urgency}")
    st.write(f"**Lizenztyp:** {license_type}")

    if license_type == "Kommerziell":
        st.write(f"**Lizenzkosten:** {license_cost}")

    if vendor_known:
        st.write(f"**Hersteller:** {vendor_name}")

    if infra_needed:
        st.write(f"**Infrastrukturabhängigkeiten:** {infra_desc}")

    st.markdown("---")
    st.markdown(f"🎟 **Ticket erstellt:** `{ticket['ticket_id']}`")


# ----------------------
# NAVIGATION BUTTON (OUTSIDE FORM)
# ----------------------
if st.session_state.get("intake_submitted"):
    if st.button("➡ Weiter zum Shop-Artikel-Prozess"):
        # Use the **exact page name** from sidebar, e.g., "5_shop_artikel"
        st.session_state.device_current_page = "5_shop_artikel"
        st.switch_page("pages/5_shop_artikel.py")

with st.expander("IT Service Direkt Freischaltung einer Anwendung in EPM"):
    st.image("images/it_service_direkt.png")

show_requirements(
    "extra info",
    items=[
        {
            "id": "extra information",
            "text": "not part of official dialog but some things are valid to be asked here need a confirmation with other stakeholders",
        }
    ],
    req_type="note"
)