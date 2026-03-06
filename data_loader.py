# data_loader.py - AlignmentOS Company Data Loader
# Loads company configuration from JSON and provides structured access

import json
import os
from pathlib import Path

DATA_DIR = Path("company_data")

def get_available_companies():
    """List all configured companies."""
    if not DATA_DIR.exists():
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        return []
    return [f.stem for f in DATA_DIR.glob("*.json")]


def load_company(company_id):
    """Load a company configuration from JSON."""
    filepath = DATA_DIR / f"{company_id}.json"
    if not filepath.exists():
        return None
    with open(filepath, "r") as f:
        return json.load(f)


def save_company(company_id, data):
    """Save a company configuration to JSON."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    filepath = DATA_DIR / f"{company_id}.json"
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)
    return filepath


def get_employees_by_role(company_data, role_level=None):
    """Get employees, optionally filtered by role level."""
    employees = company_data.get("employees", [])
    if role_level:
        return [e for e in employees if e.get("role_level") == role_level]
    return employees


def get_employee_by_name(company_data, name):
    """Find a specific employee by name."""
    for emp in company_data.get("employees", []):
        if emp.get("name") == name:
            return emp
    return None


def get_department(company_data, dept_name):
    """Get a specific department's data."""
    for dept in company_data.get("departments", []):
        if dept.get("name") == dept_name:
            return dept
    return None


def get_employee_department(company_data, employee):
    """Get the department for a given employee."""
    dept_name = employee.get("department")
    return get_department(company_data, dept_name)


def get_employee_manager(company_data, employee):
    """Get the manager for a given employee."""
    manager_name = employee.get("reports_to")
    if manager_name:
        return get_employee_by_name(company_data, manager_name)
    return None


def get_direct_reports(company_data, employee):
    """Get direct reports for a given employee."""
    name = employee.get("name")
    return [e for e in company_data.get("employees", []) if e.get("reports_to") == name]


def get_org_tree(company_data, employee):
    """Get all employees in the reporting chain below this person, recursively."""
    result = []
    directs = get_direct_reports(company_data, employee)
    for d in directs:
        result.append(d)
        result.extend(get_org_tree(company_data, d))
    return result


def get_effective_org(company_data, employee):
    """Get the org a leader should see: direct tree if available, else all employees for top-level roles."""
    org = get_org_tree(company_data, employee)
    if org:
        return org
    # Top-level exec with no reporting chain — show all other employees
    role_level = employee.get("role_level", "ic")
    if role_level in ("c-suite", "vp", "director"):
        return [e for e in company_data.get("employees", []) if e.get("name") != employee.get("name")]
    return org


def get_team_summary(reports):
    """Aggregate momentum, indicators, and activity stats for a list of reports."""
    momentum_counts = {"accelerating": 0, "building": 0, "steady": 0, "emerging": 0}
    total_activities = 0
    indicators_on_track = 0
    indicators_total = 0
    attention_people = []
    connected_depts = set()
    goal_links = {}

    for rpt in reports:
        vel = rpt.get("momentum", {}).get("velocity", "steady").lower()
        momentum_counts[vel] = momentum_counts.get(vel, 0) + 1
        acts = rpt.get("recent_activities", [])
        total_activities += len(acts)

        for act in acts:
            ct = act.get("connected_to", {})
            if ct and ct.get("department"):
                connected_depts.add(ct["department"])
            lg = act.get("linked_goal", "")
            if lg:
                goal_links[lg] = goal_links.get(lg, 0) + 1

        for key, val in rpt.get("leading_indicators", {}).items():
            if isinstance(val, dict):
                indicators_total += 1
                current = val.get("current", 0)
                target = val.get("target", 1)
                if target and current >= target * 0.7:
                    indicators_on_track += 1

        watch = rpt.get("behavior_patterns", {}).get("areas_to_watch", [])
        needs_attention = (
            vel in ("steady", "emerging")
            and (len(watch) >= 2 or indicators_total > 0 and indicators_on_track < indicators_total * 0.5)
        )
        if needs_attention:
            reason = []
            if vel == "emerging":
                reason.append("momentum is emerging")
            if len(watch) >= 2:
                reason.append(f"{len(watch)} areas to watch")
            if indicators_total > 0 and indicators_on_track < indicators_total * 0.5:
                reason.append("indicators below target")
            attention_people.append({
                "name": rpt["name"],
                "role": rpt.get("role", ""),
                "velocity": vel,
                "reasons": reason,
                "watch": watch,
                "momentum": rpt.get("momentum", {}),
            })

    return {
        "momentum_counts": momentum_counts,
        "total_activities": total_activities,
        "indicators_on_track": indicators_on_track,
        "indicators_total": indicators_total,
        "attention": attention_people,
        "connected_depts": sorted(connected_depts),
        "goal_links": goal_links,
    }


