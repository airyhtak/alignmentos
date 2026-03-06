# wizard/simulation.py
# Deterministic simulated data generation for new company setups.
# Isolated here so the AI-generation upgrade (roadmap item C) only touches this file.

import random
import hashlib
from datetime import datetime, timedelta


def _interpolate(template, ctx):
    """Interpolate {placeholders} in a template string using ctx dict. Missing keys left as-is."""
    try:
        return template.format_map(ctx)
    except (KeyError, ValueError):
        return template


def _pick_source(category, rng):
    """Pick a realistic source tool based on department category."""
    sources = {
        "engineering": ["GitHub", "Jira", "Slack", "Confluence"],
        "product": ["Jira", "Google Docs", "Zoom", "Slack"],
        "sales": ["Salesforce", "Slack", "DocuSign", "Zoom"],
        "marketing": ["Meta Ads", "Google Analytics", "Slack", "Google Docs"],
        "customer_success": ["Salesforce", "Zoom", "Slack", "Google Sheets"],
        "operations": ["Google Sheets", "Slack", "Jira", "Zoom"],
        "hr": ["HRIS", "Workable", "Google Docs", "Zoom"],
        "finance": ["NetSuite", "Google Sheets", "Google Slides", "Slack"],
    }
    pool = sources.get(category, ["Slack", "Google Docs", "Zoom"])
    return rng.choice(pool)


