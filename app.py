# app.py - AlignmentOS
# Entry point: page config, style injection, sidebar, tab routing.

import streamlit as st
from data_loader import get_available_companies, load_company, get_employee_by_name, get_direct_reports, get_effective_org
from ui.styles import inject_styles
from ui.components import render_top_bar, mom_class
from ui.views import view_your_reality, view_org_pulse, view_collective, view_team, view_chat
from setup_wizard import render_wizard

st.set_page_config(
    page_title="AlignmentOS",
    page_icon="◉",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(inject_styles(), unsafe_allow_html=True)

# ── Session State ──
for key, default in [("chat_history", []), ("current_employee", None), ("company_data", None)]:
    if key not in st.session_state:
        st.session_state[key] = default


def main():
    companies = get_available_companies()

    # ── Setup wizard for new installs ──
    if not companies or not st.session_state.get("authenticated"):
        render_wizard()
        return

    # ── Sidebar ──
    with st.sidebar:
        selected_company = st.selectbox("Company", companies, key="company_select") if len(companies) > 1 else companies[0]

    company_data = load_company(selected_company)
    if not company_data:
        st.error("Could not load company data.")
        return

    st.session_state.company_data = company_data
    employees = company_data.get("employees", [])

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
            mom = employee.get("momentum", {})
            mc = mom_class(mom.get("velocity", ""))
            st.markdown(f'<span class="mom-pill {mc}">● {mom.get("velocity","")}</span>', unsafe_allow_html=True)

        st.divider()
        if st.session_state.chat_history:
            if st.button("Clear conversation"):
                st.session_state.chat_history = []
                st.rerun()

    if not employee:
        return

    render_top_bar(company_data, employee)

    # ── Tab routing ──
    has_reports = bool(get_direct_reports(company_data, employee))
    is_leader = employee.get("role_level", "ic") in ("director", "vp", "c-suite")
    show_team = has_reports or is_leader
    if show_team:
        t1, tp, t2, t3, t4 = st.tabs(["◉  Your Reality", "🔵  Org Pulse", "👥  Team", "🌊  Collective", "💬  Align"])
    else:
        t1, tp, t3, t4 = st.tabs(["◉  Your Reality", "🔵  Org Pulse", "🌊  Collective", "💬  Align"])
        t2 = None  # noqa: F841

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
