import streamlit as st

def domain_capability_input_form(
    key_prefix: str = "dcc",
    title: str = "🧭 Domain & Capability Classification Inputs",
    as_expander: bool = True
):
    """
    Reusable structured input form for domain & capability classification.

    Returns:
        dict with structured classification inputs
    """

    container = (
        st.expander(title, expanded=True)
        if as_expander else st.container()
    )

    with container:

        # ---------------- PRIMARY PURPOSE ----------------
        primary_purpose = st.selectbox(
            "Primary purpose of the software",
            [
                "Build / develop software",
                "Test software",
                "Deploy or run software",
                "Integrate systems or APIs",
                "Store or manage data",
                "Monitor systems or applications",
                "Secure systems, identities, or data",
                "Support collaboration or productivity",
                "Manage infrastructure or cloud resources",
                "Operate networks or connectivity"
            ],
            key=f"{key_prefix}_purpose"
        )

        # ---------------- LIFECYCLE ----------------
        lifecycle_stages = st.multiselect(
            "Lifecycle stage(s) where this tool is used",
            [
                "Design",
                "Build",
                "Test",
                "Package",
                "Deploy",
                "Run",
                "Monitor",
                "Secure",
                "Decommission"
            ],
            key=f"{key_prefix}_lifecycle"
        )

        # ---------------- INTERACTION ----------------
        interaction_scope = st.multiselect(
            "What does the tool primarily interact with?",
            [
                "Source code",
                "APIs",
                "Databases",
                "Files / documents",
                "Infrastructure resources",
                "Network traffic",
                "Users / identities",
                "Logs / metrics / traces",
                "Media (image / video / audio)"
            ],
            key=f"{key_prefix}_interaction"
        )

        # ---------------- DEPLOYMENT CONTEXT ----------------
        runtime_context = st.selectbox(
            "Where does the software run?",
            [
                "Developer workstation",
                "Server / VM",
                "Container / Kubernetes",
                "Cloud managed service",
                "Network appliance",
                "SaaS only"
            ],
            key=f"{key_prefix}_runtime"
        )

        # ---------------- USAGE PATTERN ----------------
        usage_pattern = st.multiselect(
            "How is the tool primarily used?",
            [
                "Interactive (GUI)",
                "Command-line (CLI)",
                "Automated / pipeline",
                "Background service / daemon",
                "Library / runtime"
            ],
            key=f"{key_prefix}_usage"
        )

    return {
        "primary_purpose": primary_purpose,
        "lifecycle_stages": lifecycle_stages,
        "interaction_scope": interaction_scope,
        "runtime_context": runtime_context,
        "usage_pattern": usage_pattern
    }
