# AlignmentOS — Shared Reality Platform

See what your work enables. AlignmentOS creates Shared Reality — showing how individual work connects to business outcomes through living narratives, not static metrics.

## Quick Start

```bash
pip install -r requirements.txt
```

Create a `.env` file:
```
ANTHROPIC_API_KEY=your_key_here
```

Run:
```bash
streamlit run app.py
```

## How It Works

**First-time users** are guided through a setup wizard:

1. **Enter an invite code** — controlled access for design partners
2. **Company basics** — name, industry, mission, goals
3. **Departments** — org structure with strategic focus areas
4. **People** — add via CSV upload or manual entry
5. **Launch** — AlignmentOS generates realistic simulated activity data

Once setup completes, users land in the full dashboard with enablement stories, momentum indicators, network visualization, and the Align AI agent.

## Invite Codes

Default codes (update in `setup_wizard.py`):
- `ALIGNME2026`
- `SHAREDREALITY`
- `DESIGNPARTNER`

## CSV Import Format

Upload people via CSV with these columns (only **name**, **role**, **department** required):

```
name,role,department,reports_to,role_level,role_purpose
Jane Smith,Senior Engineer,Engineering,CTO,ic,Build and ship core product features
```

**role_level** values: `ic`, `manager`, `director`, `vp`, `c-suite`

## Architecture

```
User enters invite code
        ↓
Setup Wizard (company → departments → people)
        ↓
Simulated data generated (activities, momentum, patterns)
        ↓
Company JSON saved to company_data/
        ↓
Dashboard loads with full Shared Reality experience
        ↓
Align AI agent builds context from company data
```

### Files

| File | Purpose |
|---|---|
| `app.py` | Main dashboard — views, design system, routing |
| `setup_wizard.py` | Onboarding wizard + invite code auth |
| `agent.py` | Align AI agent (Claude-powered, company-agnostic) |
| `data_loader.py` | JSON config loader + enablement chain builder |
| `company_data/` | Generated company configs (JSON) |

## Deployment (Streamlit Cloud)

1. Push to GitHub
2. Connect repo to [share.streamlit.io](https://share.streamlit.io)
3. Add `ANTHROPIC_API_KEY` in Streamlit secrets
4. Share the URL with design partners + invite code

## What's Next

- [ ] Live integrations (Salesforce, Jira, Slack) replace simulated data
- [ ] Company values entry in setup wizard
- [ ] Financial data upload (quarterly actuals)
- [ ] Role-based access controls
- [ ] Top 1% performance view (exec-only)
- [ ] Management diagnostics (exec-only)
