# ui/styles.py
# Full design system CSS. Inject once at app startup via inject_styles().

CSS_STYLES = """
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
#MainMenu, footer { visibility: hidden; }

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
"""


def inject_styles():
    return CSS_STYLES
