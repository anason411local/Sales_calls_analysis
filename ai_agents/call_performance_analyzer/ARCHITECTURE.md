# 🏗️ Call Performance Analyzer - Architecture Documentation

## Overview

The Call Performance Analyzer is a sophisticated AI-powered business intelligence agent built using a modular agentic framework with LangGraph, LangChain, and Pydantic.

## System Architecture

### High-Level Design

```
┌─────────────────────────────────────────────────────────────┐
│                     INPUT DATA (CSV)                         │
│  LGS + OMC Call Transcriptions, Metadata, Outcomes          │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                  DATA HANDLER                                │
│  • Load CSV                                                  │
│  • Create Batches (10 rows)                                 │
│  • Checkpoint Management                                     │
│  • Resume Capability                                         │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              BATCH ORCHESTRATOR                              │
│  • Manages workflow execution                                │
│  • Coordinates batches                                       │
│  • Maintains global state                                    │
│  • Triggers report generation                                │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              LANGGRAPH WORKFLOW                              │
│                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐ │
│  │   Prepare    │───▶│   Analyze    │───▶│  Accumulate  │ │
│  │    Batch     │    │    Calls     │    │   Metrics    │ │
│  └──────────────┘    └──────────────┘    └──────────────┘ │
│                                                   │          │
│                                                   ▼          │
│                                          ┌──────────────┐   │
│                                          │    Check     │   │
│                                          │  Completion  │   │
│                                          └──────────────┘   │
│                                                   │          │
└───────────────────────────────────────────────────┼─────────┘
                                                    │
                     ┌──────────────────────────────┴─────────┐
                     │                                        │
                     ▼                                        ▼
            ┌─────────────────┐                    ┌─────────────────┐
            │  More Batches?  │                    │  All Complete?  │
            │  Return to Loop │                    │  Generate Report│
            └─────────────────┘                    └─────────────────┘
                                                            │
                                                            ▼
                                                   ┌─────────────────┐
                                                   │ REPORT GENERATOR│
                                                   │ • LLM synthesis │
                                                   │ • Markdown      │
                                                   │ • Statistics    │
                                                   │ • Examples      │
                                                   └─────────────────┘
                                                            │
                                                            ▼
                                                   ┌─────────────────┐
                                                   │  OUTPUT REPORT  │
                                                   │  (Markdown)     │
                                                   └─────────────────┘
```

## Component Details

### 1. Configuration Layer (`config/`)

**Purpose**: Centralized configuration management

**Files**:
- `settings.py`: All configuration parameters
  - File paths
  - API keys
  - Model settings
  - Batch size
  - Company context
  - Analysis focus areas

**Key Features**:
- Environment variable loading
- Path management
- Constants definition
- Company context storage

### 2. Data Models (`schemas/`)

**Purpose**: Structured data validation using Pydantic

**Files**:
- `analysis_schemas.py`: All Pydantic models

**Models**:

#### `CallInsight`
- Individual call analysis result
- LGS and OMC data
- Performance ratings
- Patterns identified
- Recommendations
- Notable quotes

#### `AgentPerformance`
- Aggregated agent metrics
- Call counts and durations
- Success rates
- Strengths and issues

#### `DailyTrend`
- Daily performance metrics
- Trend analysis data

#### `StatusAnalysis`
- Outcome-based analysis
- Status-specific patterns

#### `ComprehensiveReport`
- Final report structure
- All aggregated insights
- Examples and recommendations

### 3. Prompts (`prompts/`)

**Purpose**: LLM instruction management

**Files**:
- `system_instructions.txt`: Comprehensive analyst role definition
- `analysis_prompt.txt`: Call analysis task template
- `prompt_templates.py`: LangChain prompt templates

**Key Features**:
- Detailed business context
- Analysis framework
- Output requirements
- Quality guidelines

### 4. Utilities (`utils/`)

**Purpose**: Cross-cutting concerns

**Files**:
- `logger.py`: Comprehensive logging setup
- `gemini_client.py`: LLM client management

**Features**:
- Multi-level logging (console, file, error)
- LangSmith integration
- Structured output configuration
- Error handling

### 5. State Management (`graph/`)

**Purpose**: LangGraph state definition

**Files**:
- `state.py`: `AnalysisState` TypedDict
- `analysis_graph.py`: LangGraph workflow construction

**State Components**:
- Current batch data
- Accumulated insights
- Agent/daily/status metrics
- Pattern collections
- Examples
- Processing metadata
- Error tracking

### 6. Analysis Nodes (`agents/`)

**Purpose**: LangGraph workflow nodes

**Files**:
- `analysis_nodes.py`: All workflow nodes

**Nodes**:

#### `prepare_batch_node`
- Initialize state fields
- Prepare batch for processing
- Set up data structures

#### `analyze_call_node`
- Invoke Gemini LLM for each call
- Structured output extraction
- Error handling
- Failed insight creation

#### `accumulate_metrics_node`
- Aggregate agent metrics
- Collect daily trends
- Track status patterns
- Gather examples
- Identify LGS issues

#### `check_completion_node`
- Verify processing progress
- Set completion flag
- Determine next action

### 7. Data Handling (`data/`)

**Purpose**: Data I/O operations

