# agent.py - Align: The AlignmentOS AI Layer
# Company-agnostic — builds context dynamically from loaded company data

from dotenv import load_dotenv
load_dotenv()

import anthropic
import json
from datetime import datetime

SYSTEM_PROMPT = """You are Align, the Shared Reality layer for {company_name}. You help people see how their work connects to and enables the collective.

TODAY'S DATE: {current_date}
CURRENT QUARTER: {current_quarter}

═══════════════════════════════════════════════════════════════
THE ALIGNMENTOS FRAMEWORK
═══════════════════════════════════════════════════════════════

SHARED REALITY PRINCIPLES:
1. Momentum Over Perfection — direction and velocity matter more than hitting exact numbers
2. Impact Between People — value is created in the space between contributors, not in isolation
3. Work as Network — every deliverable connects to other deliverables, teams, and outcomes
4. Patterns Matching Values — surface whether behavior patterns align with stated values
5. Compass, Not Waze — provide direction and orientation, not rigid instructions
6. Embedded in System — these principles run through every response, not bolted on
7. What Work Enabled — always answer the central question: what became possible because of this work?

COMMERCIAL PILLARS:
1. Output → Commercial Outcomes — connect work to revenue and business results, not just delivery
2. Credible Technical Pathways — show that high-performing ICs create as much value as managers
3. Top 1% Performance (exec-only) — define what exceptional looks like and why
4. Diagnosing Weak Management — pattern-based evidence, not politics
5. Business Impact of People — make the commercial value of humans legible to the business

NARRATIVE ARCHITECTURE:
Every response follows Beginning → Middle → End:
• Beginning: What you did (activity)
• Middle: How it connects (through the org, to other teams, to leading indicators)
• End: What it enabled (business outcomes, commercial impact)

═══════════════════════════════════════════════════════════════
YOUR CORE PRINCIPLES
═══════════════════════════════════════════════════════════════

1. ALWAYS ANSWER "WHAT DID THIS ENABLE?"
   Never just report what someone did. Always connect it to what it unlocked.
   
2. SHOW THE NETWORK, NOT THE LIST
   Don't present activities as a checklist. Show how they connect to others' work.

3. MOMENTUM OVER PERFECTION
   Direction and velocity matter more than exact numbers. Show trajectory.

4. PATTERNS OVER MOMENTS
   Look for consistency in behavior, not isolated wins or losses.

5. COMPASS, NOT WAZE
   Provide direction and context. Let people make decisions with full visibility.

6. RADICAL TRANSPARENCY
   Share information openly. Everyone sees their place in the whole.

7. USE LEADING INDICATORS
   Bridge the gap between daily activity and quarterly outcomes. Show work flowing through the system in near-real-time.

═══════════════════════════════════════════════════════════════
HOW YOU RESPOND
═══════════════════════════════════════════════════════════════

NEVER SAY:
• "You completed X tasks" (that's a list, not impact)
• "You're behind on your KPIs" (that's judgment, not insight)
• "Your alignment score is X%" (there are no scores in Shared Reality)
• "You need to hit your targets" (we move toward direction, not fixed points)

ALWAYS FRAME AS:
• "Your work this week enabled..." 
• "The momentum you created..."
• "Here's how your contributions rippled through the network..."
• "The pattern I see..."
• "What became possible because of you..."

WHEN SOMEONE ASKS "HOW AM I DOING?":
Don't score them. Show them:
1. What their work enabled this period
2. The momentum/velocity of their contributions
3. How their patterns align with company values
4. Their position and impact in the network
5. The leading indicators that show their work moving toward outcomes

WHEN SOMEONE ASKS ABOUT GAPS:
Don't frame as failure. Frame as:
1. Where momentum could accelerate
2. What closing the gap would enable for the collective
3. Patterns that might be creating friction
4. Experiments they could try

WHEN SOMEONE ASKS ABOUT IMPACT:
Connect their daily work to system outcomes:
1. Show the chain from their work → team → department → company goals
2. Use leading indicators to bridge daily work to eventual financial outcomes
3. Name the cross-functional connections their work created

TONE:
• Warm but clear
• Factual but human
• Direct but not judgmental
• Like a trusted colleague who sees the whole system
"""


def build_company_context(company_data):
    """Build the company context block from loaded data."""
    
    context = f"""

═══════════════════════════════════════════════════════════════
COMPANY: {company_data.get('company_name', 'Unknown')}
═══════════════════════════════════════════════════════════════

INDUSTRY: {company_data.get('industry', '')}
SIZE: {company_data.get('company_size', '')}

MISSION: {company_data.get('mission', '')}
VISION: {company_data.get('vision', '')}

VALUES:
"""
    for value in company_data.get('values', []):
        context += f"• {value['name']}: {value['behavioral_definition']}\n"
    
    # Company goals
    goals = company_data.get('company_goals', {})
    context += "\nCOMPANY GOALS:\n"
    for goal in goals.get('annual_priorities', []):
        context += f"• {goal['goal']} — {goal.get('metric', '')} → {goal.get('target', '')}\n"
    
    # Financial context
    financials = goals.get('financial_targets', {})
    if financials:
        context += f"\nFINANCIAL CONTEXT:\n"
        for key, value in financials.items():
            label = key.replace('_', ' ').title()
            if isinstance(value, (int, float)) and value > 10000:
                context += f"• {label}: ${value:,.0f}\n"
            else:
                context += f"• {label}: {value}\n"
    
    # Strategic bets
    bets = goals.get('strategic_bets', [])
    if bets:
        context += "\nSTRATEGIC BETS:\n"
        for bet in bets:
            context += f"• {bet}\n"
    
    # Departments
    context += "\nDEPARTMENTS & FOCUS:\n"
    for dept in company_data.get('departments', []):
        context += f"\n{dept['name']} ({dept.get('headcount', '?')} people, led by {dept.get('head', '?')}):\n"
        context += f"  Focus: {dept.get('strategic_focus', '')}\n"
        context += f"  Contribution to goals: {dept.get('goal_contribution', '')}\n"
        indicators = dept.get('leading_indicators', [])
        if indicators:
            context += f"  Leading indicators: {', '.join(indicators)}\n"
        deps = dept.get('dependencies', [])
        if deps:
            context += f"  Depends on: {', '.join(deps)}\n"
    
    return context


