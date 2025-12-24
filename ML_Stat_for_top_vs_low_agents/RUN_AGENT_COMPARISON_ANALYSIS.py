"""
==============================================================================
AGENT-LEVEL COMPARISON ANALYSIS ORCHESTRATOR
==============================================================================

Compares TOP Agent vs WORST Agent using the same ML pipeline:
- TOP Agent: DARWINSANCHEZ24
- WORST Agent: ARTURODELEON

Runs complete analysis for each agent:
1. Data preprocessing and filtering
2. Correlation analysis
3. Feature importance (RF, XGBoost)
4. Statistical tests
5. SHAP analysis
6. LIME analysis
7. Comprehensive visualizations

Output: Identical analysis structure for both agents to enable comparison
==============================================================================
"""

import subprocess
import time
from datetime import datetime
import sys
import os

# Agent configurations
TOP_AGENT = "DARWINSANCHEZ24"
WORST_AGENT = "ARTURODELEON"

# Log file
LOG_FILE = 'agent_comparison_analysis.log'

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

def run_script(script_name, agent_name, agent_type, step, total, log_file):
    """Run a script for a specific agent"""
    header = f"\n[{step}/{total}] {agent_type} ({agent_name}): {script_name}"
    separator = "-" * 100
    
    log_and_print(header, log_file)
    log_and_print(separator, log_file)
    
    start = time.time()
    
    try:
        # Set environment variable for agent name
        env = os.environ.copy()
        env['ANALYSIS_AGENT'] = agent_name
        env['AGENT_TYPE'] = agent_type.lower().replace(' ', '_')
        
        # Run script and capture output in real-time
        process = subprocess.Popen(
            ['python', script_name, agent_name, agent_type.lower().replace(' ', '_')],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding='utf-8',
            errors='replace',
            bufsize=1,
            universal_newlines=True,
            env=env
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
        
        print_header("AGENT-LEVEL COMPARISON ANALYSIS PIPELINE", log_file)
        
        start_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_and_print(f"Start Time: {start_time}", log_file)
        log_and_print(f"Log File: {LOG_FILE}", log_file)
        log_and_print(f"\nTOP Agent: {TOP_AGENT}", log_file)
        log_and_print(f"WORST Agent: {WORST_AGENT}", log_file)
        
        # Define pipeline steps
        analysis_scripts = [
            '01_agent_preprocessing.py',
            '02_agent_correlation.py',
            '03_agent_feature_importance.py',
            '04_agent_statistical_tests.py',
            '05_agent_shap.py',
            '05b_agent_lime.py',
            '06_agent_visualizations.py'
        ]
        
        # Calculate total steps
        total_scripts = len(analysis_scripts) * 2 + 1  # 2 agents + 1 comparison report
        results = []
        overall_start = time.time()
        current_step = 0
        
        # Run pipeline for TOP Agent
        print_header(f"ANALYZING TOP AGENT: {TOP_AGENT}", log_file)
        for script in analysis_scripts:
            current_step += 1
            success, elapsed = run_script(script, TOP_AGENT, 'top_agent', current_step, total_scripts, log_file)
            results.append((f"{script} (TOP)", success, elapsed))
            
            if not success:
                log_and_print(f"\n[WARNING] {script} failed for TOP agent, but continuing...", log_file)
        
        # Run pipeline for WORST Agent
        print_header(f"ANALYZING WORST AGENT: {WORST_AGENT}", log_file)
        for script in analysis_scripts:
            current_step += 1
            success, elapsed = run_script(script, WORST_AGENT, 'worst_agent', current_step, total_scripts, log_file)
            results.append((f"{script} (WORST)", success, elapsed))
            
            if not success:
                log_and_print(f"\n[WARNING] {script} failed for WORST agent, but continuing...", log_file)
        
        # Generate comparison report
        current_step += 1
        print_header("GENERATING COMPARISON REPORT", log_file)
        success, elapsed = run_script('07_comparison_report.py', 'BOTH', 'comparison', current_step, total_scripts, log_file)
        results.append(('07_comparison_report.py', success, elapsed))
        
        # Summary
        overall_time = time.time() - overall_start
        
        print_header("PIPELINE EXECUTION SUMMARY", log_file)
        
        passed = sum(1 for _, success, _ in results if success)
        failed = total_scripts - passed
        
        log_and_print("SCRIPT RESULTS:", log_file)
        log_and_print("-" * 100, log_file)
        for script, success, elapsed in results:
            status = "[OK]  " if success else "[FAIL]"
            log_and_print(f"{status} {script:60s} ({elapsed:5.1f}s)", log_file)
        
        log_and_print("\n" + "="*100, log_file)
        log_and_print(f"Total: {passed}/{total_scripts} passed", log_file)
        log_and_print(f"Total Time: {overall_time:.1f}s ({overall_time/60:.1f} minutes)", log_file)
        end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_and_print(f"End Time: {end_time}", log_file)
        log_and_print("="*100, log_file)
        
        if passed == total_scripts:
            log_and_print("\n[SUCCESS] All scripts completed successfully!", log_file)
            log_and_print("\nOutputs:", log_file)
            log_and_print(f"  - analysis_outputs/top_agent/ ({TOP_AGENT} results)", log_file)
            log_and_print(f"  - analysis_outputs/worst_agent/ ({WORST_AGENT} results)", log_file)
            log_and_print(f"  - analysis_outputs/AGENT_COMPARISON_REPORT.txt (Comparison report)", log_file)
            log_and_print(f"  - {LOG_FILE} (Complete execution log)", log_file)
        else:
            log_and_print(f"\n[WARNING] {failed} script(s) failed. Check logs above.", log_file)
        
        return passed == total_scripts

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)