**Files**:
- `data_handler.py`: `DataHandler` class

**Capabilities**:
- CSV loading and validation
- Batch creation
- Checkpoint save/load
- Report saving
- DataFrame manipulation

### 8. Orchestration (`orchestrator/`)

**Purpose**: Workflow coordination

**Files**:
- `batch_orchestrator.py`: `BatchOrchestrator` class

**Responsibilities**:
- Load data
- Manage checkpoint/resume
- Execute LangGraph for each batch
- Coordinate state accumulation
- Trigger report generation
- Handle errors

### 9. Report Generation (`reports/`)

**Purpose**: Executive report creation

**Files**:
- `report_generator.py`: Report generation logic

**Process**:
1. Aggregate all insights
2. Prepare summaries for LLM
3. Invoke report generation LLM
4. Format Markdown output
5. Add metadata and statistics

**Report Sections**:
- Executive Summary
- Agent Performance
- Call Patterns
- LGS vs OMC Analysis
- Daily Trends
- Status Breakdown
- Recommendations
- Real Examples

### 10. Entry Point (`main.py`)

**Purpose**: CLI interface

**Features**:
- Argument parsing
- Orchestrator initialization
- Error handling
- User feedback

## Data Flow

### Batch Processing Flow

```
1. Load CSV → DataFrame
2. Split into batches (10 rows each)
3. For each batch:
   a. Convert to dict list
   b. Update state with batch
   c. Invoke LangGraph:
      - Prepare batch
      - Analyze calls (LLM)
      - Accumulate metrics
      - Check completion
   d. Save checkpoint
4. After all batches:
   a. Generate report (LLM)
   b. Save Markdown file
   c. Clear checkpoint
```

### State Accumulation

```
Batch 1 → Insights 1-10 → Metrics Update → State
Batch 2 → Insights 11-20 → Metrics Update → State (accumulated)
Batch 3 → Insights 21-30 → Metrics Update → State (accumulated)
...
Batch N → Insights X-Y → Metrics Update → Final State
                                              ↓
                                        Report Generation
```

## LangGraph Workflow

### Node Execution Order

```
START
  ↓
prepare_batch_node
  ↓
analyze_call_node (LLM invocation for each call)
  ↓
accumulate_metrics_node
  ↓
check_completion_node
  ↓
END (orchestrator checks if more batches remain)
```

### State Transitions

Each node receives the current state and returns an updated state. The orchestrator maintains state across batch iterations.

## LLM Integration

### Analysis LLM
- **Model**: Gemini 2.5 Flash
- **Temperature**: 0.1 (consistent analysis)
- **Output**: Structured (`CallInsight` Pydantic model)
- **Purpose**: Individual call analysis

### Report LLM
- **Model**: Gemini 2.5 Flash
- **Temperature**: 0.3 (creative writing)
- **Output**: Text (Markdown)
- **Purpose**: Comprehensive report synthesis

## Error Handling

### Levels
1. **Call-level**: Failed analyses create `CallInsight` with `analysis_success=False`
2. **Batch-level**: Errors logged, processing continues
3. **System-level**: Fatal errors logged and raised

### Recovery
- Checkpoint after each batch
- Resume capability
- Failed insights tracked
- Error log maintained

## Performance Considerations

### Batch Size
- Default: 10 rows
- Balances token usage and processing speed
- Adjustable in settings

### Checkpointing
- Saves progress after each batch
- Enables resume on interruption
- JSON format for easy inspection

### State Management
- Efficient accumulation
- Minimal redundancy
- Structured aggregation

## Extensibility

### Adding New Analysis
1. Extend `CallInsight` schema
2. Update analysis prompt
3. Modify `analyze_call_node`
4. Update report generation

### Adding New Metrics
1. Add to `AnalysisState`
2. Update `accumulate_metrics_node`
3. Update report generation

### Custom Reports
1. Modify `report_generator.py`
2. Add new prompt templates
3. Extend `ComprehensiveReport` schema

## Security & Configuration

### Environment Variables
- API keys stored in `.env`
- Never committed to version control
- Loaded via `python-dotenv`

### LangSmith Integration
- Optional tracing
- Configurable via environment
- Project-based organization

## Testing Strategy

### Unit Testing
- Individual nodes
- Data handler methods
- Schema validation

### Integration Testing
- Full workflow execution
- Checkpoint/resume
- Report generation

### End-to-End Testing
- Real data processing
- Report quality validation
- Performance benchmarking

## Deployment

### Requirements
- Python 3.9+
- Conda environment
- Gemini API access
- LangSmith account (optional)

### Setup Steps
1. Create conda environment
2. Install dependencies
3. Configure `.env`
4. Prepare input data
5. Run analysis

## Monitoring

### Logging
- All activities logged
- Separate error log
- Timestamped entries
- Detailed context

### LangSmith
- Trace all LLM calls
- Monitor performance
- Debug issues
- Track costs

## Future Enhancements

### Potential Additions
1. Parallel processing within batches
2. Real-time dashboard
3. Email report delivery
4. Automated scheduling
5. Historical trend analysis
6. Predictive modeling
7. Interactive visualizations
8. Multi-language support

---

**Architecture designed for scalability, maintainability, and extensibility**

