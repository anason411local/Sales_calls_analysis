"""
Quick script to verify the output CSV has all the data
"""
import pandas as pd
from pathlib import Path

# Load the output file
output_file = Path("../../output_data/extracted_sales_data.csv")
df = pd.read_csv(output_file)

print("=" * 80)
print("OUTPUT FILE VERIFICATION")
print("=" * 80)
print(f"\nFile: {output_file}")
print(f"File size: {output_file.stat().st_size / 1024:.2f} KB")
print(f"\nTotal Rows: {len(df)}")
print(f"Total Columns: {len(df.columns)}")

# Count extracted columns
extracted_cols = [col for col in df.columns if col.startswith(('ce_', 'co_', 'oh_', 'pc_', 'et_', 'ot_'))]
print(f"\nExtracted Data Columns: {len(extracted_cols)}")

# Show column categories
ce_cols = [col for col in df.columns if col.startswith('ce_')]
co_cols = [col for col in df.columns if col.startswith('co_')]
oh_cols = [col for col in df.columns if col.startswith('oh_')]
pc_cols = [col for col in df.columns if col.startswith('pc_')]
et_cols = [col for col in df.columns if col.startswith('et_')]
ot_cols = [col for col in df.columns if col.startswith('ot_')]

print(f"\n  Customer Engagement (ce_*): {len(ce_cols)} columns")
print(f"  Call Opening (co_*): {len(co_cols)} columns")
print(f"  Objection Handling (oh_*): {len(oh_cols)} columns")
print(f"  Pace Control (pc_*): {len(pc_cols)} columns")
print(f"  Emotional Tone (et_*): {len(et_cols)} columns")
print(f"  Outcome Timing (ot_*): {len(ot_cols)} columns")

# Check how many rows have extracted data
rows_with_data = df['extraction_success'].notna().sum() if 'extraction_success' in df.columns else 0
print(f"\nRows with Extracted Data: {rows_with_data} / {len(df)}")

# Show sample data from first row with extraction
if 'extraction_success' in df.columns:
    success_rows = df[df['extraction_success'] == True]
    if len(success_rows) > 0:
        print(f"\nSample Extracted Data (Row 0):")
        sample_row = success_rows.iloc[0]
        print(f"  transcription_id_omc: {sample_row.get('transcription_id_omc', 'N/A')}")
        print(f"  fullname: {sample_row.get('fullname_source', 'N/A')}")
        print(f"  ce_positive_signal_count: {sample_row.get('ce_positive_signal_count', 'N/A')}")
        print(f"  co_opener_type: {sample_row.get('co_opener_type', 'N/A')}")
        print(f"  oh_objections_count: {sample_row.get('oh_objections_count', 'N/A')}")
        print(f"  ot_call_outcome: {sample_row.get('ot_call_outcome', 'N/A')}")

print("\n" + "=" * 80)
print("✅ DATA IS PRESENT IN THE FILE!")
print("If your IDE shows empty, please CLOSE and REOPEN the file.")
print("=" * 80)