def build_person_context(company_data, employee):
    """Build the person-specific context block."""
    
    if not employee:
        return ""
    
    context = f"""

═══════════════════════════════════════════════════════════════
PERSON CONTEXT: {employee['name']}
═══════════════════════════════════════════════════════════════

ROLE: {employee.get('role', '')}
DEPARTMENT: {employee.get('department', '')}
REPORTS TO: {employee.get('reports_to', '')}
LEVEL: {employee.get('role_level', '')}

ROLE PURPOSE: {employee.get('role_purpose', '')}

KEY RESPONSIBILITIES:
"""
    for resp in employee.get('key_responsibilities', []):
        context += f"• {resp}\n"
    
    # Cross-functional connections
    connections = employee.get('cross_functional_connections', [])
    if connections:
        context += f"\nCROSS-FUNCTIONAL CONNECTIONS: {', '.join(connections)}\n"
    
    # Network position
    network = employee.get('network_position', {})
    if network:
        context += f"\nNETWORK POSITION:\n"
        context += f"Influence: {network.get('influence_description', '')}\n"
        reports = network.get('direct_reports', [])
        if reports:
            context += f"Direct reports: {', '.join(reports)}\n"
        collabs = network.get('key_collaborators', [])
        if collabs:
            context += f"Key collaborators: {', '.join(collabs)}\n"
    
    # Recent activities (Beginning)
    activities = employee.get('recent_activities', [])
    if activities:
        context += "\nRECENT WORK (Beginning — What they did):\n"
        for act in activities:
            context += f"\n• {act.get('action', '')}\n"
            context += f"  Detail: {act.get('detail', '')}\n"
            context += f"  Date: {act.get('date', '')}\n"
            context += f"  What it enabled: {act.get('what_it_enabled', '')}\n"
    
    # Leading indicators (Middle)
    indicators = employee.get('leading_indicators', {})
    if indicators:
        context += "\nLEADING INDICATORS (Middle — How work connects to outcomes):\n"
        for key, val in indicators.items():
            label = key.replace('_', ' ').title()
            if isinstance(val, dict):
                current = val.get('current', '')
                target = val.get('target', '')
                trend = val.get('trend', '')
                unit = val.get('unit', '')
                context += f"• {label}: {current} {unit} → {target} {unit} | Trend: {trend}\n"
            else:
                context += f"• {label}: {val}\n"
    
    # Momentum
    momentum = employee.get('momentum', {})
    if momentum:
        context += f"\nMOMENTUM:\n"
        context += f"Velocity: {momentum.get('velocity', '')}\n"
        context += f"Direction: {momentum.get('direction', '')}\n"
        context += f"Pattern: {momentum.get('pattern', '')}\n"
    
    # Behavior patterns
    patterns = employee.get('behavior_patterns', {})
    if patterns:
        context += "\nBEHAVIOR PATTERNS (Patterns Matching Values):\n"
        context += "Values-aligned:\n"
        for p in patterns.get('values_aligned', []):
            context += f"  ✓ {p}\n"
        context += "Areas to watch:\n"
        for p in patterns.get('areas_to_watch', []):
            context += f"  ⚡ {p}\n"
    
    # Build the enablement chain summary
    dept_name = employee.get('department', '')
    dept = None
    for d in company_data.get('departments', []):
        if d.get('name') == dept_name:
            dept = d
            break
    
    if dept:
        goals = company_data.get('company_goals', {})
        context += f"""

ENABLEMENT CHAIN (How this person's work connects to business outcomes):
Work → {dept.get('strategic_focus', '')} → {dept.get('goal_contribution', '')}
"""
        for goal in goals.get('annual_priorities', []):
            context += f"  Company goal: {goal['goal']} ({goal.get('target', '')})\n"
    
    return context


def get_align_response(user_message, company_data, employee=None, conversation_history=None):
    """Get a response from Align, the Shared Reality agent."""
    
    client = anthropic.Anthropic()
    
    company_name = company_data.get('company_name', 'Unknown Company')
    current_date = datetime.now().strftime("%B %d, %Y")
    current_quarter = company_data.get('current_quarter', 'Q1 2026')
    
    # Build full system prompt
    full_prompt = SYSTEM_PROMPT.format(
        company_name=company_name,
        current_date=current_date,
        current_quarter=current_quarter
    )
    
    # Add company context
    full_prompt += build_company_context(company_data)
    
    # Add person context if available
    if employee:
        full_prompt += build_person_context(company_data, employee)
    
    # Build messages
    messages = []
    if conversation_history:
        messages.extend(conversation_history)
    messages.append({"role": "user", "content": str(user_message)})
    
    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1500,
            system=full_prompt,
            messages=messages
        )
        return response.content[0].text
    except Exception as e:
        return f"Error connecting to AI: {str(e)}\n\nMake sure your ANTHROPIC_API_KEY is set in your .env file."


# Backward compatibility
get_shared_reality_response = get_align_response
