"""
==============================================================================
AGENT COMPARISON REPORT
==============================================================================
"""

import pandas as pd
import json
from datetime import datetime

print("="*100)
print("GENERATING AGENT COMPARISON REPORT")
print("="*100)

# Load metadata for both agents
with open('analysis_outputs/top_agent/01_metadata.json', 'r') as f:
    top_meta = json.load(f)

with open('analysis_outputs/worst_agent/01_metadata.json', 'r') as f:
    worst_meta = json.load(f)

# Load importance data
top_imp = pd.read_csv('analysis_outputs/top_agent/03_importance_combined.csv')
worst_imp = pd.read_csv('analysis_outputs/worst_agent/03_importance_combined.csv')

# Load correlation data
top_corr = pd.read_csv('analysis_outputs/top_agent/02_correlation_with_target.csv')
worst_corr = pd.read_csv('analysis_outputs/worst_agent/02_correlation_with_target.csv')

# Generate report
report = []
report.append("="*100)
report.append("AGENT COMPARISON REPORT: TOP VS WORST PERFORMER")
report.append("="*100)
report.append(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

report.append(f"\nTOP AGENT: {top_meta['agent_name']}")
report.append(f"  Total Calls: {top_meta['total_records']}")
report.append(f"  Short Calls: {top_meta['short_calls']} ({top_meta['short_calls']/top_meta['total_records']*100:.1f}%)")
report.append(f"  Long Calls: {top_meta['long_calls']} ({top_meta['long_calls']/top_meta['total_records']*100:.1f}%)")

report.append(f"\nWORST AGENT: {worst_meta['agent_name']}")
report.append(f"  Total Calls: {worst_meta['total_records']}")
report.append(f"  Short Calls: {worst_meta['short_calls']} ({worst_meta['short_calls']/worst_meta['total_records']*100:.1f}%)")
report.append(f"  Long Calls: {worst_meta['long_calls']} ({worst_meta['long_calls']/worst_meta['total_records']*100:.1f}%)")

report.append("\n" + "="*100)
report.append("TOP 10 MOST IMPORTANT VARIABLES - TOP AGENT")
report.append("="*100)
for idx, row in top_imp.head(10).iterrows():
    report.append(f"  {idx+1}. {row['Variable']}: {row['Combined_Score']:.4f}")

report.append("\n" + "="*100)
report.append("TOP 10 MOST IMPORTANT VARIABLES - WORST AGENT")
report.append("="*100)
for idx, row in worst_imp.head(10).iterrows():
    report.append(f"  {idx+1}. {row['Variable']}: {row['Combined_Score']:.4f}")

# Save report
with open('analysis_outputs/AGENT_COMPARISON_REPORT.txt', 'w') as f:
    f.write("\n".join(report))

print("\n[OK] Comparison report saved to analysis_outputs/AGENT_COMPARISON_REPORT.txt")
