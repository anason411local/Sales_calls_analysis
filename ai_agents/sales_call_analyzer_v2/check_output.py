"""Check the actual output CSV content"""
import pandas as pd
from pathlib import Path

output_file = Path("../../output_data/extracted_sales_data.csv")
df = pd.read_csv(output_file)

print("=" * 80)
print("OUTPUT CSV ANALYSIS")
print("=" * 80)

print(f"\nTotal rows in CSV: {len(df)}")
print(f"Total columns: {len(df.columns)}")

# Check transcription data
print(f"\nRows with transcription_omc (source data): {df['transcription_omc'].notna().sum()}")

# Check extracted data
if 'extraction_success' in df.columns:
    print(f"Rows with extraction_success=True: {(df['extraction_success']==True).sum()}")
    print(f"Rows with extraction_success=False/NaN: {len(df) - (df['extraction_success']==True).sum()}")

# Check specific extracted columns
extracted_cols = [col for col in df.columns if col.startswith('ce_')]
if extracted_cols:
    sample_col = extracted_cols[0]
    print(f"\nRows with data in '{sample_col}': {df[sample_col].notna().sum()}")

# Show transcription_id_omc for all rows
print(f"\nAll transcription_id_omc values:")
for idx, tid in enumerate(df['transcription_id_omc'].tolist()):
    has_extraction = df.loc[idx, 'extraction_success'] if 'extraction_success' in df.columns else None
    print(f"  Row {idx}: {tid} - Extracted: {has_extraction}")

print("\n" + "=" * 80)

