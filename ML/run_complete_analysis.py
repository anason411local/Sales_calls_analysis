"""
MASTER ANALYSIS SCRIPT
Runs the complete analysis pipeline for sales call duration analysis

This script executes all analysis steps in the correct order:
1. Statistical Analysis (T-tests, Chi-square tests)
2. Correlation Analysis
3. Feature Importance (Random Forest, Gradient Boosting)
4. Visualizations
5. Comprehensive Report Generation
"""

import os
import sys
import time
from datetime import datetime

def print_header(text):
    """Print a formatted header"""
    print("\n" + "="*100)
    print(text.center(100))
    print("="*100 + "\n")

def print_step(step_num, total_steps, description):
    """Print step information"""
    print(f"\n{'='*100}")
    print(f"STEP {step_num}/{total_steps}: {description}")
    print(f"{'='*100}\n")

def run_script(script_name, description):
    """Run a Python script and handle errors"""
    try:
        print(f"Running: {script_name}")
        print(f"Purpose: {description}")
        print("-" * 100)
        
        start_time = time.time()
        
        # Execute the script
        with open(script_name, 'r', encoding='utf-8') as f:
            script_content = f.read()
        
        exec(script_content, {'__name__': '__main__'})
        
        elapsed = time.time() - start_time
        print(f"\n[OK] {script_name} completed successfully in {elapsed:.2f} seconds")
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Error in {script_name}:")
        print(f"  {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main execution function"""
    
    print_header("SALES CALL DURATION ANALYSIS - MASTER SCRIPT")
    
    print("Analysis Parameters:")
    print(f"  - Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  - Working Directory: {os.getcwd()}")
    print(f"  - Python Version: {sys.version.split()[0]}")
    
    # Check if data files exist
    if not os.path.exists('Less_than_4.88_mnt..csv'):
        print("\n[ERROR] ERROR: Less_than_4.88_mnt..csv not found!")
        return
    if not os.path.exists('greater_than_4.88_mnt..csv'):
        print("\n[ERROR] ERROR: greater_than_4.88_mnt..csv not found!")
        return
    
    print("\n[OK] Data files found")
    
    # Create output directory
    os.makedirs('analysis_outputs', exist_ok=True)
    print("[OK] Output directory ready: analysis_outputs/")
    
    # Define analysis pipeline
    pipeline = [
        {
            'script': 'statistical_analysis.py',
            'description': 'Statistical Tests (T-tests, Mann-Whitney U, Chi-square)',
            'required_outputs': [
                'analysis_outputs/numeric_variables_tests.csv',
                'analysis_outputs/categorical_variables_tests.csv'
            ]
        },
        {
            'script': 'feature_importance_analysis.py',
            'description': 'Correlation & Feature Importance Analysis',
            'required_outputs': [
                'analysis_outputs/correlation_analysis.csv',
                'analysis_outputs/feature_importance_random_forest.csv',
                'analysis_outputs/feature_importance_gradient_boosting.csv',
                'analysis_outputs/combined_feature_importance.csv'
            ]
        },
        {
            'script': 'create_visualizations.py',
            'description': 'Create Primary Visualizations',
            'required_outputs': [
                'analysis_outputs/viz_01_numeric_variables_significance.png',
                'analysis_outputs/viz_02_correlation_analysis.png',
                'analysis_outputs/viz_03_feature_importance_comparison.png',
                'analysis_outputs/viz_04_top_variables_combined.png'
            ]
        },
        {
            'script': 'create_additional_visualizations.py',
            'description': 'Create Additional Detailed Visualizations',
            'required_outputs': [
                'analysis_outputs/viz_05_distribution_comparison.png',
                'analysis_outputs/viz_06_percentage_differences.png',
                'analysis_outputs/viz_07_statistical_overview.png',
                'analysis_outputs/viz_08_top10_detailed_distributions.png'
            ]
        },
        {
            'script': 'generate_report.py',
            'description': 'Generate Comprehensive Analysis Report',
            'required_outputs': [
                'analysis_outputs/COMPREHENSIVE_ANALYSIS_REPORT.txt'
            ]
        }
    ]
    
    total_steps = len(pipeline)
    successful_steps = 0
    failed_steps = []
    
    # Execute pipeline
    overall_start = time.time()
    
    for i, step in enumerate(pipeline, 1):
        print_step(i, total_steps, step['description'])
        
        success = run_script(step['script'], step['description'])
        
        if success:
            successful_steps += 1
            # Verify outputs
            missing_outputs = []
            for output in step['required_outputs']:
                if not os.path.exists(output):
                    missing_outputs.append(output)
            
            if missing_outputs:
                print(f"\n[WARNING] Warning: Some expected outputs not found:")
                for output in missing_outputs:
                    print(f"    - {output}")
        else:
            failed_steps.append(step['description'])
        
        print("\n" + "="*100)
    
    # Final summary
    overall_time = time.time() - overall_start
    
    print_header("ANALYSIS PIPELINE COMPLETE")
    
    print("Execution Summary:")
    print(f"  - Total Steps: {total_steps}")
    print(f"  - Successful: {successful_steps}")
    print(f"  - Failed: {len(failed_steps)}")
    print(f"  - Total Time: {overall_time:.2f} seconds ({overall_time/60:.2f} minutes)")
    print(f"  - End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if failed_steps:
        print("\n[ERROR] Failed Steps:")
        for step in failed_steps:
            print(f"    - {step}")
    else:
        print("\n[OK] All steps completed successfully!")
    
    # List all outputs
    print("\n" + "="*100)
    print("OUTPUT FILES GENERATED:")
    print("="*100)
    
    if os.path.exists('analysis_outputs'):
        files = sorted(os.listdir('analysis_outputs'))
        
        csv_files = [f for f in files if f.endswith('.csv')]
        txt_files = [f for f in files if f.endswith('.txt')]
        png_files = [f for f in files if f.endswith('.png')]
        
        if csv_files:
            print("\nDATA FILES (CSV):")
            for f in csv_files:
                size = os.path.getsize(f'analysis_outputs/{f}') / 1024
                print(f"  - {f} ({size:.1f} KB)")
        
        if txt_files:
            print("\nREPORT FILES (TXT):")
            for f in txt_files:
                size = os.path.getsize(f'analysis_outputs/{f}') / 1024
                print(f"  - {f} ({size:.1f} KB)")
        
        if png_files:
            print("\nVISUALIZATIONS (PNG):")
            for f in png_files:
                size = os.path.getsize(f'analysis_outputs/{f}') / 1024
                print(f"  - {f} ({size:.1f} KB)")
        
        print(f"\nTotal files generated: {len(files)}")
    
    print("\n" + "="*100)
    print("NEXT STEPS:")
    print("="*100)
    print("\n1. Review the comprehensive report:")
    print("   analysis_outputs/COMPREHENSIVE_ANALYSIS_REPORT.txt")
    print("\n2. Examine the visualizations in the analysis_outputs/ folder")
    print("\n3. Explore the detailed CSV files for specific variable analysis")
    print("\n4. Use the combined_feature_importance.csv for prioritizing interventions")
    
    print("\n" + "="*100)
    print("ANALYSIS COMPLETE - Thank you!")
    print("="*100 + "\n")

if __name__ == "__main__":
    main()

