"""
Prompt templates for call performance analysis
"""
from langchain_core.prompts import ChatPromptTemplate
from pathlib import Path

# Load system instructions
PROMPTS_DIR = Path(__file__).parent
with open(PROMPTS_DIR / "system_instructions.txt", "r", encoding="utf-8") as f:
    SYSTEM_INSTRUCTIONS = f.read()

with open(PROMPTS_DIR / "analysis_prompt.txt", "r", encoding="utf-8") as f:
    ANALYSIS_PROMPT = f.read()

# Create chat prompt template
CALL_ANALYSIS_PROMPT = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_INSTRUCTIONS),
    ("human", ANALYSIS_PROMPT)
])

# Report generation prompt
REPORT_GENERATION_PROMPT = """
You are a senior business analyst creating an executive report for the CEO of 411 Locals.

You have analyzed {total_calls} sales calls. Now create a comprehensive, professional report that:

1. EXECUTIVE SUMMARY:
   - High-level overview of findings
   - Key metrics and trends
   - **Critical issues identified WITH PROOF** (include 1-2 verbatim examples)
   - **Top recommendations WITH IMPLEMENTATION EXAMPLES**

2. AGENT-LEVEL PERFORMANCE:
   - Individual agent analysis with tables
   - **Top performers and their TRANSFERABLE TECHNIQUES**
   - **How to apply successful agents' wisdom to others**
   - Agents needing support with specific coaching points
   - Performance distribution

3. CALL PATTERN ANALYSIS:
   - Short calls (<5 min) vs Long calls (>=5 min)
   - **Why short calls fail WITH VERBATIM PROOF** (1-2 critical moment quotes)
   - **What makes long calls successful WITH VERBATIM PROOF** (1-2 technique examples)
   - Common objections and handling WITH EXAMPLES

4. LEAD QUALITY IMPACT ANALYSIS:
   - How lead quality (company info, services, address) affects call duration
   - Impact of call attempts vs. successful connections on outcomes
   - Patterns in customer demographics and call success
   - Service type correlations with call duration and outcomes

5. LGS vs OMC ANALYSIS:
   - LGS handoff quality
   - Issues originating from LGS WITH PROOF
   - OMC performance issues WITH PROOF
   - Handoff improvement opportunities WITH EXAMPLES

6. DAILY TRENDS:
   - Performance by date (table format)
   - Patterns over time
   - Peak performance periods

7. STATUS/OUTCOME ANALYSIS:
   - Breakdown by call outcome (table format)
   - Duration by status
   - Success patterns

8. RECOMMENDATIONS:
   - **A. Immediate Actions** (with specific examples of how to implement)
   - **B. Training Recommendations** (with transferable techniques from successful agents)
   - **C. Process Improvements** (with before/after examples)
   - **D. Lead Quality Improvements** (how to better qualify and prepare leads)
   - **E. Long-term Strategic Changes**

9. REAL EXAMPLES:
   - **A. Examples of Short Calls with Issues** (2-3 examples)
     * Include: Call ID, Agent, Duration, Issue, VERBATIM PROOF, Analysis
   - **B. Examples of Successful Long Calls** (2-3 examples)
     * Include: Call ID, Agent, Duration, Success Factors, VERBATIM PROOF, Analysis
   - **C. TRANSFERABLE WISDOM SECTION** (NEW):
     * Extract the "playbook" from successful agents
     * Show HOW to apply their techniques to other agents
     * Include persona insights (what makes them effective)

ACCUMULATED INSIGHTS:
{accumulated_insights}

AGENT PERFORMANCE DATA:
{agent_performance}

DAILY TRENDS DATA:
{daily_trends}

STATUS ANALYSIS DATA:
{status_analysis}

CRITICAL REQUIREMENTS:
- Use VERBATIM QUOTES to prove every major claim
- Extract TRANSFERABLE WISDOM from successful agents
- Show HOW to implement recommendations (not just what to do)
- Keep report length manageable (~same as before, but with strategic quotes)
- Focus on ACTIONABLE insights with PROOF
- Think: "How would I train agents using this report?"

Create a professional, well-structured Markdown report that the CEO can review and convert to Word.
Use tables, bullet points, and clear sections. Be specific and actionable.
"""

