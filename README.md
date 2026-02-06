# HCLTech License Analysis AI Agent (Streamlit)

This converts the original static HTML/JS frontend into a Streamlit app suitable for **Streamlit Community Cloud**.

## Files
- `app.py` — Streamlit UI + chat backend call
- `requirements.txt` — Python dependencies
- `.streamlit/config.toml` — theme defaults
- `.streamlit/secrets.toml.example` — copy into Streamlit Cloud Secrets
- `assets/hcltech_logo.png` — **add your official HCLTech logo here** (PNG recommended)

## Run locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy to Streamlit Cloud
1. Push this folder to GitHub.
2. Create a new Streamlit app pointing to `app.py`.
3. In **App → Settings → Secrets**, paste the contents of `.streamlit/secrets.toml.example` and fill in your API key.
4. (Optional) Add `assets/hcltech_logo.png` to your repo for the logo.

## Security note
Do **not** hardcode API keys in source files. Use Streamlit Secrets (or env vars) instead.
