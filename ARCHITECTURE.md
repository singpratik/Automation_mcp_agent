# 🏗️ System Architecture - Agentic AI for Software QA

## Overview

This document describes the complete architecture of the Agentic AI System for Software QA, matching the design in the provided architecture diagram.

## Architecture Diagram

```
┌───────────────────────────────────────────────────────────────┐
│                                                                 │
│              ORCHESTRATOR AGENT (BRAIN)                        │
│                                                                 │
│  • Decides test types (UI, API, DB)                           │
│  • Delegates to agents                                         │
│  • Collates results                                            │
│                                                                 │
└─────────────┬──────────────┬──────────────┬──────────────────┘
              │              │              │
     ┌────────▼────┐  ┌──────▼──────┐  ┌───▼───────┐
     │             │  │             │  │           │
     │  UI AGENT   │  │  API AGENT  │  │  DB AGENT │
     │             │  │             │  │           │
     │ browser-use │  │  Requests   │  │SQLAlchemy │
     │   (AI)      │  │   Pytest    │  │   Great   │
     │             │  │Schemathesis │  │Expectations│
     │ - DOM       │  │             │  │           │
     │   validation│  │ - Functional│  │ - Schema  │
     │ - Visual    │  │   tests     │  │   checks  │
     │   checks    │  │ - Contract  │  │ - Data    │
     │             │  │   tests     │  │   checks  │
     │             │  │ - Dynamic   │  │ - Post-   │
     │             │  │   test gen  │  │   test    │
     │             │  │             │  │   valid   │
     └──────┬──────┘  └──────┬──────┘  └─────┬─────┘
            │                │                │
            └────────────────┼────────────────┘
                             │
                ┌────────────▼────────────┐
                │                         │
                │   CI/CD PIPELINE        │
                │                         │
                │  • Jenkins              │
                │  • GitHub Actions       │
                │  • Trigger tests        │
                │  • Artifact deploy      │
                │                         │
                └────────────┬────────────┘
                             │
                ┌────────────▼────────────┐
                │                         │
                │  REPORTING & INSIGHTS   │
                │                         │
                │  • Allure               │
                │  • Slack/Jira           │
                │  • Unified reports      │
                │  • Alerts & dashboards  │
                │                         │
                └─────────────────────────┘
```

## Component Breakdown

### 1. Orchestrator Agent (Brain)

**File**: `orchestrator_agent.py`

**Responsibilities**:
- Parse natural language test requirements
- Classify test types (UI, API, DB)
- Delegate to appropriate specialized agents
- Aggregate results from all agents
- Generate unified reports

**Key Methods**:
```python
class OrchestratorAgent:
    def decide_test_types(task: str) -> TestPlan
    def execute_test_plan(test_plan: TestPlan) -> Dict[str, Any]
    def run_tests(task: str) -> Dict[str, Any]
    def generate_report(format: str = 'html') -> str
```

**Test Classification Logic**:
- **UI Tests**: Keywords like `browse`, `click`, `navigate`, `login`, `page`
- **API Tests**: Keywords like `api`, `endpoint`, `request`, `post`, `get`
- **DB Tests**: Keywords like `database`, `query`, `sql`, `table`, `schema`

### 2. UI Agent (browser-use AI)

**File**: `agents/browser_use_agent.py`

**Technology Stack**:
- browser-use v0.12.7 (AI-powered browser automation)
- LangChain (LLM orchestration)
- OpenAI GPT-4o-mini / Anthropic Claude / Google Gemini
- Playwright (browser control)

**Features**:
- ✅ **Natural Language Commands**: "Login with email X and password Y"
- ✅ **Vision-Based Interaction**: AI sees and interacts with UI
- ✅ **DOM Validation**: Comprehensive page structure checks
- ✅ **Visual Testing**: Screenshot comparison
- ✅ **Automatic Retry**: Smart error recovery

