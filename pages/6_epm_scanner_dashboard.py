import streamlit as st
import pandas as pd
from state.epm_lists import init_epm_lists, get_epm_lists, set_epm_lists, find_epm_entry
from state.tickets import get_latest_ticket, get_all_tickets, set_all_tickets
from state.permissions import require_system, require_role
from state.luy import init_luy_state, FIXED_LUY_PRODUCTS
from components.requirements import show_requirements

# -----------------------------
# Page setup
# -----------------------------
st.session_state["device_current_page"] = "6_epm_scanner_dashboard"
st.set_page_config(page_title="EPM Scanner Dashboard", layout="wide")
require_system("epm")

# -----------------------------
# User info
# -----------------------------
user = st.session_state.get("user")
if not user:
    st.error("Please log in to continue.")
    st.stop()

roles = user.get("roles", [])
username = user.get("username", "Unknown")
role_label = "Admin" if "admin" in roles else "User"

st.title(f"EPM Scanner Dashboard – {role_label} View")
st.caption(f"Logged in as: {username} ({', '.join(roles)})")

# -----------------------------
# Initialize LUY & EPM state
# -----------------------------
init_luy_state()
init_epm_lists()

# -----------------------------
# Populate EPM lists from LUY if empty
# -----------------------------
# Ensure LUY entries have the blocked key
st.session_state["luy_entries"] = [
    {**app, "blocked": app.get("blocked", False)} for app in FIXED_LUY_PRODUCTS
]

def populate_epm_lists_from_luy():
    blacklist, whitelist, greylist = get_epm_lists()
    if blacklist or whitelist or greylist:
        return  # already populated

    luy_apps = st.session_state.get("luy_entries", [])

    bl, wl, gl = [], [], []

    for app in luy_apps:
        name = app["name"]
        reason = app.get("Reason", "Auto-generated from LUY")
        blocked = app.get("blocked", False)

        if blocked:
            bl.append({"Software": name, "Reason": reason, "Policy": "Blacklisted"})
        else:
            gl.append({"Software": name, "Reason": reason, "Policy": "Greylist"})

    set_epm_lists(bl, wl, gl)

populate_epm_lists_from_luy()


# -----------------------------
# Fetch current lists
# -----------------------------
blacklist, whitelist, greylist = get_epm_lists()

# -----------------------------
# Update lists from latest Shop Artikel ticket
# -----------------------------
ticket = get_latest_ticket()
if ticket and ticket.get("journey") == "shop_artikel":
    app = ticket["application"]
    reason = ticket.get("reason", "No reason")
    decision = ticket.get("decision", "").lower()

    # Remove old entries
    blacklist = [x for x in blacklist if x["Software"] != app]
    whitelist = [x for x in whitelist if x["Software"] != app]
    greylist = [x for x in greylist if x["Software"] != app]

    # Apply new classification
    if decision == "blacklist":
        blacklist.append({"Software": app, "Reason": reason, "Policy": "Blacklisted"})
        st.error(f"📌 '{app}' added to BLACKLIST via Shop Artikel decision")
    elif decision == "whitelist":
        whitelist.append({"Software": app, "Reason": reason, "Policy": "Whitelisted"})
        st.success(f"📌 '{app}' added to WHITELIST via Shop Artikel decision")
    elif decision == "greylist":
        greylist.append({"Software": app, "Reason": reason, "Policy": "Greylist"})
        st.warning(f"📌 '{app}' added to GREYLIST – approval required")

    set_epm_lists(blacklist, whitelist, greylist)

# -----------------------------
# Normalize for dataframe
# -----------------------------
def normalize_for_dataframe(df):
    for col in df.columns:
        df[col] = df[col].apply(lambda x: str(x) if isinstance(x, (list, dict, tuple)) else x)
    return df

df_black = normalize_for_dataframe(pd.DataFrame(blacklist))
df_white = normalize_for_dataframe(pd.DataFrame(whitelist))
df_grey = normalize_for_dataframe(pd.DataFrame(greylist))

