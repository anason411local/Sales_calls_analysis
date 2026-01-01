"""
DPAD Analysis - Master Runner Script
=====================================

Purpose:
--------
Automate the complete DPAD analysis pipeline by running all scripts
in sequence with error handling, progress tracking, and timing.

What This Script Does:
----------------------
1. Runs all 9 analysis scripts in correct order
2. Tracks execution time for each script
3. Handles errors gracefully
4. Generates execution summary report
5. Validates outputs were created
6. Creates backup of results

Usage:
------
Simply run: python ML_for_DPAD/RUN_COMPLETE_DPAD_ANALYSIS.py

Or from command line: python ML_for_DPAD/RUN_COMPLETE_DPAD_ANALYSIS.py

Author: AI Agent
Date: 2025
"""

import subprocess
import sys
import time
from pathlib import Path
from datetime import datetime, timedelta
import json

# Fix Windows console encoding
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'ignore')


# Define all scripts in execution order
SCRIPTS = [
    {
        'id': 1,
        'name': 'Preprocessing',
        'script': 'ML_for_DPAD/01_dpad_preprocessing.py',
        'description': 'Load, clean, and encode data',
        'critical': True
    },
    {
        'id': 2,
        'name': 'Correlation Analysis',
        'script': 'ML_for_DPAD/02_dpad_correlation.py',
        'description': 'Identify feature correlations with DPAD',
        'critical': True
    },
    {
        'id': 3,
        'name': 'Feature Importance',
        'script': 'ML_for_DPAD/03_dpad_feature_importance.py',
        'description': 'Random Forest & XGBoost rankings',
        'critical': True
    },
    {
        'id': 4,
        'name': 'Statistical Tests',
        'script': 'ML_for_DPAD/04_dpad_statistical_tests.py',
        'description': 'T-tests, Mann-Whitney, Chi-square',
        'critical': True
    },
    {
        'id': 5,
        'name': 'SHAP Analysis',
        'script': 'ML_for_DPAD/05_dpad_shap.py',
        'description': 'Model interpretability with SHAP',
        'critical': False
    },
    {
        'id': 6,
        'name': 'LIME Analysis',
        'script': 'ML_for_DPAD/06_dpad_lime.py',
        'description': 'Local explanations with LIME',
        'critical': False
    },
    {
        'id': 7,
        'name': 'Visualizations',
        'script': 'ML_for_DPAD/07_dpad_visualizations.py',
        'description': 'Distribution comparisons and plots',
        'critical': False
    },
    {
        'id': 8,
        'name': 'Agent-Level Analysis',
        'script': 'ML_for_DPAD/08_dpad_agent_level.py',
        'description': 'Aggregate insights by agent',
        'critical': False
    },
    {
        'id': 9,
        'name': 'Combined Report',
        'script': 'ML_for_DPAD/09_dpad_combined_report.py',
        'description': 'Generate executive report',
        'critical': True
    }
]


