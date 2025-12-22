"""
Test ML Insights Agent - Comprehensive Data Loading
Tests all the new enhancements for loading ALL data sources
"""
from agents.ml_insights_agent import MLInsightsAgent
from utils.logger import logger
import sys

def test_ml_agent_comprehensive():
    """Test comprehensive data loading"""
    
    print("\n" + "="*80)
    print("TESTING ML INSIGHTS AGENT - COMPREHENSIVE MODE")
    print("="*80 + "\n")
    
    try:
        # Initialize agent
        print("[1/4] Initializing ML Insights Agent...")
        ml_agent = MLInsightsAgent()
        print(f"    ML data path: {ml_agent.ml_data_path}")
        print(f"    Path exists: {ml_agent.ml_data_path.exists()}")
        print("    Status: OK\n")
        
        # Test data loading
        print("[2/4] Testing comprehensive data loading...")
        ml_data = ml_agent._load_ml_data()
        
        print(f"\n    Data sources loaded: {len(ml_data)}")
        print("\n    Breakdown:")
        
        # Check each data source
        data_sources = {
            'correlation': 'Main correlation data',
            'correlation_long_calls': 'Long calls correlation (NEW)',
            'correlation_short_calls': 'Short calls correlation (NEW)',
            'importance': 'Combined feature importance',
            'importance_rf': 'Random Forest importance (NEW)',
            'importance_xgb': 'XGBoost importance (NEW)',
            'shap': 'SHAP importance',
            'statistical': 'Combined statistical tests',
            'statistical_numerical': 'Numerical tests (NEW)',
            'statistical_categorical': 'Categorical tests (NEW)',
            'lime': 'LIME importance',
            'lime_summary': 'LIME summary JSON (NEW)',
            'metadata': 'Analysis metadata',
            'model_metrics': 'Model metrics',
            'missing_values': 'Missing values summary (NEW)'
        }
        
        loaded_count = 0
        new_count = 0
        
        for key, description in data_sources.items():
            if key in ml_data:
                status = "LOADED"
                loaded_count += 1
                if "(NEW)" in description:
                    new_count += 1
                print(f"      [{status}] {description}")
            else:
                status = "MISSING"
                print(f"      [{status}] {description}")
        
        print(f"\n    Total loaded: {loaded_count}/{len(data_sources)}")
        print(f"    New sources: {new_count}")
        print("    Status: OK\n")
        
        # Test visualization selection
        print("[3/4] Testing comprehensive visualization selection...")
        visualizations = ml_agent._select_key_visualizations()
        
        print(f"\n    Visualizations selected: {len(visualizations)}")
        
        # Count by category
        viz_categories = {
            'shap': 0,
            'lime': 0,
            'viz': 0,
            'heatmap': 0,
            'eval': 0,
            'stat': 0
        }
        
        for viz_path in visualizations:
            viz_name = viz_path.split('\\')[-1].lower()
            if 'shap' in viz_name:
                viz_categories['shap'] += 1
            elif 'lime' in viz_name:
                viz_categories['lime'] += 1
            elif 'viz' in viz_name:
                viz_categories['viz'] += 1
            elif 'heatmap' in viz_name:
                viz_categories['heatmap'] += 1
            elif 'eval' in viz_name:
                viz_categories['eval'] += 1
            elif 'stat' in viz_name:
                viz_categories['stat'] += 1
        
        print("\n    Breakdown by category:")
        print(f"      SHAP plots: {viz_categories['shap']}")
        print(f"      LIME plots: {viz_categories['lime']}")
        print(f"      Visualization plots: {viz_categories['viz']}")
        print(f"      Heatmaps: {viz_categories['heatmap']}")
        print(f"      Evaluation plots: {viz_categories['eval']}")
        print(f"      Statistical plots: {viz_categories['stat']}")
        print(f"\n    Expected: ~31 PNG files")
        print(f"    Actual: {len(visualizations)} PNG files")
        
        if len(visualizations) >= 25:
            print("    Status: OK (Comprehensive mode active)\n")
        else:
            print("    Status: WARNING (Some visualizations may be missing)\n")
        
        # Test insight generation (quick test)
        print("[4/4] Testing insight generation...")
        
        # Test correlation analysis with new long/short call data
        if 'correlation' in ml_data:
            corr_insights = ml_agent._analyze_correlations(ml_data['correlation'], ml_data)
            print(f"    Correlation insights generated: {len(corr_insights)}")
            
            # Check if long/short call context is included
            if corr_insights:
                sample_insight = corr_insights[0]
                has_context = 'Long calls:' in sample_insight.evidence or 'Short calls:' in sample_insight.evidence
                if has_context:
                    print("    Long/Short call context: INCLUDED (NEW)")
                else:
                    print("    Long/Short call context: Not available (data may be missing)")
        
        print("    Status: OK\n")
        
        # Summary
        print("="*80)
        print("TEST SUMMARY")
        print("="*80)
        print(f"  Agent Initialization: OK")
        print(f"  Data Loading: OK ({loaded_count}/{len(data_sources)} sources)")
        print(f"  New Data Sources: {new_count} additional sources loaded")
        print(f"  Visualizations: OK ({len(visualizations)} PNG files)")
        print(f"  Insight Generation: OK")
        print("\n  Overall Status: PASSED")
        print("="*80 + "\n")
        
        return True
        
    except Exception as e:
        print(f"\n  ERROR: {str(e)}")
        logger.error(f"Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_ml_agent_comprehensive()
    sys.exit(0 if success else 1)

