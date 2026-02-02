from navigation import load_navigation
from state.requirements import load_all_requirements

load_all_requirements()
nav = load_navigation()
nav.run()


