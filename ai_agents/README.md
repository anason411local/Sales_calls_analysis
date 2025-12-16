# Sales Call Analyzer - AI Agent

A comprehensive AI-powered system for extracting structured data from sales call transcriptions using Gemini 2.5 Flash, LangChain, LangGraph, and Pydantic.

## Features

- **Comprehensive Data Extraction**: Extracts 200+ data points across 6 categories
- **LangGraph Workflow**: Stateful multi-step extraction process with error handling
- **Batch Processing**: Processes 10 rows at a time with progress tracking
- **Resume Capability**: Automatically saves checkpoints and can resume from interruptions
- **Retry Logic**: Automatically retries failed extractions
- **Comprehensive Logging**: Logs all activities from start to finish
- **Pydantic Validation**: Validates extracted data against structured schemas
- **Wide CSV Output**: Outputs flat CSV with all data points as separate columns

## Architecture

```
sales_call_analyzer/
├── agents/              # LangGraph extraction agent
├── config/              # Configuration and settings
├── data/                # Data handlers for I/O
├── llm/                 # Gemini LLM client
├── orchestrator/        # Batch processing orchestrator
├── schemas/             # Pydantic schemas for validation
└── utils/               # Logging and utilities
```

## Installation

1. **Activate Conda Environment**:
```bash
conda activate sales_calls_ai_agent
```

2. **Install Dependencies**:
```bash
cd ai_agents
pip install -r requirements.txt
```

3. **Configure Environment**:
Ensure `.env` file exists with your Gemini API key:
```
GEMINI_API_KEY=your_api_key_here
```

## Usage

### Basic Usage

Process all sales calls:
```bash
python main.py
```

### Test API Connection

Test Gemini API connection:
```bash
python main.py --test-connection
```

### Start Fresh (No Resume)

Start from scratch without resuming from checkpoint:
```bash
python main.py --no-resume
```

### Resume from Checkpoint

By default, the system will automatically resume from the last checkpoint if interrupted:
```bash
python main.py
```

## Data Extraction Categories

The system extracts data across 6 comprehensive categories:

### Category I: Customer Engagement & Interest
- Talk ratio (agent vs customer)
- Discovery questions (19 questions across 3 goals)
- Buying signals vs resistance signals

### Category II: Call Opening & Framing
- Time to state reason for call
- Business type & location personalization
- Call structure clarity

### Category III: Objection Handling & Friction
- Objections raised and rebutted
- Acknowledgement patterns
- Price/timeline/contract mentions near drop-off

### Category IV: Pace, Control, and Interruptions
- Agent monologue length
- Customer interruptions
- Script deviation analysis

### Category V: Emotional Tone & Rapport
- Rapport moments in first minute
- Customer sentiment over time
- Empathy statements

### Category VI: Outcome and Timing Markers
- Hang-up timing relative to stages
- Commitments secured
- Call result classification

## Output

### CSV Output
- **Location**: `output_data/sales_calls_extracted_data.csv`
- **Format**: Wide format with 200+ columns
- **Structure**: One row per input call with all extracted data

### Logs
- **Location**: `logs/`
- **Files**:
  - `sales_call_analysis_YYYYMMDD_HHMMSS.log` - Complete activity log
  - `sales_call_errors_YYYYMMDD_HHMMSS.log` - Error log

### Summary Report
- **Location**: `output_data/extraction_summary_YYYYMMDD_HHMMSS.txt`
- **Contents**: Statistics, success/fail counts, duration, failed row indices

### Checkpoints
- **Location**: `checkpoints/extraction_checkpoint.json`
- **Purpose**: Enables resume capability after interruptions

## Configuration

Edit `sales_call_analyzer/config/settings.py` to customize:

- `BATCH_SIZE`: Number of rows to process at once (default: 10)
- `MAX_RETRIES`: Number of retry attempts for failed rows (default: 3)
- `LLM_TEMPERATURE`: Temperature for LLM (default: 0.1)
- `LLM_MAX_TOKENS`: Maximum tokens for response (default: 8000)
- `ENABLE_CHECKPOINTING`: Enable/disable checkpointing (default: True)

## Error Handling

The system handles errors gracefully:

1. **Input Validation**: Validates required fields before processing
2. **LLM Errors**: Retries failed API calls up to MAX_RETRIES times
3. **Validation Errors**: Logs validation issues but continues processing
4. **Failed Rows**: Saves rows with NaN values and logs errors
5. **Interruptions**: Saves checkpoint and can resume later

## Logging

Comprehensive logging includes:

- Batch start/end with statistics
- Row-by-row processing status
- LLM API calls and responses
- Validation errors and warnings
- Checkpoint saves/loads
- Final summary statistics

## Performance

- **Processing Speed**: ~30-60 seconds per call (depends on transcription length)
- **Batch Processing**: 10 calls per batch
- **Memory Usage**: Moderate (processes in batches)
- **API Rate Limits**: Respects Gemini API limits with retry logic

## Troubleshooting

### API Connection Issues
```bash
python main.py --test-connection
```

### Missing Dependencies
```bash
pip install -r requirements.txt
```

### Checkpoint Issues
Delete checkpoint to start fresh:
```bash
rm checkpoints/extraction_checkpoint.json
python main.py
```

### Log Analysis
Check logs for detailed error information:
```bash
tail -f logs/sales_call_analysis_*.log
```

## System Instructions and Prompts

The system uses comprehensive instructions from:
- `ai_agent_for_Sales_prompt_variobles_extarctoin/system Instrutions.txt`
- `ai_agent_for_Sales_prompt_variobles_extarctoin/sales_data_extaction_prompt.txt`

These files contain the complete extraction framework and are loaded automatically.

## License

Internal use only - Sales Analytics Team

## Support

For issues or questions, check the logs first, then contact the development team.

