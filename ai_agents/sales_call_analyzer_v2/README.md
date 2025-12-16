# Sales Call Analyzer V2 - LangGraph Agentic Framework

A complete redesign of the sales call analyzer using proper LangGraph agentic architecture with Gemini 2.5 Flash Lite.

## 🎯 Key Features

- **True Agentic Framework**: Built with LangGraph nodes, states, and workflows
- **Gemini 2.5 Flash Lite**: Uses the correct model as specified
- **Structured Output**: Function calling for reliable schema adherence
- **LangSmith Integration**: Full tracing and monitoring support
- **Comprehensive Logging**: All activities logged, not just errors
- **Resume Capability**: Checkpoint system to resume from interruptions
- **Retry Logic**: Automatic retry for failed extractions
- **Wide Format Output**: All data points in separate columns for ML/NLP analysis

## 📁 Project Structure

```
sales_call_analyzer_v2/
├── config/              # Configuration settings
│   ├── __init__.py
│   └── settings.py
├── schemas/             # Pydantic schemas for structured output
│   ├── __init__.py
│   └── extraction_schemas.py
├── graph/               # LangGraph state definitions
│   ├── __init__.py
│   └── state.py
├── prompts/             # Prompt templates using ChatPromptTemplate
│   ├── __init__.py
│   └── prompt_templates.py
├── llm/                 # Gemini LLM client with structured output
│   ├── __init__.py
│   └── gemini_client.py
├── agents/              # LangGraph nodes and workflow
│   ├── __init__.py
│   ├── extraction_nodes.py
│   └── extraction_graph.py
├── data/                # Data handlers for CSV I/O
│   ├── __init__.py
│   └── data_handler.py
├── orchestrator/        # Batch processing orchestration
│   ├── __init__.py
│   └── batch_processor.py
├── utils/               # Utilities (logging, etc.)
│   ├── __init__.py
│   └── logger.py
├── main.py              # Main entry point
├── requirements.txt     # Dependencies
└── README.md            # This file
```

## 🚀 Setup

### 1. Install Dependencies

```bash
cd ai_agents/sales_call_analyzer_v2
conda activate sales_calls_ai_agent
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Ensure your `.env` file in the parent `ai_agents` directory contains:

```env
GEMINI_API_KEY=your_api_key_here
LANGSMITH_TRACING=true
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
LANGSMITH_API_KEY=your_langsmith_key_here
LANGSMITH_PROJECT=Sales_call_analysis_agent
```

## 🎮 Usage

### Test API Connection

```bash
python main.py --test-connection
```

### Run Extraction Process

```bash
python main.py --run
```

## 🏗️ Architecture

### LangGraph Workflow

The system uses a proper LangGraph StateGraph with the following nodes:

1. **prepare_extraction**: Initialize state and load prompts
2. **extract_data**: Call Gemini LLM with structured output
3. **validate_extraction**: Validate extracted data against schema
4. **check_retry**: Determine if retry is needed
5. **complete_extraction**: Finalize successful extraction
6. **fail_extraction**: Handle permanent failures

### State Management

The `AgentState` TypedDict tracks:
- Input data (transcript, metadata)
- Extraction results
- Retry attempts
- Error messages
- Workflow control flags

### Structured Output

Uses Gemini's function calling via `with_structured_output()` to ensure:
- Exact schema adherence
- No random field names
- Proper data types
- Complete extraction of all 6 categories

### Prompt Templates

Uses LangChain's `ChatPromptTemplate` with:
- Full system instructions (not truncated)
- Complete extraction prompt (not truncated)
- Proper message formatting
- Retry-specific templates

## 📊 Output Format

Creates a wide-format CSV with:
- Metadata columns (row_id, call_date, fullname, length_in_sec)
- All 6 extraction categories flattened into separate columns:
  - Customer Engagement & Interest (ce_*)
  - Call Opening & Framing (co_*)
  - Objection Handling & Friction (oh_*)
  - Pace, Control & Interruptions (pc_*)
  - Emotional Tone & Rapport (et_*)
  - Outcome & Timing Markers (ot_*)

## 📝 Logging

All activities are logged to:
- Console: INFO level and above
- Log file: DEBUG level and above (in `logs/` directory)

Logs include:
- Extraction start/success/failure
- LLM calls and responses
- Batch processing progress
- Checkpoint saves
- Retry attempts
- Final statistics

## 🔄 Resume Capability

The system automatically:
- Saves checkpoints after each batch
- Resumes from last processed row on restart
- Appends to existing output file

## ⚠️ Error Handling

- Failed extractions are retried up to MAX_RETRIES times
- After all batches, failed rows are retried once more
- Permanent failures are saved with empty/NaN values
- All errors are logged comprehensively

## 🎯 Key Improvements Over V1

1. ✅ **True LangGraph Agentic Framework** (not just a script)
2. ✅ **Correct Model**: Gemini 2.5 Flash Lite
3. ✅ **Structured Output**: Function calling for schema adherence
4. ✅ **LangSmith Integration**: Full tracing enabled
5. ✅ **Comprehensive Logging**: All activities, not just errors
6. ✅ **No Truncation**: Full system instructions and prompts used
7. ✅ **Proper State Management**: TypedDict-based state
8. ✅ **Robust Error Handling**: No None values, proper NaN handling

## 📚 Dependencies

- **langchain**: Core LangChain framework
- **langgraph**: State graph workflow engine
- **langchain-google-genai**: Gemini integration
- **pydantic**: Schema validation
- **pandas**: Data processing
- **python-dotenv**: Environment configuration
- **langsmith**: Tracing and monitoring

## 🐛 Troubleshooting

### API Connection Issues
- Verify GEMINI_API_KEY in .env
- Test connection with `--test-connection` flag

### Import Errors
- Ensure all dependencies are installed
- Activate correct conda environment

### Schema Validation Errors
- Check that all 6 categories are being extracted
- Review LangSmith traces for LLM response format

## 📄 License

Internal use only.
