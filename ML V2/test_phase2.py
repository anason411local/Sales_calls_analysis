"""
Test Phase 2 Scripts (Value-Level Analysis)
"""
import subprocess
import time

scripts = [
    '07_value_level_categorical_analysis.py',
    '08_value_level_numerical_binning.py',
    '09_value_level_feature_importance.py',
    '10_value_level_statistical_tests.py',
    '11_value_level_shap.py',
    '12_value_level_visualizations.py'
]

print("="*100)
print("TESTING PHASE 2: LEVEL 2 (VALUE-LEVEL) SCRIPTS")
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
print("PHASE 2 TEST RESULTS")
print("="*100)

for script, status, elapsed in results:
    status_icon = "[OK]" if status == 'PASS' else "[FAIL]"
    print(f"{status_icon} {script}: {elapsed:.1f}s")

passed = sum(1 for _, status, _ in results if status == 'PASS')
print(f"\nTotal: {passed}/{len(scripts)} passed")

if passed == len(scripts):
    print("\n[SUCCESS] All Phase 2 scripts passed!")
else:
    print(f"\n[WARNING] {len(scripts) - passed} script(s) failed")

