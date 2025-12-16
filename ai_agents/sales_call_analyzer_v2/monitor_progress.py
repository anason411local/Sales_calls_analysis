"""Monitor the extraction progress"""
import pandas as pd
from pathlib import Path
import time

output_file = Path("../../output_data/extracted_sales_data.csv")

print("Monitoring extraction progress...")
print("=" * 80)

while True:
    if output_file.exists():
        try:
            df = pd.read_csv(output_file)
            
            # Count rows with extracted data
            if 'extraction_success' in df.columns:
                success_count = (df['extraction_success'] == True).sum()
            else:
                # Check a sample extracted column
                extracted_cols = [col for col in df.columns if col.startswith('ce_')]
                if extracted_cols:
                    success_count = df[extracted_cols[0]].notna().sum()
                else:
                    success_count = 0
            
            print(f"\rTotal rows: {len(df)} | Rows with extracted data: {success_count}", end="", flush=True)
            
            if success_count >= 17:  # Expected successful extractions
                print("\n\nExtraction complete!")
                break
                
        except Exception as e:
            print(f"\rWaiting for file... ({str(e)[:50]})", end="", flush=True)
    else:
        print("\rWaiting for output file to be created...", end="", flush=True)
    
    time.sleep(2)

print("\n" + "=" * 80)
print("Final verification:")
df = pd.read_csv(output_file)
print(f"Total rows: {len(df)}")
print(f"Total columns: {len(df.columns)}")

if 'extraction_success' in df.columns:
    print(f"Rows with extraction_success=True: {(df['extraction_success']==True).sum()}")

# Sample some extracted data
print(f"\nSample extracted data (first row with data):")
extracted_cols = [col for col in df.columns if col.startswith(('ce_', 'co_', 'oh_'))]
for col in extracted_cols[:5]:
    val = df[col].dropna().iloc[0] if df[col].notna().any() else "NO DATA"
    print(f"  {col}: {val}")

