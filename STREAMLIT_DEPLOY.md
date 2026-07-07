# Streamlit Deployment

This repository includes `streamlit_app.py`, a hosted demo version of Portfolio Diligence Copilot that runs fully in memory.

## Deploy on Streamlit Community Cloud

1. Push this repository to GitHub.
2. Go to https://share.streamlit.io.
3. Click **New app**.
4. Select repository: `sajansshergill/portfolio-diligence-copilot`.
5. Select branch: `main`.
6. Main file path: `streamlit_app.py`.
7. Click **Deploy**.

## Notes

- The Streamlit app does not require Postgres, Docker, Temporal, or API keys.
- It accepts `.txt`, `.md`, and `.csv` uploads and runs the offline diligence pipeline in memory.
- The full FastAPI, Next.js, Postgres, Temporal, MCP, and dbt stack remains available for local development.
