# AlignmentOS — Claude Code Guide

## Before Starting Work
Check `docs/index.md` for prior decisions and research. Key docs:
- **Backlog & priorities** → `docs/backlog-consensus-matrix.md`
- **Database migration plan** → `docs/database-research.md` (MongoDB Atlas, not yet implemented)
- **Full data model** → `docs/architecture/data-model.md`
- **Deployment & secrets** → `docs/architecture/deployment.md`

When completing significant research or architectural decisions, add a doc to `docs/` and update `docs/index.md`.

## What This Is
AlignmentOS is the **interpretation layer** between tools and strategy. It reads work signals across every vendor and answers the question no tool can: **"What did this work enable?"**

Streamlit prototype — connecting individual work to commercial outcomes through a Beginning → Middle → End framework.

## Two-Sided Product

| Side | Experience | Tone |
|------|-----------|------|
| **Employee** | Recognition, visibility, motivation — passive shoutouts | "Your work matters — here's proof" |
| **Manager** | Performance intelligence, coaching signals | "Here's who's thriving, who needs support, and what to act on" |
| **Executive** | ROI, alignment, strategic decision-making | "Here's how your people drive the business — in real time" |

Momentum, engagement, and performance signals ARE the value prop for managers/execs. The employee side is recognition-first.

## Feed Item Structure

Each feed item follows this narrative format:
- WHAT YOU DID → source tool + action
- WHO IT CONNECTED → `connected_to` field (name, department, how they were unblocked)
- WHAT IT ENABLED → financial or strategic outcome, quantified where possible
- LINKED GOAL → `linked_goal` field (assigned at generation, not keyword-matched)

## Integration Vision (Roadmap Direction)

Designed to ingest signals from every tool a business uses:
- Work & Projects: Jira, Asana, Linear, GitHub
- Revenue & CRM: Salesforce, HubSpot
- Communication: Slack, Gmail
- People & HR: Workday, BambooHR, Greenhouse
- Finance: NetSuite, QuickBooks
- Marketing: Meta Ads, Google Analytics

## Run Locally
```bash
streamlit run app.py
# App: http://localhost:8501
# Secrets: .streamlit/secrets.toml (never commit)
```

## Architecture

```
app.py          — UI, design system (inline CSS), 5 tabs, Plotly network graph
agent.py        — Claude API ("Align" agent), context builders, system prompt
data_loader.py  — JSON file I/O, employee/dept lookups, build_enablement_chain
setup_wizard.py — 4-step onboarding wizard + deterministic simulated data generation
company_data/   — petfolk.json, warner_chappell_music.json (rich demo datasets)
```

### Data Flow
```
Wizard (company → depts → people) → company_data/{slug}.json → dashboard tabs → Align agent
```

### Key Schema Shapes
```python
# Employee
{"name", "role", "role_level", "department", "reports_to", "role_purpose",
 "recent_activities", "leading_indicators", "momentum", "behavior_patterns", "network_position"}

# Activity (the core unit)
{"action", "detail", "date", "source", "what_it_enabled",
 "linked_goal",    # str — assigned at generation, not keyword-matched
 "connected_to"}   # {"name", "department", "how"} — cross-functional connection

# role_level values: "ic" | "manager" | "director" | "vp" | "c-suite"

# Momentum velocity values: "accelerating" | "building" | "steady" | "emerging"
# Maps to 3 CSS states: mom-up (green), mom-mid (indigo), mom-emerging (amber)
```

## The Five Tabs
| Tab | Who Sees It | What It Shows |
|-----|-------------|---------------|
| Your Reality | Everyone | Live feed, work→outcome chain, indicators, network graph, patterns |
| Org Pulse | Everyone | Cross-company activity feed, company goals |
| Team | Managers only (`has_reports`) | Direct reports' momentum + enablement |
| Collective | Everyone | Mission, goals, financials, departments |
| Align | Everyone | Claude AI chat grounded in full company context |

## Secrets
- **Local:** `.streamlit/secrets.toml` — `ANTHROPIC_API_KEY` + `INVITE_CODES`
- **Production:** Streamlit Cloud UI → Settings → Secrets (same keys)
- **Never** put real keys in `.env.example` or any committed file

## Design System
All CSS lives in the `st.markdown("""<style>...</style>""")` block at the top of `app.py`. CSS variables:
```css
--bg, --surface, --border, --border-hi
--text, --text-2, --text-3
--accent, --accent-bg
--green, --green-bg, --amber, --amber-bg
--mono (JetBrains Mono), --sans (DM Sans)
```
Momentum pills: `.mom-up` (green/accelerating), `.mom-mid` (indigo/building+steady), `.mom-emerging` (amber/emerging).
Feed items: `.feed-connected` for cross-functional connection, `.feed-goal-tag` for linked goal.
HTML components are rendered via `st.markdown(..., unsafe_allow_html=True)`. Keep new components consistent with existing card/feed/pill patterns.

## AI Agent (Align)
- Model: `claude-sonnet-4-6`
- API key resolved via `_get_api_key()` — checks `st.secrets` first, falls back to env
- Context is built fresh per request: `build_company_context()` + `build_person_context()`
- **Two-sided behavior:** Adapts tone by `role_level` — recognition for ICs, performance intelligence for managers, strategic ROI for execs
- System prompt enforces the 7 Shared Reality principles + commercial pillars — read it before modifying

## Simulated Data Generation (`setup_wizard.py`)
- `generate_simulated_data(employee, company_data)` — deterministic, seeded by employee name
- Branches by department keyword → activity templates → indicators → momentum → patterns
- Already reads `company_data["values"]` for behavior patterns (lines ~505-520)
- Do NOT make this non-deterministic without adding async UX handling in the wizard

## Current Constraints (don't work around these without discussion)
- **No database** — flat JSON files only; all data in `company_data/`
- **No real auth** — identity is a sidebar dropdown, not a session
- **No RBAC** — tab gating is `bool(get_direct_reports(...))` only
- **No live integrations** — all activity data is simulated
- **No tests** — `data_loader.py` is the safest place to add first smoke tests

## Roadmap (priority order from consensus matrix)
- [x] C-lite — Template interpolation (company/role/goal context injected into simulation)
- [x] connected_to field — Cross-functional lens in feed items
- [x] linked_goal field — Goals assigned at generation, not keyword-matched
- [x] Momentum 3 states — accelerating (green), building/steady (indigo), emerging (amber)
- [x] Two-sided system prompt — Recognition for ICs, performance intelligence for managers/execs
- [ ] C-full — AI-powered simulated data (full Claude generation per employee)
- [ ] Reshape employee experience toward shoutout feeling
- [ ] RBAC design (foundational to delivering right experience per role)
- [ ] Enhanced Team tab — lean into performance intelligence
- [ ] G — Financial data upload (CSV, closes the narrative loop)
- [ ] E — Jira integration (first live Beginning signal)

## Invite Codes
Loaded from `st.secrets["INVITE_CODES"]` (comma-separated string). Falls back to hardcoded defaults for local dev. Change production codes in Streamlit Cloud secrets — never in source.

## Company Data
- Two demo datasets: `petfolk.json` (vet care, 201-500 employees), `warner_chappell_music.json`
- New companies created via setup wizard are saved to `company_data/{slug}.json`
- `company_data/` is committed — demo data is intentional, not sensitive

## Git / Deploy
- Remote: `https://github.com/airyhtak/alignmentos.git`
- Deploy: Streamlit Cloud (`alignmentos.streamlit.app`) — auto-deploys on push to `main`
- `.streamlit/secrets.toml` is gitignored — set secrets in Streamlit Cloud UI
