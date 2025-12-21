"""
Test Phase 1 Scripts
"""
import subprocess
import time

scripts = [
    '01_variable_level_preprocessing.py',
    '02_variable_level_correlation.py',
    '03_variable_level_feature_importance.py',
    '04_variable_level_statistical_tests.py',
    '05_variable_level_shap.py',
    '06_variable_level_visualizations.py'
]

print("="*100)
print("TESTING PHASE 1: LEVEL 1 (VARIABLE-LEVEL) SCRIPTS")
print("="*100)

results = []

for i, script in enumerate(scripts, 1):
    print(f"\n[{i}/6] Running: {script}")
    print("-" * 100)
    
    start = time.time()
    
    try:
        result = subprocess.run(['python', script], 
                              capture_output=True, 
                              text=True,
                              check=True,
                              encoding='utf-8',
                              errors='replace')
        
        elapsed = time.time() - start
        print(f"[OK] Completed in {elapsed:.1f}s")
        results.append((script, 'PASS', elapsed))
        
    except subprocess.CalledProcessError as e:
        elapsed = time.time() - start
        print(f"[ERROR] Failed in {elapsed:.1f}s")
        print(f"Error output: {e.stderr[:200]}")
        results.append((script, 'FAIL', elapsed))
    except Exception as e:
        elapsed = time.time() - start
        print(f"[ERROR] {str(e)}")
        results.append((script, 'FAIL', elapsed))

print("\n" + "="*100)
print("PHASE 1 TEST RESULTS")
print("="*100)

for script, status, elapsed in results:
    status_icon = "[OK]" if status == 'PASS' else "[FAIL]"
    print(f"{status_icon} {script}: {elapsed:.1f}s")

passed = sum(1 for _, status, _ in results if status == 'PASS')
print(f"\nTotal: {passed}/{len(scripts)} passed")

if passed == len(scripts):
    print("\n[SUCCESS] All Phase 1 scripts passed!")
else:
    print(f"\n[WARNING] {len(scripts) - passed} script(s) failed")

