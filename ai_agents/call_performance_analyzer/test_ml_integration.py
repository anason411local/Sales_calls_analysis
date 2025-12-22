"""
Quick test script to verify ML Insights Agent integration
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from agents.ml_insights_agent import MLInsightsAgent
from utils.logger import logger

def test_ml_insights_agent():
    """Test ML Insights Agent"""
    print("=" * 80)
    print("TESTING ML INSIGHTS AGENT")
    print("=" * 80)
    
    try:
        # Initialize agent
        print("\n1. Initializing ML Insights Agent...")
        agent = MLInsightsAgent()
        print("   [OK] Agent initialized")
        
        # Run analysis
        print("\n2. Running ML analysis...")
        insights = agent.analyze_ml_outputs()
        print(f"   [OK] Analysis complete")
        
        # Display results
        print("\n3. Results Summary:")
        print(f"   - Top Variables: {len(insights.top_variables)}")
        print(f"   - Key Insights: {len(insights.key_insights)}")
        print(f"   - Visualizations: {len(insights.visualizations_to_include)}")
        
        if insights.top_variables:
            print(f"\n4. Top 5 Variables:")
            for i, var in enumerate(insights.top_variables[:5], 1):
                print(f"   {i}. {var}")
        
        if insights.key_insights:
            print(f"\n5. Sample Insights:")
            for i, insight in enumerate(insights.key_insights[:3], 1):
                print(f"\n   Insight {i}:")
                print(f"   Category: {insight.category}")
                print(f"   Insight: {insight.insight}")
                print(f"   Score: {insight.importance_score:.3f}")
        
        print(f"\n6. Statistical Summary:")
        print(f"   {insights.statistical_summary}")
        
        print(f"\n7. Visualizations to Include:")
        for viz in insights.visualizations_to_include:
            print(f"   - {Path(viz).name}")
        
        print("\n" + "=" * 80)
        print("[SUCCESS] ML INSIGHTS AGENT TEST PASSED")
        print("=" * 80)
        
        return True
        
    except Exception as e:
        print(f"\n[FAILED] TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_ml_insights_agent()
    sys.exit(0 if success else 1)

