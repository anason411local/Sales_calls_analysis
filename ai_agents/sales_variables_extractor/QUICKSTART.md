# Sales Variables Extractor - Quick Start Guide

Get up and running in 5 minutes!

## Prerequisites

- Python 3.9+
- Conda environment: `sales_calls_ai_agent`
- Gemini API key
- Input CSV file: `input_data/mergeed_for_test.csv`

## Step 1: Activate Environment

```bash
conda activate sales_calls_ai_agent
```

## Step 2: Navigate to Agent Directory

```bash
cd D:\Sales_calls_analysis\ai_agents\sales_variables_extractor
```

## Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 4: Set Up Environment Variables

Create a `.env` file in the project root (`D:\Sales_calls_analysis\`) with:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

## Step 5: Test Connection

```bash
python main.py --test-connection
```

Expected output:
```
Model Configuration:
  Model: gemini-2.0-flash-exp
  API Key Configured: True
  API Key Prefix: AIzaSy...

[SUCCESS] Gemini API connection test passed!
```

## Step 6: Run Extraction

```bash
python main.py --run
```

This will:
- Load input data from `input_data/mergeed_for_test.csv`
- Extract LGS and OMC variables for each row
- Save results to `output_data/sales_variables_extracted.csv`
- Create checkpoints for resume capability
- Generate detailed logs in `logs/` directory

## Understanding the Output

The output CSV will contain:

### Metadata Columns
- `lead_id`: Unique identifier
- `row_number`: Row number in input
- `customer_name`: Customer name
- `service`: Service type
- `customer_address`: Customer location

### LGS Variables (15+ columns)
- `timezone`: Customer timezone
- `season_status`: High/Low season
- `lgs_sentiment_style`: Agent style classification
- `lgs_agent_gender`: Male/Female/unknown
- `is_decision_maker`: Yes/No/unknown
- `ready_for_customers`: Yes/No/unknown
- `customer_sentiment_lgs`: Emotional state
- `customer_language`: English/Spanish
- `technical_quality_score`: 0-5 score
- And more...

### OMC Variables (30+ columns)
- `customer_talk_percentage`: % of conversation
- `total_discovery_questions`: Count
- `total_buying_signals`: Count
- `total_objections`: Count
- `time_to_reason_seconds`: Opening speed
- `call_result_tag`: Outcome classification
- And more...

### Status Columns
- `lgs_extraction_success`: True/False
- `lgs_error_message`: Error details if failed
- `omc_extraction_success`: True/False
- `omc_error_message`: Error details if failed
- `extraction_complete`: True/False

## Monitoring Progress

### View Real-Time Logs
```bash
# In another terminal
tail -f logs/variables_extraction_*.log
```

### Check Checkpoint Status
```bash
cat checkpoints/variables_extraction_checkpoint.json
```

## Resume from Checkpoint

If the process is interrupted, simply run again:
```bash
python main.py --run
```

It will automatically resume from the last checkpoint.

## Start Fresh (Ignore Checkpoint)

```bash
python main.py --run --fresh
```

## Common Issues and Solutions

### Issue: "GEMINI_API_KEY not found"
**Solution**: Ensure `.env` file exists in project root with valid API key

### Issue: "Input file not found"
**Solution**: Verify `input_data/mergeed_for_test.csv` exists

### Issue: "JSON parsing error"
**Solution**: Check logs for details. The agent will retry automatically (up to 3 times)

### Issue: Slow processing
**Solution**: Normal! Each row requires 2 LLM calls (LGS + OMC). Expect ~5-10 seconds per row.

## Performance Tips

1. **Batch Processing**: The agent processes 5 rows before checkpointing
2. **Rate Limiting**: 1 second delay between API calls (configurable in `config/settings.py`)
3. **Parallel Processing**: For faster processing, you can run multiple instances on different subsets of data

## Customization

### Change Model
Edit `config/settings.py`:
```python
GEMINI_MODEL = "gemini-2.0-flash-exp"  # or another model
```

### Adjust Retry Logic
Edit `config/settings.py`:
```python
MAX_RETRIES = 3  # Change to desired number
```

### Modify Batch Size
Edit `config/settings.py`:
```python
BATCH_SIZE = 5  # Rows per checkpoint
```

## Next Steps

1. **Review Results**: Open `output_data/sales_variables_extracted.csv` in Excel/Pandas
2. **Analyze Logs**: Check `logs/` for detailed extraction information
3. **Merge with Original**: Use the data handler to merge results with input data
4. **Customize Prompts**: Edit prompt files in `prompts/` directory for better extraction

## Example: Viewing Results in Python

```python
import pandas as pd

# Load results
df = pd.read_csv('output_data/sales_variables_extracted.csv')

# View summary
print(f"Total rows: {len(df)}")
print(f"LGS success: {df['lgs_extraction_success'].sum()}")
print(f"OMC success: {df['omc_extraction_success'].sum()}")

# View specific variables
print(df[['lead_id', 'timezone', 'season_status', 'call_result_tag']].head())
```

## Getting Help

- **Check Logs**: `logs/variables_extraction_errors_*.log` for errors
- **Review README**: `README.md` for detailed documentation
- **Inspect Code**: All code is well-documented with docstrings

## Summary

```bash
# Complete workflow in 3 commands:
conda activate sales_calls_ai_agent
cd ai_agents/sales_variables_extractor
python main.py --test-connection && python main.py --run
```

That's it! Your sales variables will be extracted and saved to the output directory.

