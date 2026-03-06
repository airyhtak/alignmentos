# ui/components.py
# Leaf-level rendering primitives — building blocks consumed by views.py.

import streamlit as st
import numpy as np
import plotly.graph_objects as go
from html import escape as esc
from datetime import datetime
from data_loader import get_employee_department, get_direct_reports

SOURCE_ICONS = {
    "jira": "🔷", "github": "⚫", "salesforce": "☁️", "slack": "💬",
    "google docs": "📄", "google sheets": "📊", "google slides": "📑",
    "google calendar": "📅", "google analytics": "📈", "google business": "⭐",
    "emr": "🏥", "zoom": "📹", "docusign": "✍️", "workable": "👤",
    "hris": "🗂️", "training portal": "🎓", "meta ads": "📢",
    "petfolk app": "🐾", "netsuite": "💰", "confluence": "📝",
}


def get_source_icon(source):
    return SOURCE_ICONS.get(source.lower(), "📡")


def time_ago(date_str):
    try:
        dt = datetime.fromisoformat(date_str)
        diff = datetime.now() - dt
        hours = diff.total_seconds() / 3600
        if hours < 1:
            return "just now", True
        elif hours < 24:
            return f"{int(hours)}h ago", True
        elif hours < 48:
            return "yesterday", False
        else:
            return f"{int(hours / 24)}d ago", False
    except Exception:
        return date_str, False


def mom_class(velocity):
    velocity = velocity or ""
    v = velocity.lower()
    if any(w in v for w in ["accel", "strong", "upward"]):
        return "mom-up"
    if any(w in v for w in ["emerging", "new", "early"]):
        return "mom-emerging"
    return "mom-mid"


def render_top_bar(company_data, employee):
    momentum = employee.get("momentum", {}).get("velocity", "")
    mc = mom_class(momentum)
    st.markdown(
        f'<div class="top-bar">'
        f'<div class="tb-left">'
        f'<div class="tb-logo">A</div>'
        f'<div>'
        f'<div class="tb-name">AlignmentOS</div>'
        f'<div class="tb-meta">{esc(company_data.get("company_name",""))} · {esc(company_data.get("current_quarter",""))}</div>'
        f'</div>'
        f'</div>'
        f'<div class="tb-person">'
        f'<strong>{esc(employee["name"])}</strong> · {esc(employee.get("role",""))}<br/>'
        f'<span class="mom-pill {mc}">● {esc(momentum)}</span>'
        f'</div>'
        f'</div>', unsafe_allow_html=True)


def render_indicators(employee):
    indicators = employee.get("leading_indicators", {})
    if not indicators:
        return
    st.markdown('<div class="sec">Leading Indicators</div>', unsafe_allow_html=True)
    html = '<div class="ind-grid">'
    for key, val in indicators.items():
        if isinstance(val, dict):
            label = key.replace("_", " ").title()
            html += (
                f'<div class="ind">'
                f'<div class="ind-label">{esc(label)}</div>'
                f'<div class="ind-val">{esc(str(val.get("current","")))}</div>'
                f'<div class="ind-target">→ {esc(str(val.get("target","")))}</div>'
                f'<div class="ind-trend">{esc(str(val.get("trend","")))}</div>'
                f'</div>'
            )
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)


def render_chain(company_data, employee):
    dept = get_employee_department(company_data, employee)
    if not dept:
        return
    goals = company_data.get("company_goals", {})
    top = [g["goal"] for g in goals.get("annual_priorities", [])[:2]]

    def trunc(s, n=90):
        return s[:n] + "…" if len(s) > n else s

    st.markdown('<div class="sec">How Your Work Connects</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="chain">'
        f'<div class="chain-node"><div class="chain-lbl">Your Work</div><div class="chain-txt">{esc(trunc(employee.get("role_purpose","")))}</div></div>'
        f'<div class="chain-node"><div class="chain-lbl">{esc(dept.get("name",""))} Focus</div><div class="chain-txt">{esc(trunc(dept.get("strategic_focus","")))}</div></div>'
        f'<div class="chain-node"><div class="chain-lbl">Enables</div><div class="chain-txt">{esc(trunc(dept.get("goal_contribution","")))}</div></div>'
        f'<div class="chain-node"><div class="chain-lbl">Company Goals</div><div class="chain-txt">{esc(" · ".join(top))}</div></div>'
        f'</div>', unsafe_allow_html=True)


