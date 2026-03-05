# ui/views.py
# Full tab views — compose components into complete experiences.

import streamlit as st
from agent import get_align_response
from data_loader import get_direct_reports
from ui.components import (
    get_source_icon, time_ago, mom_class,
    render_indicators, render_chain, render_patterns, render_network,
)


def render_live_feed(employee, company_data):
    acts = employee.get("recent_activities", [])
    if not acts:
        return

    st.markdown('<div class="sec">Live Feed — What Your Work Is Enabling</div>', unsafe_allow_html=True)

    goals = company_data.get("company_goals", {}).get("annual_priorities", [])
    goal_keywords = {g.get("goal", ""): g.get("goal", "").lower() for g in goals}

    for act in acts:
        source = act.get("source", "")
        icon = get_source_icon(source)
        time_str, is_recent = time_ago(act.get("date", ""))
        pulse_class = "" if is_recent else " stale"
        recent_class = " feed-recent" if is_recent else ""

        enabled_text = act.get("what_it_enabled", "").lower()
        matched_goal = next(
            (gname for gname, gtext in goal_keywords.items()
             if any(w in enabled_text for w in gtext.split() if len(w) > 3)),
            ""
        )
        goal_tag = f'<div class="feed-goal-tag">↗ {matched_goal}</div>' if matched_goal else ""

        st.markdown(f"""
        <div class="feed-item{recent_class}">
            <div class="feed-header">
                <div class="feed-source">{icon} {source}</div>
                <div class="feed-time"><span class="feed-pulse{pulse_class}"></span> {time_str}</div>
            </div>
            <div class="feed-action">{act.get('action','')}</div>
            <div class="feed-detail">{act.get('detail','')}</div>
            <div class="feed-enabled">
                <div class="feed-enabled-label">What this enabled</div>
                {act.get('what_it_enabled','')}
            </div>
            {goal_tag}
        </div>""", unsafe_allow_html=True)


def render_org_pulse_feed(company_data, current_employee):
    all_activities = []
    for emp in company_data.get("employees", []):
        if emp["name"] == current_employee["name"]:
            continue
        for act in emp.get("recent_activities", [])[:1]:
            all_activities.append({
                "name": emp["name"],
                "department": emp.get("department", ""),
                "source": act.get("source", ""),
                "action": act.get("action", ""),
                "enabled": act.get("what_it_enabled", ""),
                "date": act.get("date", ""),
            })

    all_activities.sort(key=lambda x: x.get("date", ""), reverse=True)
    st.markdown('<div class="sec">Org Pulse — What the Company Is Enabling</div>', unsafe_allow_html=True)

    for item in all_activities[:8]:
        icon = get_source_icon(item["source"])
        enabled = item["enabled"][:120] + "…" if len(item["enabled"]) > 120 else item["enabled"]
        st.markdown(f"""
        <div class="org-item">
            <div class="org-header">
                <div class="org-who">{icon} {item['name']}</div>
                <div class="org-dept">{item['department']}</div>
            </div>
            <div class="org-action">{item['action']}</div>
            <div class="org-enabled">→ {enabled}</div>
        </div>""", unsafe_allow_html=True)


def view_your_reality(company_data, employee):
    render_live_feed(employee, company_data)
    render_chain(company_data, employee)

    col_l, col_r = st.columns([3, 2], gap="medium")
    with col_l:
        render_indicators(employee)
    with col_r:
        st.markdown('<div class="sec">Your Network</div>', unsafe_allow_html=True)
        fig = render_network(employee, company_data)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        net = employee.get("network_position", {})
        if net.get("influence_description"):
            st.caption(net["influence_description"])

    render_patterns(employee)


def view_org_pulse(company_data, employee):
    render_org_pulse_feed(company_data, employee)

    priorities = company_data.get("company_goals", {}).get("annual_priorities", [])
    if priorities:
        st.markdown('<div class="sec">Company Goals</div>', unsafe_allow_html=True)
        cols = st.columns(min(len(priorities), 4))
        for i, g in enumerate(priorities[:len(cols)]):
            with cols[i]:
                st.markdown(f"""<div class="goal-card">
                    <div class="goal-title">{g.get('goal','')}</div>
                    <div class="goal-target">{g.get('target','')}</div>
                </div>""", unsafe_allow_html=True)


