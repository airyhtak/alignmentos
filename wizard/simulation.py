# wizard/simulation.py
# Deterministic simulated data generation for new company setups.
# Isolated here so the AI-generation upgrade (roadmap item C) only touches this file.

import random
import hashlib
from datetime import datetime, timedelta


def generate_simulated_data(employee, company_data):
    """Generate realistic simulated activity data for an employee using deterministic logic.
    This runs locally — no AI call needed. The AI agent (Align) handles the narrative later."""

    # Seed random based on employee name for consistency
    seed = int(hashlib.md5(employee["name"].encode()).hexdigest()[:8], 16)
    rng = random.Random(seed)

    dept_name = employee.get("department", "")
    role_level = employee.get("role_level", "ic")

    # ── Activity templates by department type ──
    activity_templates = {
        "engineering": [
            {"action": "Shipped feature update", "detail": "Deployed improvements to core platform module", "what_it_enabled": "Unblocked product team's Q1 launch timeline"},
            {"action": "Resolved critical bug", "detail": "Fixed data pipeline issue affecting downstream reports", "what_it_enabled": "Restored data accuracy for customer-facing dashboards"},
            {"action": "Led architecture review", "detail": "Evaluated and proposed system design for scalability", "what_it_enabled": "Created technical foundation for 3x user capacity"},
            {"action": "Improved CI/CD pipeline", "detail": "Reduced deploy time and added automated testing stages", "what_it_enabled": "Team ships 40% faster with fewer rollbacks"},
            {"action": "Mentored junior developer", "detail": "Paired on complex integration work over two weeks", "what_it_enabled": "Junior dev now independently handling integration tickets"},
        ],
        "product": [
            {"action": "Published product requirements", "detail": "Defined scope and success metrics for upcoming feature", "what_it_enabled": "Engineering team started sprint with clear direction"},
            {"action": "Ran customer discovery calls", "detail": "Interviewed 8 customers on workflow pain points", "what_it_enabled": "Identified top 3 friction points driving churn"},
            {"action": "Prioritized Q2 roadmap", "detail": "Aligned features to strategic bets with stakeholder input", "what_it_enabled": "Cross-functional teams aligned on what to build next"},
            {"action": "Analyzed feature adoption", "detail": "Deep dive on usage patterns for recent release", "what_it_enabled": "Surfaced onboarding gap — 60% of users miss key workflow"},
        ],
        "sales": [
            {"action": "Closed enterprise deal", "detail": "Navigated multi-stakeholder procurement process", "what_it_enabled": "Added $120K ARR and validated enterprise positioning"},
            {"action": "Built partner channel pipeline", "detail": "Established relationships with 3 integration partners", "what_it_enabled": "Created referral pipeline worth estimated $200K"},
            {"action": "Refined sales playbook", "detail": "Documented winning patterns from top deals", "what_it_enabled": "New reps ramp 2 weeks faster with structured approach"},
            {"action": "Led quarterly business review", "detail": "Presented pipeline health and forecast to leadership", "what_it_enabled": "Aligned leadership on gap between pipeline and target"},
        ],
        "marketing": [
            {"action": "Launched content campaign", "detail": "Published thought leadership series across channels", "what_it_enabled": "Generated 340 MQLs — 2x previous campaign"},
            {"action": "Redesigned landing pages", "detail": "A/B tested messaging and conversion flows", "what_it_enabled": "Improved trial conversion rate from 3.2% to 5.1%"},
            {"action": "Organized industry event", "detail": "Coordinated speaker lineup and attendee experience", "what_it_enabled": "Built brand presence with 200+ target-persona attendees"},
        ],
        "customer_success": [
            {"action": "Prevented at-risk churn", "detail": "Identified usage drop pattern and intervened with executive sponsor", "what_it_enabled": "Retained $85K ARR account and expanded engagement"},
            {"action": "Built onboarding playbook", "detail": "Standardized first-90-days experience for new customers", "what_it_enabled": "Time-to-value reduced from 45 to 28 days"},
            {"action": "Led quarterly business review", "detail": "Presented ROI analysis and expansion opportunities to client", "what_it_enabled": "Client approved upsell — 40% account expansion"},
        ],
        "operations": [
            {"action": "Streamlined vendor procurement", "detail": "Consolidated vendor stack and renegotiated contracts", "what_it_enabled": "Reduced operational costs by 15% annually"},
            {"action": "Implemented new workflow system", "detail": "Rolled out automation for recurring processes", "what_it_enabled": "Team reclaimed 10 hours/week for strategic work"},
        ],
        "hr": [
            {"action": "Launched performance framework", "detail": "Rolled out updated review cycle with manager training", "what_it_enabled": "Managers have consistent lens for growth conversations"},
            {"action": "Filled critical roles", "detail": "Closed 4 priority hires across engineering and product", "what_it_enabled": "Teams at full capacity for Q2 execution"},
            {"action": "Ran engagement survey", "detail": "Designed and deployed org-wide pulse check", "what_it_enabled": "Surfaced 3 retention risks leadership can address now"},
        ],
        "finance": [
            {"action": "Delivered board financial package", "detail": "Consolidated actuals, forecast, and scenario analysis", "what_it_enabled": "Board approved runway extension strategy"},
            {"action": "Built department budgets", "detail": "Partnered with dept heads on resource allocation", "what_it_enabled": "Teams have spending clarity for next two quarters"},
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
    activities = rng.sample(templates, min(3, len(templates)))

    today = datetime.now()
    for i, act in enumerate(activities):
        delta = timedelta(days=rng.randint(1, 14) + (i * 5))
        act["date"] = (today - delta).strftime("%Y-%m-%d")

    # ── Leading indicators ──
    indicator_templates = {
        "engineering": {
            "sprint_velocity": {"current": rng.randint(18, 35), "target": 30, "trend": rng.choice(["↑ improving", "→ steady"]), "unit": "pts/sprint"},
            "code_review_turnaround": {"current": round(rng.uniform(2, 8), 1), "target": 4, "trend": rng.choice(["↑ improving", "→ steady", "↓ slowing"]), "unit": "hours"},
        },
        "product": {
            "feature_adoption": {"current": rng.randint(25, 70), "target": 60, "trend": "↑ improving", "unit": "%"},
            "customer_interviews": {"current": rng.randint(4, 12), "target": 10, "trend": "→ steady", "unit": "/month"},
        },
        "sales": {
            "pipeline_coverage": {"current": round(rng.uniform(2.0, 4.5), 1), "target": 3.0, "trend": "↑ growing", "unit": "x"},
            "win_rate": {"current": rng.randint(20, 40), "target": 30, "trend": rng.choice(["↑ improving", "→ steady"]), "unit": "%"},
        },
        "marketing": {
            "mqls_generated": {"current": rng.randint(150, 500), "target": 350, "trend": "↑ growing", "unit": "/month"},
            "content_engagement": {"current": round(rng.uniform(2, 8), 1), "target": 5, "trend": "→ steady", "unit": "% CTR"},
        },
        "customer_success": {
            "nps_score": {"current": rng.randint(35, 65), "target": 50, "trend": "↑ improving", "unit": ""},
            "time_to_value": {"current": rng.randint(20, 50), "target": 30, "trend": "↓ improving", "unit": "days"},
        },
    }
    indicators = indicator_templates.get(category, {"throughput": {"current": rng.randint(60, 95), "target": 85, "trend": "→ steady", "unit": "%"}})

    # ── Momentum ──
    velocities = ["accelerating", "building", "steady", "emerging"]
    velocity = rng.choice(velocities[:3])
    directions = {
        "accelerating": "Strong forward momentum — work is compounding across teams",
        "building": "Momentum is building — recent contributions creating ripple effects",
        "steady": "Consistent contribution — maintaining velocity on key deliverables",
        "emerging": "New patterns forming — early signals of cross-team impact",
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
                "Consistently demonstrates {v} in daily work and team interactions",
                "Embodies {v} — visible in how they approach problems and collaborate",
            ],
            "manager": [
                "Models {v} for the team and reinforces it in 1:1s and retros",
                "Creates team norms that reflect {v} in practice",
            ],
        }
        level_key = "manager" if role_level in ("manager", "director", "vp", "c-suite") else "ic"
        for v in chosen:
            values_aligned.append(rng.choice(value_behaviors[level_key]).format(v=v))

    watch_pool = [
        "Could expand cross-team visibility — impact stays local",
        "Documentation could help scale knowledge beyond immediate team",
        "Strong 1:1 collaboration but less visible in group settings",
        "Deep focus on delivery — opportunity to step back and share strategic perspective",
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
    all_employees = company_data.get("employees", [])
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
