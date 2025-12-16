import pandas as pd
import sys

def merge_lead_data(source_file, vici_file, output_file, description=""):
    """
    Merge data from Vici file into source file based on matching 
    ZC_Lead_ID and lead_id.
    
    Parameters:
    - source_file: Path to the source CSV file (has ZC_Lead_ID column)
    - vici_file: Path to the Vici CSV file (has lead_id column)
    - output_file: Path to save the merged output CSV file
    - description: Optional description for logging purposes
    """
    
    print(f"\n{'='*60}")
    if description:
        print(f"Processing: {description}")
    print(f"{'='*60}")
    print(f"Reading CSV files...")
    
    try:
        # Read the source file
        df_source = pd.read_csv(source_file, low_memory=False)
        print(f"Source file loaded: {len(df_source)} rows")
        
        # Read the Vici file
        df_vici = pd.read_csv(vici_file, low_memory=False)
        print(f"Vici file loaded: {len(df_vici)} rows")
        
        # Check if required columns exist
        if 'ZC_Lead_ID' not in df_source.columns:
            print(f"Error: 'ZC_Lead_ID' column not found in source file: {source_file}")
            return False
        
        if 'lead_id' not in df_vici.columns:
            print(f"Error: 'lead_id' column not found in Vici file: {vici_file}")
            return False
        
        # Convert ZC_Lead_ID and lead_id to string for consistent matching
        df_source['ZC_Lead_ID'] = df_source['ZC_Lead_ID'].astype(str)
        df_vici['lead_id'] = df_vici['lead_id'].astype(str)
        
        # Create a dictionary mapping lead_id to row data from Vici file
        # Get all columns from Vici file except lead_id (to avoid duplicate)
        vici_columns = [col for col in df_vici.columns if col != 'lead_id']
        
        # Create a mapping dictionary
        vici_dict = {}
        for idx, row in df_vici.iterrows():
            lead_id = str(row['lead_id'])
            if lead_id not in vici_dict:
                vici_dict[lead_id] = {}
                for col in vici_columns:
                    vici_dict[lead_id][col] = row[col]
        
        print(f"Created mapping for {len(vici_dict)} unique lead_ids")
        
        # Add columns from Vici file to source dataframe
        for col in vici_columns:
            if col not in df_source.columns:
                df_source[col] = None
        
        # Merge the data
        matched_count = 0
        for idx, row in df_source.iterrows():
            zc_lead_id = str(row['ZC_Lead_ID'])
            
            if zc_lead_id in vici_dict:
                # Update the row with data from Vici file
                for col in vici_columns:
                    df_source.at[idx, col] = vici_dict[zc_lead_id][col]
                matched_count += 1
        
        print(f"Matched {matched_count} rows out of {len(df_source)} total rows")
        
        # Save the merged dataframe
        df_source.to_csv(output_file, index=False)
        print(f"\nMerged data saved to: {output_file}")
        print(f"Total columns in output: {len(df_source.columns)}")
        print(f"Columns added from Vici file: {', '.join(vici_columns)}")
        
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
    Main function to process both file pairs:
    1. Less Then 2 Min Non Sales Human Calls.csv + Vici Sales Cluster - less than 2 min.csv
    2. Greater Then 2 Min Non Sales Human Calls.csv + Vici Sales Cluster - Greater than 2 min.csv
    """
    
    print("="*60)
    print("Lead Data Merger Script")
    print("="*60)
    
    # Process first pair: Less than 2 min files
    success1 = merge_lead_data(
        source_file="Less Then 2 Min Non Sales Human Calls.csv",
        vici_file="Vici Sales Cluster - less than 2 min.csv",
        output_file="Less Then 2 Min Non Sales Human Calls_merged.csv",
        description="Less Than 2 Min Files"
    )
    
    # Process second pair: Greater than 2 min files
    success2 = merge_lead_data(
        source_file="Greater Then 2 Min Non Sales Human Calls.csv",
        vici_file="Vici Sales Cluster - Greater than 2 min.csv",
        output_file="Greater Then 2 Min Non Sales Human Calls_merged.csv",
        description="Greater Than 2 Min Files"
    )
    
    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    if success1:
        print("[SUCCESS] Less Than 2 Min files processed successfully")
    else:
        print("[FAILED] Less Than 2 Min files processing failed")
    
    if success2:
        print("[SUCCESS] Greater Than 2 Min files processed successfully")
    else:
        print("[FAILED] Greater Than 2 Min files processing failed")
    
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()

