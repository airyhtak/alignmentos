# Backlog Consensus Matrix — AlignmentOS

**Date:** 2026-03-05
**Method:** 4 agents evaluated 10 backlog items in parallel (Sprint Prioritizer · Competitive Analyst · Tech Lead · UX Researcher)
**Goal:** Maximum value, minimal effort — design partner readiness

---

## Consensus Matrix

| Item | Sprint | Competitive | Tech Lead | UX | Avg | Verdict |
|------|--------|-------------|-----------|-----|-----|---------|
| A. Fix model ID | 10 | 9 | 10 | 2 | 7.8 | **DO NOW** ✅ Done |
| J. Deploy Streamlit Cloud | 9 | 9 | 9 | 9 | 9.0 | **DO NOW** ✅ Done |
| B. Values in wizard | 9 | 8 | 8 | 9 | 8.5 | **DO NOW** ✅ Done |
| C. AI simulated data | 7 | 9 | 6 | 8 | 7.5 | **QUEUE** |
| G. Financial upload | 5 | 7 | 6 | 7 | 6.25 | **QUEUE** |
| D. RBAC | 6 | 6 | 5 | 5 | 5.5 | **DEFER** |
| E. Jira integration | 4 | 7 | 4 | 6 | 5.25 | **DEFER** |
| I. Mgmt diagnostics | 6 | 8 | 3 | 4 | 5.25 | **DISCUSS** |
| H. Top 1% view | 6 | 7 | 2 | 4 | 4.75 | **DEFER** |
| F. Google Analytics | 3 | 8 | 3 | 4 | 4.5 | **DISCUSS** |

---

## Execution Order

```
Week 1 (done):  A (model ID) → J (deploy) → B (values in wizard)
Next:           C-lite (template interpolation) → G (financial upload) → MongoDB migration
Q2:             D (RBAC) → E (Jira) → C-full (AI generation) → I (mgmt diagnostics)
Later:          F (Google Analytics) → H (Top 1% view)
```

---

## Key Disagreements & Resolutions

**A (model ID) — UX rated 2, everyone else 10:**
UX: "already functional." Others: will break on deprecation. Fix wins — 5-minute zero-risk change.

**C (AI simulated data) — split PRIORITY/DEFER:**
Competitive + UX want it now (demo quality). Sprint + Tech say wait (async complexity, API cost per setup).
Resolution: **cheap middle path** — inject company name, role, and first goal into existing templates via string interpolation. 80% of UX value at 5% complexity. Full Claude generation later.

**F (Google Analytics) — Competitive rates 8, everyone else 3-4:**
Competitive: right Middle-layer signal strategically. Sprint/Tech: disproportionate implementation cost now.
Resolution: Google Analytics is the right first Middle signal, but Q2 after design partners validate the concept.

**I (Management diagnostics) — Competitive 8 vs Tech Lead 3:**
Competitive: "the enterprise economic buyer's view." Tech Lead: "flat JSON + no audit trail = legal/fairness risk."
Resolution: design the concept for demos now, build real logic after RBAC and persistence layer exist.

---

## Bonus Findings (UX + Tech Lead)

- **"Who are you?" dropdown** is a prototype artifact — URL query params would preserve "made for me" feeling
- **`setup_wizard.py` is 817 lines** — extract `generate_simulated_data()` into its own module before adding C or more wizard steps
- **Invite codes were hardcoded in source** — moved to `st.secrets` as part of deploy prep ✅
- **API key was in `.env.example`** — removed and rotated ✅
