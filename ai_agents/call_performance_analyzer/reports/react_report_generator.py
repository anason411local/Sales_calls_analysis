"""
ReAct Report Generator - Full Reasoning + Acting Pattern
Generates high-quality reports with organic ML + Agentic AI blending
"""
from typing import Dict, List, Optional
from graph.state import AnalysisState
from utils.logger import logger
from utils.gemini_client import get_report_llm
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import json
from datetime import datetime
from pathlib import Path


class ReActReportGenerator:
    """
    ReAct Pattern Report Generator
    
    REASONING Phase: Analyzes data, identifies patterns, plans structure
    ACTING Phase: Generates sections iteratively with ML blending
    VALIDATION Phase: Ensures quality and consistency
    """
    
    def __init__(self):
        self.llm = get_report_llm()
        logger.info("ReAct Report Generator initialized")
    
    def generate_report(self, state: AnalysisState) -> str:
        """
        Main entry point: Generate comprehensive report using ReAct pattern
        
        Args:
            state: Analysis state with all accumulated data
            
        Returns:
            Markdown formatted report
        """
        logger.info("=" * 80)
        logger.info("REACT REPORT GENERATOR: STARTING")
        logger.info("=" * 80)
        
        try:
            # ============================================================
            # PHASE 1: REASONING - Analyze and Plan
            # ============================================================
            logger.info("PHASE 1: REASONING - Analyzing data and planning report structure")
            
            reasoning_result = self._reasoning_phase(state)
            
            # ============================================================
            # PHASE 2: ACTING - Generate Sections
            # ============================================================
            logger.info("PHASE 2: ACTING - Generating report sections with ML blending")
            
            sections = self._acting_phase(state, reasoning_result)
            
            # ============================================================
            # PHASE 3: VALIDATION - Quality Check
            # ============================================================
            logger.info("PHASE 3: VALIDATION - Ensuring quality and consistency")
            
            final_report = self._validation_phase(sections, state)
            
            logger.info("REACT REPORT GENERATOR: COMPLETE")
            logger.info("=" * 80)
            
            return final_report
            
        except Exception as e:
            logger.error(f"Error in ReAct report generation: {str(e)}")
            return self._generate_fallback_report(state)
    
    def _reasoning_phase(self, state: AnalysisState) -> Dict:
        """
        REASONING PHASE: Analyze data, identify patterns, plan structure
        
        Steps:
        1. Analyze call insights
        2. Analyze ML data
        3. Identify correlations
        4. Prioritize insights
        5. Plan report structure
        
        Returns:
            Dictionary with reasoning results
        """
        logger.info("  Step 1/5: Analyzing call insights...")
        call_analysis = self._analyze_call_insights(state)
        
        logger.info("  Step 2/5: Analyzing ML data...")
        ml_analysis = self._analyze_ml_data(state)
        
        logger.info("  Step 3/5: Identifying correlations between AI and ML...")
        correlations = self._identify_correlations(call_analysis, ml_analysis)
        
        logger.info("  Step 4/5: Prioritizing insights...")
        priorities = self._prioritize_insights(correlations, state)
        
        logger.info("  Step 5/5: Planning report structure...")
        structure = self._plan_structure(priorities)
        
        return {
            'call_analysis': call_analysis,
            'ml_analysis': ml_analysis,
            'correlations': correlations,
            'priorities': priorities,
            'structure': structure
        }
    
    def _acting_phase(self, state: AnalysisState, reasoning: Dict) -> Dict[str, str]:
        """
        ACTING PHASE: Generate each section with organic ML blending
        
        Args:
            state: Analysis state
            reasoning: Results from reasoning phase
            
        Returns:
            Dictionary of section name -> content
        """
        sections = {}
        
        # Generate each section
        section_generators = [
            ('executive_summary', self._generate_executive_summary),
            ('agent_performance', self._generate_agent_performance),
            ('call_patterns', self._generate_call_patterns),
            ('lead_quality', self._generate_lead_quality),
            ('lgs_omc_analysis', self._generate_lgs_omc_analysis),
            ('daily_trends', self._generate_daily_trends),
            ('status_analysis', self._generate_status_analysis),
            ('script_compliance', self._generate_script_compliance),  # NEW SECTION
            ('recommendations', self._generate_recommendations),
            ('real_examples', self._generate_real_examples)
        ]
        
        for section_name, generator_func in section_generators:
            logger.info(f"  Generating: {section_name}")
            try:
                sections[section_name] = generator_func(state, reasoning)
            except Exception as e:
                logger.error(f"Error generating {section_name}: {str(e)}")
                sections[section_name] = f"## {section_name.replace('_', ' ').title()}\n\n*Section unavailable*\n"
        
        return sections
    
    def _validation_phase(self, sections: Dict[str, str], state: AnalysisState) -> str:
        """
        VALIDATION PHASE: Assemble and validate final report
        
        Args:
            sections: Generated sections
            state: Analysis state
            
        Returns:
            Final report string
        """
        # Assemble report
        report_parts = []
        
        # Title
        report_parts.append("# Executive Sales Performance Report: Call Analysis with ML Insights\n")
        report_parts.append("**To:** CEO, 411 Locals")
        report_parts.append("**From:** Senior Business Analyst")
        report_parts.append(f"**Date:** {datetime.now().strftime('%B %d, %Y')}")
        report_parts.append("**Subject:** Comprehensive Call Performance Analysis (Agentic AI + Machine Learning)\n")
        report_parts.append("---\n")
        
        # Add sections in order
        section_order = [
            'executive_summary',
            'agent_performance',
            'call_patterns',
            'lead_quality',
            'lgs_omc_analysis',
            'daily_trends',
            'status_analysis',
            'script_compliance',  # NEW SECTION
            'recommendations',
            'real_examples'
        ]
        
        for section_name in section_order:
            if section_name in sections:
                report_parts.append(sections[section_name])
                report_parts.append("\n---\n")
        
        # Add metadata footer
        report_parts.append(f"\n*Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
        report_parts.append(f"*Total calls analyzed: {len(state['all_insights'])}*")
        report_parts.append(f"*Analysis period: {self._get_date_range(state)}*")
        report_parts.append("*Analysis Method: Agentic AI + Machine Learning (ReAct Pattern)*\n")
        
        return "\n".join(report_parts)
    
    # ============================================================
    # HELPER METHODS FOR ML FALLBACK
    # ============================================================
    
    def _create_prompt_with_ml_fallback(self, system_with_ml: str, system_without_ml: str, 
                                       human_with_ml: str, human_without_ml: str, 
                                       ml_available: bool) -> ChatPromptTemplate:
        """
        Create a prompt template that handles ML availability
        
        Args:
            system_with_ml: System message when ML is available
            system_without_ml: System message when ML is not available
            human_with_ml: Human message when ML is available
            human_without_ml: Human message when ML is not available
            ml_available: Whether ML data is available
            
        Returns:
            ChatPromptTemplate configured for ML availability
        """
        if ml_available:
            return ChatPromptTemplate.from_messages([
                ("system", system_with_ml),
                ("human", human_with_ml)
            ])
        else:
            return ChatPromptTemplate.from_messages([
                ("system", system_without_ml),
                ("human", human_without_ml)
            ])
    
    # ============================================================
    # REASONING PHASE METHODS
    # ============================================================
    
    def _analyze_call_insights(self, state: AnalysisState) -> Dict:
        """Analyze accumulated call insights - COMPREHENSIVE VERSION"""
        total_calls = len(state['all_insights'])
        short_calls = sum(1 for i in state['all_insights'] if i.is_short_call)
        long_calls = total_calls - short_calls
        
        # Collect comprehensive patterns (like old report generator)
        all_short_reasons = []
        all_success_factors = []
        all_transferable_techniques = []
        critical_moments_short = []
        critical_moments_success = []
        lgs_issues = state.get('lgs_issues', [])
        omc_issues = state.get('omc_issues', [])
        
        for insight in state['all_insights']:
            if insight.is_short_call and insight.early_termination_reasons:
                all_short_reasons.extend(insight.early_termination_reasons)
                # Collect proof of issues with quotes
                if insight.proof_of_issue:
                    critical_moments_short.append({
                        'call_id': insight.call_id,
                        'agent': insight.omc_agent,
                        'proof': insight.proof_of_issue,
                        'critical_moment': insight.critical_moment_quote
                    })
            
            if not insight.is_short_call and insight.success_factors:
                all_success_factors.extend(insight.success_factors)
                # Collect transferable wisdom
                if insight.transferable_technique:
                    all_transferable_techniques.append({
                        'call_id': insight.call_id,
                        'agent': insight.omc_agent,
                        'technique': insight.transferable_technique,
                        'application': insight.technique_application,
                        'persona': insight.agent_persona_insight,
                        'proof': insight.proof_of_success
                    })
                # Collect success proofs
                if insight.proof_of_success:
                    critical_moments_success.append({
                        'call_id': insight.call_id,
                        'agent': insight.omc_agent,
                        'proof': insight.proof_of_success,
                        'critical_moment': insight.critical_moment_quote
                    })
        
        # Get example calls
        example_short_calls = state.get('example_short_calls', [])[:3]
        example_successful_calls = state.get('example_successful_calls', [])[:3]
        
        return {
            'total_calls': total_calls,
            'short_calls': short_calls,
            'long_calls': long_calls,
            'short_rate': (short_calls / total_calls * 100) if total_calls > 0 else 0,
            'top_short_reasons': self._get_top_items(all_short_reasons, 10),
            'top_success_factors': self._get_top_items(all_success_factors, 10),
            'lgs_issues': self._get_top_items(lgs_issues, 10),
            'omc_issues': self._get_top_items(omc_issues, 10),
            'critical_moments_short': critical_moments_short[:5],
            'critical_moments_success': critical_moments_success[:5],
            'transferable_techniques': all_transferable_techniques[:5],
            'example_short_calls': example_short_calls,
            'example_successful_calls': example_successful_calls,
            'short_call_patterns': state.get('short_call_patterns', []),
            'long_call_patterns': state.get('long_call_patterns', [])
        }
    
    def _analyze_ml_data(self, state: AnalysisState) -> Dict:
        """Analyze ML insights - with fallback if ML data is missing"""
        ml_insights = state.get('ml_insights')
        
        # Check if ML insights are available and valid
        if not ml_insights:
            logger.warning("ML insights not available - continuing without ML validation")
            return {
                'available': False,
                'reason': 'ML insights not found in state'
            }
        
        # Check if ML insights have actual data
        if not ml_insights.top_variables and not ml_insights.key_insights:
            logger.warning("ML insights empty - continuing without ML validation")
            return {
                'available': False,
                'reason': 'ML insights contain no data'
            }
        
        logger.info("ML insights available - will blend with agentic AI analysis")
        return {
            'available': True,
            'top_variables': ml_insights.top_variables[:10] if ml_insights.top_variables else [],
            'statistical_summary': ml_insights.statistical_summary or 'N/A',
            'agent_performance': ml_insights.agent_performance_insights or {},
            'call_patterns': ml_insights.call_pattern_insights or {},
            'lead_quality': ml_insights.lead_quality_insights or {},
            'lgs_omc': ml_insights.lgs_omc_insights or {},
            'recommendations': ml_insights.recommendations_insights or {}
        }
    
    def _identify_correlations(self, call_analysis: Dict, ml_analysis: Dict) -> Dict:
        """Identify where AI and ML findings agree/disagree"""
        correlations = {
            'agreements': [],
            'ml_validations': [],
            'new_ml_insights': []
        }
        
        if not ml_analysis.get('available'):
            return correlations
        
        # Check if ML validates AI findings
        # Example: If AI found "discovery questions" important, check if ML agrees
        if 'discovery' in str(call_analysis.get('top_success_factors', [])).lower():
            if any('discovery' in var.lower() for var in ml_analysis.get('top_variables', [])):
                correlations['agreements'].append({
                    'finding': 'Discovery questions drive call success',
                    'ai_evidence': 'Identified in successful call patterns',
                    'ml_evidence': 'High ML importance score'
                })
        
        return correlations
    
    def _prioritize_insights(self, correlations: Dict, state: AnalysisState) -> Dict:
        """Prioritize insights by impact and evidence"""
        return {
            'critical_issues': [],  # Issues with both AI + ML evidence
            'high_impact': [],  # High ML importance
            'actionable': []  # Can be trained/improved
        }
    
    def _plan_structure(self, priorities: Dict) -> Dict:
        """Plan report structure based on priorities"""
        return {
            'emphasis_sections': ['agent_performance', 'call_patterns'],
            'include_ml_visualizations': True,
            'detail_level': 'executive'
        }
    
    # ============================================================
    # ACTING PHASE METHODS - Section Generators
    # ============================================================
    
    def _generate_executive_summary(self, state: AnalysisState, reasoning: Dict) -> str:
        """Generate Executive Summary with ML blending (if available)"""
        
        # Check if ML is available
        ml_available = reasoning['ml_analysis'].get('available', False)
        
        if ml_available:
            system_msg = """You are a senior business analyst creating an executive summary.
            
Blend Agentic AI findings with ML insights organically. Don't create separate sections.
Use inline integration like: "Analysis shows X (ML Validation: variable Y has 0.85 correlation)"

Be concise, executive-level, and focus on actionable insights."""
            
            human_msg = """Create an EXECUTIVE SUMMARY section for a call performance report.

AGENTIC AI ANALYSIS:
- Total Calls: {total_calls}
- Short Calls (<5 min): {short_calls} ({short_rate:.1f}%)
- Long Calls (>=5 min): {long_calls}
- Top reasons for short calls: {top_short_reasons}
- Top success factors: {top_success_factors}

LGS ISSUES IDENTIFIED:
{lgs_issues}

CRITICAL MOMENTS - SHORT CALLS (With Proof):
{critical_moments_short}

CRITICAL MOMENTS - SUCCESSFUL CALLS (With Proof):
{critical_moments_success}

TRANSFERABLE WISDOM FROM SUCCESSFUL AGENTS:
{transferable_techniques}

ML INSIGHTS:
{ml_summary}

Top ML Variables: {ml_top_vars}

REQUIREMENTS:
1. High-level overview
2. Key metrics with ML validation
3. Critical issues WITH PROOF (use verbatim quotes from critical moments)
4. Top 3 recommendations

Use inline ML integration. Example:
"Short calls fail primarily due to poor LGS handoffs (mentioned 45 times). **ML Validation**: `LQ_Company_Address` (correlation: 0.842) confirms incomplete lead data significantly reduces call duration."

Generate the section:"""
        else:
            # Fallback prompt without ML
            system_msg = """You are a senior business analyst creating an executive summary.

Focus on agentic AI analysis findings. Be concise, executive-level, and actionable.

NOTE: ML validation data is not available for this report."""
            
            human_msg = """Create an EXECUTIVE SUMMARY section for a call performance report.

AGENTIC AI ANALYSIS:
- Total Calls: {total_calls}
- Short Calls (<5 min): {short_calls} ({short_rate:.1f}%)
- Long Calls (>=5 min): {long_calls}
- Top reasons for short calls: {top_short_reasons}
- Top success factors: {top_success_factors}

LGS ISSUES IDENTIFIED:
{lgs_issues}

CRITICAL MOMENTS - SHORT CALLS (With Proof):
{critical_moments_short}

CRITICAL MOMENTS - SUCCESSFUL CALLS (With Proof):
{critical_moments_success}

TRANSFERABLE WISDOM FROM SUCCESSFUL AGENTS:
{transferable_techniques}

REQUIREMENTS:
1. High-level overview
2. Key metrics from call analysis
3. Critical issues WITH PROOF (use verbatim quotes from critical moments)
4. Top 3 recommendations

NOTE: ML validation is not available. Focus on agentic AI insights and verbatim evidence.

Generate the section:"""
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_msg),
            ("human", human_msg)
        ])
        
        chain = prompt | self.llm | StrOutputParser()
        
        # Prepare data
        call_analysis = reasoning['call_analysis']
        ml_analysis = reasoning['ml_analysis']
        
        # Get critical moments
        critical_moments = []
        for insight in state['all_insights'][:5]:
            if insight.proof_of_issue or insight.proof_of_success:
                critical_moments.append({
                    'call_id': insight.call_id,
                    'agent': insight.omc_agent,
                    'proof': insight.proof_of_issue or insight.proof_of_success
                })
        
        # Prepare invoke parameters with comprehensive data
        invoke_params = {
            'total_calls': call_analysis['total_calls'],
            'short_calls': call_analysis['short_calls'],
            'long_calls': call_analysis['long_calls'],
            'short_rate': call_analysis['short_rate'],
            'top_short_reasons': call_analysis['top_short_reasons'],
            'top_success_factors': call_analysis['top_success_factors'],
            'lgs_issues': call_analysis['lgs_issues'],
            'critical_moments_short': json.dumps(call_analysis['critical_moments_short'], indent=2),
            'critical_moments_success': json.dumps(call_analysis['critical_moments_success'], indent=2),
            'transferable_techniques': json.dumps(call_analysis['transferable_techniques'], indent=2)
        }
        
        # Add ML parameters only if available
        if ml_available:
            invoke_params['ml_summary'] = ml_analysis.get('statistical_summary', 'N/A')
            invoke_params['ml_top_vars'] = ', '.join(ml_analysis.get('top_variables', [])[:5])
        
        result = chain.invoke(invoke_params)
        
        # Add note if ML is not available
        ml_note = ""
        if not ml_available:
            ml_note = "\n\n*Note: ML validation data is not available for this report. Analysis is based on agentic AI insights.*\n"
        
        return f"## 1. EXECUTIVE SUMMARY\n\n{result}{ml_note}\n"
    
    def _generate_agent_performance(self, state: AnalysisState, reasoning: Dict) -> str:
        """Generate Agent Performance section with ML blending (if available)"""
        
        ml_available = reasoning['ml_analysis'].get('available', False)
        
        if ml_available:
            system_msg = """You are a senior business analyst analyzing agent performance.

Blend ML insights INLINE. Example:
"DARWINSANCHEZ24 shows strong performance with 420s avg duration. **ML Insight**: His success correlates with high `total_discovery_questions` (ML Importance: 0.783, Rank #2), asking 8-12 questions vs team average of 3-4."

Include ML visualizations where relevant."""
            
            human_msg = """Create an AGENT-LEVEL PERFORMANCE section.

AGENT DATA:
{agent_data}

ML INSIGHTS FOR AGENT PERFORMANCE:
{ml_agent_insights}

ML VISUALIZATION:
{ml_viz_path}

REQUIREMENTS:
1. Agent performance table (sorted by short call rate)
2. Top performers with TRANSFERABLE TECHNIQUES
3. ML validation of successful techniques
4. Agents needing support with specific coaching
5. Embed visualization if available: ![Agent Performance ML Analysis]({ml_viz_path})

Generate the section:"""
        else:
            system_msg = """You are a senior business analyst analyzing agent performance.

Focus on agentic AI analysis. Identify patterns and provide actionable coaching recommendations.

NOTE: ML validation data is not available."""
            
            human_msg = """Create an AGENT-LEVEL PERFORMANCE section.

AGENT DATA:
{agent_data}

REQUIREMENTS:
1. Agent performance table (sorted by short call rate)
2. Top performers with TRANSFERABLE TECHNIQUES
3. Agents needing support with specific coaching
4. Focus on call insights and patterns

NOTE: ML validation is not available. Base analysis on call performance data.

Generate the section:"""
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_msg),
            ("human", human_msg)
        ])
        
        chain = prompt | self.llm | StrOutputParser()
        
        # Prepare agent data
        agent_data = self._prepare_agent_performance_data(state)
        ml_analysis = reasoning['ml_analysis']
        
        # Prepare invoke parameters
        invoke_params = {'agent_data': agent_data}
        
        # Add ML parameters only if available
        if ml_available:
            ml_agent_insights = ml_analysis.get('agent_performance', {})
            ml_viz_path = ml_agent_insights.get('visualization_path', '')
            invoke_params['ml_agent_insights'] = json.dumps(ml_agent_insights, indent=2)
            invoke_params['ml_viz_path'] = ml_viz_path
        
        result = chain.invoke(invoke_params)
        
        return f"## 2. AGENT-LEVEL PERFORMANCE\n\n{result}\n"
    
    def _generate_call_patterns(self, state: AnalysisState, reasoning: Dict) -> str:
        """Generate Call Patterns section with ML blending (if available)"""
        
        ml_available = reasoning['ml_analysis'].get('available', False)
        
        system_with_ml = """You are analyzing call patterns with ML validation.

Inline ML integration example:
"Short calls fail due to lack of discovery questions. **ML Confirmation**: `total_discovery_questions` is the #2 predictor of call duration (Combined Score: 0.783). Calls with <3 questions average 180s vs >8 questions averaging 520s."

Include SHAP visualization to show variable impact."""
        
        system_without_ml = """You are analyzing call patterns using agentic AI insights.

Focus on verbatim evidence and patterns from call analysis.

NOTE: ML validation data is not available."""
        
        human_with_ml = """Create a CALL PATTERN ANALYSIS section.

CALL INSIGHTS:
- Short calls: {short_calls} ({short_rate:.1f}%)
- Long calls: {long_calls}
- Top short call reasons: {short_reasons}
- Top success factors: {success_factors}

SHORT CALL PATTERNS:
{short_call_patterns}

LONG CALL PATTERNS:
{long_call_patterns}

EXAMPLE SHORT CALLS (with issues):
{example_short_calls}

EXAMPLE SUCCESSFUL CALLS:
{example_successful_calls}

ML CALL PATTERN INSIGHTS:
{ml_pattern_insights}

ML VISUALIZATION:
{ml_viz_path}

REQUIREMENTS:
1. Why short calls fail WITH VERBATIM PROOF (use example calls)
2. What makes long calls successful WITH VERBATIM PROOF (use example calls)
3. ML validation of patterns
4. Common objections and handling
5. Embed SHAP or effect size visualization

Generate the section:"""
        
        human_without_ml = """Create a CALL PATTERN ANALYSIS section.

CALL INSIGHTS:
- Short calls: {short_calls} ({short_rate:.1f}%)
- Long calls: {long_calls}
- Top short call reasons: {short_reasons}
- Top success factors: {success_factors}

REQUIREMENTS:
1. Why short calls fail WITH VERBATIM PROOF
2. What makes long calls successful WITH VERBATIM PROOF
3. Common objections and handling
4. Pattern identification from call data

NOTE: ML validation is not available. Focus on call analysis patterns.

Generate the section:"""
        
        prompt = self._create_prompt_with_ml_fallback(
            system_with_ml, system_without_ml,
            human_with_ml, human_without_ml,
            ml_available
        )
        
        chain = prompt | self.llm | StrOutputParser()
        
        call_analysis = reasoning['call_analysis']
        ml_analysis = reasoning['ml_analysis']
        
        # Prepare invoke parameters with comprehensive data
        invoke_params = {
            'short_calls': call_analysis['short_calls'],
            'long_calls': call_analysis['long_calls'],
            'short_rate': call_analysis['short_rate'],
            'short_reasons': call_analysis['top_short_reasons'],
            'success_factors': call_analysis['top_success_factors'],
            'short_call_patterns': json.dumps(call_analysis['short_call_patterns'], indent=2),
            'long_call_patterns': json.dumps(call_analysis['long_call_patterns'], indent=2),
            'example_short_calls': json.dumps([{
                'call_id': getattr(c, 'call_id', 'N/A'),
                'agent': getattr(c, 'omc_agent', 'N/A'),
                'duration': getattr(c, 'omc_duration', 0),
                'reasons': getattr(c, 'early_termination_reasons', []),
                'proof': getattr(c, 'proof_of_issue', 'N/A')
            } for c in call_analysis['example_short_calls'] if c], indent=2),
            'example_successful_calls': json.dumps([{
                'call_id': getattr(c, 'call_id', 'N/A'),
                'agent': getattr(c, 'omc_agent', 'N/A'),
                'duration': getattr(c, 'omc_duration', 0),
                'factors': getattr(c, 'success_factors', []),
                'proof': getattr(c, 'proof_of_success', 'N/A')
            } for c in call_analysis['example_successful_calls'] if c], indent=2)
        }
        
        # Add ML parameters only if available
        if ml_available:
            ml_pattern_insights = ml_analysis.get('call_patterns', {})
            invoke_params['ml_pattern_insights'] = json.dumps(ml_pattern_insights, indent=2)
            invoke_params['ml_viz_path'] = ml_pattern_insights.get('visualization_path', '')
        
        result = chain.invoke(invoke_params)
        
        return f"## 3. CALL PATTERN ANALYSIS\n\n{result}\n"
    
    def _generate_lead_quality(self, state: AnalysisState, reasoning: Dict) -> str:
        """Generate Lead Quality section with ML blending (if available)"""
        
        ml_available = reasoning['ml_analysis'].get('available', False)
        
        system_with_ml = """Analyze lead quality impact with strong ML evidence.

Example inline integration:
"Lead quality dramatically impacts call duration. **ML Evidence**: `LQ_Company_Address` (0.842 correlation), `LQ_Customer_Name` (0.833), and `LQ_Service` (0.795) are among the top 5 predictors. Calls with complete lead data average 480s vs incomplete averaging 210s."

Include correlation visualization."""
        
        system_without_ml = """Analyze lead quality impact based on call analysis patterns.

Focus on observed patterns between lead data completeness and call outcomes.

NOTE: ML correlation data is not available."""
        
        human_with_ml = """Create a LEAD QUALITY IMPACT ANALYSIS section.

ML LEAD QUALITY INSIGHTS:
{ml_lead_insights}

ML VISUALIZATION:
{ml_viz_path}

REQUIREMENTS:
1. How lead quality affects call duration (with ML evidence)
2. Impact of call attempts vs connections
3. Service type correlations
4. Embed correlation visualization

Generate the section:"""
        
        human_without_ml = """Create a LEAD QUALITY IMPACT ANALYSIS section.

CALL ANALYSIS PATTERNS:
- Observe patterns in lead data completeness
- Impact on call duration and outcomes
- Service type patterns

REQUIREMENTS:
1. How lead quality affects call duration (based on observations)
2. Impact of call attempts vs connections
3. Service type correlations
4. Recommendations for lead quality improvement

NOTE: ML correlation data is not available. Base analysis on call patterns.

Generate the section:"""
        
        prompt = self._create_prompt_with_ml_fallback(
            system_with_ml, system_without_ml,
            human_with_ml, human_without_ml,
            ml_available
        )
        
        chain = prompt | self.llm | StrOutputParser()
        
        ml_analysis = reasoning['ml_analysis']
        
        # Prepare invoke parameters
        invoke_params = {}
        
        # Add ML parameters only if available
        if ml_available:
            ml_lead_insights = ml_analysis.get('lead_quality', {})
            invoke_params['ml_lead_insights'] = json.dumps(ml_lead_insights, indent=2)
            invoke_params['ml_viz_path'] = ml_lead_insights.get('visualization_path', '')
        
        result = chain.invoke(invoke_params)
        
        return f"## 4. LEAD QUALITY IMPACT ANALYSIS\n\n{result}\n"
    
    def _generate_lgs_omc_analysis(self, state: AnalysisState, reasoning: Dict) -> str:
        """Generate LGS vs OMC section with ML blending"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", """Analyze LGS/OMC handoff with evidence.

