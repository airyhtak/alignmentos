# ui/views.py
# Full tab views — compose components into complete experiences.

import streamlit as st
from html import escape as esc
from agent import get_align_response
from data_loader import get_direct_reports, get_org_tree, get_team_summary, get_employee_department
from ui.components import (
    get_source_icon, time_ago, mom_class,
    render_indicators, render_chain, render_patterns, render_network,
)


def _build_hero(employee, company_data):
    """Build the impact summary hero block from recent activities."""
    acts = employee.get("recent_activities", [])
    if not acts:
        return ""

    # Count unique departments and goals touched
    depts_touched = set()
    goals_touched = set()
    for act in acts:
        ct = act.get("connected_to")
        if ct and ct.get("department"):
            depts_touched.add(ct["department"])
        lg = act.get("linked_goal", "")
        if lg:
            goals_touched.add(lg)

    # Pick the most impactful enabled text (first activity, typically highest impact)
    top_enabled = acts[0].get("what_it_enabled", "")

    # Build the hero statement
    parts = []
    if len(acts) >= 2:
        parts.append(f'<span class="ht-num">{len(acts)}</span> contributions this week')
    if depts_touched:
        parts.append(f'touched <span class="ht-num">{len(depts_touched)}</span> department{"s" if len(depts_touched) != 1 else ""}')
    if goals_touched:
        parts.append(f'moved <span class="ht-num">{len(goals_touched)}</span> company goal{"s" if len(goals_touched) != 1 else ""}')

    tokens_html = ""
    if parts:
        tokens_html = '<div class="hero-tokens">'
        for p in parts:
            tokens_html += f'<div class="hero-token">{p}</div>'
        tokens_html += '</div>'

    mom = employee.get("momentum", {})
    vel = mom.get("velocity", "")
    mc = mom_class(vel)
    direction = mom.get("direction", "")
    momentum_html = ""
    if vel:
        momentum_html = f'<div class="hero-momentum {mc}">● {esc(vel)} — {esc(direction)}</div>'

    return (
        f'<div class="hero-impact">'
        f'<div class="hero-statement"><strong>{esc(top_enabled)}</strong></div>'
        f'{tokens_html}'
        f'{momentum_html}'
        f'</div>'
    )


def render_impact_feed(employee, company_data):
    """Render the inverted-hierarchy impact feed — enablement first, action as attribution."""
    acts = employee.get("recent_activities", [])
    if not acts:
        return

    st.markdown('<div class="impact-header">What your work enabled</div>', unsafe_allow_html=True)

    for act in acts:
        source = act.get("source", "")
        icon = get_source_icon(source)
        time_str, is_recent = time_ago(act.get("date", ""))
        pulse_class = "" if is_recent else " stale"
        recent_class = " feed-recent" if is_recent else ""

        # Connected_to as inline bridge text
        connected = act.get("connected_to")
        connected_html = ""
        if connected:
            connected_html = (
                f'<div class="feed-connected">'
                f'{esc(connected.get("name", ""))} ({esc(connected.get("department", ""))}) — {esc(connected.get("how", ""))}'
                f'</div>'
            )

        # Goal tag
        matched_goal = act.get("linked_goal", "")
        goal_tag = f'<div class="feed-goal-tag">↗ {esc(matched_goal)}</div>' if matched_goal else ""

        # Inverted: enablement is the headline, action is the attribution
        st.markdown(
            f'<div class="feed-item{recent_class}">'
            f'<div class="feed-enabled">{esc(act.get("what_it_enabled",""))}</div>'
            f'{connected_html}'
            f'{goal_tag}'
            f'<div class="feed-action">{icon} {esc(act.get("action",""))} · {time_str}</div>'
            f'</div>', unsafe_allow_html=True)


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
        enabled_raw = item["enabled"][:120] + "…" if len(item["enabled"]) > 120 else item["enabled"]
        st.markdown(
            f'<div class="org-item">'
            f'<div class="org-header">'
            f'<div class="org-who">{icon} {esc(item["name"])}</div>'
            f'<div class="org-dept">{esc(item["department"])}</div>'
            f'</div>'
            f'<div class="org-action">{esc(item["action"])}</div>'
            f'<div class="org-enabled">→ {esc(enabled_raw)}</div>'
            f'</div>', unsafe_allow_html=True)


