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
   - Critical issues identified
   - Top recommendations

2. AGENT-LEVEL PERFORMANCE:
   - Individual agent analysis
   - Top performers and their techniques
   - Agents needing support
   - Performance distribution

3. CALL PATTERN ANALYSIS:
   - Short calls (<2 min) vs Long calls (>=2 min)
   - Why short calls fail
   - What makes long calls successful
   - Common objections and handling

4. LGS vs OMC ANALYSIS:
   - LGS handoff quality
   - Issues originating from LGS
   - OMC performance issues
   - Handoff improvement opportunities

5. DAILY TRENDS:
   - Performance by date
   - Patterns over time
   - Peak performance periods

6. STATUS/OUTCOME ANALYSIS:
   - Breakdown by call outcome
   - Duration by status
   - Success patterns

7. RECOMMENDATIONS:
   - Immediate actions (quick wins)
   - Training recommendations
   - Process improvements
   - Long-term strategic changes

8. REAL EXAMPLES:
   - Include 3-5 examples of short calls with issues
   - Include 3-5 examples of successful long calls
   - Use actual quotes and specifics

ACCUMULATED INSIGHTS:
{accumulated_insights}

AGENT PERFORMANCE DATA:
{agent_performance}

DAILY TRENDS DATA:
{daily_trends}

STATUS ANALYSIS DATA:
{status_analysis}

Create a professional, well-structured Markdown report that the CEO can review and convert to Word.
Use tables, bullet points, and clear sections. Be specific and actionable.
"""

