# 🔧 Troubleshooting Guide

## Common Issues & Solutions

### 1. SSL Certificate Errors (Extension Download)

**Symptoms**:
```
⚠️ Failed to setup uBlock Origin Lite extension: [SSL: CERTIFICATE_VERIFY_FAILED]
⚠️ Failed to setup Force Background Tab extension: [SSL: CERTIFICATE_VERIFY_FAILED]
```

**Cause**: macOS certificate chain issues when downloading browser extensions.

**Solutions**:

**Option 1: Install certificates (Recommended)**
```bash
# Run Python certificate installer
/Applications/Python\ 3.13/Install\ Certificates.command
```

**Option 2: Disable extension downloads**
```python
# In agents/browser_use_agent.py
browser = Browser(
    headless=False,
    disable_security=True,  # Skip extension downloads
    window_size={'width': 1920, 'height': 1080}
)
```

**Option 3: Update certifi**
```bash
pip install --upgrade certifi
python -m certifi
```

**Impact**: ⚠️ Non-blocking - Agent works without extensions, just without ad-blocking.

---

### 2. Agent Result Validation Failures

**Symptoms**:
```
❌ Result failed 1/6 times: items
❌ Result failed 2/6 times: items
...
❌ Stopping due to 5 consecutive failures
```

**Cause**: LLM returning unexpected JSON structure or missing required fields.

**Solutions**:

**Option 1: Use simpler tasks**
```python
# Instead of multi-step tasks
task = """
Test the example website:
1. Navigate to https://example.com
2. Verify page title and content
3. Check page accessibility
"""

# Use single-action tasks
task = "Navigate to https://example.com"
```

**Option 2: Increase max retries**
```python
# In .env
BROWSER_USE_MAX_STEPS=100  # Increase from 50
```

**Option 3: Use vision mode**
```python
# Ensure vision is enabled
agent = Agent(
    task=task,
    llm=self.llm,
    browser=browser,
    use_vision=True  # Let AI see the page
)
```

**Option 4: Upgrade LLM model**
```python
# In .env
BROWSER_USE_MODEL=gpt-4o  # Upgrade from gpt-4o-mini
```

---

### 3. Video Recording Dependency Missing

**Symptoms**:
```
ERROR [video_recorder] MP4 recording requires optional dependencies
WARNING [BrowserSession] Skipping video recording
```

**Cause**: Optional video dependencies not installed.

**Solutions**:

**Option 1: Install video dependencies**
```bash
pip install "browser-use[video]"
```

**Option 2: Disable recording**
```python
# In .env
BROWSER_USE_ENABLE_RECORDING=0
```

**Impact**: ⚠️ Non-critical - Test execution works without recording.

---

### 4. Browser Not Launching

**Symptoms**:
```
Browser not found
Playwright not installed
```

**Solutions**:

**Step 1: Install Playwright browsers**
```bash
playwright install chromium
# Or install all dependencies
playwright install --with-deps chromium
```

**Step 2: Verify installation**
```bash
python -c "from playwright.sync_api import sync_playwright; sync_playwright().start().chromium.launch()"
```

**Step 3: Check browser paths**
```bash
which chromium
ls ~/.cache/ms-playwright/
```

---

### 5. LLM API Errors

**Symptoms**:
```
OpenAI API error
Authentication failed
Rate limit exceeded
```

**Solutions**:

**Option 1: Verify API key**
```bash
# Test OpenAI connection
python -c "from openai import OpenAI; print(OpenAI().models.list())"
```

**Option 2: Check rate limits**
```bash
# View OpenAI usage
curl https://api.openai.com/v1/usage \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

**Option 3: Switch LLM provider**
```python
# In .env
BROWSER_USE_LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=your-key
BROWSER_USE_MODEL=claude-sonnet-4
```

**Option 4: Add retry logic**
```python
# Already implemented in BrowserUseAgent
max_retries = 3
for attempt in range(max_retries):
    try:
        result = await agent.run()
        break
    except Exception as e:
        if attempt < max_retries - 1:
            time.sleep(2 ** attempt)
```

---

### 6. Import Errors

**Symptoms**:
```
ModuleNotFoundError: No module named 'browser_use'
ImportError: cannot import name 'Browser'
```

**Solutions**:

**Step 1: Reinstall browser-use**
```bash
pip uninstall browser-use -y
pip install browser-use==0.12.7
```

**Step 2: Verify installation**
```bash
pip show browser-use
python -c "from browser_use import Agent, Browser; print('✅ Import successful')"
```

**Step 3: Check Python version**
```bash
python --version  # Should be 3.11 or 3.13
```

---

### 7. Database Connection Errors

**Symptoms**:
```
SQLAlchemy connection failed
Database not found
```

**Solutions**:

**Option 1: Verify connection string**
```python
# Test database connection
from sqlalchemy import create_engine
engine = create_engine('sqlite:///test.db')
with engine.connect() as conn:
    result = conn.execute("SELECT 1")
    print(result.fetchone())
```

**Option 2: Check permissions**
```bash
# Verify file permissions
ls -l test.db
chmod 644 test.db
```

---

### 8. Allure Report Not Generating

**Symptoms**:
```
allure: command not found
Allure report failed
```

**Solutions**:

**Step 1: Install Allure**
```bash
# macOS
brew install allure