def build_enablement_chain(company_data, employee):
    """Build the Beginning → Middle → End narrative chain for an employee."""
    dept = get_employee_department(company_data, employee)
    goals = company_data.get("company_goals", {})
    
    chain = {
        "beginning": {
            "activities": employee.get("recent_activities", []),
            "role_purpose": employee.get("role_purpose", ""),
        },
        "middle": {
            "department_focus": dept.get("strategic_focus", "") if dept else "",
            "department_kpis": dept.get("leading_indicators", []) if dept else [],
            "connections": employee.get("cross_functional_connections", []),
            "leading_indicators": employee.get("leading_indicators", {}),
        },
        "end": {
            "company_goals": goals.get("annual_priorities", []),
            "financial_targets": goals.get("financial_targets", {}),
            "department_to_goal_link": dept.get("goal_contribution", "") if dept else "",
        }
    }
    return chain


def create_empty_company_template():
    """Return an empty company template with the five foundation elements."""
    return {
        # ── Foundation Element 1: Company Identity & Goals ──
        "company_name": "",
        "industry": "",
        "company_size": "",
        "mission": "",
        "vision": "",
        "values": [],  # Each: {"name": "", "behavioral_definition": ""}
        
        "company_goals": {
            "annual_priorities": [],  # Each: {"goal": "", "metric": "", "target": ""}
            "financial_targets": {},
            "strategic_bets": [],
        },
        
        # ── Foundation Element 2: Org Structure ──
        "departments": [],
        # Each department:
        # {
        #     "name": "",
        #     "head": "",
        #     "headcount": 0,
        #     "strategic_focus": "",
        #     "leading_indicators": [],  # KPIs that sit between activity and revenue
        #     "goal_contribution": "",   # How this dept maps to company goals
        #     "dependencies": [],        # Other departments this one depends on
        # }
        
        # ── Foundation Element 3: People (Org Structure + JDs combined) ──
        "employees": [],
        # Each employee:
        # {
        #     "name": "",
        #     "role": "",
        #     "role_level": "",  # "ic", "manager", "director", "vp", "c-suite"
        #     "department": "",
        #     "reports_to": "",
        #     "role_purpose": "",  # What outcomes this role exists to produce
        #     "key_responsibilities": [],
        #     "cross_functional_connections": [],
        #     
        #     # ── Simulated Integration Data ──
        #     "recent_activities": [],
        #     # Each: {"action": "", "detail": "", "date": "", "what_it_enabled": ""}
        #     
        #     "leading_indicators": {},
        #     # Role-specific KPIs that show work flowing toward outcomes
        #     
        #     "momentum": {},
        #     # {"velocity": "", "direction": "", "pattern": ""}
        #     
        #     "behavior_patterns": {
        #         "values_aligned": [],
        #         "areas_to_watch": [],
        #     },
        #     
        #     "network_position": {
        #         "influence_description": "",
        #         "direct_reports": [],
        #         "key_collaborators": [],
        #     },
        # }
        
        # ── Metadata ──
        "current_quarter": "",
        "last_updated": "",
    }
