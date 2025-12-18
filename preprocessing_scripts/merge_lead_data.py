import pandas as pd
import sys
import os

def merge_lead_data(omc_file, lead_quality_file, output_file):
    """
    Merge data from Lead Quality file into OMC Calls file based on matching 
    TO_Lead_ID and LQ_Lead_Source.
    
    Parameters:
    - omc_file: Path to the OMC Calls CSV file (has TO_Lead_ID column)
    - lead_quality_file: Path to the Lead Quality CSV file (has LQ_Lead_Source column)
    - output_file: Path to save the merged output CSV file
    """
    
    print(f"\n{'='*60}")
    print(f"Merging OMC Calls with Lead Quality Data")
    print(f"{'='*60}")
    print(f"Reading CSV files...")
    
    try:
        # Read the OMC Calls file
        df_omc = pd.read_csv(omc_file, low_memory=False)
        print(f"OMC Calls file loaded: {len(df_omc)} rows")
        print(f"OMC Calls columns: {len(df_omc.columns)}")
        
        # Read the Lead Quality file
        df_lead_quality = pd.read_csv(lead_quality_file, low_memory=False)
        print(f"Lead Quality file loaded: {len(df_lead_quality)} rows")
        print(f"Lead Quality columns: {len(df_lead_quality.columns)}")
        
        # Check if required columns exist
        if 'TO_Lead_ID' not in df_omc.columns:
            print(f"Error: 'TO_Lead_ID' column not found in OMC Calls file")
            return False
        
        if 'LQ_Lead_Source' not in df_lead_quality.columns:
            print(f"Error: 'LQ_Lead_Source' column not found in Lead Quality file")
            return False
        
        # Convert TO_Lead_ID and LQ_Lead_Source to string for consistent matching
        df_omc['TO_Lead_ID'] = df_omc['TO_Lead_ID'].astype(str)
        df_lead_quality['LQ_Lead_Source'] = df_lead_quality['LQ_Lead_Source'].astype(str)
        
        # Get all columns from Lead Quality file except LQ_Lead_Source (to avoid duplicate)
        lead_quality_columns = [col for col in df_lead_quality.columns if col != 'LQ_Lead_Source']
        
        # Create a mapping dictionary from Lead Quality data
        lead_quality_dict = {}
        for idx, row in df_lead_quality.iterrows():
            lead_source = str(row['LQ_Lead_Source'])
            if lead_source not in lead_quality_dict:
                lead_quality_dict[lead_source] = {}
                for col in lead_quality_columns:
                    lead_quality_dict[lead_source][col] = row[col]
        
        print(f"Created mapping for {len(lead_quality_dict)} unique LQ_Lead_Source values")
        
        # Add columns from Lead Quality file to OMC dataframe
        for col in lead_quality_columns:
            if col not in df_omc.columns:
                df_omc[col] = None
        
        # Merge the data
        matched_count = 0
        for idx, row in df_omc.iterrows():
            to_lead_id = str(row['TO_Lead_ID'])
            
            if to_lead_id in lead_quality_dict:
                # Update the row with data from Lead Quality file
                for col in lead_quality_columns:
                    df_omc.at[idx, col] = lead_quality_dict[to_lead_id][col]
                matched_count += 1
        
        print(f"Matched {matched_count} rows out of {len(df_omc)} total rows")
        print(f"Match rate: {(matched_count/len(df_omc)*100):.2f}%")
        
        # Clean up date/time columns by removing "TT" suffix
        print(f"\nCleaning date/time columns...")
        date_columns = ['TO_Event_O', 'TO_OMC_Call_Date_O']
        for col in date_columns:
            if col in df_omc.columns:
                # Remove "TT" and extra spaces at the end of date/time strings
                df_omc[col] = df_omc[col].astype(str).str.replace(r'\s+TT\s*$', '', regex=True)
                df_omc[col] = df_omc[col].str.strip()
                print(f"  - Cleaned column: {col}")
        
        # Save the merged dataframe
        df_omc.to_csv(output_file, index=False)
        print(f"\nMerged data saved to: {output_file}")
        print(f"Total columns in output: {len(df_omc.columns)}")
        print(f"Columns added from Lead Quality file: {', '.join(lead_quality_columns)}")
        
        return True
        
    except FileNotFoundError as e:
        print(f"Error: File not found - {e}")
        return False
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """
    Main function to merge OMC Calls with Lead Quality data
    """
    
    print("="*60)
    print("Lead Data Merger Script")
    print("="*60)
    
    # Get the script directory and project root
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    
    # Define file paths relative to project root
    omc_file = os.path.join(project_root, "input_data", "OMC Calls - December 18, 2025.csv")
    lead_quality_file = os.path.join(project_root, "input_data", "Lead Quality - December 18, 2025.csv")
    output_file = os.path.join(project_root, "input_data", "Merged_OMC_LeadQuality_December_18_2025.csv")
    
    # Merge the files
    success = merge_lead_data(omc_file, lead_quality_file, output_file)
    
    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    if success:
        print("[SUCCESS] Files merged successfully")
        print(f"Output file: {output_file}")
    else:
        print("[FAILED] Merge operation failed")
    
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()

