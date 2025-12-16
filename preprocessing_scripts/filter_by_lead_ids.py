import pandas as pd
import sys

def filter_by_lead_ids():
    """
    Filter rows from 'Vici Sales Cluster - less than 2 min.csv' and 
    'Vici Sales Cluster - Greater than 2 min.csv' based on lead_ids 
    from 'export_lgs_omc_2025_12_16.csv' and merge them into the export file.
    """
    
    print("="*60)
    print("Lead ID Filter Script")
    print("="*60)
    
    # File paths
    export_file = "export_lgs_omc_2025_12_16.csv"
    less_than_2min_file = "Vici Sales Cluster - less than 2 min.csv"
    greater_than_2min_file = "Vici Sales Cluster - Greater than 2 min.csv"
    
    try:
        # Step 1: Read the export file and extract unique lead_ids
        print(f"\n[Step 1] Reading export file: {export_file}")
        df_export_original = pd.read_csv(export_file, low_memory=False)
        df_export = df_export_original.copy()  # Work on a copy
        print(f"Export file loaded: {len(df_export)} rows")
        
        # Check if file seems to have been modified (has more rows than expected)
        # Original should be around 1842 rows
        if len(df_export) > 2000:
            print(f"NOTE: Export file has {len(df_export)} rows. If you want to start fresh,")
            print(f"     restore from backup: export_lgs_omc_2025_12_16_backup.csv")
        
        # Check if lead_id column exists
        if 'lead_id' not in df_export.columns:
            print("Error: 'lead_id' column not found in export file")
            return False
        
        # Extract unique lead_ids and convert to string (handle float to int conversion)
        # First convert to int to remove decimal points, then to string
        lead_ids = df_export['lead_id'].dropna().astype(float).astype(int).astype(str).unique()
        print(f"Found {len(lead_ids)} unique lead_ids in export file")
        
        # Convert to set for faster lookup
        lead_id_set = set(lead_ids)
        print(f"Sample lead_ids: {list(lead_ids[:5])}")
        
        # Step 2: Filter Less Than 2 Min file (Vici Sales Cluster)
        print(f"\n[Step 2] Filtering: {less_than_2min_file}")
        df_less_than = pd.read_csv(less_than_2min_file, low_memory=False)
        print(f"Source file loaded: {len(df_less_than)} rows")
        
        if 'lead_id' not in df_less_than.columns:
            print("Error: 'lead_id' column not found in Less Than 2 Min file")
            return False
        
        # Convert lead_id to string for matching (handle float to int conversion)
        df_less_than['lead_id'] = pd.to_numeric(df_less_than['lead_id'], errors='coerce')
        df_less_than = df_less_than.dropna(subset=['lead_id'])
        df_less_than['lead_id'] = df_less_than['lead_id'].astype(int).astype(str)
        
        # Filter rows where lead_id is in the lead_id_set
        df_less_than_filtered = df_less_than[df_less_than['lead_id'].isin(lead_id_set)].copy()
        print(f"Filtered rows: {len(df_less_than_filtered)} out of {len(df_less_than)}")
        
        # Step 3: Filter Greater Than 2 Min file (Vici Sales Cluster)
        print(f"\n[Step 3] Filtering: {greater_than_2min_file}")
        df_greater_than = pd.read_csv(greater_than_2min_file, low_memory=False)
        print(f"Source file loaded: {len(df_greater_than)} rows")
        
        if 'lead_id' not in df_greater_than.columns:
            print("Error: 'lead_id' column not found in Greater Than 2 Min file")
            return False
        
        # Convert lead_id to string for matching (handle float to int conversion)
        df_greater_than['lead_id'] = pd.to_numeric(df_greater_than['lead_id'], errors='coerce')
        df_greater_than = df_greater_than.dropna(subset=['lead_id'])
        df_greater_than['lead_id'] = df_greater_than['lead_id'].astype(int).astype(str)
        
        # Filter rows where lead_id is in the lead_id_set
        df_greater_than_filtered = df_greater_than[df_greater_than['lead_id'].isin(lead_id_set)].copy()
        print(f"Filtered rows: {len(df_greater_than_filtered)} out of {len(df_greater_than)}")
        
        # Step 4: Combine filtered data, remove duplicates, and merge into export file by lead_id
        print(f"\n[Step 4] Combining filtered data, removing duplicates, and merging into export file by lead_id")
        
        # Store original row count
        original_row_count = len(df_export)
        print(f"Original export file row count: {original_row_count}")
        
        # Combine both filtered dataframes
        df_combined = pd.concat([df_less_than_filtered, df_greater_than_filtered], ignore_index=True)
        print(f"Combined filtered rows: {len(df_combined)}")
        
        # lead_id is already in the correct format (string), convert to int for processing
        df_combined['lead_id'] = pd.to_numeric(df_combined['lead_id'], errors='coerce')
        df_combined = df_combined.dropna(subset=['lead_id'])
        df_combined['lead_id'] = df_combined['lead_id'].astype(int)
        
        # Remove duplicates - keep only the first row for each lead_id
        duplicates_before = len(df_combined)
        df_combined = df_combined.drop_duplicates(subset=['lead_id'], keep='first')
        duplicates_removed = duplicates_before - len(df_combined)
        print(f"Removed {duplicates_removed} duplicate rows (kept first occurrence for each lead_id)")
        print(f"Unique rows after deduplication: {len(df_combined)}")
        
        # Convert lead_id to int for matching (both dataframes)
        df_combined['lead_id'] = df_combined['lead_id'].astype(int)
        
        # Convert export lead_id to int for matching
        df_export['lead_id'] = pd.to_numeric(df_export['lead_id'], errors='coerce').astype('Int64')
        
        # Get columns from source files that don't exist in export (to add them)
        source_columns = [col for col in df_combined.columns if col != 'lead_id']
        new_columns = [col for col in source_columns if col not in df_export.columns]
        
        if new_columns:
            print(f"Adding {len(new_columns)} new columns from source files: {', '.join(new_columns[:5])}...")
        else:
            print("All columns from source files already exist in export file")
            # If columns exist, we'll update them
            existing_columns = [col for col in source_columns if col in df_export.columns]
            if existing_columns:
                print(f"Will update existing columns: {', '.join(existing_columns[:5])}...")
                new_columns = existing_columns
        
        # Create a dictionary mapping lead_id to row data for faster lookup
        # This ensures one-to-one mapping
        lead_id_to_data = {}
        for idx, row in df_combined.iterrows():
            lid = int(row['lead_id'])
            if lid not in lead_id_to_data:
                lead_id_to_data[lid] = {}
                for col in source_columns:
                    lead_id_to_data[lid][col] = row[col]
        
        print(f"Created mapping for {len(lead_id_to_data)} unique lead_ids")
        
        # Initialize new columns in export dataframe with None (use object dtype to avoid dtype conflicts)
        for col in source_columns:
            if col not in df_export.columns:
                df_export[col] = None
            else:
                # Convert to object dtype to allow mixed types
                if df_export[col].dtype != 'object':
                    df_export[col] = df_export[col].astype('object')
        
        # Merge data by updating rows where lead_id matches
        matched_count = 0
        for idx, row in df_export.iterrows():
            lead_id_val = row['lead_id']
            if pd.notna(lead_id_val) and int(lead_id_val) in lead_id_to_data:
                # Update this row with data from source files
                for col in source_columns:
                    value = lead_id_to_data[int(lead_id_val)][col]
                    # Convert value to appropriate type if needed
                    if pd.isna(value):
                        df_export.at[idx, col] = None
                    else:
                        df_export.at[idx, col] = value
                matched_count += 1
        
        df_export_updated = df_export
        print(f"Matched and merged data for {matched_count} rows")
        
        # Verify row count hasn't increased
        print(f"Export file updated: {len(df_export_updated)} rows (original: {original_row_count})")
        
        if len(df_export_updated) != original_row_count:
            print(f"ERROR: Row count changed! Expected {original_row_count}, got {len(df_export_updated)}")
            return False
        else:
            print(f"SUCCESS: Row count maintained at {len(df_export_updated)} rows")
        
        # Create backup first
        backup_file = export_file.replace('.csv', '_backup.csv')
        try:
            df_export_original.to_csv(backup_file, index=False)
            print(f"Backup created: {backup_file}")
        except Exception as e:
            print(f"Warning: Could not create backup: {e}")
        
        # Save updated export file
        try:
            df_export_updated.to_csv(export_file, index=False)
            print(f"Updated export file saved to: {export_file}")
        except PermissionError:
            print(f"\nERROR: Cannot save to {export_file}")
            print("Please close the file if it's open in Excel or another program, then run the script again.")
            if 'backup_file' in locals():
                print(f"A backup has been saved to: {backup_file}")
            return False
        
        # Summary
        print(f"\n{'='*60}")
        print("SUMMARY")
        print(f"{'='*60}")
        print(f"Total unique lead_ids from export file: {len(lead_ids)}")
        print(f"Less Than 2 Min - Matched rows: {len(df_less_than_filtered)}")
        print(f"Greater Than 2 Min - Matched rows: {len(df_greater_than_filtered)}")
        print(f"Total filtered rows from source files (before dedup): {duplicates_before}")
        print(f"Unique rows after deduplication: {len(df_combined)}")
        print(f"Original export file rows: {original_row_count}")
        print(f"Updated export file rows: {len(df_export_updated)}")
        print(f"Rows with merged data: {matched_count}")
        print(f"\nOutput file: {export_file}")
        print(f"{'='*60}\n")
        
        return True
        
    except FileNotFoundError as e:
        print(f"Error: File not found - {e}")
        return False
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = filter_by_lead_ids()
    if success:
        print("[SUCCESS] Filtering completed successfully!")
    else:
        print("[FAILED] Filtering encountered errors!")

