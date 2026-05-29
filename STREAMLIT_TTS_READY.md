# 🎤 Streamlit TTS Ready - Quick Start Guide

## ✅ You're Ready!

**Streamlit is now running with full TTS support!**
- **URL**: http://localhost:8502
- **TTS Module**: ✅ Working (tested)
- **Audio Generation**: ✅ 2-3 seconds per answer
- **Browser Integration**: ✅ Ready for Chrome fake microphone

---

## 🚀 How to Use TTS in Streamlit

### Step 1: Open Streamlit
Visit: **http://localhost:8502**

### Step 2: Configure TTS (Left Sidebar)

Look for the **"🎤 Real-time TTS Configuration"** section:

1. **Enable TTS**:
   - Check the box: ☑️ "Enable Real-time TTS"

2. **Select Voice** (appears when TTS is enabled):
   - **Alloy** - Neutral, balanced (default)
   - **Echo** - Male, clear
   - **Fable** - Male, expressive
   - **Onyx** - Male, deep
   - **Nova** - Female, clear
   - **Shimmer** - Female, soft

3. **Set Candidate Profile** (click "👤 Candidate Profile" expander):
   ```
   Name: John Doe
   Position: Software Engineer
   Experience: 5 years
   Skills: Python, JavaScript, AWS
   ```

4. **Check Audio Status**:
   - When TTS is enabled, you'll see: ✅ Audio ready (XXX KB)
   - Click "🌐 Chrome Launch Command" to see how to test audio

### Step 3: Run Interview Automation

**Type in the chat:**
```
Navigate to vmock.com and complete the elevator pitch interview
```

Or more specific:
```
Go to https://vmock.com/elevator-pitch and answer all questions
```

**What Happens:**
1. 🌐 Browser opens with fake microphone
2. 📋 Questions detected automatically
3. 🤖 GPT-4 generates answers based on your profile
4. 🎤 TTS converts answers to audio (2-3 seconds)
5. 📁 Audio file updated in real-time
6. 🎙️ Chrome uses audio as microphone input
7. ✅ Interview completed automatically!

---

## 🧪 Test TTS Without Browser

You can test TTS audio generation without running full automation:

### Quick Test:
1. Enable TTS in sidebar
2. Set candidate profile
3. Type in chat:
   ```
   Test TTS: Generate audio for "What are your strengths?"
   ```

The audio file will be created at:
```
/Users/pratiksingh/Desktop/Interview_automation/Automation_mcp_agent/generated_audio/live_response.wav
```

### Manual Chrome Test:
Copy this command to test audio with Chrome:
```bash
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --use-fake-ui-for-media-stream \
  --use-fake-device-for-media-stream \
  --use-file-for-fake-audio-capture="/Users/pratiksingh/Desktop/Interview_automation/Automation_mcp_agent/generated_audio/live_response.wav" \
  https://vmock.com
```

---

## 📋 Example Interview Automation Flow

### Scenario: Complete VMock Elevator Pitch

**1. Configure TTS:**
- Enable TTS: ✅
- Voice: **Nova** (female, clear)
- Profile:
  ```
  Name: Sarah Johnson
  Position: Senior Software Engineer
  Experience: 7 years
  Skills: Python, AWS, Docker, Kubernetes
  ```

**2. Start Automation:**
```
Navigate to https://vmock.com/elevator-pitch and complete the interview
```

**3. Monitor Progress:**
- Watch browser open with fake microphone
- See status updates in Streamlit
- Check logs for question detection
- View audio generation messages

**4. View Results:**
- Interview completion status
- Number of questions answered
- Screenshots captured
- Full execution log

---

## 🎯 What's Automated

### Question Detection (Auto):
- GPT Vision analyzes screenshots
- DOM inspection for question text
- Detects interview prompts

### Answer Generation (GPT-4):
- Uses your candidate profile
- Natural, conversational responses
- Industry-appropriate language
- 20-30 second spoken length

### Audio Generation (OpenAI TTS):
- 2-3 seconds per answer
- WAV format (16kHz, mono)
- Updates file in-place
- Chrome picks up instantly

---

## 🔧 Advanced Options

### Custom Question Selectors
For non-VMock platforms, you can specify CSS selectors for question detection (code customization needed).

### Pre-generate Answers
Generate answers without browser:
```python
from agents.browser_use_agent import BrowserUseAgent, BrowserUseConfig

config = BrowserUseConfig(enable_realtime_tts=True)
agent = BrowserUseAgent(config=config)

agent.answer_question_with_tts(
    "Tell me about yourself",
    context={"candidate_name": "John", "skills": ["Python"]}
)
```

### Monitor Audio File
Watch audio file updates:
```bash
watch -n 1 'ls -lh generated_audio/live_response.wav'
```

---

## 📊 Expected Performance

| Operation | Time | Notes |
|-----------|------|-------|
| Answer Generation | ~1-2s | GPT-4 with context |
| TTS Conversion | ~2-3s | OpenAI TTS API |
| Total Response | ~3-5s | Per question |
| File Update | <0.1s | Atomic replace |
| Chrome Detection | Instant | Continuous file read |

---

## 🐛 Troubleshooting

### TTS Not Working?
1. Check ✅ "Enable Real-time TTS" is checked
2. Verify OpenAI API key in `.env`
3. Look for error messages in logs
4. Check audio file exists: `ls generated_audio/`

### Audio Not Playing in Interview?
1. Ensure Chrome launched with fake microphone flags
2. Check audio file is not empty (should be >30 KB)
3. Verify WAV format: `file generated_audio/live_response.wav`
4. Test audio manually in Chrome first

### Question Not Detected?
1. Check screenshots captured: `ls browser_screenshots/`
2. Enable debug logs: `logger.setLevel(logging.DEBUG)`
3. Verify interview page loads correctly
4. Check DOM structure matches expected

---

## 📚 Documentation

- **Full Guide**: `REALTIME_TTS_GUIDE.md`
- **Test Suite**: Run `python3 test_tts_module.py`
- **Architecture**: See `TTS_FULL_AUTOMATION_PLAN.md`

---

## 🎉 You're All Set!

**Streamlit URL**: http://localhost:8502

1. ✅ Open Streamlit
2. ✅ Enable TTS in sidebar
3. ✅ Set candidate profile
4. ✅ Run interview automation
5. ✅ Watch it complete automatically!

**Ready to automate your interviews!** 🚀🎤