# Linux
sudo apt-add-repository ppa:qameta/allure
sudo apt-get update
sudo apt-get install allure
```

**Step 2: Install pytest-allure**
```bash
pip install allure-pytest
```

**Step 3: Run tests with Allure**
```bash
pytest --alluredir=allure-results
allure generate allure-results -o allure-report --clean
allure open allure-report
```

---

### 9. Streamlit App Not Loading

**Symptoms**:
```
Streamlit not found
Port already in use
```

**Solutions**:

**Option 1: Install Streamlit**
```bash
pip install streamlit
```

**Option 2: Use different port**
```bash
streamlit run streamlit_app.py --server.port=8502
```

**Option 3: Kill existing process**
```bash
lsof -ti:8501 | xargs kill -9
```

---

### 10. Performance Issues

**Symptoms**:
- Slow browser automation
- High memory usage
- Timeouts

**Solutions**:

**Option 1: Enable headless mode**
```python
# In .env
BROWSER_USE_HEADLESS=1
```

**Option 2: Reduce max steps**
```python
# In .env
BROWSER_USE_MAX_STEPS=30
```

**Option 3: Increase timeout**
```python
# In .env
BROWSER_USE_TIMEOUT=900  # 15 minutes
```

**Option 4: Close browser between tests**
```python
# In test code
browser.close()
```

---

## Diagnostic Commands

### System Health Check

```bash
# Check Python environment
python --version
pip list | grep -E "browser-use|playwright|openai|langchain"

# Check Playwright installation
playwright --version
ls ~/.cache/ms-playwright/chromium-*/chrome-mac/Chromium.app

# Check OpenAI connection
python -c "from openai import OpenAI; OpenAI().models.list()"

# Check browser-use import
python -c "from browser_use import Agent, Browser; print('✅ OK')"
```

### Environment Validation

```bash
# Verify .env file
cat .env | grep -v "^#" | grep -v "^$"

# Test environment variables
python -c "import os; print('OPENAI_API_KEY:', os.getenv('OPENAI_API_KEY')[:10] + '...')"
```

### Browser Debugging

```bash
# Launch browser manually
python -c "
from browser_use import Browser
browser = Browser(headless=False)
browser.launch()
input('Press Enter to close...')
browser.close()
"
```

### Log Analysis

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
python orchestrator_agent.py 2>&1 | tee debug.log

# Search for errors
grep -i "error\|failed\|exception" debug.log

# Count warnings
grep -c "WARNING" debug.log
```

---

## Quick Fixes by Error Message

| Error Message | Quick Fix |
|--------------|-----------|
| `SSL: CERTIFICATE_VERIFY_FAILED` | Run `/Applications/Python\ 3.13/Install\ Certificates.command` |
| `ModuleNotFoundError: browser_use` | `pip install browser-use==0.12.7` |
| `playwright: command not found` | `pip install playwright && playwright install` |
| `OpenAI API error` | Check `OPENAI_API_KEY` in .env |
| `Result failed N/6 times` | Use simpler tasks or upgrade to gpt-4o |
| `Browser not found` | `playwright install chromium --with-deps` |
| `Port 8501 already in use` | `lsof -ti:8501 \| xargs kill -9` |
| `allure: command not found` | `brew install allure` (macOS) |
| `Video recording failed` | `pip install "browser-use[video]"` or disable recording |
| `Loop detection` | Task too complex, break into smaller steps |

---

## Best Practices

### 1. Task Design

✅ **Good Tasks**:
```python
"Navigate to https://example.com"
"Click the login button"
"Fill email field with test@example.com"
```

❌ **Complex Tasks** (may fail):
```python
"Navigate to the site, login with credentials, upload a file, 
verify the upload, then logout and check email confirmation"
```

### 2. Error Handling

```python
try:
    result = orchestrator.run_tests(task)
except Exception as e:
    logger.error(f"Test failed: {e}")
    # Fallback or retry logic
```

### 3. Resource Cleanup

```python
# Always close browsers
try:
    result = agent.run_task(task)
finally:
    agent.close_browser()
```

### 4. Environment Separation

```bash
# Development
export BROWSER_USE_HEADLESS=0
export BROWSER_USE_ENABLE_RECORDING=1

# Production/CI
export BROWSER_USE_HEADLESS=1
export BROWSER_USE_ENABLE_RECORDING=0
```

---

## Getting Help

1. **Check Logs**: Enable DEBUG logging first
2. **Search Issues**: https://github.com/browser-use/browser-use/issues
3. **Update Dependencies**: `pip install --upgrade browser-use`
4. **Simplify Task**: Break complex tasks into smaller steps
5. **Try Different LLM**: Switch to GPT-4o or Claude Sonnet

---

## Known Limitations

- ⚠️ Complex multi-step tasks may fail (use simpler tasks)
- ⚠️ SSL certificate warnings on macOS (run certificate installer)
- ⚠️ Vision mode requires good screenshots (ensure proper resolution)
- ⚠️ Rate limits on OpenAI API (implement backoff)
- ⚠️ Browser extensions download may fail (non-critical)

---

**Last Updated**: January 2025  
**Browser-Use Version**: 0.12.7  
**Status**: Actively Maintained ✅
