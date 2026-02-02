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
            "HOME": [
                st.Page("pages/a_epm_workflow_diagram.py", title="📊 Workflow Diagram"),
            ],
            "User Journey: User Device Login": [
                # As a user i starts my client , should we add client login here? 
                st.Page("pages/19_user_device_login.py", title="[I]User Device Login"),
                # I get all my possible journey
                st.Page("pages/21_user_journey_selection.py", title="[E]User Journey Selection"),
                # I open a software that i didn't used for a while and didn't knew that was in meanwhile blacklisted
                st.Page("pages/0_scanner_blacklist.py", title="[I]starting a blacklisted app"),
                # I attempted to install a software that is presently not in whitelist
                # Softwares only in whitelist in future will be permitted, is that the case?
                # I don't have admin rights so i have to provide them
                st.Page("pages/0a_admin_permission.py", title="[I]Installing software"),
                # I was reminded that software is not on whitelist or is blocked, i have to provide reason
                # for it to be reviewed by EPM team
                # This popup i think will be implemented in future and will create a ticket
                # We don't know in which system?
                st.Page("pages/0b_blocked_yellow.py", title="[F]EPM ticket"),
                # Another type of popup not sure when is which popup called
                # This popup open an outlook email and start the communicaiton
                st.Page("pages/0c_blocked_red.py", title="[I]outlook mail"),
                # As a user i want to check how many requests i have created or what is the status of my request
                st.Page("pages/17_ticket_history.py", title="[F]My Tickets"),
                # As a user i found out that we need a new software and wanted to check if it is in Black/White/Grey list
                # I found out it is already in the black or grey list i read the reason and upvote or ask for urgency 
                #st.Page("pages/6_epm_scanner_dashboard.py", title="User Login EPM dashboard"),
                # I found out that software needs to be requested 
                st.Page("pages/1_it_service_direkt.py", title="[I]IT-service-direct"),
            ],
            "EPM Team": [
                # EPM login happens here
                st.Page("pages/20_epm_login.py", title="[I]EPM Login"),
                # As EPM Admin i check actively the present list of black/white/grey listed softwares and or see the new requests
                # Statistics about how many requests are pending or processed and avg. time, urgency levels are also mentioned here
                st.Page("pages/6_epm_scanner_dashboard.py", title="[F]EPM Lists Dashboard"),
                # As EPM admin i am also interested in active state of software that are white/black/grey listed
                # Does this information comes from EIRMA, Internet, Beyond Trust, MPI??  
                # As EPM Admin i have been informed that a new request has appeared and MPI Shop artikel process needs to be started
                # We do our first analysis of request, filter out requests, communicate back with customer if more information is needed
                # Also one of the three decision are made here freigabe process needed, not needed, can't be approved
                st.Page("pages/5_shop_artikel.py", title="[F]Shop Artikel"),
                # After Ersteeinschätzung we do deeper analysis of software, check with architecture team, security team, license team
                st.Page("pages/8_approval_required.py", title="[F]Approval Required"),
                # We communicate wiht customer that it is in freigabe process 
                # We inform customer about decision
            ],
            "Architecture flow (IS-P / EAM)": [
                # After Ersteeinschätzung EPM team forwards request to IS-P architecture team for deeper analysis
                # IS-P architects check the software from architecture point of view
                # What does architectural point of view means that needs to be clarified
                # One of the ways are used by shop article - inform the responsible person in EAM 
                # in future may be we can either open a luy decision page or eam task page directly from here
                st.Page("pages/14_is_p_architecture_flow.py", title="[F]Architecture Review")
                
            ],
            "Finance Flow (IS-V)": [
                # In case if a purchasing is required IS-V departments needs to be informed to check liscene and resources
                st.Page("pages/18_backend_spyder.py", title="[F]SPYDER Backend Process"),
            ],
            "Security Flow (CSO-I / IS-G)": [
                # Rest two stakeholders are also involved simaltaneously as IS-P
                # Collaboration model and interoperability of tools needs to be defined between stakeholders
                st.Page("pages/10_backend_eirma.py", title="[F]CSO-I Review"),
                st.Page("pages/11_backend_cmdb.py", title="[F]IS-G Review"),
                st.Page("pages/12_backend_mpi.py", title="[F]MPI check"),
            ],
            "PV-Responsibilities" : [
                st.Page("pages/22_PV_context_mapping.py",title="[F]PV context Mapping")
            ],
            "Others" : [
                st.Page("pages/requirements_overview.py",title="[E]Project Requirements"),
            ]

        }
    )