def _render_prose_chain(company_data, employee):
    """Render the alignment chain as a single prose sentence instead of boxes."""
    dept = get_employee_department(company_data, employee)
    if not dept:
        return
    goals = company_data.get("company_goals", {})
    top = [g["goal"] for g in goals.get("annual_priorities", [])[:2]]
    if not top:
        return

    st.markdown(
        f'<div style="font-size:.82rem;color:var(--text-2);line-height:1.6;padding:16px 20px;'
        f'background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);margin-top:12px;">'
        f'Your work in <span style="color:var(--accent);font-weight:600;">{esc(dept.get("name",""))}</span> '
        f'drives {esc(dept.get("strategic_focus","").lower())}, '
        f'enabling <span style="color:var(--green);">{esc(dept.get("goal_contribution","").split("—")[0].strip().lower())}</span> '
        f'toward <span style="color:var(--text);font-weight:500;">{esc(top[0])}</span>.'
        f'</div>', unsafe_allow_html=True)


def view_your_reality(company_data, employee):
    # Hero impact summary — the shoutout moment
    hero_html = _build_hero(employee, company_data)
    if hero_html:
        st.markdown(hero_html, unsafe_allow_html=True)

    # Impact feed — inverted hierarchy (enablement first)
    render_impact_feed(employee, company_data)

    # Prose alignment chain
    _render_prose_chain(company_data, employee)


def view_org_pulse(company_data, employee):
    render_org_pulse_feed(company_data, employee)

    priorities = company_data.get("company_goals", {}).get("annual_priorities", [])
    if priorities:
        st.markdown('<div class="sec">Company Goals</div>', unsafe_allow_html=True)
        cols = st.columns(min(len(priorities), 4))
        for i, g in enumerate(priorities[:len(cols)]):
            with cols[i]:
                st.markdown(
                    f'<div class="goal-card">'
                    f'<div class="goal-title">{esc(g.get("goal",""))}</div>'
                    f'<div class="goal-target">{esc(g.get("target",""))}</div>'
                    f'</div>', unsafe_allow_html=True)


def view_collective(company_data):
    st.markdown(
        f'<div class="card" style="text-align:center;padding:24px 28px;">'
        f'<div style="font-size:1.05rem;color:var(--text);font-weight:500;line-height:1.5;">'
        f'"{esc(company_data.get("mission",""))}"'
        f'</div>'
        f'<div style="font-size:.78rem;color:var(--text-3);margin-top:6px;">'
        f'{esc(company_data.get("company_name",""))} · {esc(company_data.get("company_size",""))}'
        f'</div>'
        f'</div>', unsafe_allow_html=True)

    goals = company_data.get("company_goals", {})
    priorities = goals.get("annual_priorities", [])

    # Build goal activity linkage from all employees
    goal_activity = {}
    for emp in company_data.get("employees", []):
        for act in emp.get("recent_activities", []):
            lg = act.get("linked_goal", "")
            if lg:
                if lg not in goal_activity:
                    goal_activity[lg] = {"count": 0, "depts": set(), "people": set()}
                goal_activity[lg]["count"] += 1
                goal_activity[lg]["depts"].add(emp.get("department", ""))
                goal_activity[lg]["people"].add(emp["name"])

    if priorities:
        st.markdown('<div class="sec">Company Goals</div>', unsafe_allow_html=True)
        cols = st.columns(min(len(priorities), 4))
        for i, g in enumerate(priorities[:len(cols)]):
            gname = g.get("goal", "")
            linkage = goal_activity.get(gname, {})
            act_count = linkage.get("count", 0) if linkage else 0
            dept_count = len(linkage.get("depts", set())) if linkage else 0
            people_count = len(linkage.get("people", set())) if linkage else 0
            linkage_html = ""
            if act_count:
                linkage_html = f'<div style="font-size:.68rem;color:var(--green);margin-top:6px;">{act_count} activities · {people_count} people · {dept_count} depts</div>'
            elif priorities:
                linkage_html = '<div style="font-size:.68rem;color:var(--text-3);margin-top:6px;">No linked activity yet</div>'
            with cols[i]:
                st.markdown(
                    f'<div class="goal-card">'
                    f'<div class="goal-title">{esc(gname)}</div>'
                    f'<div class="goal-target">{esc(g.get("target",""))}</div>'
                    f'{linkage_html}'
                    f'</div>', unsafe_allow_html=True)

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
            st.markdown(f'<div class="card" style="padding:12px 18px;margin-bottom:6px;"><span style="color:var(--accent);">◉</span> <span style="color:#cbd5e1;">{esc(b)}</span></div>', unsafe_allow_html=True)

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


