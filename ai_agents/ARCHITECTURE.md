# Sales Call Analyzer - System Architecture

## Overview

The Sales Call Analyzer is a sophisticated AI-powered system that extracts structured data from sales call transcriptions using Google's Gemini 2.0 Flash model, LangChain, LangGraph, and Pydantic for validation.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         Main Entry Point                         │
│                         (main.py)                                │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Batch Processor                             │
│                  (Orchestrator Layer)                            │
│  - Manages batch processing (10 rows at a time)                 │
│  - Implements retry logic                                        │
│  - Handles checkpointing for resume capability                  │
│  - Progress tracking with tqdm                                   │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Data Handler                                  │
│                    (Data Layer)                                  │
│  - CSV I/O operations                                            │
│  - Checkpoint management                                         │
│  - Data preparation and validation                              │
│  - Summary report generation                                     │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│              LangGraph Extraction Agent                          │
│                  (Agent Layer)                                   │
│                                                                  │
│  Workflow Nodes:                                                 │
│  1. validate_input    → Check required fields                   │
│  2. extract_data      → Call Gemini LLM                         │
│  3. validate_extraction → Validate extracted data               │
│  4. flatten_data      → Convert to flat CSV format              │
│  5. handle_error      → Create fallback data                    │
│  6. finalize          → Add metadata                             │
│                                                                  │
│  State Management:                                               │
│  - Tracks processing state                                       │
│  - Manages retry count                                           │
│  - Stores errors and validation issues                          │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Gemini LLM Client                             │
│                    (LLM Layer)                                   │
│  - API integration with Gemini 2.0 Flash                        │
│  - Prompt construction from system instructions                 │
│  - JSON parsing and validation                                  │
│  - Error handling and retries                                   │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                  Pydantic Schemas                                │
│                (Validation Layer)                                │
│  - SalesCallExtraction (nested structure)                       │
│  - FlattenedCallData (flat CSV structure)                       │
│  - 6 Category schemas with 200+ fields                          │
│  - Type validation and data integrity                           │
└─────────────────────────────────────────────────────────────────┘
```

## Module Structure

```
sales_call_analyzer/
│
├── agents/
│   ├── __init__.py
│   └── extraction_agent.py          # LangGraph workflow agent
│       - ExtractionState (TypedDict)
│       - SalesCallExtractionAgent
│       - Workflow nodes and routing
│       - Data flattening logic
│
├── config/
│   ├── __init__.py
│   └── settings.py                  # Configuration management
│       - Settings (Pydantic BaseSettings)
│       - Environment variables
│       - Path configuration
│       - Processing parameters
│
├── data/
│   ├── __init__.py
│   └── data_handler.py              # Data I/O operations
│       - DataHandler class
│       - CSV reading/writing
│       - Checkpoint management
│       - Batch creation
│
├── llm/
│   ├── __init__.py
│   └── gemini_client.py             # Gemini API integration
│       - GeminiClient class
│       - API calls and error handling
│       - Prompt construction
│       - Response parsing
│
├── orchestrator/
│   ├── __init__.py
│   └── batch_processor.py           # Batch processing orchestration
│       - BatchProcessor class
│       - Multi-batch processing
│       - Retry logic
│       - Statistics tracking
│
├── schemas/
│   ├── __init__.py
│   └── extraction_schemas.py        # Pydantic data models
│       - Category I: Customer Engagement (15%)
│       - Category II: Call Opening (10%)
│       - Category III: Objection Handling (20%)
│       - Category IV: Pace & Control (15%)
│       - Category V: Emotional Tone (20%)
│       - Category VI: Outcome & Timing (20%)
│       - FlattenedCallData (200+ fields)
│
└── utils/
    ├── __init__.py
    └── logger.py                    # Comprehensive logging
        - SalesCallLogger class
        - Multi-handler logging
        - Activity tracking
        - Error logging
```

## Data Flow

### 1. Initialization Phase
```
main.py
  ↓
ensure_directories()
  ↓
BatchProcessor.__init__()
  ↓
  ├─→ SalesCallExtractionAgent.__init__()
  │     ↓
  │   GeminiClient.__init__()
  │     ↓
  │   Load system instructions & prompts
  │     ↓
  │   Build LangGraph workflow
  │
  └─→ DataHandler.__init__()
        ↓
      Configure paths
```

### 2. Processing Phase
```
BatchProcessor.process_all()
  ↓
DataHandler.load_input_data()
  ↓
DataHandler.load_checkpoint() [if resume enabled]
  ↓
DataHandler.get_rows_to_process()
  ↓
DataHandler.create_batches(batch_size=10)
  ↓
FOR EACH BATCH:
  ↓
  BatchProcessor._process_batch()
    ↓
    FOR EACH ROW:
      ↓
      DataHandler.prepare_row_data()
        ↓
      SalesCallExtractionAgent.process_call()
        ↓
        LangGraph Workflow Execution:
          ↓
        1. validate_input
          ↓
        2. extract_data
          ↓
          GeminiClient.extract_call_data()
            ↓
            Build extraction prompt
            ↓
            Call Gemini API
            ↓
            Parse JSON response
            ↓
            Validate with Pydantic
          ↓
        3. validate_extraction
          ↓
        4. flatten_data
          ↓
        5. finalize
          ↓
        Return flattened data
      ↓
      Collect results
    ↓
    DataHandler.save_checkpoint()
  ↓
  Continue to next batch