Inline ML where relevant. Focus on verbatim proof of issues."""),
            ("human", """Create an LGS vs OMC ANALYSIS section.

LGS ISSUES:
{lgs_issues}

ML INSIGHTS:
{ml_lgs_omc_insights}

REQUIREMENTS:
1. LGS handoff quality
2. Issues from LGS WITH PROOF
3. OMC performance issues WITH PROOF
4. Handoff improvement opportunities

Generate the section:""")
        ])
        
        chain = prompt | self.llm | StrOutputParser()
        
        ml_analysis = reasoning['ml_analysis']
        lgs_issues = self._get_top_items(state.get('lgs_issues', []), 10)
        
        result = chain.invoke({
            'lgs_issues': lgs_issues,
            'ml_lgs_omc_insights': json.dumps(ml_analysis.get('lgs_omc', {}), indent=2)
        })
        
        return f"## 5. LGS vs OMC ANALYSIS\n\n{result}\n"
    
    def _generate_daily_trends(self, state: AnalysisState, reasoning: Dict) -> str:
        """Generate Daily Trends section"""
        daily_data = self._prepare_daily_trends_data(state)
        
        return f"""## 6. DAILY TRENDS

{daily_data}

### Patterns Over Time
Performance varies by day, with no consistent upward/downward trend. This suggests systemic issues in agent training and lead quality rather than time-based factors.

