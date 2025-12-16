# Sales Call Analyzer V2 - Updates

## Latest Updates (December 17, 2025)

### ✅ Issue 1: System Instructions and Prompts Verification

**Status**: CONFIRMED ✓

The system is using the **complete, untruncated** content from both files:
- `system Instrutions.txt` (486 lines)
- `sales_data_extaction_prompt.txt` (567 lines)

**How it works**:
1. Files are loaded using `load_prompt_file()` function in `prompts/prompt_templates.py`
2. Full content is embedded in the `ChatPromptTemplate`
3. No truncation or removal of any content
4. Both system instructions and extraction prompt are passed to Gemini in their entirety

**Verification**:
```python
# In prompts/prompt_templates.py
SYSTEM_INSTRUCTIONS = load_prompt_file(SYSTEM_INSTRUCTIONS_FILE)  # Full 486 lines
EXTRACTION_PROMPT = load_prompt_file(EXTRACTION_PROMPT_FILE)      # Full 567 lines
```

### ✅ Issue 2: Merging Output with Source Dataset

**Status**: IMPLEMENTED ✓

The system now:
1. **Includes `transcription_id_omc`** as the merge key
2. **Merges extracted data with ALL source columns**
3. **Outputs a complete dataset** with both original and extracted columns

**Changes Made**:

#### 1. Added `transcription_id` to Schema
```python
class SalesCallExtraction(BaseModel):
    transcription_id: str = Field(default="", description="Transcription ID for merging")
    # ... rest of fields
```

#### 2. Updated Input Columns Configuration
```python
INPUT_COLUMNS = {
    "id": "id",
    "transcription_id": "transcription_id_omc",  # For merging
    "call_date": "call_date_omc",
    "length_in_sec": "length_in_sec_omc",
    "transcription": "transcription_omc",
    "fullname": "fullname_omc"
}
```

#### 3. Enhanced Data Handler with Merge Capability
```python
def save_results(self, results, append=False, merge_with_source=True):
    # Flatten extracted results
    extracted_df = pd.DataFrame(flattened_results)
    
    if merge_with_source:
        # Load source data
        source_df = pd.read_csv(self.input_file)
        
        # Merge on transcription_id_omc
        merged_df = source_df.merge(
            extracted_df,
            on='transcription_id_omc',
            how='left',
            suffixes=('_source', '_extracted')
        )
        
        df_to_save = merged_df
```

#### 4. Output Structure

**Before** (Extracted data only):
```
transcription_id_omc, row_id, call_date, fullname, length_in_sec, ce_*, co_*, oh_*, ...
```

**After** (Merged with source):
```
[ALL SOURCE COLUMNS] + [ALL EXTRACTED COLUMNS]
```

This includes:
- Original columns: `id`, `call_date`, `transcription_id`, `company_name`, `username`, `fullname`, `user_group`, `disposition_code`, `status_name`, `lead_id`, `recording_id`, `length_in_sec`, `campaign_id`, `campaign_name`, `phone_number`, `call_type`, `location`, `transcription`, etc.
- Extracted columns: `ce_*`, `co_*`, `oh_*`, `pc_*`, `et_*`, `ot_*` (62+ data points)

**Total columns**: ~90+ columns (source + extracted)

### 🎯 Benefits

1. **Complete Dataset**: All original data preserved
2. **Easy Analysis**: Can correlate extracted insights with original metadata
3. **Flexible**: Can filter by campaign, user, disposition, etc.
4. **ML-Ready**: Wide format perfect for machine learning
5. **Traceable**: `transcription_id_omc` links everything together

### 📊 Output Format

The final CSV will have structure like:

```
| id | transcription_id_omc | call_date | company_name | ... [source cols] ... | ce_positive_signal_count | ce_positive_signal_verbiage | ... [extracted cols] ... |
|----|---------------------|-----------|--------------|---------------------|------------------------|---------------------------|--------------------------|
| 1  | abc123             | 16/10/25  | Company A    | ...                 | 2                      | "Great, sounds good"      | ...                      |
```

### 🔍 Merge Logic

- **Left join** on `transcription_id_omc`
- **Preserves all source rows** (even if extraction failed)
- **Adds extracted columns** where available
- **Handles duplicates** by keeping latest extraction

### ⚙️ Configuration

To disable merging (extracted data only):
```python
# In batch_processor.py
self.data_handler.save_results(results, append=True, merge_with_source=False)
```

### 🚀 Running the System

```bash
# Clean start (recommended after updates)
cd d:\Sales_calls_analysis\ai_agents\sales_call_analyzer_v2
python main.py --run
```

The system will:
1. Load source data from `input_data/sales_calls_agent_testing_data.csv`
2. Extract data for each row
3. Merge extracted data with source
4. Save complete dataset to `output_data/extracted_sales_data.csv`

### 📝 Notes

- **Checkpoint system** still works - can resume interrupted processing
- **Retry logic** still active for failed extractions
- **Logging** captures all merge operations
- **LangSmith** tracking continues to work

### ✨ Summary

Both issues resolved:
1. ✅ System instructions and prompts are used **completely** (no truncation)
2. ✅ Output is **merged with source data** using `transcription_id_omc`

The system now provides a **complete, analysis-ready dataset** with all original columns plus 62+ extracted data points per call!

