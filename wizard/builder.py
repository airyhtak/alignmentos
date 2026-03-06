# wizard/builder.py
# Data assembly and auth primitives for the setup wizard.
# When RBAC arrives, check_invite_code / _load_invite_codes are the starting point.

import re
import streamlit as st
from datetime import datetime
from data_loader import save_company
from wizard.simulation import generate_simulated_data, enhance_with_ai


# ── Invite codes — loaded from st.secrets in production, fallback for local dev ──
def _load_invite_codes():
    try:
        raw = st.secrets.get("INVITE_CODES", "")
        if raw:
            return {c.strip().upper() for c in raw.split(",") if c.strip()}
    except Exception:
        pass
    return {"ALIGNME2026", "SHAREDREALITY", "DESIGNPARTNER"}

VALID_INVITE_CODES = _load_invite_codes()


def check_invite_code(code):
    return code.strip().upper() in VALID_INVITE_CODES


def slugify(name):
    return re.sub(r'[^a-z0-9]+', '_', name.lower()).strip('_')


def build_company_json(wizard_data, on_progress=None):
    """Convert wizard form data into the full company JSON config.
    on_progress(step, total, message) is called during generation if provided."""

    financials = {}
    fin = wizard_data.get("financials", {})
    for key, str_key in [("current_arr", "current_arr_str"), ("target_arr", "target_arr_str")]:
        val = fin.get(str_key, "").strip()
        if val:
            try:
                financials[key] = int(float(val))
            except ValueError:
                pass
    for key, str_key in [("gross_margin", "gross_margin_str"), ("current_nrr", "nrr_str")]:
        val = fin.get(str_key, "").strip()
        if val:
            try:
                financials[key] = float(val)
            except ValueError:
                pass

    company_data = {
        "company_name": wizard_data["company_name"],
        "industry": wizard_data["industry"],
        "company_size": wizard_data["company_size"],
        "mission": wizard_data["mission"],
        "vision": wizard_data.get("vision", ""),
        "values": wizard_data.get("values", []),
        "company_goals": {
            "annual_priorities": [g for g in wizard_data.get("goals", []) if g.get("goal")],
            "financial_targets": financials,
            "strategic_bets": wizard_data.get("strategic_bets", []),
        },
        "departments": [],
        "employees": [],
        "current_quarter": wizard_data.get("current_quarter", "Q1 2026"),
        "last_updated": datetime.now().isoformat(),
    }

    for dept in wizard_data.get("departments", []):
        if not dept.get("name"):
            continue
        try:
            hc = int(dept.get("headcount", 0))
        except (ValueError, TypeError):
            hc = 0
        company_data["departments"].append({
            "name": dept["name"],
            "head": dept.get("head", ""),
            "headcount": hc,
            "strategic_focus": dept.get("strategic_focus", ""),
            "leading_indicators": [],
            "goal_contribution": dept.get("goal_contribution", ""),
            "dependencies": [],
        })

    for emp in wizard_data.get("employees", []):
        company_data["employees"].append({
            "name": emp["name"],
            "role": emp["role"],
            "role_level": emp.get("role_level", "ic"),
            "department": emp.get("department", ""),
            "reports_to": emp.get("reports_to", ""),
            "role_purpose": emp.get("role_purpose", ""),
            "key_responsibilities": emp.get("key_responsibilities", []),
        })

    # Generate simulated data after all employees added (network connections need full list)
    emp_count = len(company_data["employees"])
    total_steps = emp_count * 2  # deterministic + AI pass

    for i, emp in enumerate(company_data["employees"]):
        if on_progress:
            on_progress(i + 1, total_steps, f"Generating data for {emp['name']}...")
        generate_simulated_data(emp, company_data)

    # AI enhancement pass — enriches narratives with industry-specific language
    # Falls back silently to template data if no API key or on failure
    ai_enhanced = 0
    for i, emp in enumerate(company_data["employees"]):
        if on_progress:
            on_progress(emp_count + i + 1, total_steps, f"Enhancing {emp['name']} with AI...")
        if enhance_with_ai(emp, company_data):
            ai_enhanced += 1
    company_data["_ai_enhanced"] = ai_enhanced

    return company_data