def print_banner():
    """Print welcome banner"""
    banner = """
    ╔═══════════════════════════════════════════════════════════════════╗
    ║                                                                   ║
    ║          DPAD ANALYSIS - COMPLETE PIPELINE RUNNER                ║
    ║                                                                   ║
    ║     Analyzing High-DPAD vs Low-DPAD Calling Agents               ║
    ║                                                                   ║
    ╚═══════════════════════════════════════════════════════════════════╝
    """
    print(banner)
    print(f"\n    Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"    Total Scripts: {len(SCRIPTS)}")
    print("\n" + "="*70)


def run_script(script_info):
    """Run a single analysis script"""
    script_id = script_info['id']
    script_name = script_info['name']
    script_path = script_info['script']
    
    print(f"\n{'='*70}")
    print(f"SCRIPT {script_id}/9: {script_name}")
    print(f"{'='*70}")
    print(f"Description: {script_info['description']}")
    print(f"File: {script_path}")
    print(f"Critical: {'Yes' if script_info['critical'] else 'No'}")
    print(f"\n🚀 Starting execution...")
    print("-"*70)
    
    start_time = time.time()
    
    try:
        # Run the script
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        
        execution_time = time.time() - start_time
        
        # Check result
        if result.returncode == 0:
            print(result.stdout)
            print("-"*70)
            print(f"✅ SUCCESS - Completed in {execution_time:.2f} seconds")
            return {
                'success': True,
                'time': execution_time,
                'output': result.stdout,
                'error': None
            }
        else:
            print(result.stdout)
            print("\n⚠️  STDERR:")
            print(result.stderr)
            print("-"*70)
            print(f"❌ FAILED - Error after {execution_time:.2f} seconds")
            return {
                'success': False,
                'time': execution_time,
                'output': result.stdout,
                'error': result.stderr
            }
            
    except Exception as e:
        execution_time = time.time() - start_time
        print(f"❌ EXCEPTION: {str(e)}")
        print("-"*70)
        print(f"❌ FAILED - Exception after {execution_time:.2f} seconds")
        return {
            'success': False,
            'time': execution_time,
            'output': None,
            'error': str(e)
        }


def validate_outputs():
    """Validate that expected output files were created"""
    print(f"\n{'='*70}")
    print("VALIDATING OUTPUTS")
    print(f"{'='*70}")
    
    expected_files = [
        'ML_for_DPAD/analysis_outputs/preprocessed_data/X_features.csv',
        'ML_for_DPAD/analysis_outputs/correlations/all_correlations.csv',
        'ML_for_DPAD/analysis_outputs/feature_importance/rf_gini_importance.csv',
        'ML_for_DPAD/analysis_outputs/statistical_tests/t_test_results.csv',
        'ML_for_DPAD/analysis_outputs/shap_analysis/shap_feature_importance.csv',
        'ML_for_DPAD/analysis_outputs/lime_analysis/lime_feature_importance.csv',
        'ML_for_DPAD/analysis_outputs/visualizations/summary_dashboard.png',
        'ML_for_DPAD/analysis_outputs/agent_level_comparison/agent_aggregated_data.csv',
        'ML_for_DPAD/analysis_outputs/final_report/EXECUTIVE_REPORT.txt',
        'ML_for_DPAD/analysis_outputs/final_report/EXECUTIVE_REPORT.html'
    ]
    
    missing_files = []
    found_files = []
    
    for file_path in expected_files:
        if Path(file_path).exists():
            found_files.append(file_path)
            print(f"   ✓ {file_path}")
        else:
            missing_files.append(file_path)
            print(f"   ✗ {file_path}")
    
    print(f"\n{'='*70}")
    print(f"Files found: {len(found_files)}/{len(expected_files)}")
    
    if missing_files:
        print(f"\n⚠️  Warning: {len(missing_files)} expected files missing")
        return False
    else:
        print(f"\n✅ All expected files created successfully!")
        return True


def generate_execution_report(results, total_time):
    """Generate execution summary report"""
    print(f"\n{'='*70}")
    print("GENERATING EXECUTION REPORT")
    print(f"{'='*70}")
    
    report = []
    report.append("DPAD ANALYSIS - PIPELINE EXECUTION REPORT")
    report.append("="*70)
    report.append("")
    report.append(f"Execution Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"Total Execution Time: {timedelta(seconds=int(total_time))}")
    report.append("")
    report.append("="*70)
    report.append("SCRIPT EXECUTION SUMMARY")
    report.append("="*70)
    report.append("")
    
    successful = 0
    failed = 0
    
    for script, result in zip(SCRIPTS, results):
        status = "✓ SUCCESS" if result['success'] else "✗ FAILED"
        report.append(f"Script {script['id']}: {script['name']}")
        report.append(f"  Status: {status}")
        report.append(f"  Time: {result['time']:.2f} seconds")
        if not result['success'] and result['error']:
            report.append(f"  Error: {result['error'][:200]}")
        report.append("")
        
        if result['success']:
            successful += 1
        else:
            failed += 1
    
    report.append("="*70)
    report.append("OVERALL SUMMARY")
    report.append("="*70)
    report.append("")
    report.append(f"Total Scripts: {len(SCRIPTS)}")
    report.append(f"Successful: {successful}")
    report.append(f"Failed: {failed}")
    report.append(f"Success Rate: {(successful/len(SCRIPTS)*100):.1f}%")
    report.append("")
    report.append(f"Total Time: {timedelta(seconds=int(total_time))}")
    report.append(f"Average Time per Script: {total_time/len(SCRIPTS):.2f} seconds")
    report.append("")
    
    # Save report
    report_path = Path("ML_for_DPAD/analysis_outputs/execution_report.txt")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report))
    
    print(f"✅ Execution report saved: {report_path}")
    
    return successful, failed


def print_final_summary(successful, failed, total_time, validation_passed):
    """Print final execution summary"""
    print(f"\n{'='*70}")
    print("PIPELINE EXECUTION COMPLETE")
    print(f"{'='*70}")
    print(f"\n📊 Results:")
    print(f"   ✓ Successful: {successful}/{len(SCRIPTS)}")
    print(f"   ✗ Failed: {failed}/{len(SCRIPTS)}")
    print(f"   ⏱️  Total Time: {timedelta(seconds=int(total_time))}")
    print(f"   📁 Validation: {'✅ Passed' if validation_passed else '⚠️  Some files missing'}")
    
    if successful == len(SCRIPTS):
        print(f"\n🎉 ALL SCRIPTS COMPLETED SUCCESSFULLY!")
        print(f"\n📄 Key Outputs:")
        print(f"   • Executive Report: ML_for_DPAD/analysis_outputs/final_report/EXECUTIVE_REPORT.txt")
        print(f"   • HTML Report: ML_for_DPAD/analysis_outputs/final_report/EXECUTIVE_REPORT.html")
        print(f"   • Quick Summary: ML_for_DPAD/analysis_outputs/final_report/QUICK_SUMMARY.txt")
        print(f"   • Dashboard: ML_for_DPAD/analysis_outputs/visualizations/summary_dashboard.png")
    else:
        print(f"\n⚠️  SOME SCRIPTS FAILED")
        print(f"   Please check the execution report for details:")
        print(f"   ML_for_DPAD/analysis_outputs/execution_report.txt")
    
    print(f"\n{'='*70}")


def main():
    """Main pipeline execution"""
    
    print_banner()
    
    # Start timing
    pipeline_start = time.time()
    
    # Run all scripts
    results = []
    continue_execution = True
    
    for script in SCRIPTS:
        if not continue_execution:
            print(f"\n⚠️  Skipping {script['name']} due to critical failure")
            results.append({
                'success': False,
                'time': 0,
                'output': None,
                'error': 'Skipped due to previous critical failure'
            })
            continue
        
        result = run_script(script)
        results.append(result)
        
        # Stop if critical script fails
        if not result['success'] and script['critical']:
            print(f"\n❌ CRITICAL SCRIPT FAILED: {script['name']}")
            print(f"   Stopping pipeline execution.")
            continue_execution = False
    
    # Total execution time
    total_time = time.time() - pipeline_start
    
    # Validate outputs
    validation_passed = validate_outputs()
    
    # Generate execution report
    successful, failed = generate_execution_report(results, total_time)
    
    # Print final summary
    print_final_summary(successful, failed, total_time, validation_passed)
    
    # Exit with appropriate code
    if successful == len(SCRIPTS):
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Pipeline execution interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n❌ FATAL ERROR: {str(e)}")
        sys.exit(1)