def view_collective(company_data):
    st.markdown(f"""
    <div class="card" style="text-align:center;padding:24px 28px;">
        <div style="font-size:1.05rem;color:var(--text);font-weight:500;line-height:1.5;">
            "{company_data.get('mission','')}"
        </div>
        <div style="font-size:.78rem;color:var(--text-3);margin-top:6px;">
            {company_data.get('company_name','')} · {company_data.get('company_size','')}
        </div>
    </div>""", unsafe_allow_html=True)

    goals = company_data.get("company_goals", {})
    priorities = goals.get("annual_priorities", [])
    if priorities:
        st.markdown('<div class="sec">Company Goals</div>', unsafe_allow_html=True)
        cols = st.columns(min(len(priorities), 4))
        for i, g in enumerate(priorities[:len(cols)]):
            with cols[i]:
                st.markdown(f"""<div class="goal-card">
                    <div class="goal-title">{g.get('goal','')}</div>
                    <div class="goal-target">{g.get('target','')}</div>
                </div>""", unsafe_allow_html=True)

    fin = goals.get("financial_targets", {})
    if fin:
        st.markdown('<div class="sec">Financial Snapshot</div>', unsafe_allow_html=True)
        fmap = {"current_arr": ("Current ARR", True), "target_arr": ("Target ARR", True),
                "gross_margin": ("Gross Margin", "%"), "current_nrr": ("NRR", "%"),
                "burn_multiple": ("Burn Multiple", "x")}
        html = '<div class="fin-grid">'
        for k, (lbl, fmt) in fmap.items():
            if k in fin:
                v = fin[k]
                d = f"${v/1e6:.1f}M" if fmt is True else f"{v}{fmt}"
                html += f'<div class="fin-item"><div class="fin-lbl">{lbl}</div><div class="fin-val">{d}</div></div>'
        html += '</div>'
        st.markdown(html, unsafe_allow_html=True)

    bets = goals.get("strategic_bets", [])
    if bets:
        st.markdown('<div class="sec">Strategic Bets</div>', unsafe_allow_html=True)
        for b in bets:
            st.markdown(f'<div class="card" style="padding:12px 18px;margin-bottom:6px;"><span style="color:var(--accent);">◉</span> <span style="color:#cbd5e1;">{b}</span></div>', unsafe_allow_html=True)

    st.markdown('<div class="sec">Departments</div>', unsafe_allow_html=True)
    for dept in company_data.get("departments", []):
        with st.expander(f"**{dept['name']}** — {dept.get('head','')} · {dept.get('headcount','?')} people"):
            st.markdown(f"**Focus:** {dept.get('strategic_focus','')}")
            st.markdown(f"**Goal contribution:** {dept.get('goal_contribution','')}")
            inds = dept.get("leading_indicators", [])
            if inds:
                st.caption(f"Indicators: {', '.join(inds)}")
            deps = dept.get("dependencies", [])
            if deps:
                st.caption(f"Depends on: {', '.join(deps)}")


def view_team(company_data, employee):
    reports = get_direct_reports(company_data, employee)
    if not reports:
        st.info("No direct reports found.")
        return

    st.markdown(f'<div class="sec">Your Team · {len(reports)} direct reports</div>', unsafe_allow_html=True)
    for rpt in reports:
        mom = rpt.get("momentum", {})
        vel = mom.get("velocity", "")
        mc = mom_class(vel)
        with st.expander(f"**{rpt['name']}** — {rpt.get('role','')}"):
            st.markdown(f'<span class="mom-pill {mc}">● {vel}</span>', unsafe_allow_html=True)
            st.markdown(f"*{mom.get('direction','')}*")
            for act in rpt.get("recent_activities", [])[:2]:
                source = act.get("source", "")
                icon = get_source_icon(source)
                st.markdown(f"""<div class="feed-item">
                    <div class="feed-source">{icon} {source}</div>
                    <div class="feed-action">{act.get('action','')}</div>
                    <div class="feed-enabled">
                        <div class="feed-enabled-label">What this enabled</div>
                        {act.get('what_it_enabled','')}
                    </div>
                </div>""", unsafe_allow_html=True)
            for w in rpt.get("behavior_patterns", {}).get("areas_to_watch", []):
                st.markdown(f'<span class="pat-watch">⚡ {w}</span>', unsafe_allow_html=True)


def view_chat(company_data, employee):
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("🌊 What did my work enable?", use_container_width=True):
            st.session_state.suggested_q = "What did my work enable this week? Walk me through the impact."
    with c2:
        if st.button("📈 Where to create momentum?", use_container_width=True):
            st.session_state.suggested_q = "Where are the biggest opportunities for me to create momentum right now?"
    with c3:
        if st.button("🔗 How does my work connect?", use_container_width=True):
            st.session_state.suggested_q = "How does my daily work connect through the system to company goals?"

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if "suggested_q" in st.session_state:
        prompt = st.session_state.suggested_q
        del st.session_state.suggested_q
        _do_chat(prompt, company_data, employee)

    if prompt := st.chat_input("Ask about your impact, momentum, or what your work enables..."):
        _do_chat(prompt, company_data, employee)


def _do_chat(prompt, company_data, employee):
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        with st.spinner("Seeing the connections..."):
            response = get_align_response(prompt, company_data, employee, st.session_state.chat_history[:-1])
            st.markdown(response)
    st.session_state.chat_history.append({"role": "assistant", "content": response})
    st.rerun()
