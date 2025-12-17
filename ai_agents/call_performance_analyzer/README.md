# 📊 Call Performance Analyzer

An AI-powered business intelligence agent that analyzes sales call performance for 411 Locals, identifying patterns, issues, and opportunities to improve conversion rates.

## 🎯 Purpose

This agent analyzes call transcriptions from two departments:
- **LGS (Lead Generation System)**: Initial calls and lead qualification
- **OMC (Outbound Marketing Center)**: Deal closing and sales

**Key Business Problem**: Calls under 2 minutes in OMC are not converting. This agent identifies why and provides actionable recommendations.

## 🏗️ Architecture

### Modular Agentic Framework
```
call_performance_analyzer/
├── config/           # Configuration and settings
├── schemas/          # Pydantic data models
├── prompts/          # System instructions and prompts
├── utils/            # Logging and LLM clients
├── graph/            # LangGraph state management
├── agents/           # LangGraph analysis nodes
├── data/             # Data handling and checkpointing
├── orchestrator/     # Batch processing orchestration
├── reports/          # Report generation engine
└── main.py           # Entry point
```

### LangGraph Workflow
1. **Prepare Batch** → Load and prepare data
2. **Analyze Calls** → LLM analysis with structured output
3. **Accumulate Metrics** → Aggregate insights across batches
4. **Check Completion** → Determine if more batches remain
5. **Generate Report** → Create comprehensive Markdown report

## 📋 Features

- ✅ **Batch Processing**: Processes 10 rows at a time to avoid token limits
- ✅ **Parallel Processing**: All 10 calls in a batch analyzed simultaneously (ThreadPoolExecutor)
- ✅ **State Accumulation**: Maintains insights across all batches
- ✅ **Checkpoint/Resume**: Can resume from interruption
- ✅ **Structured Output**: Pydantic schemas ensure data quality
- ✅ **LangSmith Integration**: Full tracing and monitoring
- ✅ **Comprehensive Logging**: All activities logged
- ✅ **Executive Report**: Professional Markdown output for CEO

## 📊 Analysis Components

### 1. LGS Handoff Quality
- Lead qualification assessment
- Information transfer quality
- Customer expectation setting
- Issues affecting OMC performance

### 2. OMC Call Analysis
- Call duration patterns
- Early termination reasons
- Success factors in long calls
- Agent performance ratings
- Objection handling

### 3. Pattern Identification
- Short call (<2 min) failure patterns
- Long call (>=2 min) success patterns
- Common objections
- Effective techniques

### 4. Agent Performance
- Individual agent metrics
- Top performers vs those needing support
- Performance scores
- Specific recommendations

### 5. Trends & Insights
- Daily performance trends
- Status/outcome breakdown
- Real call examples
- Actionable recommendations

## 🚀 Setup

### 1. Environment Setup
```bash
# Activate conda environment
conda activate sales_calls_ai_agent

# Navigate to project directory
cd d:\Sales_calls_analysis\ai_agents\call_performance_analyzer

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Variables
Ensure `.env` file exists in `ai_agents/` directory:
```env
GEMINI_API_KEY=your_api_key
LANGSMITH_TRACING=true
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
LANGSMITH_API_KEY=your_langsmith_key
LANGSMITH_PROJECT=Call_Performance_Analysis
```

### 3. Input Data
Place your CSV file at: `input_data/sales_calls_agent_testing_data.csv`

Required columns:
- `username` (LGS agent)
- `transcription` (LGS call)
- `username_omc` (OMC agent)
- `status_name_omc` (Call outcome)
- `length_in_sec_omc` (Call duration)
- `transcription_omc` (OMC call)
- `call_date_omc` (Call date)
- `id` (Row identifier)

## 🎮 Usage

### Run Analysis
```bash
python main.py --run
```

### Start Fresh (Ignore Checkpoint)
```bash
python main.py --run --fresh
```

### Resume from Checkpoint
```bash
python main.py --run --resume
```

## 📄 Output

### Report Location
`reports/call_performance_analysis_report.md`

### Report Sections
1. **Executive Summary** - High-level findings for CEO
2. **Agent-Level Performance** - Individual agent analysis
3. **Call Pattern Analysis** - Short vs long call comparison
4. **LGS vs OMC Analysis** - Handoff quality assessment
5. **Daily Trends** - Performance over time
6. **Status/Outcome Analysis** - Breakdown by call result
7. **Recommendations** - Immediate actions, training needs, process improvements
8. **Real Examples** - Actual call excerpts with quotes

### Converting to Word
The Markdown report can be opened directly in Microsoft Word or converted using:
- Pandoc: `pandoc report.md -o report.docx`
- Online converters
- Word's "Open" dialog (supports .md files)

## 🔧 Configuration

Edit `config/settings.py` to customize:
- Batch size (default: 10)
- Call duration threshold (default: 120 seconds)
- Model name (default: gemini-2.5-flash)
- File paths
- Analysis focus areas

## 📝 Logging

Logs are saved to `logs/` directory:
- `call_analysis_YYYYMMDD_HHMMSS.log` - All activities
- `call_analysis_errors_YYYYMMDD_HHMMSS.log` - Errors only

## 🎯 Key Insights Provided

- **Why short calls fail**: Specific reasons and patterns
- **What makes long calls succeed**: Techniques and approaches
- **Agent performance**: Who's excelling and who needs support
- **LGS issues**: Problems originating from lead generation
- **OMC issues**: Problems in the closing process
- **Training needs**: Specific skills to develop
- **Process improvements**: Systemic changes needed
- **Real examples**: Actual quotes and scenarios for training

## 🔄 Workflow Details

### Batch Processing
- Processes 10 rows at a time
- **Parallel execution**: All 10 calls analyzed simultaneously using ThreadPoolExecutor
- Saves checkpoint after each batch
- Can resume if interrupted
- Accumulates insights across all batches

### State Management
- Maintains all insights in LangGraph state
- Aggregates metrics by agent, date, status
- Collects patterns and examples
- Tracks errors and retries

### Report Generation
- Uses accumulated insights from all batches
- LLM generates comprehensive narrative
- Includes tables, statistics, examples
- Professional format for executive review

## 🚨 Troubleshooting

### Missing Columns
Check that input CSV has all required columns listed above.

### API Errors
Verify `GEMINI_API_KEY` is set correctly in `.env` file.

### Memory Issues
Reduce `BATCH_SIZE` in `config/settings.py` if encountering memory problems.

### Checkpoint Issues
Delete `output_data/analysis_checkpoint.json` to start fresh.

## 📚 Technical Stack

- **LangChain**: Prompt management and LLM orchestration
- **LangGraph**: Agentic workflow and state management
- **Pydantic**: Structured output and data validation
- **Gemini 2.5 Flash**: LLM for analysis and report generation
- **LangSmith**: Tracing and monitoring
- **Pandas**: Data processing and manipulation

## 🎓 Business Value

This agent provides:
1. **Data-Driven Insights**: Objective analysis of call performance
2. **Scalable Analysis**: Processes hundreds of calls efficiently
3. **Actionable Recommendations**: Specific steps to improve
4. **Training Material**: Real examples for coaching
5. **Executive Visibility**: Clear reporting for leadership
6. **Continuous Improvement**: Identifies patterns for optimization

---

**Developed for 411 Locals - Improving Call Performance Through AI-Powered Analysis**

