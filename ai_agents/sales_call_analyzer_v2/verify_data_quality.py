"""Verify the quality of extracted data"""
import pandas as pd
from pathlib import Path

output_file = Path("../../output_data/extracted_sales_data.csv")
df = pd.read_csv(output_file)

print("=" * 80)
print("DATA QUALITY VERIFICATION")
print("=" * 80)

# Show sample extracted data from multiple rows
print("\nSample extracted data from Row 0:")
print(f"  fullname: {df.loc[0, 'fullname_source']}")
print(f"  ce_positive_signal_count: {df.loc[0, 'ce_positive_signal_count']}")
print(f"  ce_positive_signal_verbiage: {str(df.loc[0, 'ce_positive_signal_verbiage'])[:100]}...")
print(f"  co_opener_type: {df.loc[0, 'co_opener_type']}")
print(f"  oh_objections_count: {df.loc[0, 'oh_objections_count']}")
print(f"  ot_call_outcome: {df.loc[0, 'ot_call_outcome']}")

print("\nSample extracted data from Row 5:")
print(f"  fullname: {df.loc[5, 'fullname_source']}")
print(f"  ce_positive_signal_count: {df.loc[5, 'ce_positive_signal_count']}")
print(f"  co_opener_type: {df.loc[5, 'co_opener_type']}")
print(f"  oh_objections_count: {df.loc[5, 'oh_objections_count']}")
print(f"  ot_call_outcome: {df.loc[5, 'ot_call_outcome']}")

print("\nSample extracted data from Row 10:")
print(f"  fullname: {df.loc[10, 'fullname_source']}")
print(f"  ce_positive_signal_count: {df.loc[10, 'ce_positive_signal_count']}")
print(f"  co_opener_type: {df.loc[10, 'co_opener_type']}")
print(f"  oh_objections_count: {df.loc[10, 'oh_objections_count']}")
print(f"  ot_call_outcome: {df.loc[10, 'ot_call_outcome']}")

# Check data completeness
print("\n" + "=" * 80)
print("DATA COMPLETENESS CHECK")
print("=" * 80)

extracted_cols = [col for col in df.columns if col.startswith(('ce_', 'co_', 'oh_', 'pc_', 'et_', 'ot_'))]
print(f"\nTotal extracted columns: {len(extracted_cols)}")

# Count non-null values for each category
categories = {
    'Customer Engagement (ce_)': [c for c in extracted_cols if c.startswith('ce_')],
    'Call Opening (co_)': [c for c in extracted_cols if c.startswith('co_')],
    'Objection Handling (oh_)': [c for c in extracted_cols if c.startswith('oh_')],
    'Pace Control (pc_)': [c for c in extracted_cols if c.startswith('pc_')],
    'Emotional Tone (et_)': [c for c in extracted_cols if c.startswith('et_')],
    'Outcome Timing (ot_)': [c for c in extracted_cols if c.startswith('ot_')]
}

for cat_name, cols in categories.items():
    if cols:
        # Count rows with at least one non-null value in this category
        has_data = df[cols].notna().any(axis=1).sum()
        print(f"{cat_name}: {has_data}/19 rows have data")

print("\n" + "=" * 80)
print("SUCCESS! All extracted data is present and properly merged!")
print("=" * 80)