"""
    
    def _generate_status_analysis(self, state: AnalysisState, reasoning: Dict) -> str:
        """Generate Status/Outcome Analysis section"""
        status_data = self._prepare_status_analysis_data(state)
        
        return f"""## 7. STATUS/OUTCOME ANALYSIS

{status_data}

### Success Patterns
Successful outcomes (P2P, SALE, CALLBK) correlate with longer durations and sustained engagement, validating the importance of discovery and objection handling.

"""
    
    def _generate_script_compliance(self, state: AnalysisState, reasoning: Dict) -> str:
        """
        Generate Script Compliance Analysis section - NEW
        
        This section answers 5 key questions:
        1. In how many calls is the script being followed?
        2. Of script-followed calls, how many exceed 5 minutes?
        3. Why is the script not followed?
        4. Are correct rebuttals being used for objections?
        5. Are agents returning to script after objections?
        """
        
        # Get script compliance report data from state
        report_data = state.get('script_compliance_report_data', {})
        
        if not report_data or 'error' in report_data:
            return """## 8. SCRIPT COMPLIANCE ANALYSIS

*Script compliance data not available. This section requires script compliance analysis to be run.*

"""
        
        # Build the section
        section = "## 8. SCRIPT COMPLIANCE ANALYSIS\n\n"
        section += "This section analyzes how well OMC calling agents follow the mandatory 10-section sales script.\n\n"
        
        # =====================================================================
        # QUESTION 1: Script Following Rate
        # =====================================================================
        section += "### 8.1 Script Adherence Rate (Question 1)\n\n"
        section += "**In how many calls is the Calling Script being followed?**\n\n"
        
        total = report_data.get('q1_total_calls', 0)
        followed = report_data.get('q1_calls_script_followed_count', 0)
        followed_pct = report_data.get('q1_calls_script_followed_percentage', 0)
        
        section += f"| Metric | Count | Percentage |\n"
        section += f"|--------|-------|------------|\n"
        section += f"| Calls with Script Followed | {followed} | {followed_pct:.1f}% |\n"
        section += f"| Calls without Script Compliance | {total - followed} | {100 - followed_pct:.1f}% |\n"
        section += f"| **Total Calls Analyzed** | **{total}** | **100%** |\n\n"
        
        # Compliance tier distribution
        high_comp = report_data.get('compliance_high_count', 0)
        med_comp = report_data.get('compliance_medium_count', 0)
        low_comp = report_data.get('compliance_low_count', 0)
        
        section += "**Compliance Tier Distribution:**\n\n"
        section += f"| Tier | Definition | Count | Percentage |\n"
        section += f"|------|------------|-------|------------|\n"
        section += f"| High | >70% compliance | {high_comp} | {high_comp/total*100 if total > 0 else 0:.1f}% |\n"
        section += f"| Medium | 40-70% compliance | {med_comp} | {med_comp/total*100 if total > 0 else 0:.1f}% |\n"
        section += f"| Low | <40% compliance | {low_comp} | {low_comp/total*100 if total > 0 else 0:.1f}% |\n\n"
        
        # =====================================================================
        # QUESTION 2: Script Followed + Over 5 Minutes
        # =====================================================================
        section += "### 8.2 Script Compliance + Call Duration (Question 2)\n\n"
        section += "**Of calls where script is followed, how many go beyond 5 minutes?**\n\n"
        
        script_and_long = report_data.get('q2_script_followed_over_5min_count', 0)
        script_and_long_pct = report_data.get('q2_script_followed_over_5min_percentage', 0)
        denominator = report_data.get('q2_denominator', followed)
        
        section += f"| Metric | Count | Percentage |\n"
        section += f"|--------|-------|------------|\n"
        section += f"| Script Followed AND >5 min | {script_and_long} | {script_and_long_pct:.1f}% |\n"
        section += f"| Script Followed BUT ≤5 min | {denominator - script_and_long} | {100 - script_and_long_pct:.1f}% |\n"
        section += f"| **Total Calls with Script Followed** | **{denominator}** | **100%** |\n\n"
        
        section += f"**Key Insight:** When agents follow the script, **{script_and_long_pct:.1f}%** of calls exceed 5 minutes, "
        section += f"indicating that script compliance is {'positively' if script_and_long_pct > 50 else 'not strongly'} correlated with longer call durations.\n\n"
        
        # =====================================================================
        # QUESTION 3: Why Script Not Followed
        # =====================================================================
        section += "### 8.3 Non-Compliance Reasons (Question 3)\n\n"
        section += "**If the script is not being followed, why? External factors or agent errors?**\n\n"
        
        ext_factors = report_data.get('q3_external_factors_count', 0)
        client_int = report_data.get('q3_client_interruption_count', 0)
        agent_err = report_data.get('q3_agent_error_count', 0)
        total_non_comp = ext_factors + client_int + agent_err
        
        section += "**By Category:**\n\n"
        section += f"| Category | Count | Percentage | Description |\n"
        section += f"|----------|-------|------------|-------------|\n"
        section += f"| Client Interruptions | {client_int} | {client_int/total_non_comp*100 if total_non_comp > 0 else 0:.1f}% | Customer hung up, objected, not interested |\n"
        section += f"| External Factors | {ext_factors} | {ext_factors/total_non_comp*100 if total_non_comp > 0 else 0:.1f}% | Technical issues, language barrier, already client |\n"
        section += f"| Agent Errors | {agent_err} | {agent_err/total_non_comp*100 if total_non_comp > 0 else 0:.1f}% | Skipped sections, deviated from script |\n\n"
        
        # Detailed breakdown
        breakdown = report_data.get('q3_non_compliance_breakdown', {})
        if breakdown:
            section += "**Detailed Breakdown:**\n\n"
            section += f"| Reason | Count |\n"
            section += f"|--------|-------|\n"
            sorted_reasons = sorted(breakdown.items(), key=lambda x: x[1], reverse=True)
            for reason, count in sorted_reasons[:10]:
                reason_display = reason.replace('_', ' ').title()
                section += f"| {reason_display} | {count} |\n"
            section += "\n"
        
        # =====================================================================
        # QUESTION 4: Objection-Rebuttal Analysis
        # =====================================================================
        section += "### 8.4 Objection Handling & Rebuttals (Question 4)\n\n"
        section += "**When objections are raised, are the right rebuttals being used?**\n\n"
        
        total_obj = report_data.get('q4_total_objections', 0)
        obj_with_reb = report_data.get('q4_objections_with_rebuttals', 0)
        rebuttal_rate = report_data.get('q4_rebuttal_rate', 0)
        
        section += f"| Metric | Count | Rate |\n"
        section += f"|--------|-------|------|\n"
        section += f"| Total Objections Raised | {total_obj} | - |\n"
        section += f"| Objections with Rebuttals | {obj_with_reb} | {rebuttal_rate:.1f}% |\n"
        section += f"| Objections without Rebuttals | {total_obj - obj_with_reb} | {100 - rebuttal_rate:.1f}% |\n\n"
        
        if rebuttal_rate >= 70:
            section += f"**Assessment:** ✅ Strong rebuttal usage ({rebuttal_rate:.1f}%). Agents are effectively handling objections.\n\n"
        elif rebuttal_rate >= 40:
            section += f"**Assessment:** ⚠️ Moderate rebuttal usage ({rebuttal_rate:.1f}%). Room for improvement in objection handling.\n\n"
        else:
            section += f"**Assessment:** ❌ Low rebuttal usage ({rebuttal_rate:.1f}%). Significant training needed on AVQ rebuttal pattern.\n\n"
        
        # =====================================================================
        # QUESTION 5: Returning to Script After Objection
        # =====================================================================
        section += "### 8.5 Script Recovery After Objections (Question 5)\n\n"
        section += "**Are agents returning to the calling script after handling objections?**\n\n"
        
        script_return = report_data.get('q5_objections_with_script_return', 0)
        script_return_rate = report_data.get('q5_script_return_rate', 0)
        
        section += f"| Metric | Count | Rate |\n"
        section += f"|--------|-------|------|\n"
        section += f"| Objections with Script Return | {script_return} | {script_return_rate:.1f}% |\n"
        section += f"| Objections without Script Return | {total_obj - script_return} | {100 - script_return_rate:.1f}% |\n\n"
        
        if script_return_rate >= 70:
            section += f"**Assessment:** ✅ Excellent script recovery ({script_return_rate:.1f}%). Agents effectively return to script flow.\n\n"
        elif script_return_rate >= 40:
            section += f"**Assessment:** ⚠️ Moderate script recovery ({script_return_rate:.1f}%). Training needed on returning to script after rebuttals.\n\n"
        else:
            section += f"**Assessment:** ❌ Poor script recovery ({script_return_rate:.1f}%). Agents lose script flow after objections.\n\n"
        
        # =====================================================================
        # Section-Level Analysis
        # =====================================================================
        section += "### 8.6 Section-by-Section Compliance\n\n"
        section += "**Which script sections are followed most/least?**\n\n"
        
        section_avgs = report_data.get('section_compliance_averages', {})
        if section_avgs:
            section += f"| Section | Avg Compliance | Assessment |\n"
            section += f"|---------|----------------|------------|\n"
            sorted_sections = sorted(section_avgs.items(), key=lambda x: x[1], reverse=True)
            for sect_name, avg_comp in sorted_sections:
                if avg_comp >= 70:
                    assessment = "✅ Strong"
                elif avg_comp >= 40:
                    assessment = "⚠️ Moderate"
                else:
                    assessment = "❌ Needs Work"
                section += f"| {sect_name} | {avg_comp:.1f}% | {assessment} |\n"
            section += "\n"
        
        most_followed = report_data.get('most_followed_sections', [])
        least_followed = report_data.get('least_followed_sections', [])
        
        section += f"**Best Performed Sections:** {', '.join(most_followed[:3]) if most_followed else 'N/A'}\n\n"
        section += f"**Sections Needing Improvement:** {', '.join(least_followed[:3]) if least_followed else 'N/A'}\n\n"
        
        # =====================================================================
        # Agent Rankings
        # =====================================================================
        section += "### 8.7 Agent Script Compliance Rankings\n\n"
        
        agent_rankings = report_data.get('agent_rankings', [])
        if agent_rankings:
            section += f"| Agent | Total Calls | Compliance Rate | Avg Score |\n"
            section += f"|-------|-------------|-----------------|------------|\n"
            for agent in agent_rankings[:15]:
                section += f"| {agent['agent']} | {agent['total_calls']} | {agent['compliance_rate']:.1f}% | {agent['avg_score']:.1f} |\n"
            section += "\n"
        
        top_agents = report_data.get('top_compliant_agents', [])
        bottom_agents = report_data.get('agents_needing_training', [])
        
        section += f"**Top Script-Compliant Agents:** {', '.join(top_agents[:5]) if top_agents else 'N/A'}\n\n"
        section += f"**Agents Needing Script Training:** {', '.join(bottom_agents[:5]) if bottom_agents else 'N/A'}\n\n"
        
        # =====================================================================
        # Examples
        # =====================================================================
        examples = report_data.get('examples', {})
        if examples:
            # High compliance examples
            high_examples = examples.get('high_compliance_examples', [])
            if high_examples:
                section += "### 8.8 Example: High Script Compliance\n\n"
                for idx, ex in enumerate(high_examples[:2], 1):
                    section += f"**{idx}. Call ID: {ex.get('call_id', 'N/A')}**\n"
                    section += f"- Agent: {ex.get('agent', 'N/A')}\n"
                    section += f"- Duration: {ex.get('duration', 0)} seconds\n"
                    section += f"- Compliance: {ex.get('compliance_pct', 0):.1f}%\n"
                    section += f"- Sections Attempted: {ex.get('sections_attempted', 0)}\n"
                    if ex.get('best_practice_quote'):
                        section += f"- Best Practice Quote: \"{ex['best_practice_quote']}\"\n"
                    section += "\n"
            
            # Low compliance examples
            low_examples = examples.get('low_compliance_examples', [])
            if low_examples:
                section += "### 8.9 Example: Low Script Compliance\n\n"
                for idx, ex in enumerate(low_examples[:2], 1):
                    section += f"**{idx}. Call ID: {ex.get('call_id', 'N/A')}**\n"
                    section += f"- Agent: {ex.get('agent', 'N/A')}\n"
                    section += f"- Duration: {ex.get('duration', 0)} seconds\n"
                    section += f"- Compliance: {ex.get('compliance_pct', 0):.1f}%\n"
                    section += f"- Non-Compliance Reason: {ex.get('non_compliance_reason', 'N/A')}\n"
                    if ex.get('proof'):
                        section += f"- Proof: \"{ex['proof']}\"\n"
                    section += "\n"
            
            # Good objection handling examples
            objection_examples = examples.get('good_objection_handling_examples', [])
            if objection_examples:
                section += "### 8.10 Example: Good Objection Handling\n\n"
                for idx, ex in enumerate(objection_examples[:2], 1):
                    section += f"**{idx}. Call ID: {ex.get('call_id', 'N/A')}**\n"
                    section += f"- Agent: {ex.get('agent', 'N/A')}\n"
                    section += f"- Objections Handled: {ex.get('objections_handled', 0)}\n"
                    section += f"- Returned to Script: {'Yes ✅' if ex.get('returned_to_script') else 'No ❌'}\n"
                    section += f"- Recovery Quality: {ex.get('recovery_quality', 'N/A')}\n"
                    if ex.get('example_objection'):
                        obj = ex['example_objection']
                        section += f"- Objection Type: {obj.get('type', 'N/A')}\n"
                        section += f"- Customer: \"{obj.get('customer_quote', 'N/A')}\"\n"
                        section += f"- Agent Rebuttal: \"{obj.get('agent_rebuttal', 'N/A')}\"\n"
                    section += "\n"
        
        # =====================================================================
        # Key Findings & Recommendations
        # =====================================================================
        section += "### 8.11 Script Compliance Key Findings\n\n"
        
        section += "**Summary:**\n"
        section += f"- **{followed_pct:.1f}%** of calls have meaningful script compliance\n"
        section += f"- **{script_and_long_pct:.1f}%** of script-compliant calls exceed 5 minutes\n"
        section += f"- **{rebuttal_rate:.1f}%** objection rebuttal rate\n"
        section += f"- **{script_return_rate:.1f}%** script return rate after objections\n\n"
        
        section += "**Recommendations:**\n"
        if followed_pct < 50:
            section += "1. **Mandatory Script Training**: Less than half of calls follow the script. Implement refresher training.\n"
        if rebuttal_rate < 50:
            section += "2. **AVQ Rebuttal Training**: Focus on Acknowledge-Value-Question pattern for objection handling.\n"
        if script_return_rate < 50:
            section += "3. **Script Flow Recovery**: Train agents to return to script after handling objections.\n"
        if least_followed:
            section += f"4. **Focus on Weak Sections**: Prioritize training on {', '.join(least_followed[:2])}.\n"
        section += "\n"
        
        return section
    
    def _generate_recommendations(self, state: AnalysisState, reasoning: Dict) -> str:
        """Generate Recommendations section with ML prioritization (if available)"""
        
        ml_available = reasoning['ml_analysis'].get('available', False)
        
        system_with_ml = """Create actionable recommendations prioritized by ML importance.

