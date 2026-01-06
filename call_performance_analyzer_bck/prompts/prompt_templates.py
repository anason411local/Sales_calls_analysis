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
   - **Incorporate AGENT PERFORMANCE OVERVIEW data** (DPAD, Conversion Rate, Payability)
   - **Top performers and their TRANSFERABLE TECHNIQUES**
   - **Correlate high DPAD agents with their call techniques**
   - **How to apply successful agents' wisdom to others**
   - Agents needing support with specific coaching points
   - Performance distribution
   - **Link payability metrics to call quality patterns**

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

9. WHAT TO SAY IN THE FIRST 5 MINUTES TO KEEP THE CUSTOMER (CRITICAL NEW SECTION):
   This is the most important section - what agents need to SAY in the first 5 minutes.
   
   **A. THE FIRST 5 MINUTES PROBLEM:**
   - Show statistics: What % of calls end before 5 minutes?
   - Why this window is critical for customer engagement
   - What happens in the first 5 minutes that determines call fate
   
   **B. COMPARISON: <5 MIN vs >5 MIN CALLS:**
   Create a detailed comparison table showing:
   | Aspect | Short Calls (<5 min) | Long Calls (>=5 min) |
   |--------|---------------------|---------------------|
   | Opening Statement | What failed | What worked |
   | Rapport Building | Missing elements | Successful elements |
   | Value Proposition | How it failed | How it succeeded |
   | Discovery Questions | What wasn't asked | What was asked |
   | Customer Response | Negative patterns | Positive patterns |
   | Turning Point | Where lost | Where engaged |
   
   **C. THE WINNING VERBIAGE - EXACT PHRASES THAT WORK:**
   List the TOP 10 key phrases that keep customers engaged with VERBATIM EXAMPLES:
   1. Opening hooks that work
   2. Rapport-building statements
   3. Value proposition phrases
   4. Discovery questions that engage
   5. Transition phrases that maintain interest
   
   **D. THE LOSING VERBIAGE - WHAT NOT TO SAY:**
   List the TOP 10 phrases/approaches that LOSE customers:
   1. Weak openings
   2. Pushy statements
   3. Missing value communication
   4. Poor question timing
   5. Phrases that trigger hang-ups
   
   **E. THE FIRST 5 MINUTES PLAYBOOK:**
   Create a step-by-step guide for agents:
   - **0-30 seconds**: What to say (with exact script)
   - **30-60 seconds**: How to build rapport (with examples)
   - **1-2 minutes**: Value proposition delivery (with verbiage)
   - **2-3 minutes**: Discovery questions (specific questions to ask)
   - **3-5 minutes**: Engagement hooks (how to keep them talking)
   
   **F. TURNING POINTS - WHERE CALLS ARE WON OR LOST:**
   Show specific examples of:
   - The exact moment customers became engaged (with quotes)
   - The exact moment customers disengaged (with quotes)
   - What triggered each turning point
   
   **G. AGENT-SPECIFIC FIRST 5 MIN TECHNIQUES:**
   For top-performing agents, extract their specific first 5 min approach:
   - Agent name + their unique opening
   - Their rapport-building technique
   - Their value proposition style
   - Their discovery question sequence
   
   **H. TRAINING RECOMMENDATIONS FOR FIRST 5 MINUTES:**
   Specific, actionable training points:
   - Scripts to practice
   - Role-play scenarios
   - Key phrases to memorize
   - Common mistakes to avoid

10. REAL EXAMPLES:
   - **A. Examples of Short Calls with Issues** (2-3 examples)
     * Include: Call ID, Agent, Duration, Issue, VERBATIM PROOF, Analysis
   - **B. Examples of Successful Long Calls** (2-3 examples)
     * Include: Call ID, Agent, Duration, Success Factors, VERBATIM PROOF, Analysis
   - **C. TRANSFERABLE WISDOM SECTION**:
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

FIRST 5 MINUTES ANALYSIS DATA (CRITICAL FOR NEW SECTION):
{first_5min_analysis}

AGENT PERFORMANCE OVERVIEW (HIGH-LEVEL BUSINESS METRICS):
{agent_performance_overview}

This data provides DPAD (Deals Per Agent Per Day), Conversion Rate, and Payability metrics.
Use this to:
- Identify which agents have highest productivity (DPAD) and correlate with their call techniques
- Understand conversion rates and how they relate to call patterns
- Analyze payability to understand revenue quality
- Cross-reference top DPAD performers with their First 5 Minutes techniques

CRITICAL REQUIREMENTS:
- Use VERBATIM QUOTES to prove every major claim
- Extract TRANSFERABLE WISDOM from successful agents
- Show HOW to implement recommendations (not just what to do)
- Keep report length manageable (~same as before, but with strategic quotes)
- Focus on ACTIONABLE insights with PROOF
- Think: "How would I train agents using this report?"
- **INTEGRATE AGENT PERFORMANCE OVERVIEW**: Correlate DPAD, Conversion Rate, and Payability with call analysis
- **IDENTIFY PATTERNS**: Link high-performing agents (by DPAD) to their specific call techniques
- **BUSINESS IMPACT**: Show how call quality affects revenue (payability metrics)

FIRST 5 MINUTES SECTION REQUIREMENTS (CRITICAL):
- This section should be HIGHLY PRACTICAL and ACTIONABLE
- Include EXACT VERBIAGE that agents should use
- Create a STEP-BY-STEP script for the first 5 minutes
- Show SIDE-BY-SIDE comparison of what works vs what fails
- Extract SPECIFIC PHRASES from successful calls
- Identify TURNING POINTS with exact quotes
- Make it TRAINING-READY - agents should be able to practice from this section
- Focus on WHAT TO SAY, not just what to do

Create a professional, well-structured Markdown report that the CEO can review and convert to Word.
Use tables, bullet points, and clear sections. Be specific and actionable.
"""

