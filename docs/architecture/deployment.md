# Deployment Guide

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Configure secrets
cp .streamlit/secrets.toml.example .streamlit/secrets.toml  # if exists
# Or create .streamlit/secrets.toml manually (see Secrets section)

# Run
streamlit run app.py
# → http://localhost:8501
```

## Secrets

**Never commit secrets.** `.streamlit/secrets.toml` is in `.gitignore`.

### Local: `.streamlit/secrets.toml`
```toml
ANTHROPIC_API_KEY = "sk-ant-..."
INVITE_CODES = "ALIGNME2026,SHAREDREALITY,DESIGNPARTNER"
# MONGODB_URI = "mongodb+srv://..."  # add when Atlas migration is done
```

### Production: Streamlit Cloud UI
Settings → Secrets — same keys as above.

---

## Streamlit Cloud

- **Repo:** `https://github.com/airyhtak/alignmentos`
- **Branch:** `main`
- **Main file:** `app.py`
- **URL:** `alignmentos.streamlit.app`
- **Auto-deploys** on every push to `main`

### First-time setup
1. [share.streamlit.io](https://share.streamlit.io) → Create app
2. Connect `airyhtak/alignmentos` · branch `main` · file `app.py`
3. Advanced settings → paste secrets (see above)
4. Deploy

---

## Invite Codes

Loaded from `st.secrets["INVITE_CODES"]` (comma-separated string) in `setup_wizard.py`.
Falls back to hardcoded defaults for local dev without a secrets file.
Change production codes in Streamlit Cloud secrets only — never in source.

**Current codes:** `ALIGNME2026`, `SHAREDREALITY`, `DESIGNPARTNER`

---

## API Key Management

- Key is read via `_get_api_key()` in `agent.py` — checks `st.secrets` first, falls back to env
- **Rotate immediately** if a key is ever committed to git history
- Rotation: [console.anthropic.com/settings/keys](https://console.anthropic.com/settings/keys)

---

## Git Flow

```bash
# All work on main (prototype stage — no branch strategy yet)
git add <files>
git commit -m "description"
git push origin main
# Streamlit Cloud auto-deploys within ~2 minutes
```

---

## Pending: MongoDB Atlas Setup

See [database-research.md](../database-research.md) for full migration plan.

When ready:
1. Create free M0 cluster at [cloud.mongodb.com](https://cloud.mongodb.com)
2. Network Access → Add IP → `0.0.0.0/0` (required for Streamlit Cloud)
3. Create database user, copy SRV connection string
4. Add `MONGODB_URI` to `.streamlit/secrets.toml` and Streamlit Cloud secrets
5. Add `pymongo[srv]>=4.6.0` to `requirements.txt`
6. Swap 4 functions in `data_loader.py` (see database-research.md)
7. Run one-time migration script to move existing JSON files into Atlas