**Key Configuration**:
```python
@dataclass
class BrowserUseConfig:
    llm_provider: str = "openai"
    model_name: str = "gpt-4o-mini"
    max_steps: int = 100
    headless: bool = False
    enable_recording: bool = True
```

**Supported LLMs**:
- OpenAI (gpt-4o-mini, gpt-4o)
- Anthropic (claude-sonnet-4-6)
- Google (gemini-3-flash-preview)
- Ollama (local models)
- DeepSeek (deepseek-chat)

### 3. API Agent

**File**: `agents/api_agent.py`

**Technology Stack**:
- Requests (HTTP client)
- Pytest (test framework)
- Schemathesis (API contract testing)

**Features**:
- ✅ **Functional Testing**: REST API validation
- ✅ **Contract Testing**: OpenAPI/Swagger schema validation
- ✅ **Dynamic Test Generation**: AI-powered test case creation
- ✅ **Response Validation**: JSON, status codes, headers

**Test Types**:
1. **Functional Tests**: Endpoint behavior validation
2. **Contract Tests**: Schema compliance (Schemathesis)
3. **Negative Tests**: Error handling validation
4. **Property-Based Tests**: Hypothesis integration

### 4. DB Agent

**File**: `agents/sql_agent.py`

**Technology Stack**:
- SQLAlchemy (database ORM)
- Great Expectations (data quality)

**Features**:
- ✅ **Schema Validation**: Table structure verification
- ✅ **Data Quality Checks**: Great Expectations suites
- ✅ **Post-Test Validation**: Database state verification
- ✅ **Query Testing**: SQL injection prevention

**Validation Types**:
1. **Schema Checks**: Column types, constraints
2. **Data Integrity**: Foreign keys, referential integrity
3. **Query Performance**: Execution time monitoring
4. **State Validation**: Pre/post-test data consistency

### 5. CI/CD Pipeline Integration

**Supported Systems**:
- GitHub Actions
- Jenkins
- GitLab CI
- CircleCI

**GitHub Actions Example**:
```yaml
name: Agentic QA Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run Tests
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        run: python orchestrator_agent.py
```

**Jenkins Pipeline Example**:
```groovy
pipeline {
    agent any
    stages {
        stage('QA Tests') {
            steps {
                sh 'python orchestrator_agent.py'
            }
        }
    }
}
```

### 6. Reporting & Insights

**File**: `reporting.py`

**Report Types**:
1. **Allure Reports**: Rich, interactive HTML reports
2. **JSON Reports**: Machine-readable results
3. **HTML Reports**: Unified visual reports
4. **Slack Notifications**: Real-time alerts
5. **Jira Integration**: Automatic ticket creation

**Report Features**:
- ✅ **Unified Dashboard**: All test results in one view
- ✅ **Trend Analysis**: Historical data tracking
- ✅ **Failure Analysis**: Root cause identification
- ✅ **Screenshots**: Visual evidence of failures
- ✅ **Logs**: Detailed execution traces

## Data Flow

### Test Execution Flow

```
1. User Input (Natural Language)
        ↓
2. Orchestrator Receives Task
        ↓
3. Task Classification
   - Parse keywords
   - Identify test types
   - Create TestPlan
        ↓
4. Agent Delegation
   ├─→ UI Agent (if UI keywords)
   ├─→ API Agent (if API keywords)
   └─→ DB Agent (if DB keywords)
        ↓
5. Parallel Execution
   - Each agent runs independently
   - Results collected asynchronously
        ↓
6. Result Aggregation
   - Combine all agent results
   - Calculate summary stats
        ↓
7. Report Generation
   - Allure report
   - HTML/JSON reports
   - Slack/Jira notifications
        ↓
8. Return to User
```

### Result Structure

```python
{
    'ui': [
        {
            'test': 'Login test',
            'result': {...},
            'status': 'passed'
        }
    ],
    'api': [...],
    'db': [...],
    'summary': {
        'total_tests': 10,
        'passed': 8,
        'failed': 2,
        'skipped': 0
    }
}
```

