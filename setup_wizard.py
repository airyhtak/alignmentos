# setup_wizard.py - AlignmentOS Company Setup Wizard
# Guided onboarding: company → departments → people → AI-generated activity data

import streamlit as st
import pandas as pd
from data_loader import save_company
from wizard.builder import build_company_json, slugify, check_invite_code


# ══════════════════════════════════════════════════
# STEP 1: COMPANY BASICS
# ══════════════════════════════════════════════════

def render_step_company():
    """Collect company identity and goals."""

    st.markdown("""
    <div style="margin-bottom:24px;">
        <div style="font-size:1.4rem;font-weight:700;color:var(--text);margin-bottom:4px;">
            Tell us about your company
        </div>
        <div style="font-size:.85rem;color:var(--text-2);">
            This is the foundation — your mission, goals, and what success looks like.
        </div>
    </div>
    """, unsafe_allow_html=True)

    w = st.session_state.wizard_data

    col1, col2 = st.columns(2)
    with col1:
        w["company_name"] = st.text_input("Company name *", value=w.get("company_name", ""))
        w["industry"] = st.text_input("Industry *", value=w.get("industry", ""), placeholder="e.g., SaaS, Healthcare, Fintech")
    with col2:
        w["company_size"] = st.selectbox("Company size *", 
            ["", "1-50", "51-200", "201-500", "501-1000", "1000+"],
            index=["", "1-50", "51-200", "201-500", "501-1000", "1000+"].index(w.get("company_size", "")))
        w["current_quarter"] = st.text_input("Current quarter", value=w.get("current_quarter", "Q1 2026"), placeholder="e.g., Q1 2026")

    w["mission"] = st.text_area("Mission *", value=w.get("mission", ""), 
        placeholder="What does your company exist to do?", height=80)
    w["vision"] = st.text_area("Vision", value=w.get("vision", ""), 
        placeholder="Where are you headed? (optional)", height=80)

    # Company values
    st.markdown('<div class="sec">Values</div>', unsafe_allow_html=True)
    st.caption("What does your company stand for? Add 2-5 values with behavioral definitions.")

    if "values" not in w:
        w["values"] = [{"name": "", "behavioral_definition": ""}]

    values_to_remove = None
    for i, val in enumerate(w["values"]):
        c1, c2, c3 = st.columns([2, 4, 0.5])
        with c1:
            val["name"] = st.text_input("Value", value=val.get("name", ""), key=f"val_name_{i}",
                placeholder="e.g., Move Fast")
        with c2:
            val["behavioral_definition"] = st.text_input("What does this look like in practice?",
                value=val.get("behavioral_definition", ""), key=f"val_def_{i}",
                placeholder="e.g., We ship before perfect and iterate based on real feedback")
        with c3:
            st.markdown("<br>", unsafe_allow_html=True)
            if len(w["values"]) > 1 and st.button("✕", key=f"rm_val_{i}"):
                values_to_remove = i

    if values_to_remove is not None:
        w["values"].pop(values_to_remove)
        st.rerun()

    if len(w["values"]) < 6:
        if st.button("＋ Add value"):
            w["values"].append({"name": "", "behavioral_definition": ""})
            st.rerun()

    # Company goals
    st.markdown('<div class="sec">Company Goals</div>', unsafe_allow_html=True)
    st.caption("What are you trying to achieve this year? Add 2-4 priorities.")

    if "goals" not in w:
        w["goals"] = [{"goal": "", "metric": "", "target": ""}]

    goals_to_remove = None
    for i, goal in enumerate(w["goals"]):
        c1, c2, c3, c4 = st.columns([3, 2, 2, 0.5])
        with c1:
            goal["goal"] = st.text_input(f"Goal", value=goal.get("goal", ""), key=f"goal_{i}",
                placeholder="e.g., Grow ARR to $10M")
        with c2:
            goal["metric"] = st.text_input(f"Metric", value=goal.get("metric", ""), key=f"metric_{i}",
                placeholder="e.g., ARR")
        with c3:
            goal["target"] = st.text_input(f"Target", value=goal.get("target", ""), key=f"target_{i}",
                placeholder="e.g., $10M by Q4")
        with c4:
            st.markdown("<br>", unsafe_allow_html=True)
            if len(w["goals"]) > 1 and st.button("✕", key=f"rm_goal_{i}"):
                goals_to_remove = i

    if goals_to_remove is not None:
        w["goals"].pop(goals_to_remove)
        st.rerun()

    if len(w["goals"]) < 5:
        if st.button("＋ Add goal"):
            w["goals"].append({"goal": "", "metric": "", "target": ""})
            st.rerun()

    # Financial targets (optional)
    with st.expander("Financial targets (optional)"):
        if "financials" not in w:
            w["financials"] = {}
        c1, c2 = st.columns(2)
        with c1:
            arr = st.text_input("Current ARR ($)", value=w["financials"].get("current_arr_str", ""), placeholder="e.g., 5000000")
            w["financials"]["current_arr_str"] = arr
            target_arr = st.text_input("Target ARR ($)", value=w["financials"].get("target_arr_str", ""), placeholder="e.g., 10000000")
            w["financials"]["target_arr_str"] = target_arr
        with c2:
            gm = st.text_input("Gross margin (%)", value=w["financials"].get("gross_margin_str", ""), placeholder="e.g., 72")
            w["financials"]["gross_margin_str"] = gm
            nrr = st.text_input("Net revenue retention (%)", value=w["financials"].get("nrr_str", ""), placeholder="e.g., 115")
            w["financials"]["nrr_str"] = nrr

    # Validation
    valid = all([w.get("company_name"), w.get("industry"), w.get("company_size"), w.get("mission")])
    has_goals = any(g.get("goal") for g in w.get("goals", []))

    st.markdown("<br>", unsafe_allow_html=True)
    col_l, col_r = st.columns([4, 1])
    with col_r:
        if st.button("Next →", use_container_width=True, disabled=not (valid and has_goals)):
            st.session_state.wizard_step = 2
            st.rerun()

    if not valid:
        st.caption("Fill in all required fields (*) to continue.")
    elif not has_goals:
        st.caption("Add at least one company goal to continue.")


