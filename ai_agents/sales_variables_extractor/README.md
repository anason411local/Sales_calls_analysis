# Sales Variables Extractor - Agentic AI Framework

An advanced AI agent built with LangGraph and Gemini 2.0 Flash for extracting structured variables from sales call transcripts.

## Overview

This agent extracts two sets of variables from sales call data:

1. **LGS (Lead Generation Specialist) Variables**: Timing, seasonality, agent sentiment, customer qualification, and technical quality
2. **OMC (Outbound Marketing Closer) Variables**: Customer engagement, call opening, objection handling, pace control, emotional tone, and outcomes

## Architecture

```
sales_variables_extractor/
├── agents/              # LangGraph extraction nodes
├── config/              # Configuration settings
├── data/                # Data handlers for CSV operations
├── graph/               # LangGraph workflow definition
├── llm/                 # Gemini LLM client
├── orchestrator/        # Batch processing orchestration
├── prompts/             # Prompt templates and files
├── schemas/             # Pydantic data models
├── utils/               # Logging and utilities
├── main.py              # Main entry point
└── requirements.txt     # Python dependencies
```

## Features

- **Agentic Workflow**: Uses LangGraph for stateful, multi-step extraction
- **Dual Extraction**: Processes both LGS and OMC transcriptions independently
- **Retry Logic**: Automatic retry with configurable max attempts
- **Checkpoint Support**: Resume processing from where it left off
- **Structured Output**: Pydantic models ensure data quality
- **Comprehensive Logging**: Detailed logs for debugging and monitoring
- **Rate Limiting**: Built-in delays to respect API limits

## Installation

1. Activate the conda environment:
```bash
conda activate sales_calls_ai_agent
```

2. Install dependencies:
```bash
cd ai_agents/sales_variables_extractor
pip install -r requirements.txt
```

3. Set up environment variables in `.env`:
```
GEMINI_API_KEY=your_api_key_here
LANGSMITH_API_KEY=your_langsmith_key  # Optional
LANGSMITH_PROJECT=sales-variables-extractor  # Optional
LANGSMITH_TRACING=false  # Optional
```

## Usage

### Test API Connection
```bash
python main.py --test-connection
```

### Run Extraction (Resume from checkpoint)
```bash
python main.py --run
```

### Run Extraction (Start fresh)
```bash
python main.py --run --fresh
```

## Input Data

The agent expects a CSV file at `input_data/mergeed_for_test.csv` with the following columns:

### LGS Columns:
- `TO_User_M`: LGS agent name
- `TO_Event_O`: Event timestamp
- `TO_length_in_sec`: Call duration
- `TO_Transcription_VICI(0-32000) Words`: LGS transcription

### OMC Columns:
- `TO_OMC_User`: OMC agent name
- `TO_OMC_Call_Date_O`: Call date
- `TO_OMC_Duration`: Call duration
- `TO_OMC_Transcription_VICI`: OMC transcription

### Common Columns:
- `TO_Lead_ID`: Unique lead identifier
- `LQ_Company_Address`: Customer address
- `LQ_Service`: Service type
- `LQ_Customer_Name`: Customer name

## Output Data

Results are saved to `output_data/sales_variables_extracted.csv` with all extracted variables flattened into columns.

### LGS Variables Output:
- Timezone, season status
- Agent sentiment style, gender
- Decision maker status, readiness for customers
- Customer sentiment, language, availability
- Marketing sophistication level
- Technical call quality score

### OMC Variables Output:
- Customer engagement metrics (talk ratio, discovery questions, signals)
- Call opening metrics (time to reason, personalization)
- Objection handling metrics (objections, acknowledgements, rebuttals)
- Pace control metrics (monologue length, interruptions)
- Emotional tone metrics (rapport, sentiment progression, empathy)
- Outcome metrics (call duration, disconnect stage, result tag)

## Workflow

The LangGraph workflow follows this sequence:

```
1. prepare_extraction
   ↓
2. extract_lgs → [success] → extract_omc
   ↓ [failure]
3. check_lgs_retry → [retry] → extract_lgs
   ↓ [max retries]
4. extract_omc → [success] → complete_extraction
   ↓ [failure]
5. check_omc_retry → [retry] → extract_omc
   ↓ [max retries]
6. complete_extraction → END
```

## Configuration

Edit `config/settings.py` to customize:
- Input/output file paths
- Gemini model selection
- Batch size and rate limiting
- Max retry attempts
- Logging settings

## Prompts

The agent uses specialized prompts for different variable categories:

- `sales_data_extaction_prompt.txt`: OMC variables framework
- `LGS_Sentiiment_analysis.txt`: Agent sentiment classification
- `LGS_Qualifying.txt`: Lead qualification criteria
- `LGS_Customer_sentiment_analysis.txt`: Customer emotional state
- `LGS_Customer_marketing_understanfing.txt`: Marketing sophistication
- `LGS_technical_quality_of__call.txt`: Technical call quality
- `timezone.txt`: US timezone mappings
- `system Instrutions.txt`: System-level instructions

## Logging

Logs are saved to `logs/` directory:
- `variables_extraction_TIMESTAMP.log`: Main log
- `variables_extraction_errors_TIMESTAMP.log`: Error log

## Checkpoints

Checkpoints are saved to `checkpoints/variables_extraction_checkpoint.json` and include:
- List of processed row IDs
- Last update timestamp
- Total rows processed

## Error Handling

The agent includes robust error handling:
- Automatic retries with exponential backoff
- Detailed error logging
- Graceful degradation (continues processing even if some rows fail)
- Checkpoint recovery for interrupted runs

## Performance

- Processes ~5 rows per batch with checkpointing
- Rate limiting: 1 second delay between API calls
- Supports resuming from checkpoint for long-running jobs
- Parallel-ready architecture (can be extended for concurrent processing)

## Troubleshooting

### API Connection Issues
- Verify `GEMINI_API_KEY` is set correctly
- Run `--test-connection` to diagnose
- Check API quota and rate limits

### Missing Data
- Ensure input CSV has required columns
- Check for null/empty transcriptions
- Review logs for specific row failures

### Extraction Failures
- Review error logs for specific issues
- Check prompt templates for formatting
- Verify Pydantic schema matches expected output

## Development

To extend the agent:

1. **Add new variables**: Update `schemas/variable_schemas.py`
2. **Modify prompts**: Edit files in `prompts/`
3. **Change workflow**: Update `graph/extraction_graph.py`
4. **Add nodes**: Create new functions in `agents/extraction_nodes.py`

## License

Internal use only - Sales Analysis Team

## Support

For issues or questions, contact the development team or check the logs directory for detailed error information.