def render_patterns(employee):
    patterns = employee.get("behavior_patterns", {})
    aligned = patterns.get("values_aligned", [])
    watch = patterns.get("areas_to_watch", [])
    if not aligned and not watch:
        return

    st.markdown('<div class="sec">Behavior Patterns</div>', unsafe_allow_html=True)
    c1, c2 = st.columns([3, 2])
    with c1:
        html = ""
        for p in aligned:
            if ":" in p:
                name, desc = p.split(":", 1)
                html += f'<div class="pat"><span class="pat-vname">{name.strip()}</span> <span class="pat-desc">{desc.strip()}</span></div>'
            else:
                html += f'<div class="pat"><span class="pat-desc">✓ {p}</span></div>'
        st.markdown(f'<div class="card">{html}</div>', unsafe_allow_html=True)
    with c2:
        html = "".join(f'<div class="pat"><span class="pat-watch">⚡ {p}</span></div>' for p in watch)
        if html:
            st.markdown(f'<div class="card">{html}</div>', unsafe_allow_html=True)


def render_network(employee, company_data):
    fig = go.Figure()
    nodes, edges = [], []
    nodes.append({"id": "c", "label": employee["name"].split()[0], "size": 30, "color": "#6366f1"})

    mgr = employee.get("reports_to", "")
    if mgr and mgr != "CEO":
        nodes.append({"id": "m", "label": mgr.split()[0], "size": 20, "color": "#8b5cf6"})
        edges.append(("c", "m"))

    reports = get_direct_reports(company_data, employee)
    for i, r in enumerate(reports[:5]):
        nid = f"d{i}"
        nodes.append({"id": nid, "label": r["name"].split()[0], "size": 16, "color": "#a78bfa"})
        edges.append(("c", nid))

    net = employee.get("network_position", {})
    for i, co in enumerate(net.get("key_collaborators", [])[:4]):
        nid = f"k{i}"
        label = co.split("(")[0].strip().split()[0]
        nodes.append({"id": nid, "label": label, "size": 12, "color": "#c4b5fd"})
        edges.append(("c", nid))

    n = len(nodes)
    angles = np.linspace(0, 2 * np.pi, n, endpoint=False)
    pos = {"c": (0, 0)}
    for i, nd in enumerate(nodes[1:], 1):
        r = 1.5 if i <= 1 + len(reports) else 2.2
        pos[nd["id"]] = (r * np.cos(angles[i]), r * np.sin(angles[i]))

    for s, d in edges:
        x0, y0 = pos[s]
        x1, y1 = pos[d]
        fig.add_trace(go.Scatter(x=[x0, x1], y=[y0, y1], mode="lines",
            line=dict(color="rgba(99,102,241,.18)", width=1.5), hoverinfo="none", showlegend=False))

    for nd in nodes:
        x, y = pos[nd["id"]]
        fig.add_trace(go.Scatter(x=[x], y=[y], mode="markers+text",
            marker=dict(size=nd["size"], color=nd["color"], line=dict(width=0)),
            text=[nd["label"]], textposition="bottom center",
            textfont=dict(size=9, color="#94a3b8", family="DM Sans"),
            hoverinfo="text", showlegend=False))

    fig.update_layout(showlegend=False, height=200, margin=dict(l=0, r=0, t=0, b=0),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-3, 3]),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-3, 3]),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
    return fig
