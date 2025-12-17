# 🚀 Quick Start Guide - Call Performance Analyzer

## Prerequisites

✅ Conda environment: `sales_calls_ai_agent`  
✅ Input data: `input_data/sales_calls_agent_testing_data.csv`  
✅ API keys configured in `ai_agents/.env`

## Installation

```bash
# Navigate to project directory
cd d:\Sales_calls_analysis\ai_agents\call_performance_analyzer

# Install dependencies (if not already installed)
C:\Users\Rtx_5090\.conda\envs\sales_calls_ai_agent\python.exe -m pip install -r requirements.txt
```

## Configuration Check

Verify your `.env` file at `d:\Sales_calls_analysis\ai_agents\.env`:

```env
GEMINI_API_KEY=your_api_key_here
LANGSMITH_TRACING=true
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
LANGSMITH_API_KEY=your_langsmith_key_here
LANGSMITH_PROJECT=Call_Performance_Analysis
```

## Running the Analysis

### Option 1: Full Analysis (Recommended)

```bash
cd d:\Sales_calls_analysis\ai_agents\call_performance_analyzer
C:\Users\Rtx_5090\.conda\envs\sales_calls_ai_agent\python.exe main.py --run
```

### Option 2: Start Fresh (Ignore Checkpoint)

```bash
C:\Users\Rtx_5090\.conda\envs\sales_calls_ai_agent\python.exe main.py --run --fresh
```

### Option 3: Resume from Checkpoint

```bash
C:\Users\Rtx_5090\.conda\envs\sales_calls_ai_agent\python.exe main.py --run --resume
```

## What Happens During Execution

1. **Data Loading**: Loads CSV from `input_data/`
2. **Batch Processing**: Processes 10 rows at a time
3. **LLM Analysis**: Each call analyzed by Gemini 2.5 Flash
4. **Metric Accumulation**: Insights aggregated across batches
5. **Checkpoint Saving**: Progress saved after each batch
6. **Report Generation**: Comprehensive Markdown report created
7. **Output**: Report saved to `reports/call_performance_analysis_report.md`

## Expected Output

```
================================================================================
STARTING CALL PERFORMANCE ANALYSIS
================================================================================
2025-12-17 02:15:13 - INFO - Loading input data...
2025-12-17 02:15:13 - INFO - Loaded 49 rows from input file
2025-12-17 02:15:13 - INFO - Created 5 batches of size 10
================================================================================
PROCESSING BATCH 1/5
================================================================================
2025-12-17 02:15:14 - INFO - Analyzing call 1/10 - ID: 12345
...
================================================================================
GENERATING COMPREHENSIVE REPORT
================================================================================
2025-12-17 02:20:30 - INFO - Report saved to: D:\Sales_calls_analysis\reports\call_performance_analysis_report.md
================================================================================
ANALYSIS COMPLETE
Total calls analyzed: 49
Report saved to: D:\Sales_calls_analysis\reports\call_performance_analysis_report.md
================================================================================
```

## Output Files

### Main Report
📄 `reports/call_performance_analysis_report.md`
- Executive summary
- Agent performance analysis
- Call pattern insights
- Recommendations
- Real examples

### Logs
📝 `logs/call_analysis_YYYYMMDD_HHMMSS.log` - All activities  
❌ `logs/call_analysis_errors_YYYYMMDD_HHMMSS.log` - Errors only

### Checkpoint
💾 `output_data/analysis_checkpoint.json` - Resume capability

## Viewing the Report

### Option 1: Open in Text Editor
```bash
notepad reports\call_performance_analysis_report.md
```

### Option 2: Open in Word
- Right-click the `.md` file
- Open with Microsoft Word
- Word will render the Markdown

### Option 3: Convert to DOCX
```bash
# If you have Pandoc installed
pandoc reports\call_performance_analysis_report.md -o reports\report.docx
```

### Option 4: View in VS Code
```bash
code reports\call_performance_analysis_report.md
```

## Troubleshooting

### Issue: "GEMINI_API_KEY not found"
**Solution**: Check that `.env` file exists at `ai_agents/.env` and contains the API key

### Issue: "No such file or directory: input_data/sales_calls_agent_testing_data.csv"
**Solution**: Verify the CSV file exists at the correct location

### Issue: "Failed to analyze call"
**Solution**: Check logs in `logs/` directory for detailed error messages

### Issue: Process interrupted
**Solution**: Simply run again with `--resume` flag to continue from checkpoint

### Issue: "Module not found"
**Solution**: Ensure you're running from the correct directory and using the conda environment's Python

## Performance

- **Processing Speed**: ~30-60 seconds per batch (10 calls)
- **Total Time**: ~5-10 minutes for 49 calls
- **Token Usage**: ~500-1000 tokens per call analysis
- **Report Generation**: ~30-60 seconds

## Next Steps

1. ✅ Run the analysis
2. ✅ Review the generated report
3. ✅ Share with CEO/management
4. ✅ Implement recommendations
5. ✅ Re-run analysis after changes to measure improvement

## Tips

- **First Run**: Use `--fresh` to ensure clean start
- **Interrupted**: Use `--resume` to continue
- **Multiple Runs**: Delete checkpoint file between runs if starting over
- **Large Datasets**: The system handles any size via batching
- **Customization**: Edit `config/settings.py` for custom parameters

## Support

For issues or questions:
1. Check logs in `logs/` directory
2. Review `ARCHITECTURE.md` for technical details
3. Check `README.md` for comprehensive documentation

---

**Ready to improve your call performance? Let's go! 🚀**

