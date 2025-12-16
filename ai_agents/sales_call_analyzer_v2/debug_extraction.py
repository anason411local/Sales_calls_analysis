"""Debug what's actually being extracted"""
import pandas as pd
from pathlib import Path

# Check source data
input_file = Path("../../input_data/sales_calls_agent_testing_data.csv")
source_df = pd.read_csv(input_file)

print("=" * 80)
print("SOURCE DATA CHECK")
print("=" * 80)
print(f"\nTotal rows: {len(source_df)}")
print(f"\nFirst 5 transcription_id_omc values from SOURCE:")
for idx in range(min(5, len(source_df))):
    tid = source_df.loc[idx, 'transcription_id_omc']
    print(f"  Row {idx}: {tid}")

# Check output data
output_file = Path("../../output_data/extracted_sales_data.csv")
output_df = pd.read_csv(output_file)

print(f"\n\nFirst 5 transcription_id_omc values from OUTPUT:")
for idx in range(min(5, len(output_df))):
    tid = output_df.loc[idx, 'transcription_id_omc']
    print(f"  Row {idx}: {tid}")

# Check if they match
print(f"\n\nDo the transcription_id_omc values match?")
for idx in range(min(5, len(source_df))):
    source_tid = source_df.loc[idx, 'transcription_id_omc']
    output_tid = output_df.loc[idx, 'transcription_id_omc']
    match = "✓" if source_tid == output_tid else "✗"
    print(f"  Row {idx}: {match} (Source: {source_tid}, Output: {output_tid})")

print("\n" + "=" * 80)