# -----------------------------
# Tabs
# -----------------------------
tabs = ["🚫 Blacklist", "✔ Whitelist", "⚪ Greylist – Needs Review"]
if "admin" in roles:
    tabs.append("📝 All Tickets (Admin)")

tab1, tab2, tab3, *admin_tab = st.tabs(tabs)

# -----------------------------
# BLACKLIST TAB
# -----------------------------
with tab1:
    st.header("🚫 Blacklisted Software")
    search = st.text_input("Search Blacklist", key="search_black")
    filtered = df_black[df_black["Software"].str.contains(search, case=False)] if search else df_black
    st.dataframe(filtered, use_container_width=True)

# -----------------------------
# WHITELIST TAB
# -----------------------------
with tab2:
    st.header("✔ Whitelisted Software")
    search = st.text_input("Search Whitelist", key="search_white")
    filtered = df_white[df_white["Software"].str.contains(search, case=False)] if search else df_white
    st.dataframe(filtered, use_container_width=True)

# -----------------------------
# GREYLIST TAB
# -----------------------------
with tab3:
    st.header("⚪ Greylist – Needs Review")
    search = st.text_input("Search Greylist", key="search_grey")
    filtered = df_grey[df_grey["Software"].str.contains(search, case=False)] if search else df_grey
    st.dataframe(filtered, use_container_width=True)

    if "admin" in roles and len(df_grey) > 0:
        require_role("admin")
        selected = st.selectbox("Select software to classify:", df_grey["Software"])
        action = st.radio("Classify as:", ["Whitelist", "Blacklist"])
        if st.button("Apply Classification", key=f"apply_{selected}"):
            greylist = [x for x in greylist if x["Software"] != selected]
            if action.lower() == "whitelist":
                whitelist.append({"Software": selected, "Reason": "Manual review completed", "Policy": "Whitelisted"})
            else:
                blacklist.append({"Software": selected, "Reason": "Manual review completed", "Policy": "Blacklisted"})
            set_epm_lists(blacklist, whitelist, greylist)
            st.success(f"Updated classification: {selected} → {action.upper()}")
            st.experimental_rerun()

# -----------------------------
# ADMIN TICKETS TAB
# -----------------------------
if admin_tab:
    require_role("admin")
    with admin_tab[0]:
        st.header("📝 All Tickets Overview (Admin)")
        tickets = get_all_tickets()
        if tickets:
            df_tickets = pd.DataFrame(tickets)
            df_tickets = normalize_for_dataframe(df_tickets)
            df_tickets.sort_values(by=["urgency", "date"], ascending=[False, False], inplace=True)
            st.dataframe(df_tickets, use_container_width=True)

            selected_ticket = st.selectbox(
                "Select ticket to delete:",
                df_tickets["application"] + " | " + df_tickets["created_by"]
            )
            if st.button("Delete Selected Ticket"):
                app_name, user_name = selected_ticket.split(" | ")
                tickets = [t for t in tickets if not (t["application"] == app_name and t["username"] == user_name)]
                set_all_tickets(tickets)
                st.success(f"Deleted ticket for {app_name} ({user_name})")
                st.experimental_rerun()
        else:
            st.info("No tickets available.")

# -----------------------------
# Footer / Todos
# -----------------------------
st.markdown("---")
st.caption("EPM Scanner – Mocked Frontend © 2025")

show_requirements(
    "Beyond Trust Dashboard",
    items=[
        {"id": "UX_transparency", "text": "Make Blacklist / Whitelist / Greylist transparent with polling"},
        {"id": "discrepency", "text": "Synchronize LUY, blocked apps, and dashboard categories"},
        {"id": "Delete Selected Ticket button", "text": "Fix username bug on deletion"},
        {"id": "Software classify", "text": "Fix rerun bug on Apply Classification"},
    ],
    req_type="todo"
)
