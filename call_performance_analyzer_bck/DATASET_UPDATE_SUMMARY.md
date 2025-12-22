# Dataset Update Summary

## Date: December 18, 2025

## Overview
The Call Performance Analyzer has been successfully updated to work with the new dataset structure (`mergeed_for_test.csv`).

## Changes Made

### 1. Configuration Updates (`config/settings.py`)

#### Input File
- **Old**: `sales_calls_agent_testing_data.csv`
- **New**: `mergeed_for_test.csv`

#### Column Mappings
Updated `INPUT_COLUMNS` dictionary to reflect new column names:

| Purpose | Old Column Name | New Column Name |
|---------|----------------|-----------------|
| LGS Agent | `username` | `TO_User_M` |
| LGS Call Date | N/A | `TO_Event_O` |
| LGS Duration | N/A | `TO_length_in_sec` |
| LGS Transcription | `transcription` | `TO_Transcription_VICI(0-32000) Words` |
| OMC Agent | `username_omc` | `TO_OMC_User` |
| OMC Call Date | `call_date_omc` | `TO_OMC_Call_Date_O` |
| OMC Duration | `length_in_sec_omc` | `TO_OMC_Duration` |
| OMC Transcription | `transcription_omc` | `TO_OMC_Transcription_VICI` |
| OMC Status | `status_name_omc` | `TO_OMC_Disposiion` |
| Row Identifier | `id` | `TO_Lead_ID` |

### 2. Analysis Nodes Updates (`agents/analysis_nodes.py`)

Updated all references to use the new `INPUT_COLUMNS` mapping:
- `_analyze_single_call()` function
- Error handling sections
- All row data access points

**Key Changes**:
```python
# Old approach (hardcoded column names)
call_id = row.get('id', 'unknown')
lgs_agent = str(row.get('username', 'unknown'))

# New approach (dynamic column mapping)
from config.settings import INPUT_COLUMNS
call_id = row.get(INPUT_COLUMNS['lead_id'], 'unknown')
lgs_agent = str(row.get(INPUT_COLUMNS['lgs_agent'], 'unknown'))
```

### 3. Documentation Updates

- Updated `README.md` with new column names and requirements
- Created this summary document

## Dataset Information

### New Dataset: `mergeed_for_test.csv`
- **Total Rows**: 1,229 calls
- **Format**: CSV with UTF-8 encoding
- **Location**: `input_data/mergeed_for_test.csv`

### Column Details

#### LGS (Lead Generation System) Columns
1. **TO_User_M**: LGS Department User who generates and transfers the lead
2. **TO_Event_O**: Date and precise time of LGS Agent sending/transferring the call
3. **TO_length_in_sec**: LGS Call duration in seconds (time LGS agent talked to client)
4. **TO_Transcription_VICI(0-32000) Words**: Transcription between LGS Agent and Customer (may be in English, Spanish, or other languages)

#### OMC (Outbound Marketing Center) Columns
5. **TO_OMC_User**: OMC Department User who receives the lead from LGS Agent
6. **TO_OMC_Call_Date_O**: Date and precise time of OMC Agent receiving the transferred call
7. **TO_OMC_Duration**: OMC Call duration in seconds (time OMC agent talked to client)
8. **TO_OMC_Transcription_VICI**: Transcription between OMC Agent and Customer (may be in English, Spanish, or other languages)
9. **TO_OMC_Disposiion**: Call outcome/disposition
10. **TO_Lead_ID**: Unique Lead ID (Row identifier)

## Testing

### Verification Steps Completed
1. ✅ Column mappings verified - all required columns exist in new dataset
2. ✅ Single call analysis test - successfully analyzed one call from new dataset
3. ✅ LLM connection test - Gemini 2.5 Flash working correctly
4. ✅ Structured output test - CallInsight schema working as expected
5. ✅ No linter errors in updated files

### Test Results
- **Test Call ID**: 16265388.0
- **LGS Agent**: JUDITACLARIDAD
- **OMC Agent**: JOHNMENARDESCOTE25
- **OMC Duration**: 1639 seconds (27 minutes)
- **Call Category**: Long call (successful)
- **LGS Quality Score**: 8/10
- **Agent Performance Rating**: 9/10
- **Customer Engagement**: High

## System Flow (Unchanged)

The analysis flow remains the same:
1. Load data from CSV
2. Split into batches (40 calls per batch)
3. Analyze each call in parallel using Gemini LLM
4. Accumulate metrics across batches
5. Generate comprehensive report

**Call Duration Threshold**: 120 seconds (2 minutes)
- Calls < 120 seconds = "Short calls" (analyzed for failure patterns)
- Calls >= 120 seconds = "Long calls" (analyzed for success factors)

## Backward Compatibility

The system is **NOT backward compatible** with the old dataset structure. To use the old dataset:
1. Revert `INPUT_FILE` in `config/settings.py`
2. Revert `INPUT_COLUMNS` mapping to old column names

## Next Steps

The system is ready to run with the new dataset:

```bash
# Navigate to the project directory
cd d:\Sales_calls_analysis\ai_agents\call_performance_analyzer

# Run the analysis
python main.py --run

# Or start fresh (ignore checkpoint)
python main.py --run --fresh
```

## Files Modified

1. `config/settings.py` - Updated INPUT_FILE and INPUT_COLUMNS
2. `agents/analysis_nodes.py` - Updated all column references to use INPUT_COLUMNS
3. `README.md` - Updated documentation with new column names
4. `DATASET_UPDATE_SUMMARY.md` - Created this summary document

## Notes

- All other system components remain unchanged (schemas, prompts, graph structure, etc.)
- The `data_handler.py` already uses `INPUT_COLUMNS` dynamically, so no changes were needed
- LangSmith tracing continues to work with project: `Sales_call_analysis_agent`
- Gemini model: `gemini-2.5-flash` (as configured)

---

**Status**: ✅ System successfully updated and tested with new dataset structure

