"""
==============================================================================
COMPLETE ANALYSIS ORCHESTRATOR
==============================================================================

Runs all 13 analysis scripts in correct order:
- Phase 1: Level 1 (Variable-Level) - 6 scripts
- Phase 2: Level 2 (Value-Level) - 6 scripts  
- Phase 3: Combined Report - 1 script

Logs: Both terminal output and complete_analysis.log file
==============================================================================
"""

import subprocess
import time
from datetime import datetime
import sys

# Log file
LOG_FILE = 'complete_analysis.log'

def log_and_print(message, log_file=None):
    """Print to terminal and write to log file"""
    print(message)
    if log_file:
        log_file.write(message + '\n')
        log_file.flush()

def print_header(text, log_file=None):
    separator = "\n" + "="*100 + "\n"
    header = separator + text.center(100) + separator
    log_and_print(header, log_file)

def run_script(script_name, phase, step, total, log_file):
    """Run a script and track time with full output logging"""
    header = f"\n[{step}/{total}] {phase}: {script_name}"
    separator = "-" * 100
    
    log_and_print(header, log_file)
    log_and_print(separator, log_file)
    
    start = time.time()
    
    try:
        # Run script and capture output in real-time
        process = subprocess.Popen(
            ['python', script_name],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding='utf-8',
            errors='replace',
            bufsize=1,
            universal_newlines=True
        )
        
        # Stream output line by line
        for line in iter(process.stdout.readline, ''):
            if line:
                line = line.rstrip()
                log_and_print(f"  {line}", log_file)
        
        process.wait()
        elapsed = time.time() - start
        
        if process.returncode == 0:
            log_and_print(f"\n[OK] Completed in {elapsed:.1f}s", log_file)
            return True, elapsed
        else:
            log_and_print(f"\n[ERROR] Failed in {elapsed:.1f}s (exit code: {process.returncode})", log_file)
            return False, elapsed
        
    except Exception as e:
        elapsed = time.time() - start
        log_and_print(f"\n[ERROR] {str(e)}", log_file)
        return False, elapsed

def main():
    # Open log file
    with open(LOG_FILE, 'w', encoding='utf-8') as log_file:
        
        print_header("COMPLETE TWO-LEVEL ANALYSIS PIPELINE", log_file)
        
        start_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_and_print(f"Start Time: {start_time}", log_file)
        log_and_print(f"Log File: {LOG_FILE}", log_file)
        
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
            success, elapsed = run_script(script, phase, i, total_scripts, log_file)
            results.append((script, phase, success, elapsed))
            
            if not success:
                log_and_print(f"\n[WARNING] {script} failed, but continuing...", log_file)
        
        # Summary
        overall_time = time.time() - overall_start
        
        print_header("PIPELINE EXECUTION SUMMARY", log_file)
        
        passed = sum(1 for _, _, success, _ in results if success)
        failed = total_scripts - passed
        
        log_and_print("SCRIPT RESULTS:", log_file)
        log_and_print("-" * 100, log_file)
        for script, phase, success, elapsed in results:
            status = "[OK]  " if success else "[FAIL]"
            log_and_print(f"{status} {script:50s} ({elapsed:5.1f}s) - {phase}", log_file)
        
        log_and_print("\n" + "="*100, log_file)
        log_and_print(f"Total: {passed}/{total_scripts} passed", log_file)
        log_and_print(f"Total Time: {overall_time:.1f}s ({overall_time/60:.1f} minutes)", log_file)
        end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_and_print(f"End Time: {end_time}", log_file)
        log_and_print("="*100, log_file)
        
        if passed == total_scripts:
            log_and_print("\n[SUCCESS] All scripts completed successfully!", log_file)
            log_and_print("\nOutputs:", log_file)
            log_and_print("  - analysis_outputs/level1_variable/ (Variable-level results)", log_file)
            log_and_print("  - analysis_outputs/level2_value/ (Value-level results)", log_file)
            log_and_print("  - analysis_outputs/COMPLETE_ANALYSIS_REPORT.txt (Final report)", log_file)
            log_and_print(f"  - {LOG_FILE} (Complete execution log)", log_file)
        else:
            log_and_print(f"\n[WARNING] {failed} script(s) failed. Check logs above.", log_file)
        
        return passed == total_scripts

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)

