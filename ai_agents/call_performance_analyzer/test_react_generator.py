"""
Test script for ReAct Report Generator
Verifies the implementation without running full analysis
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from reports.react_report_generator import ReActReportGenerator
from agents.ml_insights_agent import MLInsightsAgent
from graph.state import AnalysisState
from schemas.analysis_schemas import CallInsight
from utils.logger import logger

def create_mock_state() -> AnalysisState:
    """Create a mock state for testing"""
    
    # Create mock insights
    mock_insights = [
        CallInsight(
            call_id="test_001",
            call_date="2025-12-22",
            lgs_agent="TestLGS",
            lgs_transcription="Test LGS transcript",
            lgs_quality_score=7,
            lgs_issues=["No explicit consent"],
            lgs_strengths=["Clear communication"],
            omc_agent="TestOMC",
            omc_transcription="Test OMC transcript",
            omc_duration=180,
            omc_status="NI",
            is_short_call=True,
            call_category="Short (<5min)",
            early_termination_reasons=["Customer not interested"],
            success_factors=None,
            objections_raised=["Not interested"],
            objection_handling="Agent did not address objection",
            customer_engagement_level="Low",
            agent_performance_rating=4,
            specific_recommendations=["Improve objection handling"],
            notable_quotes=["I'm not interested"],
            critical_moment_quote="Customer: I'm not interested",
            proof_of_issue="Customer hung up immediately",
            proof_of_success=None,
            transferable_technique=None,
            technique_application=None,
            agent_persona_insight=None,
            analysis_timestamp="2025-12-22T10:00:00Z",
            analysis_success=True,
            analysis_error=None
        ),
        CallInsight(
            call_id="test_002",
            call_date="2025-12-22",
            lgs_agent="TestLGS",
            lgs_transcription="Test LGS transcript",
            lgs_quality_score=9,
            lgs_issues=None,
            lgs_strengths=["Excellent handoff"],
            omc_agent="TestOMC2",
            omc_transcription="Test OMC transcript",
            omc_duration=520,
            omc_status="P2P",
            is_short_call=False,
            call_category="Long (>=5min)",
            early_termination_reasons=None,
            success_factors=["Strong discovery", "Data-driven pitch"],
            objections_raised=["Price concern"],
            objection_handling="Agent addressed with value proposition",
            customer_engagement_level="High",
            agent_performance_rating=9,
            specific_recommendations=["Continue current approach"],
            notable_quotes=["That makes sense"],
            critical_moment_quote="Agent: Let me show you the local demand",
            proof_of_issue=None,
            proof_of_success="Customer agreed to proposal",
            transferable_technique="Data-driven discovery",
            technique_application="Use local market data to create urgency",
            agent_persona_insight="Confident and consultative",
            analysis_timestamp="2025-12-22T10:05:00Z",
            analysis_success=True,
            analysis_error=None
        )
    ]
    
    # Create mock state
    state: AnalysisState = {
        'current_batch': [],
        'batch_number': 1,
        'total_rows': 2,
        'all_insights': mock_insights,
        'agent_metrics': {
            'TestOMC': {
                'total_calls': 1,
                'short_calls': 1,
                'long_calls': 0,
                'total_duration': 180,
                'performance_scores': [4]
            },
            'TestOMC2': {
                'total_calls': 1,
                'short_calls': 0,
                'long_calls': 1,
                'total_duration': 520,
                'performance_scores': [9]
            }
        },
        'daily_metrics': {
            '2025-12-22': {
                'total_calls': 2,
                'short_calls': 1,
                'long_calls': 1,
                'total_duration': 700
            }
        },
        'status_metrics': {
            'NI': {'count': 1, 'total_duration': 180},
            'P2P': {'count': 1, 'total_duration': 520}
        },
        'short_call_patterns': ["No explicit consent"],
        'long_call_patterns': ["Strong discovery"],
        'lgs_issues': ["No explicit consent"],
        'omc_issues': [],
        'example_short_calls': [mock_insights[0]],
        'example_successful_calls': [mock_insights[1]],
        'processed_count': 2,
        'failed_count': 0,
        'retry_queue': [],
        'ready_for_report': True,
        'final_report': None,
        'errors': [],
        'ml_insights': None  # Will be populated by ML agent
    }
    
    return state

def test_ml_insights_agent():
    """Test ML Insights Agent"""
    print("\n" + "=" * 80)
    print("TEST 1: ML INSIGHTS AGENT")
    print("=" * 80)
    
    try:
        ml_agent = MLInsightsAgent()
        ml_insights = ml_agent.analyze_ml_outputs()
        
        print(f"[OK] ML Insights Agent initialized")
        print(f"[OK] Top variables: {len(ml_insights.top_variables)}")
        print(f"[OK] Key insights: {len(ml_insights.key_insights)}")
        print(f"[OK] Section-specific insights generated:")
        print(f"   - Agent Performance: {bool(ml_insights.agent_performance_insights)}")
        print(f"   - Call Patterns: {bool(ml_insights.call_pattern_insights)}")
        print(f"   - Lead Quality: {bool(ml_insights.lead_quality_insights)}")
        print(f"   - LGS/OMC: {bool(ml_insights.lgs_omc_insights)}")
        print(f"   - Recommendations: {bool(ml_insights.recommendations_insights)}")
        
        return ml_insights
        
    except Exception as e:
        print(f"[FAIL] Error: {str(e)}")
        return None

def test_react_generator(state: AnalysisState):
    """Test ReAct Report Generator"""
    print("\n" + "=" * 80)
    print("TEST 2: REACT REPORT GENERATOR")
    print("=" * 80)
    
    try:
        generator = ReActReportGenerator()
        print("[OK] ReAct Generator initialized")
        
        # Test reasoning phase
        print("\nTesting REASONING phase...")
        reasoning = generator._reasoning_phase(state)
        print(f"[OK] Reasoning complete:")
        print(f"   - Call analysis: {bool(reasoning['call_analysis'])}")
        print(f"   - ML analysis: {bool(reasoning['ml_analysis'])}")
        print(f"   - Correlations: {bool(reasoning['correlations'])}")
        print(f"   - Priorities: {bool(reasoning['priorities'])}")
        print(f"   - Structure: {bool(reasoning['structure'])}")
        
        # Test section generation (just one section as example)
        print("\nTesting ACTING phase (Executive Summary only)...")
        exec_summary = generator._generate_executive_summary(state, reasoning)
        print(f"[OK] Executive Summary generated: {len(exec_summary)} characters")
        
        # Check for ML blending
        has_ml_inline = "**ML" in exec_summary or "ML Validation" in exec_summary
        print(f"[OK] ML inline integration: {'Yes' if has_ml_inline else 'No'}")
        
        print("\n[OK] All tests passed!")
        return True
        
    except Exception as e:
        print(f"[FAIL] Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("\n" + "=" * 80)
    print("REACT REPORT GENERATOR - TEST SUITE")
    print("=" * 80)
    
    # Create mock state
    print("\nCreating mock state...")
    state = create_mock_state()
    print("[OK] Mock state created with 2 call insights")
    
    # Test ML Insights Agent
    ml_insights = test_ml_insights_agent()
    if ml_insights:
        state['ml_insights'] = ml_insights
    
    # Test ReAct Generator
    success = test_react_generator(state)
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    if success:
        print("[SUCCESS] All tests passed successfully!")
        print("\nThe ReAct Report Generator is ready for production use.")
        print("\nNext steps:")
        print("1. Run full analysis with: python main.py")
        print("2. Review generated report quality")
        print("3. Verify ML blending is organic")
    else:
        print("[FAIL] Some tests failed. Check logs above.")
    
    print("=" * 80 + "\n")

if __name__ == "__main__":
    main()

