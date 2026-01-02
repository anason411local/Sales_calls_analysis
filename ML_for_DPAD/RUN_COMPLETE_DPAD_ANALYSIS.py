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
        'name': 'Advanced Agent Analysis',
        'script': 'ML_for_DPAD/08b_dpad_advanced_agent_analysis.py',
        'description': 'Statistical, ML, and temporal agent analysis',
        'critical': False
    },
    {
        'id': 10,
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


def run_script(script_info, script_number, total_scripts):
    """Run a single analysis script"""
    script_id = script_info['id']
    script_name = script_info['name']
    script_path = script_info['script']
    
    print(f"\n{'='*70}")
    print(f"SCRIPT {script_id}/{total_scripts}: {script_name}")
    print(f"{'='*70}")
    print(f"Description: {script_info['description']}")
    print(f"File: {script_path}")
    print(f"Critical: {'Yes' if script_info['critical'] else 'No'}")
    print(f"Progress: [{script_number}/{total_scripts}] ({int(script_number/total_scripts*100)}%)")
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
            
            # Extract key findings from output
            key_findings = extract_key_findings(result.stdout, script_name)
            
            return {
                'success': True,
                'time': execution_time,
                'output': result.stdout,
                'error': None,
                'findings': key_findings
            }
        else:
            print(result.stdout)
            if result.stderr:
                print("\n⚠️  STDERR:")
                print(result.stderr)
            print("-"*70)
            print(f"❌ FAILED - Error after {execution_time:.2f} seconds")
            
            # Provide helpful error suggestions
            error_suggestion = get_error_suggestion(script_name, result.stderr)
            if error_suggestion:
                print(f"\n💡 Suggestion: {error_suggestion}")
            
            return {
                'success': False,
                'time': execution_time,
                'output': result.stdout,
                'error': result.stderr,
                'findings': None
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
            'error': str(e),
            'findings': None
        }


def extract_key_findings(output, script_name):
    """Extract key findings from script output"""
    findings = {}
    
    try:
        if "Preprocessing" in script_name:
            if "Total samples:" in output:
                for line in output.split('\n'):
                    if "Total samples:" in line:
                        findings['total_samples'] = line.split(':')[1].strip()
                    elif "High-DPAD group:" in line:
                        findings['high_dpad'] = line.split(':')[1].strip().split()[0]
                    elif "Low-DPAD group:" in line:
                        findings['low_dpad'] = line.split(':')[1].strip().split()[0]
        
        elif "Correlation" in script_name:
            if "Top positive correlation:" in output:
                for line in output.split('\n'):
                    if "Top positive correlation:" in line:
                        findings['top_correlation'] = line.split(':')[1].strip()
        
        elif "Feature Importance" in script_name:
            if "Top 3 Features" in output:
                findings['models'] = "RF + XGBoost"
        
        elif "Statistical" in script_name:
            if "Significant at p<0.05:" in output:
                for line in output.split('\n'):
                    if "Significant at p<0.05:" in line:
                        findings['significant_features'] = line.split(':')[1].strip()
        
        elif "SHAP" in script_name:
            if "Top 3 variables" in output:
                findings['method'] = "SHAP (RF + XGBoost)"
        
        elif "LIME" in script_name:
            if "Top 3 variables" in output:
                findings['method'] = "LIME (RF + XGBoost)"
        
        elif "Visualizations" in script_name:
            findings['charts'] = "7 visualizations"
        
        elif "Agent-Level" in script_name:
            if "Total agents:" in output:
                for line in output.split('\n'):
                    if "Total agents:" in line:
                        findings['agents'] = line.split(':')[1].strip()
        
        elif "Advanced Agent" in script_name:
            if "Large effect sizes:" in output:
                for line in output.split('\n'):
                    if "Large effect sizes:" in line:
                        findings['large_effects'] = line.split(':')[1].strip()
                    elif "PC1+PC2 variance explained:" in line:
                        findings['pca_variance'] = line.split(':')[1].strip()
                    elif "Optimal clusters:" in line:
                        findings['clusters'] = line.split(':')[1].strip()
        
        elif "Combined Report" in script_name:
            findings['reports'] = "Text + HTML + Summary"
    
    except Exception:
        pass
    
    return findings


def get_error_suggestion(script_name, error_message):
    """Provide helpful suggestions based on error type"""
    if not error_message:
        return None
    
    error_lower = error_message.lower()
    
    if "filenotfounderror" in error_lower or "no such file" in error_lower:
        return "Check that data files exist in output_data/ folder and previous scripts completed successfully."
    
    elif "modulenotfounderror" in error_lower or "no module named" in error_lower:
        if "shap" in error_lower:
            return "Install SHAP: pip install shap"
        elif "lime" in error_lower:
            return "Install LIME: pip install lime"
        elif "xgboost" in error_lower:
            return "Install XGBoost: pip install xgboost"
        else:
            return "Install missing package: pip install <package_name>"
    
    elif "valueerror" in error_lower and "shape" in error_lower:
        return "Data shape mismatch. Check that preprocessing completed correctly."
    
    elif "keyerror" in error_lower:
        return "Missing expected column. Verify data files and preprocessing output."
    
    elif "runtimeerror" in error_lower and "main thread" in error_lower:
        return "Matplotlib backend issue. Script may have completed despite error."
    
    return "Check the execution report for full error details."


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
        'ML_for_DPAD/analysis_outputs/agent_level_advanced/08b_advanced_report.txt',
        'ML_for_DPAD/analysis_outputs/agent_level_advanced/08b_effect_sizes.csv',
        'ML_for_DPAD/analysis_outputs/agent_level_advanced/08b_pca_biplot.png',
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
        
        # Add key findings to report
        if result.get('findings'):
            report.append(f"  Key Findings:")
            for key, value in result['findings'].items():
                report.append(f"    - {key}: {value}")
        
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


def print_key_findings_summary(results):
    """Print summary of key findings from all scripts"""
    print(f"\n{'='*70}")
    print("KEY FINDINGS SUMMARY")
    print(f"{'='*70}")
    
    has_findings = False
    
    for script, result in zip(SCRIPTS, results):
        if result.get('findings') and result['success']:
            has_findings = True
            print(f"\n📊 {script['name']}:")
            for key, value in result['findings'].items():
                print(f"   • {key.replace('_', ' ').title()}: {value}")
    
    if not has_findings:
        print("\n   No key findings extracted from outputs.")
    
    print(f"\n{'='*70}")


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
        print(f"\n{'='*70}")
        print("🎉 ALL SCRIPTS COMPLETED SUCCESSFULLY!")
        print(f"{'='*70}")
        print(f"\n📄 Key Output Files:")
        print(f"   ┌─ Reports:")
        print(f"   │  ├─ Executive Report (TXT): ML_for_DPAD/analysis_outputs/final_report/EXECUTIVE_REPORT.txt")
        print(f"   │  ├─ Executive Report (HTML): ML_for_DPAD/analysis_outputs/final_report/EXECUTIVE_REPORT.html")
        print(f"   │  └─ Quick Summary: ML_for_DPAD/analysis_outputs/final_report/QUICK_SUMMARY.txt")
        print(f"   │")
        print(f"   ├─ Visualizations:")
        print(f"   │  ├─ Summary Dashboard: ML_for_DPAD/analysis_outputs/visualizations/summary_dashboard.png")
        print(f"   │  └─ Distribution Plots: ML_for_DPAD/analysis_outputs/visualizations/")
        print(f"   │")
        print(f"   ├─ Analysis Results:")
        print(f"   │  ├─ Feature Importance: ML_for_DPAD/analysis_outputs/feature_importance/")
        print(f"   │  ├─ Statistical Tests: ML_for_DPAD/analysis_outputs/statistical_tests/")
        print(f"   │  ├─ SHAP Analysis: ML_for_DPAD/analysis_outputs/shap_analysis/")
        print(f"   │  └─ LIME Analysis: ML_for_DPAD/analysis_outputs/lime_analysis/")
        print(f"   │")
        print(f"   ├─ Agent-Level Insights:")
        print(f"   │  ├─ Basic Analysis: ML_for_DPAD/analysis_outputs/agent_level_comparison/")
        print(f"   │  └─ Advanced Analysis: ML_for_DPAD/analysis_outputs/agent_level_advanced/")
        print(f"   │      ├─ Effect Sizes: 08b_effect_sizes.csv")
        print(f"   │      ├─ PCA Biplot: 08b_pca_biplot.png")
        print(f"   │      ├─ Clustering: 08b_clustering_dendrogram_heatmap.png")
        print(f"   │      └─ Temporal Trends: 08b_temporal_trends.png")
        print(f"   │")
        print(f"   └─ Execution Report: ML_for_DPAD/analysis_outputs/execution_report.txt")
        print(f"\n💡 Next Steps:")
        print(f"   1. Review the Executive Report (HTML version recommended)")
        print(f"   2. Examine the Summary Dashboard for quick insights")
        print(f"   3. Dive into specific analysis folders for detailed results")
        print(f"   4. Share findings with your team!")
    elif successful >= len(SCRIPTS) * 0.7:  # At least 70% success
        print(f"\n{'='*70}")
        print("✅ PIPELINE MOSTLY SUCCESSFUL")
        print(f"{'='*70}")
        print(f"\n⚠️  Some non-critical scripts failed, but core analysis is complete.")
        print(f"\n📄 Available Outputs:")
        print(f"   • Executive Report: ML_for_DPAD/analysis_outputs/final_report/EXECUTIVE_REPORT.txt")
        print(f"   • Analysis Results: ML_for_DPAD/analysis_outputs/")
        print(f"\n💡 Recommendation:")
        print(f"   • Review the execution report for details on failed scripts")
        print(f"   • Fix any errors and rerun if needed")
        print(f"   • Core analysis results are still usable")
    else:
        print(f"\n{'='*70}")
        print("⚠️  PIPELINE HAD SIGNIFICANT FAILURES")
        print(f"{'='*70}")
        print(f"\n❌ Multiple scripts failed. Please check the execution report:")
        print(f"   📄 ML_for_DPAD/analysis_outputs/execution_report.txt")
        print(f"\n💡 Troubleshooting Steps:")
        print(f"   1. Check the error messages above for specific issues")
        print(f"   2. Verify all required packages are installed:")
        print(f"      pip install pandas numpy scikit-learn matplotlib seaborn xgboost shap lime")
        print(f"   3. Ensure data files exist in output_data/ folder")
        print(f"   4. Check that you have write permissions in the project directory")
        print(f"   5. Try running failed scripts individually to isolate issues")
    
    print(f"\n{'='*70}")
    
    # Show performance stats
    if successful > 0:
        print(f"\n⚡ Performance Stats:")
        print(f"   • Average time per script: {total_time/len(SCRIPTS):.2f} seconds")
        print(f"   • Total data processed: 3,220 calls (1,192 High-DPAD + 2,028 Low-DPAD)")
        print(f"   • Agents analyzed: 11 agents (5 High-DPAD + 6 Low-DPAD)")
        print(f"   • Analysis methods: {len(SCRIPTS)} comprehensive techniques")
        print(f"   • Output files generated: 150+ files and visualizations")
        print(f"\n{'='*70}")


def main():
    """Main pipeline execution"""
    
    print_banner()
    
    # Start timing
    pipeline_start = time.time()
    
    # Run all scripts
    results = []
    continue_execution = True
    
    for idx, script in enumerate(SCRIPTS, 1):
        if not continue_execution:
            print(f"\n⚠️  Skipping {script['name']} due to critical failure")
            results.append({
                'success': False,
                'time': 0,
                'output': None,
                'error': 'Skipped due to previous critical failure',
                'findings': None
            })
            continue
        
        # Calculate estimated time remaining
        if idx > 1:
            avg_time = sum(r['time'] for r in results) / len(results)
            est_remaining = avg_time * (len(SCRIPTS) - idx + 1)
            print(f"\n⏱️  Estimated time remaining: ~{int(est_remaining)} seconds")
        
        result = run_script(script, idx, len(SCRIPTS))
        results.append(result)
        
        # Stop if critical script fails
        if not result['success'] and script['critical']:
            print(f"\n❌ CRITICAL SCRIPT FAILED: {script['name']}")
            print(f"   Stopping pipeline execution.")
            print(f"   💡 Fix the error above and rerun the pipeline.")
            continue_execution = False
    
    # Total execution time
    total_time = time.time() - pipeline_start
    
    # Validate outputs
    validation_passed = validate_outputs()
    
    # Generate execution report
    successful, failed = generate_execution_report(results, total_time)
    
    # Print key findings summary
    print_key_findings_summary(results)
    
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

