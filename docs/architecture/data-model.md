# Data Model Reference

**Storage:** Flat JSON files in `company_data/` (current) → MongoDB Atlas (planned, see [database-research.md](../database-research.md))

---

## Top-Level Company Document

```json
{
  "company_name": "string",
  "industry": "string",
  "company_size": "1-50 | 51-200 | 201-500 | 501-1000 | 1000+",
  "mission": "string",
  "vision": "string",
  "current_quarter": "Q1 2026",
  "last_updated": "ISO timestamp",

  "values": [
    { "name": "string", "behavioral_definition": "string" }
  ],

  "company_goals": {
    "annual_priorities": [
      { "goal": "string", "metric": "string", "target": "string" }
    ],
    "financial_targets": {
      "current_arr": 5000000,
      "target_arr": 10000000,
      "gross_margin": 72.0,
      "current_nrr": 115.0,
      "burn_multiple": 1.4
    },
    "strategic_bets": ["string"]
  },

  "departments": [ /* see Department shape */ ],
  "employees": [ /* see Employee shape */ ]
}
```

---

## Department

```json
{
  "name": "Engineering",
  "head": "string",
  "headcount": 25,
  "strategic_focus": "string — what this dept is focused on this period",
  "goal_contribution": "string — how this dept maps to company goals",
  "leading_indicators": ["string"],
  "dependencies": ["string — other dept names"]
}
```

---

## Employee

```json
{
  "name": "string",
  "role": "string",
  "role_level": "ic | manager | director | vp | c-suite",
  "department": "string — must match a department name",
  "reports_to": "string — employee name or empty string",
  "role_purpose": "string — what outcomes this role exists to produce",
  "key_responsibilities": ["string"],
  "cross_functional_connections": ["string — dept names"],

  "recent_activities": [ /* see Activity shape */ ],
  "leading_indicators": { /* see Indicators shape */ },
  "momentum": { /* see Momentum shape */ },
  "behavior_patterns": { /* see Patterns shape */ },
  "network_position": { /* see Network shape */ }
}
```

---

## Activity (the core narrative unit)

```json
{
  "action": "string — short verb phrase, e.g. 'Shipped feature update'",
  "detail": "string — one sentence of context",
  "date": "YYYY-MM-DD",
  "source": "string — tool name: jira | github | salesforce | slack | google analytics | ...",
  "what_it_enabled": "string — the enablement narrative (Beginning → End connection)"
}
```

Source icons are mapped in `app.py → SOURCE_ICONS`.

---

## Leading Indicators

```json
{
  "indicator_name": {
    "current": "value",
    "target": "value",
    "trend": "↑ improving | → steady | ↓ slowing",
    "unit": "string — pts/sprint | % | days | /month | x"
  }
}
```

---

## Momentum

```json
{
  "velocity": "accelerating | building | steady | emerging",
  "direction": "string — one sentence describing trajectory",
  "pattern": "string — behavioral pattern description"
}
```

---

## Behavior Patterns

```json
{
  "values_aligned": ["string — e.g. 'Innovation: consistently proposes new approaches'"],
  "areas_to_watch": ["string — e.g. 'Documentation could help scale knowledge'"]
}
```

`values_aligned` entries reference company values by name. The `generate_simulated_data()` function in `setup_wizard.py` populates these from `company_data["values"]`.

---

## Network Position

```json
{
  "influence_description": "string",
  "direct_reports": ["string — employee names"],
  "key_collaborators": ["string — employee names with optional role context"]
}
```

---

## Narrative Framework Mapping

Every field maps to one of three narrative layers:

| Layer | Fields |
|-------|--------|
| **Beginning** (what you did) | `recent_activities`, `key_responsibilities`, `role_purpose` |
| **Middle** (how it connects) | `leading_indicators`, `cross_functional_connections`, `network_position`, `department.strategic_focus` |
| **End** (what it enabled) | `activity.what_it_enabled`, `department.goal_contribution`, `company_goals.annual_priorities` |
