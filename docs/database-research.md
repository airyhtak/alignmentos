# Database Research — Replacing Flat JSON Storage

**Decision date:** 2026-03-05
**Status:** Decided — MongoDB Atlas. Not yet implemented.
**Next step:** Create Atlas M0 cluster, paste connection string, implement `data_loader.py` migration.

---

## Decision: MongoDB Atlas (M0 free tier)

### Option Matrix

| Option | Fit (1-10) | Free Tier | Complexity | Verdict |
|--------|-----------|-----------|------------|---------|
| **MongoDB Atlas** | **9** | 512 MB, never pauses | Low — pymongo mirrors json.load/dump | **Selected** |
| Supabase | 7 | 500 MB, pauses after 7 days | Medium — relational schema redesign | Use instead if RBAC is next priority |
| Firebase Firestore | 6 | 1 GB, 50K reads/day | Low-Medium | GCP auth friction on Streamlit Cloud |
| Neon (Postgres) | 5 | 0.5 GB | Medium-High — full normalization required | Too much overhead at prototype stage |
| Airtable | 4 | 1,000 records/base | Low | Record limit too low |
| PocketBase | 2 | Self-hosted only | High on Streamlit Cloud | Eliminated — requires external VPS |

### Why Atlas

- Current data model is already a MongoDB document — `petfolk.json` maps 1:1 to a Mongo document
- Zero schema redesign, zero migrations
- Only 4 functions change in `data_loader.py` (~20 lines); all other files untouched
- Free M0 tier never pauses (Supabase pauses after 7 inactive days — bad for pilot)
- Schema accommodates full roadmap (live integrations, RBAC) without redesign until real-user scale
- Streamlit Cloud connection via URI secret — same pattern as `ANTHROPIC_API_KEY`

---

## Migration Plan

### 1. Dependency
Add to `requirements.txt`:
```
pymongo[srv]>=4.6.0
```

### 2. Secrets
Add to `.streamlit/secrets.toml` (local) and Streamlit Cloud secrets (production):
```toml
MONGODB_URI = "mongodb+srv://user:pass@cluster.mongodb.net/?retryWrites=true&w=majority"
```

### 3. data_loader.py — Only These 4 Functions Change

```python
import os
import streamlit as st
from pymongo import MongoClient

def _get_db():
    """Get MongoDB handle, cached per session to avoid connection pool issues."""
    if "mongo_client" not in st.session_state:
        uri = st.secrets.get("MONGODB_URI") or os.environ.get("MONGODB_URI")
        st.session_state.mongo_client = MongoClient(uri)
    return st.session_state.mongo_client["alignmentos"]

def get_available_companies():
    return [doc["_id"] for doc in _get_db().companies.find({}, {"_id": 1})]

def load_company(company_id):
    doc = _get_db().companies.find_one({"_id": company_id})
    if doc:
        doc.pop("_id", None)  # strip Mongo _id so callers get clean dict
    return doc

def save_company(company_id, data):
    _get_db().companies.replace_one(
        {"_id": company_id},
        {**data, "_id": company_id},
        upsert=True
    )
    return company_id
```

All other functions (`get_employee_by_name`, `get_direct_reports`, `build_enablement_chain`, etc.) are unchanged — they operate on the Python dict returned by `load_company`.

### 4. Migrate Existing Data
Run once after Atlas cluster is created:
```python
from data_loader import save_company, load_company  # old JSON version
import json
from pathlib import Path

for f in Path("company_data").glob("*.json"):
    data = json.loads(f.read_text())
    save_company(f.stem, data)  # new Atlas version
```

---

## Atlas Setup Gotchas

- **IP Whitelist:** Set to `0.0.0.0/0` in Atlas Network Access — required for Streamlit Cloud (no fixed IPs)
- **Session state caching:** Use `st.session_state` for the MongoClient, NOT a module-level singleton — Streamlit's multi-threaded model causes connection errors with singletons
- **`_id` field:** Use `company_id` (the slug, e.g. `"petfolk"`) as `_id` — direct index hit, replaces the filename as natural key
- **16 MB BSON limit:** Not a concern until thousands of employees per company document

---

## Schema Evolution Path (Roadmap)

| Trigger | Change |
|---------|--------|
| **RBAC (roadmap D)** | Add `users` collection: `{_id: email, company_id, role_level, employee_name}`. Company document unchanged. |
| **Live Jira data (roadmap E)** | `recent_activities` arrays grow — extract to separate `activities` collection with index on `(company_id, employee_name, date)` when employees accumulate 500+ activities |
| **Financial uploads (roadmap G)** | Add `financial_uploads` array to company document — no schema change needed |
