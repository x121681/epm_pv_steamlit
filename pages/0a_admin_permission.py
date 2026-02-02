import streamlit as st
from state.permissions import require_system
from components.requirements import show_requirements
from state.user import USERS
from state.luy import get_current_luy_app



st.session_state["device_current_page"] = "0a_admin_permission"  # unique per page

# ------------------------
# Require login to device system
# ------------------------
require_system("device")

st.title("🛡 Admin Permission Check")


app_name = get_current_luy_app()
st.write(f"**{app_name}** software requires administrative permissions to proceed.")


st.info("Please provide your Admin credentials to continue.")

# ------------------------
# Input Fields
# ------------------------
admin_user = st.text_input("Admin Username")
admin_pass = st.text_input("Admin Password", type="password")

col1, col2 = st.columns(2)

with col1:
    if st.button("OK"):
        # ------------------------
        # VALIDATE USER
        # ------------------------
        if admin_user in USERS:
            user_record = USERS[admin_user]
            if user_record["password"] == admin_pass:
                if "admin" in user_record["roles"]:
                    st.success(f"✅ Admin credentials verified for {admin_user}. You may proceed.")
                    # Store verification in session_state
                    st.session_state.admin_verified = True
                else:
                    st.error("❌ User does not have Admin rights!")
                    st.session_state.admin_verified = False
            else:
                st.error("❌ Invalid password!")
                st.session_state.admin_verified = False
        else:
            st.error("❌ User not found!")
            st.session_state.admin_verified = False

with col2:
    if st.button("Cancel"):
        st.warning("Operation canceled by user.")
        st.session_state.admin_verified = False

# ------------------------
# Optional Pop-up / Info
# ------------------------
with st.expander("Popup that shows an admin permission required"):
    st.image("images/admin_permission.png")


# ------------------------
# Example: Use admin_verified elsewhere
# ------------------------
if st.session_state.get("admin_verified"):
    st.info("Admin operations unlocked! You can now perform restricted actions.")
else:
    st.warning("Admin operations are locked until valid credentials are provided.")


# -----------------------------
# Questions / Todos / Notes
# -----------------------------

show_requirements(
    "admin permission check",
    items=[
        {
            "id": "Admin login",
            "text": "This process is shown in this prototype for the sake of completeness, but it doesn't impact Whitelisting process as such."
        }
    ],
    req_type="note"
)