def generate_simulated_data(employee, company_data):
    """Generate realistic simulated activity data for an employee using deterministic logic.
    This runs locally -- no AI call needed. The AI agent (Align) handles the narrative later."""

    # Seed random based on employee name for consistency
    seed = int(hashlib.md5(employee["name"].encode()).hexdigest()[:8], 16)
    rng = random.Random(seed)

    dept_name = employee.get("department", "")
    role_level = employee.get("role_level", "ic")
    company_name = company_data.get("company_name", "the company")

    # Build interpolation context
    goals = company_data.get("company_goals", {}).get("annual_priorities", [])
    goal_names = [g.get("goal", "") for g in goals]
    dept_obj = None
    for d in company_data.get("departments", []):
        if d.get("name") == dept_name:
            dept_obj = d
            break

    ctx = {
        "company": company_name,
        "department": dept_name,
        "role": employee.get("role", ""),
        "role_purpose": employee.get("role_purpose", ""),
        "dept_focus": dept_obj.get("strategic_focus", "") if dept_obj else "",
        "dept_contribution": dept_obj.get("goal_contribution", "") if dept_obj else "",
        "goal_1": goal_names[0] if len(goal_names) > 0 else "company growth targets",
        "goal_2": goal_names[1] if len(goal_names) > 1 else "operational excellence",
    }

    # All employees for cross-functional connections
    all_employees = company_data.get("employees", [])
    other_dept_people = [e for e in all_employees if e.get("department") != dept_name and e["name"] != employee["name"]]

    # ── Activity templates by department type ──
    # Each template now includes connected_to hints and linked_goal index
    activity_templates = {
        "engineering": [
            {"action": "Shipped feature update", "detail": "Deployed improvements to core platform module for {company}", "what_it_enabled": "Unblocked downstream teams on {dept_focus} — accelerating progress toward {goal_1}", "connected_to_dept": "product", "goal_idx": 0},
            {"action": "Resolved critical bug", "detail": "Fixed data pipeline issue affecting {department} reports", "what_it_enabled": "Restored data accuracy for customer-facing systems — protects {goal_2}", "connected_to_dept": "customer_success", "goal_idx": 1},
            {"action": "Led architecture review", "detail": "Evaluated system design to support {company}'s scaling needs", "what_it_enabled": "Created technical foundation for growth — directly enables {goal_1}", "connected_to_dept": "operations", "goal_idx": 0},
            {"action": "Improved CI/CD pipeline", "detail": "Reduced deploy time and added automated testing for {department}", "what_it_enabled": "Team ships 40% faster with fewer rollbacks — more capacity toward {dept_focus}", "connected_to_dept": "engineering", "goal_idx": 0},
            {"action": "Mentored junior developer", "detail": "Paired on complex integration work supporting {dept_focus}", "what_it_enabled": "Junior dev now independently handling integration tickets — team capacity increased", "connected_to_dept": "hr", "goal_idx": 1},
        ],
        "product": [
            {"action": "Published product requirements", "detail": "Defined scope and success metrics for {company}'s next release", "what_it_enabled": "Engineering started sprint with clear direction — aligned to {goal_1}", "connected_to_dept": "engineering", "goal_idx": 0},
            {"action": "Ran customer discovery calls", "detail": "Interviewed 8 customers on workflow pain points at {company}", "what_it_enabled": "Identified top 3 friction points driving churn — directly impacts {goal_2}", "connected_to_dept": "customer_success", "goal_idx": 1},
            {"action": "Prioritized Q2 roadmap", "detail": "Aligned features to {company}'s strategic bets with stakeholder input", "what_it_enabled": "Cross-functional teams aligned on what to build next — drives {dept_contribution}", "connected_to_dept": "sales", "goal_idx": 0},
            {"action": "Analyzed feature adoption", "detail": "Deep dive on usage patterns for {company}'s recent release", "what_it_enabled": "Surfaced onboarding gap affecting 60% of users — fix accelerates {goal_1}", "connected_to_dept": "marketing", "goal_idx": 0},
        ],
        "sales": [
            {"action": "Closed enterprise deal", "detail": "Navigated multi-stakeholder procurement at target account for {company}", "what_it_enabled": "Added $120K ARR — validates {company}'s enterprise positioning toward {goal_1}", "connected_to_dept": "finance", "goal_idx": 0},
            {"action": "Built partner channel pipeline", "detail": "Established relationships with 3 integration partners for {company}", "what_it_enabled": "Created referral pipeline worth estimated $200K — accelerates {goal_1}", "connected_to_dept": "marketing", "goal_idx": 0},
            {"action": "Refined sales playbook", "detail": "Documented winning patterns from top deals at {company}", "what_it_enabled": "New reps ramp 2 weeks faster — scales {department}'s capacity toward {goal_1}", "connected_to_dept": "hr", "goal_idx": 0},
            {"action": "Led quarterly business review", "detail": "Presented pipeline health and forecast to {company} leadership", "what_it_enabled": "Aligned leadership on gap between pipeline and target — informed {goal_2} strategy", "connected_to_dept": "finance", "goal_idx": 1},
        ],
        "marketing": [
            {"action": "Launched content campaign", "detail": "Published thought leadership series for {company} across channels", "what_it_enabled": "Generated 340 MQLs (2x previous campaign) — fuels pipeline toward {goal_1}", "connected_to_dept": "sales", "goal_idx": 0},
            {"action": "Redesigned landing pages", "detail": "A/B tested messaging and conversion flows for {company}", "what_it_enabled": "Improved trial conversion from 3.2% to 5.1% — directly accelerates {goal_1}", "connected_to_dept": "product", "goal_idx": 0},
            {"action": "Organized industry event", "detail": "Coordinated speaker lineup and attendee experience for {company}", "what_it_enabled": "Built brand presence with 200+ target-persona attendees — supports {goal_2}", "connected_to_dept": "sales", "goal_idx": 1},
        ],
        "customer_success": [
            {"action": "Prevented at-risk churn", "detail": "Identified usage drop and intervened with executive sponsor at {company} client", "what_it_enabled": "Retained $85K ARR account — protects revenue toward {goal_1}", "connected_to_dept": "sales", "goal_idx": 0},
            {"action": "Built onboarding playbook", "detail": "Standardized first-90-days experience for new {company} customers", "what_it_enabled": "Time-to-value reduced from 45 to 28 days — improves retention metrics for {goal_2}", "connected_to_dept": "product", "goal_idx": 1},
            {"action": "Led quarterly business review", "detail": "Presented ROI analysis and expansion opportunities to {company} client", "what_it_enabled": "Client approved upsell — 40% account expansion driving {goal_1}", "connected_to_dept": "sales", "goal_idx": 0},
        ],
        "operations": [
            {"action": "Streamlined vendor procurement", "detail": "Consolidated {company}'s vendor stack and renegotiated contracts", "what_it_enabled": "Reduced operational costs by 15% annually — frees budget toward {goal_1}", "connected_to_dept": "finance", "goal_idx": 0},
            {"action": "Implemented new workflow system", "detail": "Rolled out automation for recurring {department} processes at {company}", "what_it_enabled": "Team reclaimed 10 hours/week for strategic work on {dept_focus}", "connected_to_dept": "engineering", "goal_idx": 1},
        ],
        "hr": [
            {"action": "Launched performance framework", "detail": "Rolled out updated review cycle with manager training at {company}", "what_it_enabled": "Managers have consistent lens for growth conversations — supports {goal_2}", "connected_to_dept": "operations", "goal_idx": 1},
            {"action": "Filled critical roles", "detail": "Closed 4 priority hires across {company}'s key departments", "what_it_enabled": "Teams at full capacity for execution — directly enables {goal_1}", "connected_to_dept": "engineering", "goal_idx": 0},
            {"action": "Ran engagement survey", "detail": "Designed and deployed org-wide pulse check at {company}", "what_it_enabled": "Surfaced 3 retention risks leadership can address now — protects {goal_2}", "connected_to_dept": "operations", "goal_idx": 1},
        ],
        "finance": [
            {"action": "Delivered board financial package", "detail": "Consolidated {company} actuals, forecast, and scenario analysis", "what_it_enabled": "Board approved runway extension strategy — secures execution capacity for {goal_1}", "connected_to_dept": "operations", "goal_idx": 0},
            {"action": "Built department budgets", "detail": "Partnered with {company} dept heads on resource allocation", "what_it_enabled": "Teams have spending clarity for next two quarters — aligned to {goal_1}", "connected_to_dept": "operations", "goal_idx": 0},
        ],
    }

    # Match department to template category
    dept_lower = dept_name.lower()
    category = "operations"  # default
    for key in activity_templates:
        if key in dept_lower or dept_lower in key:
            category = key
            break
    if any(x in dept_lower for x in ["eng", "dev", "tech", "platform"]):
        category = "engineering"
    elif any(x in dept_lower for x in ["product", "pm"]):
        category = "product"
    elif any(x in dept_lower for x in ["sale", "revenue", "business dev"]):
        category = "sales"
    elif any(x in dept_lower for x in ["market", "growth", "brand"]):
        category = "marketing"
    elif any(x in dept_lower for x in ["success", "support", "cx"]):
        category = "customer_success"
    elif any(x in dept_lower for x in ["people", "hr", "human", "talent"]):
        category = "hr"
    elif any(x in dept_lower for x in ["finance", "accounting", "fp&a"]):
        category = "finance"

    templates = activity_templates.get(category, activity_templates["operations"])
    selected = rng.sample(templates, min(3, len(templates)))

    today = datetime.now()
    activities = []
    for i, tmpl in enumerate(selected):
        delta = timedelta(days=rng.randint(1, 14) + (i * 5))
        act = {
            "action": _interpolate(tmpl["action"], ctx),
            "detail": _interpolate(tmpl["detail"], ctx),
            "date": (today - delta).strftime("%Y-%m-%d"),
            "source": _pick_source(category, rng),
            "what_it_enabled": _interpolate(tmpl["what_it_enabled"], ctx),
        }

        # Assign linked_goal during generation (not keyword matching at render time)
        goal_idx = tmpl.get("goal_idx", 0)
        if goal_idx < len(goal_names):
            act["linked_goal"] = goal_names[goal_idx]

        # Assign connected_to — pick a real person from the connected department
        target_dept = tmpl.get("connected_to_dept", "")
        candidates = [e for e in other_dept_people if target_dept.lower() in e.get("department", "").lower()]
        if not candidates:
            candidates = other_dept_people
        if candidates:
            connected_person = rng.choice(candidates)
            act["connected_to"] = {
                "name": connected_person["name"],
                "department": connected_person.get("department", ""),
                "how": f"Unblocked {connected_person.get('department', 'their team')}'s work on {ctx.get('dept_focus', 'key priorities')}",
            }

        activities.append(act)

    # ── Leading indicators ──
    indicator_templates = {
        "engineering": {
            "sprint_velocity": {"current": rng.randint(18, 35), "target": 30, "trend": rng.choice(["up improving", "steady"]), "unit": "pts/sprint"},
            "code_review_turnaround": {"current": round(rng.uniform(2, 8), 1), "target": 4, "trend": rng.choice(["up improving", "steady", "slowing"]), "unit": "hours"},
        },
        "product": {
            "feature_adoption": {"current": rng.randint(25, 70), "target": 60, "trend": "up improving", "unit": "%"},
            "customer_interviews": {"current": rng.randint(4, 12), "target": 10, "trend": "steady", "unit": "/month"},
        },
        "sales": {
            "pipeline_coverage": {"current": round(rng.uniform(2.0, 4.5), 1), "target": 3.0, "trend": "up growing", "unit": "x"},
            "win_rate": {"current": rng.randint(20, 40), "target": 30, "trend": rng.choice(["up improving", "steady"]), "unit": "%"},
        },
        "marketing": {
            "mqls_generated": {"current": rng.randint(150, 500), "target": 350, "trend": "up growing", "unit": "/month"},
            "content_engagement": {"current": round(rng.uniform(2, 8), 1), "target": 5, "trend": "steady", "unit": "% CTR"},
        },
        "customer_success": {
            "nps_score": {"current": rng.randint(35, 65), "target": 50, "trend": "up improving", "unit": ""},
            "time_to_value": {"current": rng.randint(20, 50), "target": 30, "trend": "down improving", "unit": "days"},
        },
    }
    indicators = indicator_templates.get(category, {"throughput": {"current": rng.randint(60, 95), "target": 85, "trend": "steady", "unit": "%"}})

    # ── Momentum (3 states: accelerating, building/steady, emerging) ──
    velocities = ["accelerating", "building", "steady", "emerging"]
    velocity = rng.choice(velocities)
    directions = {
        "accelerating": f"Strong forward momentum — work is compounding across {company_name}",
        "building": f"Momentum is building — recent contributions creating ripple effects at {company_name}",
        "steady": f"Consistent contribution — maintaining velocity on {ctx.get('dept_focus', 'key deliverables')}",
        "emerging": f"New patterns forming — early signals of cross-team impact at {company_name}",
    }
    patterns = {
        "accelerating": "Consistent high-impact delivery with increasing cross-functional reach",
        "building": "Steady delivery cadence with growing network connections",
        "steady": "Reliable output maintaining team velocity",
        "emerging": "Shifting from individual delivery to broader organizational impact",
    }
    momentum = {"velocity": velocity, "direction": directions[velocity], "pattern": patterns[velocity]}

    # ── Behavior patterns ──
    company_values = [v.get("name", "") for v in company_data.get("values", [])]
    values_aligned = []
    if company_values:
        chosen = rng.sample(company_values, min(2, len(company_values)))
        value_behaviors = {
            "ic": [
                "{v}: Consistently demonstrates this in daily work and team interactions",
                "{v}: Visible in how they approach problems and collaborate across {company}",
            ],
            "manager": [
                "{v}: Models this for the team and reinforces it in 1:1s and retros",
                "{v}: Creates team norms that reflect this value in practice at {company}",
            ],
        }
        level_key = "manager" if role_level in ("manager", "director", "vp", "c-suite") else "ic"
        for v in chosen:
            values_aligned.append(rng.choice(value_behaviors[level_key]).format(v=v, company=company_name))

    watch_pool = [
        f"Could expand cross-team visibility at {company_name} — impact stays local",
        "Documentation could help scale knowledge beyond immediate team",
        "Strong 1:1 collaboration but less visible in group settings",
        f"Deep focus on delivery — opportunity to share strategic perspective across {company_name}",
        "Tendency to take on too much — could delegate more to grow team capacity",
    ]
    areas_to_watch = rng.sample(watch_pool, rng.randint(1, 2))

    # ── Key responsibilities (if not provided) ──
    if not employee.get("key_responsibilities"):
        resp_pool = {
            "engineering": ["Ship features on sprint cadence", "Maintain code quality and review standards", "Collaborate with product on technical feasibility"],
            "product": ["Define product requirements and success metrics", "Conduct customer research and discovery", "Align cross-functional teams on roadmap priorities"],
            "sales": ["Build and manage qualified pipeline", "Close deals aligned to ICP", "Provide market feedback to product team"],
            "marketing": ["Drive demand generation and brand awareness", "Create content that resonates with target personas", "Measure and optimize campaign performance"],
            "customer_success": ["Drive customer adoption and retention", "Identify expansion opportunities", "Surface product feedback from customer base"],
            "hr": ["Attract and retain top talent", "Build scalable people processes", "Support manager development"],
            "finance": ["Deliver accurate financial reporting", "Support strategic planning with data", "Manage cash flow and runway"],
        }
        employee["key_responsibilities"] = resp_pool.get(category, ["Deliver on department priorities", "Collaborate cross-functionally", "Drive measurable outcomes"])

    # ── Cross-functional connections ──
    all_depts = [d["name"] for d in company_data.get("departments", []) if d["name"] != dept_name]
    connections = rng.sample(all_depts, min(2, len(all_depts))) if all_depts else []

    # ── Network position ──
    collaborators = [e["name"] for e in all_employees if e["name"] != employee["name"] and e.get("department") != dept_name]
    key_collabs = rng.sample(collaborators, min(2, len(collaborators))) if collaborators else []
    reports = [e["name"] for e in all_employees if e.get("reports_to") == employee["name"]]
    influence_map = {
        "ic": "Individual contributor with growing cross-team influence",
        "manager": "Team leader shaping department output and developing people",
        "director": "Cross-functional leader connecting department strategy to company goals",
        "vp": "Executive influencing company direction and resource allocation",
        "c-suite": "Executive shaping company strategy and culture",
    }
    network_position = {
        "influence_description": influence_map.get(role_level, influence_map["ic"]),
        "direct_reports": reports,
        "key_collaborators": key_collabs,
    }

    # ── Assemble ──
    employee["recent_activities"] = activities
    employee["leading_indicators"] = indicators
    employee["momentum"] = momentum
    employee["behavior_patterns"] = {"values_aligned": values_aligned, "areas_to_watch": areas_to_watch}
    employee["cross_functional_connections"] = connections
    employee["network_position"] = network_position

    return employee