## Configuration

### Environment Variables (.env)

```bash
# LLM Configuration
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key
GOOGLE_API_KEY=your-google-key

# Browser-Use Settings
BROWSER_USE_MODEL=gpt-4o-mini
BROWSER_USE_LLM_PROVIDER=openai
BROWSER_USE_MAX_STEPS=50
BROWSER_USE_TIMEOUT=600
BROWSER_USE_HEADLESS=0
BROWSER_USE_ENABLE_RECORDING=1

# Reporting
SLACK_WEBHOOK_URL=your-slack-webhook
JIRA_API_TOKEN=your-jira-token
JIRA_PROJECT_KEY=QA
```

## Deployment Scenarios

### 1. Local Development
```bash
python orchestrator_agent.py
```

### 2. CI/CD Pipeline
```bash
# Triggered on git push
python orchestrator_agent.py --env=staging
```

### 3. Scheduled Testing
```bash
# Cron job for nightly tests
0 2 * * * python orchestrator_agent.py --env=production
```

### 4. On-Demand Testing
```bash
# Manual trigger via API
curl -X POST http://qa-server/run-tests -d '{"task": "..."}'
```

## Performance Characteristics

- **Test Classification**: <1 second
- **UI Agent (browser-use)**: 2-5 seconds per action
- **API Agent**: <1 second per request
- **DB Agent**: <1 second per query
- **Report Generation**: <2 seconds

## Scalability

- **Parallel Agent Execution**: All agents run concurrently
- **Multiple Browser Sessions**: Support for parallel UI tests
- **API Rate Limiting**: Built-in retry logic
- **Database Connection Pooling**: Efficient resource usage

## Security Considerations

1. **API Keys**: Stored in environment variables only
2. **Database Credentials**: Never logged or exposed
3. **Browser Security**: Sandboxed execution
4. **Report Sanitization**: Sensitive data redaction

## Extensibility

### Adding New Agents

```python
from orchestrator_agent import OrchestratorAgent

class CustomAgent:
    def run_tests(self, test_list):
        # Custom test logic
        pass

# Extend orchestrator
orchestrator = OrchestratorAgent()
orchestrator.custom_agent = CustomAgent()
```

### Custom Report Formats

```python
# Add new report format
def generate_pdf_report(results):
    # PDF generation logic
    pass

orchestrator.reporting.add_format('pdf', generate_pdf_report)
```

## Maintenance

### Updating browser-use
```bash
pip install --upgrade browser-use
playwright install chromium
```

### Updating LLM Models
```python
# In .env
BROWSER_USE_MODEL=gpt-4o  # Upgrade to GPT-4o
```

### Log Rotation
```bash
# Configure in logging_config.py
ROTATING_FILE_HANDLER_MAX_BYTES = 10485760  # 10MB
ROTATING_FILE_HANDLER_BACKUP_COUNT = 5
```

## Troubleshooting

### Common Issues

1. **Browser not launching**
   ```bash
   playwright install --with-deps chromium
   ```

2. **LLM API errors**
   ```bash
   # Verify API key
   python -c "from openai import OpenAI; OpenAI().models.list()"
   ```

3. **Import errors**
   ```bash
   pip install --force-reinstall browser-use
   ```

## Future Enhancements

- [ ] Multi-browser support (Firefox, Safari)
- [ ] Visual regression testing
- [ ] Accessibility testing (WCAG compliance)
- [ ] Performance testing integration
- [ ] Mobile testing support
- [ ] Real-time collaboration features

## Conclusion

This architecture provides a comprehensive, AI-powered testing framework that:
- ✅ Automates UI, API, and DB testing
- ✅ Uses natural language for test definition
- ✅ Integrates with existing CI/CD pipelines
- ✅ Generates unified, actionable reports
- ✅ Scales for enterprise use cases

---

**Last Updated**: May 19, 2026  
**Version**: 1.0.0  
**Status**: Production Ready ✅
