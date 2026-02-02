import streamlit as st
from components.requirements import show_requirements
from state.permissions import require_system
from state.luy import get_current_luy_app  # <- LUY source of truth



st.session_state["device_current_page"] = "0_scanner_blacklist"  # unique per page

# -----------------------------
# Require login / permission
# -----------------------------
require_system("device")

st.title("🚨 Scanner - Blacklisted Software")
st.write("Checking software against blacklist...")

# -----------------------------
# Get current software from LUY
# -----------------------------
if "blacklist_app" not in st.session_state:
    st.session_state.blacklist_app = get_current_luy_app()

# -----------------------------
# Warning / popup
# -----------------------------
st.warning(f"You are trying to start a software **{st.session_state.blacklist_app}** that is **blacklisted**!")
if st.button("Learn more in EPM Dashboard"):
    st.switch_page("pages/6_epm_scanner_dashboard.py")  # Use the actual page name in your app
col1, col2 = st.columns(2)
with col1:
    if st.button("OK"):
        st.success("Acknowledged. We can continue.")

with col2:
    if st.button("Return to Journey"):
        st.switch_page("pages/21_user_journey_selection.py")  # redirect

with st.expander("Popup that shows a software that is blacklisted"):
    st.image("images/blacklist_red.png")

# -----------------------------
# Questions / Todos / Notes
# -----------------------------

show_requirements(
    "scanner blacklist",
    items=[
        {
            "id": "Dynamism",
            "text": "Presently we are considering simple scenarios but e.g. postman situation showed us that black / whitelist needs to be dynamic?",
        },
        {
            "id": "ticket_already_blacklisted",
            "text": "Is it possible to create a request in IT-Service-Direct for already blacklisted software that can't be challenged?"
        }
    ],
    req_type="question"
)

show_requirements(
    "scanner blacklist",
    items=[
        {
            "id": "User_challenge",
            "text": "Not only we need to integrate flexibility of white / blacklist swapping but also user can challenge it",
        },
        {
            "id": "Blocked_vs_Blacklist",
            "text": "Clarify with IBW difference between blocked and blacklisted software and their decision process"
        },
        {
            "id":"state blacklist",
            "text":"If on this page user sees a luy app as blacklist then for learn more in EPM dashbaord he should be "
            "able to see the same app in blacklist section"
        }
    ],
    req_type="todo"
)

show_requirements(
    "scanner blacklist",
    items=[
        {
            "id": "Challenging_not_required",
            "text": "IBW thinks here is no need of providing objections possibilities",
        },
        {
            "id": "Challenging_reasoning",
            "text": "Although it is reasonably true that some softwares / sites are always to be blacklisted (e.g. hacking tools)"
        }
    ],
    req_type="note"
)