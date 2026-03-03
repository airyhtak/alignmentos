# app.py - AlignmentOS Prototype
# Live feed — tool-sourced activities, enablement narratives, org pulse

import streamlit as st
import numpy as np
import plotly.graph_objects as go
from datetime import datetime

from data_loader import (
    get_available_companies, load_company, get_employee_by_name,
    get_employee_department, get_direct_reports,
)
from agent import get_align_response

# ── Page Config ──
st.set_page_config(
    page_title="AlignmentOS",
    page_icon="◉",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Source icon map
SOURCE_ICONS = {
    "jira": "🔷", "github": "⚫", "salesforce": "☁️", "slack": "💬",
    "google docs": "📄", "google sheets": "📊", "google slides": "📑",
    "google calendar": "📅", "google analytics": "📈", "google business": "⭐",
    "emr": "🏥", "zoom": "📹", "docusign": "✍️", "workable": "👤",
    "hris": "🗂️", "training portal": "🎓", "meta ads": "📢",
    "petfolk app": "🐾", "netsuite": "💰", "confluence": "📝",
}

def _get_source_icon(source):
    return SOURCE_ICONS.get(source.lower(), "📡")

def _time_ago(date_str):
    """Convert ISO date to relative time."""
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
            days = int(hours / 24)
            return f"{days}d ago", False
    except:
        return date_str, False


# ══════════════════════════════════════════════════════════
# DESIGN SYSTEM
# ══════════════════════════════════════════════════════════

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;1,9..40,400&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── base ── */
:root {
    --bg:        #0c0e14;
    --surface:   rgba(255,255,255,0.025);
    --border:    rgba(255,255,255,0.06);
    --border-hi: rgba(129,140,248,0.35);
    --text:      #e2e8f0;
    --text-2:    #94a3b8;
    --text-3:    #475569;
    --accent:    #818cf8;
    --accent-bg: rgba(99,102,241,0.08);
    --green:     #34d399;
    --green-bg:  rgba(16,185,129,0.10);
    --amber:     #fbbf24;
    --amber-bg:  rgba(251,191,36,0.10);
    --mono:      'JetBrains Mono', monospace;
    --sans:      'DM Sans', -apple-system, sans-serif;
    --radius:    10px;
}
html, body, [class*="css"] { font-family: var(--sans); }
.block-container { max-width: 1160px; padding: 1.5rem 2rem 3rem; }
#MainMenu, footer, header { visibility: hidden; }

/* ── top bar ── */
.top-bar {
    display: flex; justify-content: space-between; align-items: center;
    padding-bottom: 1.2rem; margin-bottom: .4rem;
    border-bottom: 1px solid var(--border);
}
.tb-left { display:flex; align-items:center; gap:10px; }
.tb-logo {
    width:30px; height:30px; border-radius:8px;
    background: linear-gradient(135deg,#6366f1,#a78bfa);
    display:flex; align-items:center; justify-content:center;
    font-size:14px; color:#fff; font-weight:700;
}
.tb-name  { font-size:.95rem; font-weight:600; color:var(--text); letter-spacing:-.02em; }
.tb-meta  { font-size:.72rem; color:var(--text-3); }
.tb-person { text-align:right; font-size:.82rem; color:var(--text-2); }
.tb-person strong { color:var(--text); }

/* ── momentum pill ── */
.mom-pill {
    display:inline-flex; align-items:center; gap:5px;
    padding:4px 12px; border-radius:16px;
    font-size:.78rem; font-weight:600;
}
.mom-up   { background:var(--green-bg); color:var(--green); border:1px solid rgba(16,185,129,.2); }
.mom-mid  { background:var(--amber-bg); color:var(--amber); border:1px solid rgba(251,191,36,.2); }

/* ── cards ── */
.card {
    background: var(--surface); border:1px solid var(--border);
    border-radius: var(--radius); padding:18px 22px;
    transition: border-color .15s;
}
.card:hover { border-color: var(--border-hi); }
.card-label {
    font-size:.62rem; font-weight:600; text-transform:uppercase;
    letter-spacing:.09em; color:var(--text-3); margin-bottom:10px;
}

/* ── live feed ── */
.feed-item {
    background: var(--surface); border:1px solid var(--border);
    border-radius: var(--radius); padding:16px 20px; margin-bottom:10px;
    transition: border-color .15s, background .15s;
    border-left: 3px solid transparent;
}
.feed-item:hover { border-color: var(--border-hi); background: var(--accent-bg); }
.feed-item.feed-recent { border-left-color: var(--green); }
.feed-header {
    display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;
}
.feed-source {
    display:inline-flex; align-items:center; gap:6px;
    font-size:.68rem; font-weight:600; text-transform:uppercase;
    letter-spacing:.06em; color:var(--text-3);
    padding:3px 10px; border-radius:12px;
    background: rgba(255,255,255,0.04); border:1px solid var(--border);
}
.feed-time {
    font-size:.68rem; color:var(--text-3); font-family:var(--mono);
    display:flex; align-items:center; gap:4px;
}
.feed-pulse {
    width:6px; height:6px; border-radius:50%; background:var(--green);
    display:inline-block;
}
.feed-pulse.stale { background:var(--text-3); }
.feed-action { font-size:.92rem; font-weight:600; color:var(--text); margin-bottom:6px; line-height:1.4; }
.feed-detail { font-size:.82rem; color:var(--text-2); line-height:1.45; margin-bottom:10px; }
.feed-enabled {
    font-size:.82rem; color:var(--accent); line-height:1.45;
    padding:10px 14px; background:var(--accent-bg);
    border-radius:8px; border-left:2px solid #6366f1;
}
.feed-enabled-label {
    font-size:.6rem; font-weight:600; text-transform:uppercase;
    letter-spacing:.08em; color:rgba(129,140,248,0.6); margin-bottom:4px;
}
.feed-goal-tag {
    display:inline-block; font-size:.62rem; font-weight:500;
    padding:2px 8px; border-radius:10px; margin-top:8px;
    background:var(--green-bg); color:var(--green); border:1px solid rgba(16,185,129,.15);
}

/* ── org pulse feed ── */
.org-item {
    background: var(--surface); border:1px solid var(--border);
    border-radius: var(--radius); padding:12px 16px; margin-bottom:6px;
    transition: border-color .15s;
}
.org-item:hover { border-color: var(--border-hi); }
.org-header { display:flex; justify-content:space-between; align-items:center; margin-bottom:4px; }
.org-who { font-size:.82rem; font-weight:600; color:var(--text); }
.org-dept { font-size:.62rem; color:var(--text-3); padding:2px 8px; border-radius:8px; background:rgba(255,255,255,0.03); }
.org-action { font-size:.82rem; color:var(--text-2); margin-bottom:4px; }
.org-enabled { font-size:.78rem; color:var(--accent); }

/* ── indicator pills ── */
.ind-grid { display:flex; gap:8px; flex-wrap:wrap; }
.ind {
    flex:1; min-width:125px;
    background:var(--surface); border:1px solid var(--border);
    border-radius:var(--radius); padding:14px 16px;
}
.ind-label  { font-size:.6rem; font-weight:600; text-transform:uppercase; letter-spacing:.07em; color:var(--text-3); margin-bottom:3px; }
.ind-val    { font-size:1.1rem; font-weight:700; color:var(--text); font-family:var(--mono); }
.ind-target { font-size:.72rem; color:var(--accent); margin-top:1px; }
.ind-trend  { font-size:.68rem; color:var(--text-3); margin-top:1px; }

/* ── chain (horizontal flow) ── */
.chain { display:flex; gap:0; margin:8px 0; overflow-x:auto; }
.chain-node {
    flex:1; min-width:140px;
    background:var(--surface); border:1px solid var(--border);
    padding:14px 16px; position:relative;
}
.chain-node:first-child { border-radius:var(--radius) 0 0 var(--radius); }
.chain-node:last-child  { border-radius:0 var(--radius) var(--radius) 0; }
.chain-node:not(:last-child)::after {
    content:'→'; position:absolute; right:-9px; top:50%;
    transform:translateY(-50%); color:var(--accent); font-size:.95rem;
    z-index:1; background:var(--bg); padding:0 3px;
}
.chain-lbl  { font-size:.58rem; font-weight:600; text-transform:uppercase; letter-spacing:.08em; color:var(--accent); margin-bottom:5px; }
.chain-txt  { font-size:.78rem; color:#cbd5e1; line-height:1.4; }

/* ── patterns ── */
.pat       { padding:7px 0; border-bottom:1px solid var(--border); font-size:.82rem; line-height:1.5; }
.pat:last-child { border-bottom:none; }
.pat-vname { color:var(--accent); font-weight:600; }
.pat-desc  { color:var(--text-2); }
.pat-watch { color:var(--amber); }

/* ── section divider ── */
.sec {
    font-size:.62rem; font-weight:600; text-transform:uppercase;
    letter-spacing:.1em; color:var(--text-3);
    margin:20px 0 10px; padding-bottom:6px;
    border-bottom:1px solid var(--border);
}

/* ── collective view ── */
.goal-card {
    background:var(--accent-bg); border:1px solid rgba(99,102,241,.15);
    border-radius:var(--radius); padding:16px 18px; text-align:center;
    height:100%;
}
.goal-title  { font-size:.9rem; font-weight:600; color:var(--text); margin-bottom:3px; }
.goal-target { font-size:.78rem; color:var(--accent); }

.fin-grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(120px,1fr)); gap:8px; }
.fin-item {
    background:var(--surface); border:1px solid var(--border);
    border-radius:var(--radius); padding:14px 16px; text-align:center;
}
.fin-lbl { font-size:.6rem; text-transform:uppercase; letter-spacing:.07em; color:var(--text-3); margin-bottom:3px; }
.fin-val { font-size:1.15rem; font-weight:700; color:var(--text); font-family:var(--mono); }

/* ── streamlit overrides ── */
.stTabs [data-baseweb="tab-list"] {
    gap:2px; background:var(--surface); border-radius:var(--radius);
    padding:3px; border:1px solid var(--border);
}
.stTabs [data-baseweb="tab"] {
    border-radius:8px; font-size:.82rem; padding:6px 18px;
    font-family:var(--sans); font-weight:500;
}
.stTabs [aria-selected="true"] { background:var(--accent-bg) !important; }
div[data-testid="stExpander"] {
    background:var(--surface); border:1px solid var(--border); border-radius:var(--radius);
}
.stChatMessage { background:transparent !important; }
[data-testid="stChatInput"] textarea { font-family:var(--sans) !important; }
.stSelectbox > div > div { background:var(--surface); border-color:var(--border); }
div[data-testid="stMetricValue"] { font-family:var(--mono); }
</style>
""", unsafe_allow_html=True)

# ── Session State ──
for key, default in [("chat_history", []), ("current_employee", None), ("company_data", None)]:
    if key not in st.session_state:
        st.session_state[key] = default


# ══════════════════════════════════════════════════════════
# COMPONENTS
# ══════════════════════════════════════════════════════════

def _mom_class(velocity):
    return "mom-up" if any(w in velocity.lower() for w in ["accel", "strong", "upward"]) else "mom-mid"


def render_top_bar(company_data, employee):
    momentum = employee.get("momentum", {}).get("velocity", "")
    mc = _mom_class(momentum)
    st.markdown(f"""
    <div class="top-bar">
        <div class="tb-left">
            <div class="tb-logo">A</div>
            <div>
                <div class="tb-name">AlignmentOS</div>
                <div class="tb-meta">{company_data.get('company_name','')} · {company_data.get('current_quarter','')}</div>
            </div>
        </div>
        <div class="tb-person">
            <strong>{employee['name']}</strong> · {employee.get('role','')}<br/>
            <span class="mom-pill {mc}">● {momentum}</span>
        </div>
    </div>""", unsafe_allow_html=True)


def render_live_feed(employee, company_data):
    """Live activity feed with tool sources and enablement connections."""
    acts = employee.get("recent_activities", [])
    if not acts:
        return
    
    st.markdown('<div class="sec">Live Feed — What Your Work Is Enabling</div>', unsafe_allow_html=True)
    
    # Find relevant goals for tagging
    goals = company_data.get("company_goals", {}).get("annual_priorities", [])
    goal_keywords = {}
    for g in goals:
        goal_text = g.get("goal", "").lower()
        goal_keywords[g.get("goal", "")] = goal_text

    for i, act in enumerate(acts):
        source = act.get("source", "")
        icon = _get_source_icon(source)
        time_str, is_recent = _time_ago(act.get("date", ""))
        pulse_class = "" if is_recent else " stale"
        recent_class = " feed-recent" if is_recent else ""
        
        # Try to match to a company goal
        enabled_text = act.get("what_it_enabled", "").lower()
        matched_goal = ""
        for gname, gtext in goal_keywords.items():
            # Simple keyword matching
            gwords = [w for w in gtext.split() if len(w) > 3]
            if any(w in enabled_text for w in gwords):
                matched_goal = gname
                break
        
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


def render_org_pulse(company_data, current_employee):
    """Cross-company activity feed — what others are doing and enabling."""
    all_activities = []
    for emp in company_data.get("employees", []):
        if emp["name"] == current_employee["name"]:
            continue
        for act in emp.get("recent_activities", [])[:1]:  # Top 1 per person
            all_activities.append({
                "name": emp["name"],
                "department": emp.get("department", ""),
                "source": act.get("source", ""),
                "action": act.get("action", ""),
                "enabled": act.get("what_it_enabled", ""),
                "date": act.get("date", ""),
            })
    
    # Sort by date (most recent first)
    all_activities.sort(key=lambda x: x.get("date", ""), reverse=True)
    
    st.markdown('<div class="sec">Org Pulse — What the Company Is Enabling</div>', unsafe_allow_html=True)
    
    for item in all_activities[:8]:
        icon = _get_source_icon(item["source"])
        time_str, is_recent = _time_ago(item.get("date", ""))
        
        # Truncate enablement for feed
        enabled = item["enabled"]
        if len(enabled) > 120:
            enabled = enabled[:120] + "…"
        
        st.markdown(f"""
        <div class="org-item">
            <div class="org-header">
                <div class="org-who">{icon} {item['name']}</div>
                <div class="org-dept">{item['department']}</div>
            </div>
            <div class="org-action">{item['action']}</div>
            <div class="org-enabled">→ {enabled}</div>
        </div>""", unsafe_allow_html=True)


def render_indicators(employee):
    indicators = employee.get("leading_indicators", {})
    if not indicators:
        return
    st.markdown('<div class="sec">Leading Indicators</div>', unsafe_allow_html=True)
    html = '<div class="ind-grid">'
    for key, val in indicators.items():
        if isinstance(val, dict):
            label = key.replace("_", " ").title()
            html += f"""<div class="ind">
                <div class="ind-label">{label}</div>
                <div class="ind-val">{val.get('current','')}</div>
                <div class="ind-target">→ {val.get('target','')}</div>
                <div class="ind-trend">{val.get('trend','')}</div>
            </div>"""
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
    st.markdown(f"""
    <div class="chain">
        <div class="chain-node"><div class="chain-lbl">Your Work</div><div class="chain-txt">{trunc(employee.get('role_purpose',''))}</div></div>
        <div class="chain-node"><div class="chain-lbl">{dept.get('name','')} Focus</div><div class="chain-txt">{trunc(dept.get('strategic_focus',''))}</div></div>
        <div class="chain-node"><div class="chain-lbl">Enables</div><div class="chain-txt">{trunc(dept.get('goal_contribution',''))}</div></div>
        <div class="chain-node"><div class="chain-lbl">Company Goals</div><div class="chain-txt">{' · '.join(top)}</div></div>
    </div>""", unsafe_allow_html=True)


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
        html = ""
        for p in watch:
            html += f'<div class="pat"><span class="pat-watch">⚡ {p}</span></div>'
        if html:
            st.markdown(f'<div class="card">{html}</div>', unsafe_allow_html=True)


def render_network(employee, company_data):
    fig = go.Figure()
    nodes, edges = [], []
    nodes.append({"id":"c","label":employee["name"].split()[0],"size":30,"color":"#6366f1"})

    mgr = employee.get("reports_to","")
    if mgr and mgr != "CEO":
        nodes.append({"id":"m","label":mgr.split()[0],"size":20,"color":"#8b5cf6"})
        edges.append(("c","m"))

    reports = get_direct_reports(company_data, employee)
    for i,r in enumerate(reports[:5]):
        nid=f"d{i}"; nodes.append({"id":nid,"label":r["name"].split()[0],"size":16,"color":"#a78bfa"})
        edges.append(("c",nid))

    net = employee.get("network_position",{})
    for i,co in enumerate(net.get("key_collaborators",[])[:4]):
        nid=f"k{i}"; label=co.split("(")[0].strip().split()[0]
        nodes.append({"id":nid,"label":label,"size":12,"color":"#c4b5fd"})
        edges.append(("c",nid))

    n=len(nodes); angles=np.linspace(0,2*np.pi,n,endpoint=False)
    pos={"c":(0,0)}
    for i,nd in enumerate(nodes[1:],1):
        r=1.5 if i<=1+len(reports) else 2.2
        pos[nd["id"]]=(r*np.cos(angles[i]),r*np.sin(angles[i]))

    for s,d in edges:
        x0,y0=pos[s]; x1,y1=pos[d]
        fig.add_trace(go.Scatter(x=[x0,x1],y=[y0,y1],mode="lines",
            line=dict(color="rgba(99,102,241,.18)",width=1.5),hoverinfo="none",showlegend=False))

    for nd in nodes:
        x,y=pos[nd["id"]]
        fig.add_trace(go.Scatter(x=[x],y=[y],mode="markers+text",
            marker=dict(size=nd["size"],color=nd["color"],line=dict(width=0)),
            text=[nd["label"]],textposition="bottom center",
            textfont=dict(size=9,color="#94a3b8",family="DM Sans"),
            hoverinfo="text",showlegend=False))

    fig.update_layout(showlegend=False,height=200,margin=dict(l=0,r=0,t=0,b=0),
        xaxis=dict(showgrid=False,zeroline=False,showticklabels=False,range=[-3,3]),
        yaxis=dict(showgrid=False,zeroline=False,showticklabels=False,range=[-3,3]),
        plot_bgcolor="rgba(0,0,0,0)",paper_bgcolor="rgba(0,0,0,0)")
    return fig


# ══════════════════════════════════════════════════════════
# VIEWS
# ══════════════════════════════════════════════════════════

def view_your_reality(company_data, employee):
    """Live feed first, then connection chain, indicators + network, patterns."""
    
    # ── Hero: Live activity feed ──
    render_live_feed(employee, company_data)

    # ── How your work connects ──
    render_chain(company_data, employee)

    # ── Two columns: indicators left, network right ──
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

    # ── Patterns ──
    render_patterns(employee)


def view_org_pulse(company_data, employee):
    """Company-wide live feed — see what everyone is enabling."""
    render_org_pulse(company_data, employee)
    
    # Company goals with progress context
    goals = company_data.get("company_goals", {})
    priorities = goals.get("annual_priorities", [])
    if priorities:
        st.markdown('<div class="sec">Company Goals</div>', unsafe_allow_html=True)
        cols = st.columns(min(len(priorities), 4))
        for i, g in enumerate(priorities):
            with cols[i]:
                st.markdown(f"""<div class="goal-card">
                    <div class="goal-title">{g.get('goal','')}</div>
                    <div class="goal-target">{g.get('target','')}</div>
                </div>""", unsafe_allow_html=True)


def view_collective(company_data):
    """Company-wide overview."""

    # Mission banner
    st.markdown(f"""
    <div class="card" style="text-align:center;padding:24px 28px;">
        <div style="font-size:1.05rem;color:var(--text);font-weight:500;line-height:1.5;">
            "{company_data.get('mission','')}"
        </div>
        <div style="font-size:.78rem;color:var(--text-3);margin-top:6px;">
            {company_data.get('company_name','')} · {company_data.get('company_size','')}
        </div>
    </div>""", unsafe_allow_html=True)

    # Goals
    goals = company_data.get("company_goals", {})
    priorities = goals.get("annual_priorities", [])
    if priorities:
        st.markdown('<div class="sec">Company Goals</div>', unsafe_allow_html=True)
        cols = st.columns(min(len(priorities), 4))
        for i, g in enumerate(priorities):
            with cols[i]:
                st.markdown(f"""<div class="goal-card">
                    <div class="goal-title">{g.get('goal','')}</div>
                    <div class="goal-target">{g.get('target','')}</div>
                </div>""", unsafe_allow_html=True)

    # Financials
    fin = goals.get("financial_targets", {})
    if fin:
        st.markdown('<div class="sec">Financial Snapshot</div>', unsafe_allow_html=True)
        fmap = {"current_arr":("Current ARR",True),"target_arr":("Target ARR",True),
                "gross_margin":("Gross Margin","%"),"current_nrr":("NRR","%"),
                "burn_multiple":("Burn Multiple","x")}
        html = '<div class="fin-grid">'
        for k,(lbl,fmt) in fmap.items():
            if k in fin:
                v=fin[k]
                d=f"${v/1e6:.1f}M" if fmt is True else f"{v}{fmt}"
                html+=f'<div class="fin-item"><div class="fin-lbl">{lbl}</div><div class="fin-val">{d}</div></div>'
        html+='</div>'
        st.markdown(html, unsafe_allow_html=True)

    # Strategic bets
    bets = goals.get("strategic_bets", [])
    if bets:
        st.markdown('<div class="sec">Strategic Bets</div>', unsafe_allow_html=True)
        for b in bets:
            st.markdown(f'<div class="card" style="padding:12px 18px;margin-bottom:6px;"><span style="color:var(--accent);">◉</span> <span style="color:#cbd5e1;">{b}</span></div>', unsafe_allow_html=True)

    # Departments
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
    """Manager view — direct reports."""
    reports = get_direct_reports(company_data, employee)
    if not reports:
        st.info("No direct reports found.")
        return

    st.markdown(f'<div class="sec">Your Team · {len(reports)} direct reports</div>', unsafe_allow_html=True)
    for rpt in reports:
        mom = rpt.get("momentum",{})
        vel = mom.get("velocity","")
        mc = _mom_class(vel)
        with st.expander(f"**{rpt['name']}** — {rpt.get('role','')}"):
            st.markdown(f'<span class="mom-pill {mc}">● {vel}</span>', unsafe_allow_html=True)
            st.markdown(f"*{mom.get('direction','')}*")
            for act in rpt.get("recent_activities",[])[:2]:
                source = act.get("source", "")
                icon = _get_source_icon(source)
                st.markdown(f"""<div class="feed-item">
                    <div class="feed-source">{icon} {source}</div>
                    <div class="feed-action">{act.get('action','')}</div>
                    <div class="feed-enabled">
                        <div class="feed-enabled-label">What this enabled</div>
                        {act.get('what_it_enabled','')}
                    </div>
                </div>""", unsafe_allow_html=True)
            for w in rpt.get("behavior_patterns",{}).get("areas_to_watch",[]):
                st.markdown(f'<span class="pat-watch">⚡ {w}</span>', unsafe_allow_html=True)


def view_chat(company_data, employee):
    """Align — AI chat grounded in company context."""

    # Quick prompts
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

    # History
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Suggested question
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
            history = st.session_state.chat_history[:-1]
            response = get_align_response(prompt, company_data, employee, history)
            st.markdown(response)
    st.session_state.chat_history.append({"role": "assistant", "content": response})
    st.rerun()


# ══════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════

def main():
    companies = get_available_companies()
    if not companies:
        st.markdown("""<div style="text-align:center;padding:80px 40px;">
            <div style="font-size:2rem;margin-bottom:8px;">◉ AlignmentOS</div>
            <div style="color:var(--text-3);">Add a company JSON to <code>company_data/</code> to begin.</div>
        </div>""", unsafe_allow_html=True)
        return

    # ── Sidebar ──
    with st.sidebar:
        # Company selector (always visible)
        if len(companies) > 1:
            selected_company = st.selectbox("Company", companies, key="company_select")
        else:
            selected_company = companies[0]

    company_data = load_company(selected_company)
    if not company_data:
        st.error("Could not load company data.")
        return

    st.session_state.company_data = company_data
    employees = company_data.get("employees", [])

    # ── Sidebar: person picker ──
    with st.sidebar:
        st.markdown("### Who are you?")
        selected = st.selectbox("Name", [e["name"] for e in employees], label_visibility="collapsed")
        employee = get_employee_by_name(company_data, selected)
        st.session_state.current_employee = employee

        if "last_employee" not in st.session_state or st.session_state.last_employee != selected:
            st.session_state.chat_history = []
            st.session_state.last_employee = selected

        if employee:
            st.caption(f"{employee.get('role','')}")
            st.caption(f"{employee.get('department','')}")
            mom = employee.get("momentum",{})
            mc = _mom_class(mom.get("velocity",""))
            st.markdown(f'<span class="mom-pill {mc}">● {mom.get("velocity","")}</span>', unsafe_allow_html=True)

        st.divider()
        if st.session_state.chat_history:
            if st.button("Clear conversation"):
                st.session_state.chat_history = []
                st.rerun()

    if not employee:
        return

    # ── Top bar ──
    render_top_bar(company_data, employee)

    # ── Tabs ──
    has_reports = bool(get_direct_reports(company_data, employee))

    if has_reports:
        t1, tp, t2, t3, t4 = st.tabs(["◉  Your Reality", "🔵  Org Pulse", "👥  Team", "🌊  Collective", "💬  Align"])
    else:
        t1, tp, t3, t4 = st.tabs(["◉  Your Reality", "🔵  Org Pulse", "🌊  Collective", "💬  Align"])
        t2 = None

    with t1:
        view_your_reality(company_data, employee)
    with tp:
        view_org_pulse(company_data, employee)
    if t2:
        with t2:
            view_team(company_data, employee)
    with t3:
        view_collective(company_data)
    with t4:
        view_chat(company_data, employee)


if __name__ == "__main__":
    main()