def _render_exec_overview(company_data, employee):
    """Executive overlay: org momentum, department cards, talent signals."""
    org = get_org_tree(company_data, employee)
    if len(org) < 2:
        return

    summary = get_team_summary(org)
    mc = summary["momentum_counts"]
    total_people = sum(mc.values()) or 1

    st.markdown('<div class="sec">Organization Overview</div>', unsafe_allow_html=True)

    # Momentum heatmap
    colors = {"accelerating": "var(--green)", "building": "var(--accent)", "steady": "#64748b", "emerging": "var(--amber)"}
    bars_html = ""
    for vel in ["accelerating", "building", "steady", "emerging"]:
        count = mc.get(vel, 0)
        pct = int(count / total_people * 100) if count else 0
        bars_html += (
            f'<div class="exec-momentum-bar">'
            f'<div class="exec-mom-label">{vel}</div>'
            f'<div style="flex:1;background:var(--surface);border-radius:4px;height:14px;overflow:hidden;">'
            f'<div class="exec-mom-fill" style="width:{max(pct, 2)}%;background:{colors[vel]};"></div>'
            f'</div>'
            f'<div class="exec-mom-count">{count}</div>'
            f'</div>'
        )
    st.markdown(bars_html, unsafe_allow_html=True)

    # Department cards
    dept_people = {}
    for p in org:
        d = p.get("department", "Other")
        dept_people.setdefault(d, []).append(p)

    dept_names = list(dept_people.keys())
    if dept_names:
        cols = st.columns(min(len(dept_names), 3))
        for i, dname in enumerate(dept_names[:6]):
            people = dept_people[dname]
            dept_obj = get_employee_department(company_data, people[0]) if people else None
            dept_mc = {}
            top_act = None
            for p in people:
                v = p.get("momentum", {}).get("velocity", "steady").lower()
                dept_mc[v] = dept_mc.get(v, 0) + 1
                if not top_act:
                    acts = p.get("recent_activities", [])
                    if acts:
                        top_act = {"name": p["name"], "enabled": acts[0].get("what_it_enabled", "")}

            mom_parts = []
            for v in ["accelerating", "building", "steady", "emerging"]:
                if dept_mc.get(v, 0) > 0:
                    mom_parts.append(f"{dept_mc[v]} {v}")
            mom_text = ", ".join(mom_parts) if mom_parts else "—"
            top_html = ""
            if top_act:
                enabled_short = top_act["enabled"][:80] + "..." if len(top_act["enabled"]) > 80 else top_act["enabled"]
                top_html = f'<div style="font-size:.72rem;color:var(--accent);margin-top:6px;">Top: {esc(enabled_short)}</div>'

            with cols[i % len(cols)]:
                st.markdown(
                    f'<div class="exec-dept-card">'
                    f'<div class="exec-dept-name">{esc(dname)}</div>'
                    f'<div class="exec-dept-head">{esc(dept_obj.get("head", "") if dept_obj else "")} · {len(people)} people</div>'
                    f'<div class="exec-dept-mom">{esc(mom_text)}</div>'
                    f'{top_html}'
                    f'</div>', unsafe_allow_html=True)

    # Cross-functional signals
    cross_acts = []
    for p in org:
        for act in p.get("recent_activities", []):
            ct = act.get("connected_to")
            if ct and ct.get("department") and ct["department"] != p.get("department"):
                cross_acts.append({"person": p["name"], "dept": p.get("department", ""), **act})
    if cross_acts:
        st.markdown('<div class="sec">Cross-Functional Signals</div>', unsafe_allow_html=True)
        for ca in cross_acts[:4]:
            ct = ca.get("connected_to", {})
            icon = get_source_icon(ca.get("source", ""))
            st.markdown(
                f'<div class="feed-item">'
                f'<div class="feed-header">'
                f'<div class="feed-source">{icon} {esc(ca.get("source",""))}</div>'
                f'<div style="font-size:.72rem;color:var(--text-3);">{esc(ca["person"])} · {esc(ca["dept"])}</div>'
                f'</div>'
                f'<div class="feed-action">{esc(ca.get("action",""))}</div>'
                f'<div class="feed-connected">'
                f'<div class="feed-connected-label">Connected to</div>'
                f'{esc(ct.get("name",""))} ({esc(ct.get("department",""))})'
                f'</div>'
                f'<div class="feed-enabled">'
                f'<div class="feed-enabled-label">What this enabled</div>'
                f'{esc(ca.get("what_it_enabled",""))}'
                f'</div>'
                f'</div>', unsafe_allow_html=True)

    # Talent signals
    thriving = [p for p in org if p.get("momentum", {}).get("velocity", "").lower() == "accelerating"]
    support = summary["attention"]
    if thriving or support:
        st.markdown('<div class="sec">Talent Signals</div>', unsafe_allow_html=True)
        tc1, tc2 = st.columns(2)
        with tc1:
            if thriving:
                items = ""
                for p in thriving[:4]:
                    pat = p.get("momentum", {}).get("pattern", "")
                    items += f'<div class="exec-talent-item"><strong>{esc(p["name"])}</strong> — {esc(pat)}</div>'
                st.markdown(
                    f'<div class="exec-talent-card">'
                    f'<div class="exec-talent-title thriving">Momentum Building</div>'
                    f'{items}'
                    f'</div>', unsafe_allow_html=True)
        with tc2:
            if support:
                items = ""
                for p in support[:4]:
                    reason_text = "; ".join(p["reasons"])
                    items += f'<div class="exec-talent-item"><strong>{esc(p["name"])}</strong> — {esc(reason_text)}</div>'
                st.markdown(
                    f'<div class="exec-talent-card">'
                    f'<div class="exec-talent-title support">May Benefit from Support</div>'
                    f'{items}'
                    f'</div>', unsafe_allow_html=True)

    st.markdown("---")