Example:
"**1. Intensive Discovery Question Training (ML Priority: #2, Score: 0.783)**
   - Action: Mandate 8-12 discovery questions per call
   - Implementation: Create discovery checklist, QA scoring
   - Expected Impact: +40% call duration based on ML analysis"

Focus on trainable, high-impact variables."""
        
        system_without_ml = """Create actionable recommendations based on call analysis patterns.

Focus on practical, implementable actions based on observed patterns.

NOTE: ML prioritization data is not available."""
        
        human_with_ml = """Create a RECOMMENDATIONS section.

ML RECOMMENDATIONS INSIGHTS:
{ml_rec_insights}

ML VISUALIZATION:
{ml_viz_path}

REQUIREMENTS:
A. Immediate Actions (with ML priority)
B. Training Recommendations (focus on trainable variables)
C. Process Improvements
D. Lead Quality Improvements (based on LQ_ variable importance)
E. Long-term Strategic Changes

Include ROC curve visualization showing ML model performance.

Generate the section:"""
        
        human_without_ml = """Create a RECOMMENDATIONS section.

CALL ANALYSIS INSIGHTS:
- Top issues identified from call patterns
- Successful techniques from top performers
- Common failure points

REQUIREMENTS:
A. Immediate Actions (based on frequency and impact)
B. Training Recommendations (based on observed patterns)
C. Process Improvements
D. Lead Quality Improvements
E. Long-term Strategic Changes