# ══════════════════════════════════════════════════
# STEP 2: DEPARTMENTS
# ══════════════════════════════════════════════════

def render_step_departments():
    """Collect department structure."""

    st.markdown("""
    <div style="margin-bottom:24px;">
        <div style="font-size:1.4rem;font-weight:700;color:var(--text);margin-bottom:4px;">
            Your departments
        </div>
        <div style="font-size:.85rem;color:var(--text-2);">
            How is your company organized? These become the connective tissue between people and goals.
        </div>
    </div>
    """, unsafe_allow_html=True)

    w = st.session_state.wizard_data

    if "departments" not in w:
        w["departments"] = [{"name": "", "head": "", "headcount": "", "strategic_focus": "", "goal_contribution": ""}]

    dept_to_remove = None
    for i, dept in enumerate(w["departments"]):
        st.markdown(f'<div class="card" style="margin-bottom:12px;padding:16px 20px;">', unsafe_allow_html=True)
        c1, c2, c3 = st.columns([3, 2, 1])
        with c1:
            dept["name"] = st.text_input("Department name *", value=dept.get("name", ""), key=f"dept_name_{i}",
                placeholder="e.g., Engineering")
        with c2:
            dept["head"] = st.text_input("Department head", value=dept.get("head", ""), key=f"dept_head_{i}",
                placeholder="e.g., Sarah Chen")
        with c3:
            dept["headcount"] = st.text_input("Headcount", value=dept.get("headcount", ""), key=f"dept_hc_{i}",
                placeholder="e.g., 25")

        dept["strategic_focus"] = st.text_input("Strategic focus *", value=dept.get("strategic_focus", ""), key=f"dept_focus_{i}",
            placeholder="What is this department focused on right now?")
        dept["goal_contribution"] = st.text_input("How does this dept contribute to company goals?", 
            value=dept.get("goal_contribution", ""), key=f"dept_goal_{i}",
            placeholder="e.g., Drives product velocity to unlock ARR growth")

        if len(w["departments"]) > 1:
            if st.button(f"Remove {dept.get('name', 'department')}", key=f"rm_dept_{i}"):
                dept_to_remove = i

        st.markdown('</div>', unsafe_allow_html=True)

    if dept_to_remove is not None:
        w["departments"].pop(dept_to_remove)
        st.rerun()

    if st.button("＋ Add department"):
        w["departments"].append({"name": "", "head": "", "headcount": "", "strategic_focus": "", "goal_contribution": ""})
        st.rerun()

    valid = any(d.get("name") and d.get("strategic_focus") for d in w["departments"])

    st.markdown("<br>", unsafe_allow_html=True)
    col_l, col_m, col_r = st.columns([1, 3, 1])
    with col_l:
        if st.button("← Back", use_container_width=True):
            st.session_state.wizard_step = 1
            st.rerun()
    with col_r:
        if st.button("Next →", use_container_width=True, disabled=not valid):
            st.session_state.wizard_step = 3
            st.rerun()

    if not valid:
        st.caption("Add at least one department with a name and strategic focus.")