def view_team(company_data, employee):
    reports = get_direct_reports(company_data, employee)
    if not reports:
        st.info("No direct reports found.")
        return

    # Executive overlay for director+ roles
    role_level = employee.get("role_level", "ic")
    if role_level in ("director", "vp", "c-suite"):
        _render_exec_overview(company_data, employee)

    # -- Layer 1: Team Pulse Summary --
    summary = get_team_summary(reports)
    mc = summary["momentum_counts"]
    dept = get_employee_department(company_data, employee)
    dept_focus = dept.get("strategic_focus", "") if dept else ""

    accel_build = mc.get("accelerating", 0) + mc.get("building", 0)
    mom_text = f"{accel_build} of {len(reports)} building or accelerating"
    attn_count = len(summary["attention"])
    ind_text = f"{summary['indicators_on_track']}/{summary['indicators_total']}" if summary["indicators_total"] else "—"
    dept_count = len(summary["connected_depts"])

    st.markdown(f'<div class="sec">Your Team · {len(reports)} direct reports</div>', unsafe_allow_html=True)

    if dept_focus:
        st.caption(f"Department focus: {dept_focus}")

    attn_style = 'color:var(--amber);' if attn_count else ''
    st.markdown(
        f'<div class="team-pulse">'
        f'<div class="team-pulse-item">'
        f'<div class="team-pulse-label">Momentum</div>'
        f'<div class="team-pulse-val">{accel_build}<span style="font-size:.72rem;color:var(--text-3);font-weight:400;">/{len(reports)}</span></div>'
        f'<div class="team-pulse-sub">{esc(mom_text)}</div>'
        f'</div>'
        f'<div class="team-pulse-item">'
        f'<div class="team-pulse-label">Needs Attention</div>'
        f'<div class="team-pulse-val" style="{attn_style}">{attn_count}</div>'
        f'<div class="team-pulse-sub">coaching moments</div>'
        f'</div>'
        f'<div class="team-pulse-item">'
        f'<div class="team-pulse-label">Indicators</div>'
        f'<div class="team-pulse-val">{ind_text}</div>'
        f'<div class="team-pulse-sub">on track</div>'
        f'</div>'
        f'<div class="team-pulse-item">'
        f'<div class="team-pulse-label">Connections</div>'
        f'<div class="team-pulse-val">{dept_count}</div>'
        f'<div class="team-pulse-sub">departments reached</div>'
        f'</div>'
        f'</div>', unsafe_allow_html=True)

    # -- Layer 2: Attention Cards --
    for attn in summary["attention"][:3]:
        reasons = "; ".join(attn["reasons"])
        watch_text = attn["watch"][0] if attn["watch"] else ""
        suggest = f"Consider: {watch_text}" if watch_text else ""
        st.markdown(
            f'<div class="team-attention">'
            f'<div class="team-attn-name">{esc(attn["name"])} — {esc(attn["role"])}</div>'
            f'<div class="team-attn-signal">{esc(reasons.capitalize())}</div>'
            f'<div class="team-attn-suggest">{esc(suggest)}</div>'
            f'</div>', unsafe_allow_html=True)

    # -- Layer 2b: Team Behavior Patterns (aggregated from reports) --
    all_values = []
    all_watch = []
    for rpt in reports:
        bp = rpt.get("behavior_patterns", {})
        all_values.extend(bp.get("values_aligned", []))
        all_watch.extend(bp.get("areas_to_watch", []))

    if all_values or all_watch:
        tc1, tc2 = st.columns([3, 2])
        with tc1:
            if all_values:
                val_html = ""
                for p in all_values[:4]:
                    if ":" in p:
                        name, desc = p.split(":", 1)
                        val_html += f'<div class="pat"><span class="pat-vname">{esc(name.strip())}</span> <span class="pat-desc">{esc(desc.strip())}</span></div>'
                    else:
                        val_html += f'<div class="pat"><span class="pat-desc">✓ {esc(p)}</span></div>'
                st.markdown(
                    f'<div class="card">'
                    f'<div style="font-size:.58rem;font-weight:600;text-transform:uppercase;letter-spacing:.08em;color:var(--green);margin-bottom:8px;">Values showing up</div>'
                    f'{val_html}'
                    f'</div>', unsafe_allow_html=True)
        with tc2:
            if all_watch:
                # Deduplicate similar watch areas
                seen = set()
                unique_watch = []
                for w in all_watch:
                    key = w[:30].lower()
                    if key not in seen:
                        seen.add(key)
                        unique_watch.append(w)
                watch_html = "".join(f'<div class="pat"><span class="pat-watch">⚡ {esc(w)}</span></div>' for w in unique_watch[:3])
                st.markdown(
                    f'<div class="card">'
                    f'<div style="font-size:.58rem;font-weight:600;text-transform:uppercase;letter-spacing:.08em;color:var(--amber);margin-bottom:8px;">Coaching opportunities</div>'
                    f'{watch_html}'
                    f'</div>', unsafe_allow_html=True)

    # -- Layer 3: Team Grid (2-column cards) --
    for row_start in range(0, len(reports), 2):
        row = reports[row_start:row_start + 2]
        cols = st.columns(2)
        for col_idx, rpt in enumerate(row):
            mom = rpt.get("momentum", {})
            vel = mom.get("velocity", "")
            mc_cls = mom_class(vel)
            direction = mom.get("direction", "")

            # Latest activity — lead with enablement
            acts = rpt.get("recent_activities", [])
            latest_act = acts[0] if acts else {}
            act_text = latest_act.get("action", "")
            enabled_text = latest_act.get("what_it_enabled", "")
            if len(enabled_text) > 100:
                enabled_text = enabled_text[:100] + "..."
            goal_tag = ""
            lg = latest_act.get("linked_goal", "")
            if lg:
                goal_tag = f'<div class="feed-goal-tag" style="margin-top:6px;">↗ {esc(lg)}</div>'

            # Indicator summary
            on_track = 0
            total_ind = 0
            for key, val in rpt.get("leading_indicators", {}).items():
                if isinstance(val, dict):
                    total_ind += 1
                    current = val.get("current", 0)
                    target = val.get("target", 1)
                    if target and current >= target * 0.7:
                        on_track += 1
            ind_cls = "on-track" if total_ind == 0 or on_track >= total_ind * 0.7 else "off-track"
            ind_label = f"{on_track}/{total_ind} on track" if total_ind else ""

            watch_count = len(rpt.get("behavior_patterns", {}).get("areas_to_watch", []))
            watch_html = f'<div class="team-card-watch">{watch_count} to watch</div>' if watch_count else ""

            with cols[col_idx]:
                st.markdown(
                    f'<div class="team-card">'
                    f'<div class="team-card-header">'
                    f'<div class="team-card-name">{esc(rpt["name"])}</div>'
                    f'<span class="mom-pill {mc_cls}" style="font-size:.68rem;padding:2px 8px;">● {esc(vel)}</span>'
                    f'</div>'
                    f'<div class="team-card-role">{esc(rpt.get("role",""))}</div>'
                    f'<div class="team-card-direction">{esc(direction)}</div>'
                    f'<div class="team-card-enabled" style="font-size:.85rem;color:var(--text);font-weight:500;margin:8px 0 4px;">{esc(enabled_text)}</div>'
                    f'<div class="team-card-activity" style="font-size:.72rem;color:var(--text-3);">from: {esc(act_text)}</div>'
                    f'{goal_tag}'
                    f'<div class="team-card-footer">'
                    f'<div class="team-card-ind {ind_cls}">{ind_label}</div>'
                    f'{watch_html}'
                    f'</div>'
                    f'</div>', unsafe_allow_html=True)

    # -- Layer 4: Detail Expanders --
    st.markdown('<div class="sec">Detail View</div>', unsafe_allow_html=True)
    for rpt in reports:
        mom = rpt.get("momentum", {})
        vel = mom.get("velocity", "")
        mc_cls = mom_class(vel)
        with st.expander(f"**{rpt['name']}** — {rpt.get('role','')}"):
            st.markdown(f'<span class="mom-pill {mc_cls}">● {esc(vel)}</span> <span style="font-size:.82rem;color:var(--text-2);font-style:italic;">{esc(mom.get("direction",""))}</span>', unsafe_allow_html=True)
            st.markdown(f'<div style="font-size:.78rem;color:var(--text-3);margin:6px 0;">{esc(mom.get("pattern",""))}</div>', unsafe_allow_html=True)

            # Inverted feed — enablement first
            for act in rpt.get("recent_activities", []):
                source = act.get("source", "")
                icon = get_source_icon(source)
                time_str, _ = time_ago(act.get("date", ""))
                connected = act.get("connected_to")
                connected_html = ""
                if connected:
                    connected_html = (
                        f'<div class="feed-connected">'
                        f'{esc(connected.get("name", ""))} ({esc(connected.get("department", ""))}) — {esc(connected.get("how", ""))}'
                        f'</div>'
                    )
                goal_tag = ""
                lg = act.get("linked_goal", "")
                if lg:
                    goal_tag = f'<div class="feed-goal-tag">↗ {esc(lg)}</div>'
                st.markdown(
                    f'<div class="feed-item">'
                    f'<div class="feed-enabled">{esc(act.get("what_it_enabled",""))}</div>'
                    f'{connected_html}'
                    f'{goal_tag}'
                    f'<div class="feed-action">{icon} {esc(act.get("action",""))} · {time_str}</div>'
                    f'</div>', unsafe_allow_html=True)

            # Leading indicators
            render_indicators(rpt)

            # Behavior patterns — values aligned + areas to watch
            patterns = rpt.get("behavior_patterns", {})
            watch = patterns.get("areas_to_watch", [])
            aligned = patterns.get("values_aligned", [])
            if aligned or watch:
                st.markdown('<div style="font-size:.62rem;font-weight:600;text-transform:uppercase;letter-spacing:.08em;color:var(--text-3);margin:12px 0 6px;">Behavior Patterns</div>', unsafe_allow_html=True)
                pat_html = ""
                for p in aligned:
                    if ":" in p:
                        name, desc = p.split(":", 1)
                        pat_html += f'<div class="pat"><span class="pat-vname">{esc(name.strip())}</span> <span class="pat-desc">{esc(desc.strip())}</span></div>'
                    else:
                        pat_html += f'<div class="pat"><span class="pat-desc">✓ {esc(p)}</span></div>'
                for w in watch:
                    pat_html += f'<div class="pat"><span class="pat-watch">⚡ {esc(w)}</span></div>'
                st.markdown(f'<div class="card">{pat_html}</div>', unsafe_allow_html=True)


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
