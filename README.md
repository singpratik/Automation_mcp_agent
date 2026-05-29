# 🤖 Agentic AI System for Software QA

> **Full Architecture with Browser-Use AI Integration**

A comprehensive, AI-powered testing framework that orchestrates UI, API, and Database testing through specialized agents - exactly as shown in the architecture diagram.

> **Single source of truth:** This `README.md` is the **main guide** for installing, running, and using the QA MCP agent. You can safely treat it as the only document you need for day‑to‑day work. Other `.md` files in this repo are either deeper technical references or historical notes and can be ignored unless you are debugging internals.

## 🏗️ Architecture

```
┌───────────────────────────────────────────────┐
│      Orchestrator Agent (Brain)               │
│      • Decides test types (UI/API/DB)         │
│      • Delegates to specialized agents        │
│      • Collates results                       │
└──────────────────┬────────────────────────────┘
                   │
        ┌──────────┼──────────┐
        │          │          │
    ┌───▼───┐  ┌──▼────┐  ┌──▼────┐
    │UI Agt │  │API Agt│  │DB Agt │
    │browser│  │Request│  │SQLAlch│
    │-use AI│  │Pytest │  │emy    │
    │       │  │Schemat│  │Great  │
    │Vision │  │hesis  │  │Expect │
    └───────┘  └───┬───┘  └───┬───┘
                   │          │
            ┌──────┴──────────┴──────┐
            │                        │
      ┌─────▼──────┐      ┌─────────▼────────┐
      │  CI/CD     │      │  Reporting &     │
      │  Pipeline  │      │  Insights        │
      │  •Jenkins  │      │  •Allure         │
      │  •GitHub   │      │  •Slack/Jira     │
      │  Actions   │      │  •Unified Rpts   │
      └────────────┘      └──────────────────┘
```

## ✨ Key Features

### 🧠 Orchestrator Agent (Brain)
- ✅ Intelligent test type detection (UI/API/DB)
- ✅ Automatic agent delegation
- ✅ Unified result aggregation
- ✅ CI/CD pipeline ready

### 🌐 UI Agent (browser-use AI)
- ✅ Natural language automation
- ✅ Vision-based element detection  
- ✅ DOM validation
- ✅ Multi-LLM support (OpenAI, Anthropic, Google, Ollama)
- ✅ **Uses Chrome** (not Chromium) via Playwright

### 🔌 API Agent
- ✅ Functional testing (Requests)
- ✅ Contract testing (Pytest, Schemathesis)
- ✅ Dynamic test generation

### 🗄️ DB Agent
- ✅ Schema validation (SQLAlchemy)
- ✅ Data quality checks (Great Expectations)
- ✅ Post-test validation

### 📊 Reporting & Insights
- ✅ Allure reports
- ✅ Slack/Jira integration
- ✅ Unified dashboards
- ✅ Alerts & notifications

## 🚀 Quick Start (QA MCP Agent + Interview TTS)

```bash
# 1. Activate the Python 3.12 environment used by the QA MCP agent
source /Users/pratiksingh/Desktop/Interview_automation/.venv312/bin/activate

# 2. Go to the Automation_mcp_agent project
cd /Users/pratiksingh/Desktop/Interview_automation/Automation_mcp_agent

# 3. (Recommended) Start Streamlit via the canonical script
./start_streamlit_py312.sh
# Streamlit UI: http://localhost:8501

# 4. (Optional) Launch Chrome with fake audio for interview answers
#    If you already have a TTS audio file (e.g. generated_audio/live_response.wav)
./launch_chrome_with_audio.sh generated_audio/live_response.wav

# 5. (Optional) Run the end‑to‑end TTS/interview test suite
pytest -q  # runs test_agent_tts.py, test_realtime_tts.py, test_tts_module.py, etc.
```

In practice, as a QA engineer you typically only need:

- `./start_streamlit_py312.sh` – start the full QA MCP + Streamlit UI on Python 3.12.
- `./launch_chrome_with_audio.sh <audio_file>` – launch Chrome wired to a TTS audio file for interview flows.

All other shell scripts are either historical or for niche/advanced use; you can ignore them in normal workflows.

## ✨ Recent Updates

### Schema Validation Fix (Latest)
- ✅ **Fixed**: "Result failed N/6 times: items" error
- ✅ **Solution**: Using native browser-use ChatOpenAI instead of LangChain wrapper
- ✅ **Model**: Configured for GPT-5
- ✅ **Status**: All systems operational

### Streamlit UI Fixes
- ✅ Removed obsolete module dependencies
- ✅ Fixed orchestrator integration
- ✅ Proper BrowserUseAgent initialization
- ✅ Ready for production use



## 📖 Usage

