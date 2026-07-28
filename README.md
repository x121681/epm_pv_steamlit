# EPM PV Streamlit App

This repository contains a Streamlit-based application for exploring and presenting the Endpoint Privilege Management (EPM) and PV context mapping process.

## What this app does

The app guides users through a simplified journey for:

- end users who encounter blocked or blacklisted applications,
- users who need to request software installation,
- EPM admins who review requests and workflows,
- reviewers and architects involved in approval and context mapping.

It includes:

- a workflow overview page,
- guided user journey pages,
- approval and review flow diagrams,
- a requirements overview section.

## Project structure

- app.py: main Streamlit entry point
- navigation.py: app navigation configuration
- pages/: Streamlit page modules
- components/: reusable UI and logic components
- state/: application state helpers
- requirement_store/: stored requirement content

## Requirements

Install dependencies with:

```bash
pip install -r requirements.txt
```

## Run locally

From the project root, start the app with:

```bash
streamlit run app.py
```

## Recommended usage

When you open the app for the first time:

1. Start from the workflow overview page.
2. Choose the path that matches your role:
   - End User
   - EPM Admin
   - Reviewer / Architect
3. Follow the guided steps from there.

## Notes

This app is designed to be understandable for both technical and non-technical audiences. The interface has been simplified to make the approval flow easier to follow.

Credentials used for working with the app are available in [state/user.py](state/user.py).