NOTE: ML prioritization is not available. Base recommendations on call analysis frequency and impact.

Generate the section:"""
        
        prompt = self._create_prompt_with_ml_fallback(
            system_with_ml, system_without_ml,
            human_with_ml, human_without_ml,
            ml_available
        )
        
        chain = prompt | self.llm | StrOutputParser()
        
        ml_analysis = reasoning['ml_analysis']
        
        # Prepare invoke parameters
        invoke_params = {}
        
        # Add ML parameters only if available
        if ml_available:
            ml_rec_insights = ml_analysis.get('recommendations', {})
            invoke_params['ml_rec_insights'] = json.dumps(ml_rec_insights, indent=2)
            invoke_params['ml_viz_path'] = ml_rec_insights.get('visualization_path', '')
        
        result = chain.invoke(invoke_params)
        
        return f"## 9. RECOMMENDATIONS\n\n{result}\n"
    
    def _generate_real_examples(self, state: AnalysisState, reasoning: Dict) -> str:
        """Generate Real Examples section"""
        # Get best examples
        short_examples = [i for i in state['all_insights'] if i.is_short_call and i.proof_of_issue][:3]
        long_examples = [i for i in state['all_insights'] if not i.is_short_call and i.proof_of_success][:3]
        
        examples_text = "## 10. REAL EXAMPLES\n\n"
        
        # Short call examples
        examples_text += "### A. Examples of Short Calls with Issues\n\n"
        for idx, insight in enumerate(short_examples, 1):
            examples_text += f"""**{idx}. Call ID: {insight.call_id}**
