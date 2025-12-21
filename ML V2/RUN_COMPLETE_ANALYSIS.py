"""
==============================================================================
COMPLETE ANALYSIS ORCHESTRATOR
==============================================================================

Runs all 13 analysis scripts in correct order:
- Phase 1: Level 1 (Variable-Level) - 6 scripts
- Phase 2: Level 2 (Value-Level) - 6 scripts  
- Phase 3: Combined Report - 1 script

==============================================================================
"""

import subprocess
import time
from datetime import datetime

def print_header(text):
    print("\n" + "="*100)
    print(text.center(100))
    print("="*100 + "\n")

def run_script(script_name, phase, step, total):
    """Run a script and track time"""
    print(f"\n[{step}/{total}] {phase}: {script_name}")
    print("-" * 100)
    
    start = time.time()
    
    try:
        result = subprocess.run(
            ['python', script_name],
            capture_output=True,
            text=True,
            check=True,
            encoding='utf-8',
            errors='replace'
        )
        
        elapsed = time.time() - start
        print(f"[OK] Completed in {elapsed:.1f}s")
        return True, elapsed
        
    except subprocess.CalledProcessError as e:
        elapsed = time.time() - start
        print(f"[ERROR] Failed in {elapsed:.1f}s")
        print(f"Error: {e.stderr[:300]}")
        return False, elapsed
    except Exception as e:
        elapsed = time.time() - start
        print(f"[ERROR] {str(e)}")
        return False, elapsed

def main():
    print_header("COMPLETE TWO-LEVEL ANALYSIS PIPELINE")
    
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Define pipeline
    pipeline = [
        # PHASE 1: LEVEL 1 (VARIABLE-LEVEL)
        ('Phase 1: Level 1', '01_variable_level_preprocessing.py'),
        ('Phase 1: Level 1', '02_variable_level_correlation.py'),
        ('Phase 1: Level 1', '03_variable_level_feature_importance.py'),
        ('Phase 1: Level 1', '04_variable_level_statistical_tests.py'),
        ('Phase 1: Level 1', '05_variable_level_shap.py'),
        ('Phase 1: Level 1', '06_variable_level_visualizations.py'),
        
        # PHASE 2: LEVEL 2 (VALUE-LEVEL)
        ('Phase 2: Level 2', '07_value_level_categorical_analysis.py'),
        ('Phase 2: Level 2', '08_value_level_numerical_binning.py'),
        ('Phase 2: Level 2', '09_value_level_feature_importance.py'),
        ('Phase 2: Level 2', '10_value_level_statistical_tests.py'),
        ('Phase 2: Level 2', '11_value_level_shap.py'),
        ('Phase 2: Level 2', '12_value_level_visualizations.py'),
        
        # PHASE 3: COMBINED REPORT
        ('Phase 3: Report', '13_combined_report.py')
    ]
    
    total_scripts = len(pipeline)
    results = []
    overall_start = time.time()
    
    # Run pipeline
    for i, (phase, script) in enumerate(pipeline, 1):
        success, elapsed = run_script(script, phase, i, total_scripts)
        results.append((script, phase, success, elapsed))
        
        if not success:
            print(f"\n[WARNING] {script} failed, but continuing...")
    
    # Summary
    overall_time = time.time() - overall_start
    
    print_header("PIPELINE EXECUTION SUMMARY")
    
    passed = sum(1 for _, _, success, _ in results if success)
    failed = total_scripts - passed
    
    print("SCRIPT RESULTS:")
    print("-" * 100)
    for script, phase, success, elapsed in results:
        status = "[OK]  " if success else "[FAIL]"
        print(f"{status} {script:50s} ({elapsed:5.1f}s) - {phase}")
    
    print("\n" + "="*100)
    print(f"Total: {passed}/{total_scripts} passed")
    print(f"Total Time: {overall_time:.1f}s ({overall_time/60:.1f} minutes)")
    print(f"End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*100)
    
    if passed == total_scripts:
        print("\n[SUCCESS] All scripts completed successfully!")
        print("\nOutputs:")
        print("  - analysis_outputs/level1_variable/ (Variable-level results)")
        print("  - analysis_outputs/level2_value/ (Value-level results)")
        print("  - analysis_outputs/COMPLETE_ANALYSIS_REPORT.txt (Final report)")
    else:
        print(f"\n[WARNING] {failed} script(s) failed. Check logs above.")
    
    return passed == total_scripts

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)

