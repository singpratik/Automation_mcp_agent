# 🚀 Quick Start Guide

## Problem: Getting pydantic/chromadb errors?

**Root Cause**: You're running **system Streamlit** (Homebrew Python) instead of **virtual environment Streamlit**.

---

## ✅ SOLUTION: Use one of these methods

### Method 1: Use the Helper Script (EASIEST)
```bash
cd /Users/pratiksingh/Desktop/Interview_automation/Automation_mcp_agent
./start_streamlit.sh
```

### Method 2: Activate venv first, then run
```bash
cd /Users/pratiksingh/Desktop/Interview_automation
source .venv/bin/activate
cd Automation_mcp_agent
streamlit run streamlit_app.py
```

### Method 3: Use full path to venv streamlit
```bash
cd /Users/pratiksingh/Desktop/Interview_automation/Automation_mcp_agent
/Users/pratiksingh/Desktop/Interview_automation/.venv/bin/python -m streamlit run streamlit_app.py
```

---

## ❌ DON'T DO THIS:
```bash
# This uses system Python and will fail!
streamlit run streamlit_app.py  # ❌ WRONG
```

---

## 🎯 Current Status

**Streamlit is ALREADY RUNNING on http://localhost:8503** ✅

Just open your browser to that URL!

---

## 📊 Verify Which Streamlit You're Using

To check which streamlit you're running:
```bash
which streamlit
```

Should show:
✅ `/Users/pratiksingh/Desktop/Interview_automation/.venv/bin/streamlit` (CORRECT)

NOT:
❌ `/opt/homebrew/bin/streamlit` (WRONG - system Python)

---

## 🔥 If You See the Error Again

1. Press `Ctrl+C` to stop the wrong Streamlit
2. Run: `./start_streamlit.sh` or use Method 2/3 above
3. Open: http://localhost:8503 (or whatever port it shows)
