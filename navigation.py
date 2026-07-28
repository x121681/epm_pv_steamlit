import streamlit as st

def load_navigation():
    """
    Main navigation structure mapping user roles to workflows.
    Legends:
    I - Inmplemented
    E - Extra
    F - Feature
    """
    return st.navigation(
        {
            "Start Here": [
                st.Page("pages/a_epm_workflow_diagram.py", title="📊 Workflow Overview"),
            ],
            "End User Journey": [
                st.Page("pages/19_user_device_login.py", title="[Implemented] User Device Login"),
                st.Page("pages/21_user_journey_selection.py", title="[Preview] Choose Your Next Step"),
                st.Page("pages/0_scanner_blacklist.py", title="[Implemented] Blacklisted App"),
                st.Page("pages/0a_admin_permission.py", title="[Implemented] Software Installation"),
                st.Page("pages/0b_blocked_yellow.py", title="[Planned] EPM Ticket"),
                st.Page("pages/0c_blocked_red.py", title="[Implemented] Outlook Mail"),
                st.Page("pages/17_ticket_history.py", title="[Planned] My Tickets"),
                st.Page("pages/1_it_service_direkt.py", title="[Implemented] IT Service Direct"),
            ],
            "EPM Team": [
                st.Page("pages/20_epm_login.py", title="[Implemented] EPM Login"),
                st.Page("pages/6_epm_scanner_dashboard.py", title="[Planned] EPM Lists Dashboard"),
                st.Page("pages/5_shop_artikel.py", title="[Planned] Shop Artikel"),
                st.Page("pages/8_approval_required.py", title="[Planned] Approval Required"),
            ],
            "Architecture flow (IS-P / EAM)": [
                st.Page("pages/14_is_p_architecture_flow.py", title="[Planned] Architecture Review")
            ],
            "Finance Flow (IS-V)": [
                st.Page("pages/18_backend_spyder.py", title="[Planned] SPYDER Backend Process"),
            ],
            "Security Flow (CSO-I / IS-G)": [
                st.Page("pages/10_backend_eirma.py", title="[Planned] CSO-I Review"),
                st.Page("pages/11_backend_cmdb.py", title="[Planned] IS-G Review"),
                st.Page("pages/12_backend_mpi.py", title="[Planned] MPI Check"),
            ],
            "PV Responsibilities": [
                st.Page("pages/22_PV_context_mapping.py", title="[Planned] PV Context Mapping")
            ],
            "Project Details": [
                st.Page("pages/requirements_overview.py", title="[Preview] Project Requirements"),
            ]

        }
    )