```

### 3. Retry Phase
```
IF failed_rows exist:
  ↓
  Create retry batches
  ↓
  Process failed rows again
  ↓
  Update results
```

### 4. Finalization Phase
```
DataHandler.save_output_data()
  ↓
DataHandler.export_summary_report()
  ↓
DataHandler.clear_checkpoint()
  ↓
Display statistics
```

## Key Design Patterns

### 1. **State Machine Pattern** (LangGraph)
- Workflow represented as a state graph
- Each node performs a specific transformation
- Conditional routing based on state
- Maintains processing context

### 2. **Strategy Pattern** (Error Handling)
- Multiple error handling strategies
- Retry with exponential backoff
- Fallback data generation
- Graceful degradation

### 3. **Builder Pattern** (Prompt Construction)
- Systematic prompt building
- System instructions + extraction framework
- Call-specific data injection
- Structured output specification

### 4. **Repository Pattern** (Data Handler)
- Abstraction over data persistence
- Checkpoint management
- CSV I/O operations
- Batch management

### 5. **Observer Pattern** (Logging)
- Comprehensive activity logging
- Multiple log handlers
- Event-driven logging
- Progress tracking

## Configuration Management

### Environment Variables (.env)
```
GEMINI_API_KEY=your_api_key_here
```

### Settings (settings.py)
```python
# Processing
BATCH_SIZE = 10
MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 2

# LLM
LLM_TEMPERATURE = 0.1
LLM_MAX_TOKENS = 8000
LLM_TIMEOUT_SECONDS = 120

# Checkpointing
ENABLE_CHECKPOINTING = True
CHECKPOINT_FREQUENCY = 1
```

## Error Handling Strategy

### Level 1: Input Validation
- Check required fields
- Validate data types
- Handle missing data

### Level 2: LLM Call Errors
- Retry on API failures
- Handle rate limiting
- Timeout management

### Level 3: Validation Errors
- Pydantic validation
- Schema compliance
- Data quality checks

### Level 4: Processing Errors
- Exception catching
- Fallback data generation
- Error logging

### Level 5: Batch Errors
- Continue on row failure
- Collect failed indices
- Retry failed rows

## Performance Considerations

### Optimization Strategies
1. **Batch Processing**: Process 10 rows at a time
2. **Checkpointing**: Save progress after each batch
3. **Lazy Loading**: Load data in chunks
4. **Progress Tracking**: Real-time progress with tqdm
5. **Error Recovery**: Resume from checkpoint

### Resource Usage
- **Memory**: Moderate (processes in batches)
- **CPU**: Low (I/O bound)
- **Network**: API calls to Gemini
- **Disk**: Logs, checkpoints, output CSV

### Scalability
- **Horizontal**: Can process multiple files in parallel
- **Vertical**: Batch size can be adjusted
- **Resumable**: Checkpoint system allows interruption
- **Extensible**: Modular architecture

## Security Considerations

1. **API Key Management**: Environment variables
2. **Data Privacy**: Local processing, no data sent except to Gemini
3. **Error Handling**: No sensitive data in logs
4. **Validation**: Pydantic ensures data integrity

## Testing Strategy

### Unit Tests (Future)
- Test individual components
- Mock LLM responses
- Validate schemas

### Integration Tests (Future)
- Test workflow execution
- Test data pipeline
- Test error handling

### System Tests
- API connection test: `python main.py --test-connection`
- Full pipeline test: Process sample data

## Monitoring and Logging

### Log Levels
- **DEBUG**: Detailed execution flow
- **INFO**: Major operations and progress
- **WARNING**: Non-critical issues
- **ERROR**: Failures and exceptions
- **CRITICAL**: Fatal errors

### Log Files
1. **Main Log**: All activities from start to finish
2. **Error Log**: Only errors and critical issues
3. **Summary Report**: Statistics and results

### Metrics Tracked
- Total rows processed
- Success/failure counts
- Processing duration
- Average time per row
- Retry attempts
- API call statistics

## Future Enhancements

1. **Parallel Processing**: Process multiple rows simultaneously
2. **Streaming**: Stream large files
3. **Database Support**: Store results in database
4. **Web Interface**: Dashboard for monitoring
5. **Advanced Analytics**: Statistical analysis of extracted data
6. **Model Comparison**: Test multiple LLM models
7. **Fine-tuning**: Custom model training
8. **API Service**: RESTful API for extraction

## Dependencies

### Core
- `pandas`: Data manipulation
- `numpy`: Numerical operations
- `google-generativeai`: Gemini API
- `langchain`: LLM framework
- `langgraph`: Workflow orchestration
- `pydantic`: Data validation

### Utilities
- `python-dotenv`: Environment management
- `tqdm`: Progress bars
- `typing-extensions`: Type hints

## Conclusion

The Sales Call Analyzer is a production-ready, enterprise-grade system designed for scalability, reliability, and maintainability. The modular architecture allows for easy extension and modification, while the comprehensive error handling and logging ensure robust operation in production environments.