# ══════════════════════════════════════════════════
# STEP 3: PEOPLE
# ══════════════════════════════════════════════════

def render_step_people():
    """Collect people — CSV upload or manual entry."""

    w = st.session_state.wizard_data
    dept_names = [d["name"] for d in w.get("departments", []) if d.get("name")]

    st.markdown("""
    <div style="margin-bottom:24px;">
        <div style="font-size:1.4rem;font-weight:700;color:var(--text);margin-bottom:4px;">
            Add your people
        </div>
        <div style="font-size:.85rem;color:var(--text-2);">
            Add team members who'll experience Shared Reality. Start with 5-15 people for the best pilot experience.
        </div>
    </div>
    """, unsafe_allow_html=True)

    if "employees" not in w:
        w["employees"] = []

    tab_csv, tab_manual = st.tabs(["📄  Upload CSV", "✏️  Add manually"])

    with tab_csv:
        st.markdown("""
        Upload a CSV with these columns (only **name**, **role**, and **department** are required):
        
        `name, role, department, reports_to, role_level, role_purpose`
        
        **role_level** values: `ic`, `manager`, `director`, `vp`, `c-suite`
        """)

        # Generate and offer template download
        template_df = pd.DataFrame({
            "name": ["Jane Smith", "Alex Johnson", "Maria Garcia"],
            "role": ["Senior Engineer", "Product Manager", "Sales Lead"],
            "department": [dept_names[0] if dept_names else "Engineering", 
                          dept_names[1] if len(dept_names) > 1 else "Product",
                          dept_names[2] if len(dept_names) > 2 else "Sales"],
            "reports_to": ["CTO", "VP Product", "VP Sales"],
            "role_level": ["ic", "manager", "ic"],
            "role_purpose": ["Build and ship core product features", "Define product roadmap and priorities", "Drive new business revenue"]
        })

        csv_template = template_df.to_csv(index=False)
        st.download_button("⬇ Download CSV template", csv_template, "alignmentos_people_template.csv", "text/csv")

        uploaded = st.file_uploader("Upload your people CSV", type=["csv"])
        if uploaded:
            try:
                df = pd.read_csv(uploaded)
                required = {"name", "role", "department"}
                if not required.issubset(set(df.columns)):
                    st.error(f"CSV must include columns: {', '.join(required)}. Found: {', '.join(df.columns)}")
                else:
                    new_employees = []
                    for _, row in df.iterrows():
                        emp = {
                            "name": str(row.get("name", "")).strip(),
                            "role": str(row.get("role", "")).strip(),
                            "department": str(row.get("department", "")).strip(),
                            "reports_to": str(row.get("reports_to", "")).strip() if pd.notna(row.get("reports_to")) else "",
                            "role_level": str(row.get("role_level", "ic")).strip().lower() if pd.notna(row.get("role_level")) else "ic",
                            "role_purpose": str(row.get("role_purpose", "")).strip() if pd.notna(row.get("role_purpose")) else "",
                        }
                        if emp["name"] and emp["role"]:
                            new_employees.append(emp)

                    if new_employees:
                        # Merge with existing (replace duplicates by name)
                        existing_names = {e["name"] for e in w["employees"]}
                        for emp in new_employees:
                            if emp["name"] not in existing_names:
                                w["employees"].append(emp)
                                existing_names.add(emp["name"])
                        st.success(f"Added {len(new_employees)} people from CSV.")
                        st.rerun()
            except Exception as e:
                st.error(f"Error reading CSV: {e}")

    with tab_manual:
        st.markdown("Add people one at a time.")

        with st.form("add_person", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                name = st.text_input("Name *", placeholder="e.g., Sarah Chen")
                role = st.text_input("Role *", placeholder="e.g., Senior Engineer")
                department = st.selectbox("Department *", [""] + dept_names)
            with c2:
                reports_to = st.text_input("Reports to", placeholder="e.g., VP Engineering")
                role_level = st.selectbox("Role level", ["ic", "manager", "director", "vp", "c-suite"])
                role_purpose = st.text_input("Role purpose", placeholder="What outcomes does this role produce?")

            submitted = st.form_submit_button("Add person")
            if submitted and name and role and department:
                w["employees"].append({
                    "name": name.strip(),
                    "role": role.strip(),
                    "department": department,
                    "reports_to": reports_to.strip(),
                    "role_level": role_level,
                    "role_purpose": role_purpose.strip(),
                })
                st.rerun()

    # Show current people
    if w["employees"]:
        st.markdown(f'<div class="sec">People added · {len(w["employees"])}</div>', unsafe_allow_html=True)

        emp_to_remove = None
        for i, emp in enumerate(w["employees"]):
            c1, c2, c3, c4 = st.columns([3, 2, 2, 0.5])
            with c1:
                st.markdown(f"**{emp['name']}**")
            with c2:
                st.caption(f"{emp['role']} · {emp.get('role_level', 'ic')}")
            with c3:
                st.caption(emp.get('department', ''))
            with c4:
                if st.button("✕", key=f"rm_emp_{i}"):
                    emp_to_remove = i

        if emp_to_remove is not None:
            w["employees"].pop(emp_to_remove)
            st.rerun()

    valid = len(w.get("employees", [])) >= 2

    st.markdown("<br>", unsafe_allow_html=True)
    col_l, col_m, col_r = st.columns([1, 3, 1])
    with col_l:
        if st.button("← Back", use_container_width=True):
            st.session_state.wizard_step = 2
            st.rerun()
    with col_r:
        if st.button("Next →", use_container_width=True, disabled=not valid):
            st.session_state.wizard_step = 4
            st.rerun()

    if not valid:
        st.caption("Add at least 2 people to continue.")


# ══════════════════════════════════════════════════
# STEP 4: REVIEW & GENERATE
# ══════════════════════════════════════════════════

def render_step_review():
    """Review and generate the company config."""

    w = st.session_state.wizard_data

    st.markdown("""
    <div style="margin-bottom:24px;">
        <div style="font-size:1.4rem;font-weight:700;color:var(--text);margin-bottom:4px;">
            Review & launch
        </div>
        <div style="font-size:.85rem;color:var(--text-2);">
            Here's what we'll set up. AlignmentOS will generate realistic activity data so you can experience Shared Reality immediately.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Summary cards
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""<div class="card" style="text-align:center;">
            <div class="card-label">Company</div>
            <div style="font-size:1.1rem;font-weight:600;color:var(--text);">{w.get('company_name', '')}</div>
            <div style="font-size:.78rem;color:var(--text-2);margin-top:4px;">{w.get('industry', '')} · {w.get('company_size', '')}</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        dept_count = len([d for d in w.get("departments", []) if d.get("name")])
        st.markdown(f"""<div class="card" style="text-align:center;">
            <div class="card-label">Departments</div>
            <div style="font-size:1.1rem;font-weight:600;color:var(--text);">{dept_count}</div>
            <div style="font-size:.78rem;color:var(--text-2);margin-top:4px;">{', '.join(d['name'] for d in w.get('departments', []) if d.get('name'))}</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        emp_count = len(w.get("employees", []))
        st.markdown(f"""<div class="card" style="text-align:center;">
            <div class="card-label">People</div>
            <div style="font-size:1.1rem;font-weight:600;color:var(--text);">{emp_count}</div>
            <div style="font-size:.78rem;color:var(--text-2);margin-top:4px;">Ready for Shared Reality</div>
        </div>""", unsafe_allow_html=True)

    # Goals
    goals = [g for g in w.get("goals", []) if g.get("goal")]
    if goals:
        st.markdown('<div class="sec">Goals</div>', unsafe_allow_html=True)
        for g in goals:
            st.markdown(f"""<div class="card" style="padding:10px 16px;margin-bottom:4px;">
                <span style="color:var(--accent);font-weight:600;">◉</span>
                <span style="color:var(--text);">{g['goal']}</span>
                <span style="color:var(--text-3);font-size:.8rem;"> → {g.get('target', '')}</span>
            </div>""", unsafe_allow_html=True)

    # People preview
    st.markdown('<div class="sec">People</div>', unsafe_allow_html=True)
    for emp in w.get("employees", []):
        st.markdown(f"""<div style="padding:4px 0;font-size:.85rem;">
            <span style="color:var(--text);font-weight:500;">{emp['name']}</span>
            <span style="color:var(--text-3);"> · {emp['role']} · {emp.get('department', '')} · {emp.get('role_level', 'ic')}</span>
        </div>""", unsafe_allow_html=True)

    st.markdown("""
    <div style="margin-top:20px;padding:16px 20px;background:var(--accent-bg);border:1px solid rgba(99,102,241,.15);border-radius:var(--radius);">
        <div style="font-size:.85rem;color:var(--accent);font-weight:600;margin-bottom:4px;">What happens next</div>
        <div style="font-size:.82rem;color:var(--text-2);line-height:1.5;">
            AlignmentOS will generate realistic simulated activity data for each person — recent work, momentum indicators, 
            behavior patterns, and network connections. This lets you experience Shared Reality immediately.<br><br>
            Once live integrations are connected (Jira, Salesforce, Slack), real data replaces the simulation seamlessly.
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col_l, col_m, col_r = st.columns([1, 2, 1.5])
    with col_l:
        if st.button("← Back", use_container_width=True):
            st.session_state.wizard_step = 3
            st.rerun()
    with col_r:
        if st.button("🚀 Launch AlignmentOS", use_container_width=True, type="primary"):
            with st.spinner("Generating your Shared Reality..."):
                company_data = build_company_json(w)
                company_id = slugify(w["company_name"])
                save_company(company_id, company_data)
                st.session_state.setup_complete = True
                st.session_state.active_company = company_id
                # Clean up wizard state
                if "wizard_data" in st.session_state:
                    del st.session_state.wizard_data
                if "wizard_step" in st.session_state:
                    del st.session_state.wizard_step
                st.rerun()


# ══════════════════════════════════════════════════
# MAIN WIZARD RENDER
# ══════════════════════════════════════════════════

def render_wizard():
    """Main wizard entry point — handles auth + multi-step flow."""

    # ── Auth check ──
    if not st.session_state.get("authenticated"):
        render_auth()
        return

    # ── Initialize wizard state ──
    if "wizard_step" not in st.session_state:
        st.session_state.wizard_step = 1
    if "wizard_data" not in st.session_state:
        st.session_state.wizard_data = {}

    step = st.session_state.wizard_step

    # ── Progress bar ──
    steps = ["Company", "Departments", "People", "Launch"]
    progress_html = '<div style="display:flex;gap:4px;margin-bottom:28px;">'
    for i, s in enumerate(steps, 1):
        active = i == step
        done = i < step
        color = "var(--accent)" if active else ("var(--green)" if done else "var(--text-3)")
        bg = "var(--accent-bg)" if active else ("var(--green-bg)" if done else "transparent")
        border = f"1px solid {color}" if active else ("1px solid rgba(52,211,153,.2)" if done else "1px solid var(--border)")
        progress_html += f'<div style="flex:1;text-align:center;padding:8px;border-radius:8px;background:{bg};border:{border};font-size:.75rem;font-weight:600;color:{color};">'
        progress_html += f'{"✓ " if done else ""}{s}</div>'
    progress_html += '</div>'
    st.markdown(progress_html, unsafe_allow_html=True)

    # ── Render step ──
    if step == 1:
        render_step_company()
    elif step == 2:
        render_step_departments()
    elif step == 3:
        render_step_people()
    elif step == 4:
        render_step_review()


def render_auth():
    """Invite code authentication."""

    st.markdown("""
    <div style="text-align:center;padding:60px 40px 20px;">
        <div style="width:60px;height:60px;border-radius:16px;background:linear-gradient(135deg,#6366f1,#a78bfa);
            display:inline-flex;align-items:center;justify-content:center;font-size:24px;color:#fff;font-weight:700;margin-bottom:16px;">
            ◉
        </div>
        <div style="font-size:1.8rem;font-weight:700;color:var(--text);margin-bottom:6px;">
            AlignmentOS
        </div>
        <div style="font-size:.92rem;color:var(--text-2);max-width:400px;margin:0 auto;">
            See what your work enables. Enter your invite code to get started.
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_l, col_m, col_r = st.columns([1, 2, 1])
    with col_m:
        code = st.text_input("Invite code", placeholder="Enter your code", label_visibility="collapsed")
        if st.button("Get started →", use_container_width=True, type="primary"):
            if check_invite_code(code):
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Invalid invite code. Contact your AlignmentOS partner for access.")

        st.markdown("""
        <div style="text-align:center;margin-top:20px;font-size:.78rem;color:var(--text-3);">
            Don't have a code? <a href="mailto:kat@alignmentos.com" style="color:var(--accent);">Request access</a>
        </div>
        """, unsafe_allow_html=True)