```python
from orchestrator_agent import OrchestratorAgent

# Initialize with AI-powered agents
orchestrator = OrchestratorAgent(use_browser_ai=True)

# Natural language task - orchestrator routes automatically
task = """
Test VMock platform:
1. Login with credentials
2. Upload CV via API
3. Verify data in database
"""

# Execute - orchestrator delegates to UI/API/DB agents
results = orchestrator.run_tests(task)

# Generate unified report
orchestrator.generate_report(format='html')
```

## 📁 Project Structure

```
Automation_mcp_agent/
├── orchestrator_agent.py       # 🧠 Brain - Main orchestrator
├── agents/
│   ├── browser_use_agent.py   # 🌐 UI Agent (AI-powered)
│   ├── api_agent.py           # 🔌 API Agent  
│   └── sql_agent.py           # 🗄️ DB Agent
├── reporting.py               # 📊 Unified reporting
├── streamlit_app.py          # 🖥️ Web UI
├── test_vmock_browser_use.py # 🧪 VMock test suite
└── .env                      # ⚙️ Configuration
```

## 🎯 Test Examples

### 1. UI Testing (Natural Language)
```python
task = "Navigate to vmock.com and login with test@example.com"
results = orchestrator.run_tests(task)
```

### 2. API Testing
```python
task = "Test POST /api/interview endpoint with sample data"
results = orchestrator.run_tests(task)
```

### 3. Database Validation
```python
task = "Verify user table schema and check active users count"
results = orchestrator.run_tests(task)
```

### 4. Full Workflow
```python
task = """
Complete E2E test:
1. UI: Login to platform
2. API: Upload CV via endpoint
3. DB: Verify CV data stored
"""
results = orchestrator.run_tests(task)
```

## 🔧 Configuration

### .env File
```bash
# LLM Configuration (Current Setup)
OPENAI_API_KEY=your-key
BROWSER_USE_MODEL=gpt-5              # ✅ Using GPT-5
BROWSER_USE_LLM_PROVIDER=openai

# Browser Settings
BROWSER_USE_HEADLESS=0               # Show browser (1 for headless)
BROWSER_USE_ENABLE_RECORDING=1       # Enable session recording
BROWSER_USE_MAX_STEPS=50            # Max automation steps
BROWSER_USE_TIMEOUT=600              # 10 minute timeout
BROWSER_USE_MAX_FAILURES=8           # Max consecutive failures
```

### LLM Configuration Notes
- **Native browser-use ChatOpenAI**: Better schema validation
- **No LangChain wrapper needed**: Direct integration
- **Supported models**: gpt-5, gpt-4o, gpt-4o-mini, gpt-4-turbo

## 📊 Reports

### Generate Reports
```python
# HTML Report
orchestrator.generate_report(format='html')

# JSON Report  
orchestrator.generate_report(format='json')
```

### Allure Reports
```bash
pytest --alluredir=allure-results
allure generate allure-results -o allure-report
allure open allure-report
```

## 🏭 CI/CD Integration

### GitHub Actions
```yaml
- name: Run Agentic Tests
  env:
    OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
  run: python orchestrator_agent.py
```

### Jenkins
```groovy
stage('QA Tests') {
    steps {
        sh 'python orchestrator_agent.py'
    }
}
```

## ✅ Status

**All Systems Operational** 🟢

- ✅ Orchestrator Agent (Brain) - Working
- ✅ UI Agent (browser-use with native ChatOpenAI) - **Fixed & Working**
- ✅ API Agent - Working
- ✅ DB Agent - Working
- ✅ Reporting System - Working
- ✅ VMock Integration - Working
- ✅ Streamlit UI - **Fixed & Running on :8502**

### Recent Fixes
- ✅ Schema validation "items" error resolved
- ✅ Streamlit architecture cleaned up
- ✅ Native browser-use ChatOpenAI integration
- ✅ All imports and dependencies fixed

## 📚 Documentation

For day‑to‑day QA work, **this `README.md` is the only document you need**. The following additional files are optional deep‑dives:

- `ARCHITECTURE.md` – detailed system design and component breakdown.
- `REALTIME_TTS_GUIDE.md` – in‑depth explanation of the real‑time TTS (Option C, hybrid file‑based) pipeline.
- `TROUBLESHOOTING.md` – comprehensive problem‑solving guide for common browser/LLM/TTS issues.
- `SECURITY.md` – security guidelines and considerations.

If you feel overwhelmed by the number of `.md` files, you can safely ignore everything except **this `README.md`** unless you are debugging a specific issue.

## 🐛 Troubleshooting

```bash
# Reinstall browser
playwright install chromium

# Test LLM connection
python -c "from openai import OpenAI; print('OK')"

# Check browser-use
python -c "from browser_use import Agent; print('OK')"
```

## 🔗 Links

- [browser-use GitHub](https://github.com/browser-use/browser-use)
- [browser-use Web UI](https://github.com/browser-use/web-ui)
- [Documentation](./docs/)

---

**Built with browser-use AI** | **Ready for Production** ✅
