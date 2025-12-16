"""Check the timing of the parallel vs sequential processing"""
from pathlib import Path
from datetime import datetime

# Sequential processing log (from earlier)
sequential_log = Path("../../logs/sales_call_analysis_20251217_001443.log")

# Parallel processing log (most recent)
parallel_log = Path("../../logs/sales_call_analysis_20251217_002529.log")

def get_processing_time(log_file):
    """Extract processing time from log file"""
    if not log_file.exists():
        return None
    
    with open(log_file, 'r') as f:
        lines = f.readlines()
    
    start_time = None
    end_time = None
    
    for line in lines:
        if 'Starting processing of' in line and 'rows' in line:
            # Extract timestamp: 2025-12-17 00:14:45
            timestamp_str = line.split(' - ')[0]
            start_time = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
        
        if 'PROCESSING COMPLETE' in line:
            timestamp_str = line.split(' - ')[0]
            end_time = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
            break
    
    if start_time and end_time:
        return (end_time - start_time).total_seconds()
    return None

print("=" * 80)
print("PERFORMANCE COMPARISON: Sequential vs Parallel Processing")
print("=" * 80)

seq_time = get_processing_time(sequential_log)
par_time = get_processing_time(parallel_log)

if seq_time:
    print(f"\nSequential Processing (one row at a time):")
    print(f"  Time: {seq_time:.1f} seconds ({seq_time/60:.2f} minutes)")
    print(f"  Log: {sequential_log.name}")

if par_time:
    print(f"\nParallel Processing (10 rows simultaneously):")
    print(f"  Time: {par_time:.1f} seconds ({par_time/60:.2f} minutes)")
    print(f"  Log: {parallel_log.name}")

if seq_time and par_time:
    speedup = seq_time / par_time
    time_saved = seq_time - par_time
    print(f"\n{'='*80}")
    print(f"SPEEDUP: {speedup:.2f}x faster!")
    print(f"TIME SAVED: {time_saved:.1f} seconds ({time_saved/60:.2f} minutes)")
    print(f"{'='*80}")

print("\nWith parallel processing, all 10 rows in a batch are processed")
print("simultaneously, dramatically reducing total processing time!")
print("=" * 80)