- **Agent:** {insight.omc_agent}
- **Duration:** {insight.omc_duration} seconds
- **Issue:** {', '.join(insight.early_termination_reasons[:2]) if insight.early_termination_reasons else 'N/A'}
- **VERBATIM PROOF:**
  {insight.proof_of_issue}
- **Analysis:** {insight.critical_moment_quote}

"""
        
        # Long call examples
        examples_text += "### B. Examples of Successful Long Calls\n\n"
        for idx, insight in enumerate(long_examples, 1):
            examples_text += f"""**{idx}. Call ID: {insight.call_id}**
- **Agent:** {insight.omc_agent}
- **Duration:** {insight.omc_duration} seconds
- **Success Factors:** {', '.join(insight.success_factors[:2]) if insight.success_factors else 'N/A'}
- **VERBATIM PROOF:**
  {insight.proof_of_success}
- **Transferable Technique:** {insight.transferable_technique}

"""
        
        return examples_text
    
    # ============================================================
    # HELPER METHODS
    # ============================================================
    
    def _prepare_agent_performance_data(self, state: AnalysisState) -> str:
        """Prepare agent performance data as table"""
        agent_data = []
        for agent, metrics in state.get('agent_metrics', {}).items():
            avg_duration = metrics['total_duration'] / metrics['total_calls'] if metrics['total_calls'] > 0 else 0
            avg_score = sum(metrics['performance_scores']) / len(metrics['performance_scores']) if metrics['performance_scores'] else 0
            short_rate = metrics['short_calls'] / metrics['total_calls'] * 100 if metrics['total_calls'] > 0 else 0
            
            agent_data.append({
                'agent': agent,
                'total_calls': metrics['total_calls'],
                'short_calls': metrics['short_calls'],
                'long_calls': metrics['long_calls'],
                'avg_duration': round(avg_duration, 1),
                'avg_score': round(avg_score, 1),
                'short_call_rate': round(short_rate, 1)
            })
        
        agent_data.sort(key=lambda x: x['short_call_rate'])
        
        # Format as markdown table
        table = "| Agent | Total Calls | Short Calls | Long Calls | Avg Duration (s) | Avg Score | Short Call Rate (%) |\n"
        table += "|-------|-------------|-------------|------------|------------------|-----------|---------------------|\n"
        
        for agent in agent_data:
            table += f"| {agent['agent']} | {agent['total_calls']} | {agent['short_calls']} | {agent['long_calls']} | {agent['avg_duration']} | {agent['avg_score']} | {agent['short_call_rate']} |\n"
        
        return table
    
    def _prepare_daily_trends_data(self, state: AnalysisState) -> str:
        """Prepare daily trends as table"""
        daily_data = []
        for date, metrics in state.get('daily_metrics', {}).items():
            avg_duration = metrics['total_duration'] / metrics['total_calls'] if metrics['total_calls'] > 0 else 0
            short_rate = metrics['short_calls'] / metrics['total_calls'] * 100 if metrics['total_calls'] > 0 else 0
            
            daily_data.append({
                'date': date,
                'total_calls': metrics['total_calls'],
                'short_calls': metrics['short_calls'],
                'long_calls': metrics['long_calls'],
                'avg_duration': round(avg_duration, 1),
                'short_call_rate': round(short_rate, 1)
            })
        
        daily_data.sort(key=lambda x: x['date'])
        
        # Format as markdown table
        table = "| Date | Total Calls | Short Calls | Long Calls | Avg Duration (s) | Short Call Rate (%) |\n"
        table += "|------|-------------|-------------|------------|------------------|---------------------|\n"
        
        for day in daily_data[:20]:  # Limit to 20 rows
            table += f"| {day['date']} | {day['total_calls']} | {day['short_calls']} | {day['long_calls']} | {day['avg_duration']} | {day['short_call_rate']} |\n"
        
        return table
    
    def _prepare_status_analysis_data(self, state: AnalysisState) -> str:
        """Prepare status analysis as table"""
        status_data = []
        for status, metrics in state.get('status_metrics', {}).items():
            avg_duration = metrics['total_duration'] / metrics['count'] if metrics['count'] > 0 else 0
            
            status_data.append({
                'status': status,
                'count': metrics['count'],
                'avg_duration': round(avg_duration, 1)
            })
        
        status_data.sort(key=lambda x: x['count'], reverse=True)
        
        # Format as markdown table
        table = "| Status | Count | Avg Duration (s) |\n"
        table += "|--------|-------|------------------|\n"
        
        for status in status_data:
            table += f"| {status['status']} | {status['count']} | {status['avg_duration']} |\n"
        
        return table
    
    def _get_top_items(self, items: List[str], top_n: int = 10) -> str:
        """Get top N most common items"""
        from collections import Counter
        
        if not items:
            return "None identified"
        
        counter = Counter(items)
        top_items = counter.most_common(top_n)
        
        result = []
        for item, count in top_items:
            result.append(f"- {item} (mentioned {count} times)")
        
        return "\n".join(result)
    
    def _get_date_range(self, state: AnalysisState) -> str:
        """Get date range from daily metrics"""
        dates = list(state.get('daily_metrics', {}).keys())
        if not dates:
            return "Unknown"
        
        dates.sort()
        if len(dates) == 1:
            return dates[0]
        
        return f"{dates[0]} to {dates[-1]}"
    
    def _generate_fallback_report(self, state: AnalysisState) -> str:
        """Generate basic report if ReAct fails"""
        total_calls = len(state['all_insights'])
        short_calls = sum(1 for i in state['all_insights'] if i.is_short_call)
        
        return f"""# CALL PERFORMANCE ANALYSIS REPORT

## Executive Summary

**Total Calls Analyzed:** {total_calls}
**Short Calls (<5 min):** {short_calls} ({short_calls/total_calls*100:.1f}%)

*This is a fallback report. Full ReAct generation encountered an error.*
*Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

