# Sales Variables Extractor - Deployment Checklist

## Pre-Deployment Checklist

### ✅ Environment Setup

- [ ] Conda environment `sales_calls_ai_agent` is activated
- [ ] Python 3.9+ is installed
- [ ] All dependencies are installed (`pip install -r requirements.txt`)

### ✅ Configuration

- [ ] `.env` file exists in project root (`D:\Sales_calls_analysis\`)
- [ ] `GEMINI_API_KEY` is set in `.env`
- [ ] API key is valid and has sufficient quota
- [ ] (Optional) `LANGSMITH_API_KEY` is set for tracing

### ✅ Input Data

- [ ] `input_data/mergeed_for_test.csv` exists
- [ ] CSV has required columns:
  - `TO_Lead_ID`
  - `TO_User_M` (LGS user)
  - `TO_Transcription_VICI(0-32000) Words` (LGS transcription)
  - `TO_OMC_User` (OMC user)
  - `TO_OMC_Transcription_VICI` (OMC transcription)
  - `LQ_Company_Address` (Customer address)
  - `LQ_Service` (Service type)
- [ ] CSV is properly encoded (UTF-8)
- [ ] No completely empty transcription columns

### ✅ Reference Data

- [ ] `input_data/seasonality.csv` exists (optional but recommended)
- [ ] Seasonality CSV has service categories and monthly data

### ✅ Directory Structure

- [ ] `output_data/` directory exists
- [ ] `checkpoints/` directory exists
- [ ] `logs/` directory exists
- [ ] All prompt files are in `prompts/` directory

## Verification Steps

### Step 1: Run Setup Test

```bash
cd ai_agents/sales_variables_extractor
python test_setup.py
```

**Expected Output**: All tests should pass
- ✓ Imports
- ✓ Configuration
- ✓ Schemas
- ✓ Data Handler
- ✓ Gemini Client
- ✓ LangGraph Workflow

### Step 2: Test API Connection

```bash
python main.py --test-connection
```

**Expected Output**:
```
Model Configuration:
  Model: gemini-2.0-flash-exp
  API Key Configured: True
  API Key Prefix: AIzaSy...

[SUCCESS] Gemini API connection test passed!
```

### Step 3: Test Single Row (Optional)

Modify `config/settings.py` temporarily:
```python
# For testing, process only 1 row
BATCH_SIZE = 1
```

Then run:
```bash
python main.py --run --fresh
```

Check output CSV has 1 row with extracted variables.

## Deployment Steps

### Step 1: Start Fresh Run

```bash
python main.py --run --fresh
```

This will:
- Process all rows from the beginning
- Create checkpoints every 5 rows
- Save results to `output_data/sales_variables_extracted.csv`
- Generate logs in `logs/` directory

### Step 2: Monitor Progress

**In another terminal**:
```bash
# Watch real-time logs
tail -f logs/variables_extraction_*.log

# Check checkpoint
cat checkpoints/variables_extraction_checkpoint.json
```

### Step 3: Handle Interruptions

If the process is interrupted:
```bash
# Resume from checkpoint
python main.py --run
```

The agent will automatically continue from the last processed row.

## Post-Deployment Verification

### ✅ Output Validation

- [ ] `output_data/sales_variables_extracted.csv` exists
- [ ] CSV has expected number of rows
- [ ] CSV has 45+ columns
- [ ] `lgs_extraction_success` column has True values
- [ ] `omc_extraction_success` column has True values
- [ ] No completely empty rows

### ✅ Quality Checks

```python
import pandas as pd

# Load results
df = pd.read_csv('output_data/sales_variables_extracted.csv')

# Check success rates
print(f"Total rows: {len(df)}")
print(f"LGS success rate: {df['lgs_extraction_success'].mean():.2%}")
print(f"OMC success rate: {df['omc_extraction_success'].mean():.2%}")
print(f"Both successful: {(df['lgs_extraction_success'] & df['omc_extraction_success']).mean():.2%}")

# Check for missing data
print("\nMissing data per column:")
print(df.isnull().sum()[df.isnull().sum() > 0])

# Sample extracted variables
print("\nSample LGS variables:")
print(df[['lead_id', 'timezone', 'season_status', 'lgs_sentiment_style']].head())

print("\nSample OMC variables:")
print(df[['lead_id', 'total_discovery_questions', 'call_result_tag']].head())
```

### ✅ Log Review

- [ ] Check `logs/variables_extraction_*.log` for errors
- [ ] Review extraction statistics at end of log
- [ ] Verify no critical errors in `logs/variables_extraction_errors_*.log`

### ✅ Checkpoint Integrity

- [ ] `checkpoints/variables_extraction_checkpoint.json` exists
- [ ] Checkpoint has correct number of processed rows
- [ ] Checkpoint timestamp is recent

## Common Issues and Solutions

### Issue: Low Success Rate (<80%)

**Possible Causes**:
- Poor transcription quality
- API rate limiting
- Prompt issues

**Solutions**:
1. Check error logs for specific failures
2. Review failed rows manually
3. Adjust prompts if needed
4. Increase `MAX_RETRIES` in settings

### Issue: Missing Variables

**Possible Causes**:
- Transcription doesn't contain required information
- Prompt not specific enough
- Schema mismatch

**Solutions**:
1. Review sample transcriptions
2. Adjust prompts to be more flexible
3. Check schema field names match prompt output

### Issue: Slow Processing

**Expected**: 5-10 seconds per row (2 LLM calls)

**If slower**:
1. Check API rate limits
2. Verify network connection
3. Consider parallel processing for large datasets

### Issue: JSON Parse Errors

**Solutions**:
- Agent automatically retries (up to 3 times)
- Check if Gemini is returning valid JSON
- Review prompt formatting
- Check for special characters in transcriptions

## Performance Benchmarks

| Metric | Expected Value |
|--------|---------------|
| Processing Speed | 5-10 seconds/row |
| LGS Success Rate | >90% |
| OMC Success Rate | >85% |
| Both Successful | >80% |
| Retry Rate | <10% |
| API Errors | <5% |

## Rollback Plan

If critical issues occur:

1. **Stop the process**: Press Ctrl+C
2. **Review logs**: Check error logs for issues
3. **Fix configuration**: Adjust settings/prompts
4. **Clear checkpoint** (if needed):
   ```bash
   rm checkpoints/variables_extraction_checkpoint.json
   ```
5. **Restart**: `python main.py --run --fresh`

## Production Recommendations

### For Large Datasets (>1000 rows)

1. **Test first**: Run on 10-20 rows to validate
2. **Monitor closely**: Watch logs for first 100 rows
3. **Checkpoint frequently**: Keep `BATCH_SIZE = 5`
4. **Schedule wisely**: Run during off-peak hours
5. **Backup data**: Keep original CSV safe

### For Continuous Operation

1. **Set up monitoring**: Alert on error rate >10%
2. **Automate restarts**: Script to resume on failure
3. **Log rotation**: Archive old logs regularly
4. **Checkpoint cleanup**: Remove old checkpoints after success

### For Multiple Datasets

1. **Create separate configs**: One per dataset
2. **Use different output files**: Avoid overwriting
3. **Parallel processing**: Run multiple instances on subsets
4. **Merge results**: Combine outputs after completion

## Sign-Off Checklist

Before considering deployment complete:

- [ ] All pre-deployment checks passed
- [ ] Setup test successful
- [ ] API connection test successful
- [ ] At least 1 test row processed successfully
- [ ] Full dataset processed (or in progress)
- [ ] Output CSV validated
- [ ] Success rates meet benchmarks
- [ ] Logs reviewed for errors
- [ ] Results backed up
- [ ] Documentation reviewed
- [ ] Team notified of completion

## Support

For issues or questions:
1. Check logs first: `logs/variables_extraction_errors_*.log`
2. Review documentation: `README.md` and `QUICKSTART.md`
3. Run setup test: `python test_setup.py`
4. Contact development team with:
   - Error logs
   - Sample problematic row
   - Configuration settings used

## Success Criteria

✅ **Deployment is successful when**:
- All rows processed (or checkpoint shows progress)
- Success rate >80% for both LGS and OMC
- Output CSV has expected structure
- No critical errors in logs
- Results are actionable and accurate

---

**Last Updated**: December 18, 2025
**Version**: 1.0.0
**Status**: Ready for Production

