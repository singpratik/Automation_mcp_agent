# 🤖 Automatic Interview Audio Responses - User Guide

## ✅ What's New?

Your Streamlit agent now **automatically detects interview scenarios** and **pre-generates audio responses** before running automation!

---

## 🎯 How It Works

```
User types interview prompt
         ↓
Streamlit detects keywords ("interview", "calibration", etc.)
         ↓
GPT-5.1 predicts likely questions (3-5 questions)
         ↓
OpenAI TTS generates audio for each question
         ↓
Shows Chrome launch instructions
         ↓
User launches Chrome with audio
         ↓
Automation runs with audio responses!
```

---

## 🚀 Usage (Step-by-Step)

### Step 1: Open Streamlit
```bash
cd Automation_mcp_agent
./start_streamlit.sh
```

Open: http://localhost:8501

### Step 2: Enter Interview Automation Prompt

Type any prompt containing interview keywords:
- "interview"
- "calibration"
- "elevator pitch"
- "mock interview"
- "question"
- "tell me about"

**Example prompts:**
```
Navigate to VMock and start the elevator pitch interview, 
complete the calibration, and answer the questions
```

```
Go to the mock interview page, login, and complete the interview
answering all questions
```

### Step 3: Audio Auto-Generation

Streamlit will:
1. 🎤 Detect it's an interview
2. 💭 Ask GPT-5.1 what questions might be asked
3. 🎵 Generate 3-5 audio responses automatically
4. 📁 Save to `generated_audio/interview_q1.mp3`, `interview_q2.mp3`, etc.
5. 🔊 Show audio player to preview responses

**You'll see:**
```
🎤 Interview detected! Preparing audio responses...
🎯 Generating audio for 3 predicted questions...

📝 Q1: Tell me about yourself
✅ Audio 1 generated (1024 KB)

📝 Q2: What are your key strengths?
✅ Audio 2 generated (896 KB)

📝 Q3: Why do you want this job?
✅ Audio 3 generated (912 KB)

🎤 Audio Responses Ready!

To use these audio responses:
1. Stop current Chrome
2. Launch Chrome with audio
3. Continue automation
```

### Step 4: Launch Chrome with Audio

**Option A: Using Helper Script (Recommended)**
```bash
# Open new terminal
cd Automation_mcp_agent
./launch_chrome_with_audio.sh generated_audio/interview_q1.mp3
```

**Option B: Manual Launch**
```bash
pkill -f 'remote-debugging-port=9222'

/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --use-fake-ui-for-media-stream \
  --use-fake-device-for-media-stream \
  --use-file-for-fake-audio-capture="/full/path/to/interview_q1.mp3" \
  --remote-debugging-port=9222 \
  --user-data-dir=/tmp/chrome-auto-allow &
```

### Step 5: Continue Automation

Return to Streamlit and click **Continue** or re-enter your prompt.

The browser automation will run and Chrome will use the generated audio as microphone input!

---

## 🎨 UI Features

### Sidebar Chrome Status

Streamlit sidebar now shows:
- ✅ **Chrome running with audio** (green) - Audio configured
- ℹ️ **Chrome: No audio configured** (blue) - No audio setup

### Audio Preview

When audio is generated, you can:
- 🔊 **Play audio** directly in Streamlit
- 📝 **See generated questions**  
- 📊 **View file sizes**
- 🔗 **Get Chrome launch commands**

---

## 📋 Example Workflow

**Complete automation with audio:**

1. **Open Streamlit**: http://localhost:8501

2. **Type prompt**:
   ```
   Navigate to https://dashboard-uat-us.vmock.dev/elevator-pitch, 
   login with email pratik_singh@mailidrop.cc and password Welcome@123, 
   start the interview, complete calibration, and answer all questions
   ```

3. **Wait for audio generation** (15-30 seconds):
   - Streamlit automatically generates 3-5 audio responses
   - Shows preview and download options

4. **Launch Chrome** (new terminal):
   ```bash
   cd Automation_mcp_agent
   ./launch_chrome_with_audio.sh generated_audio/interview_q1.mp3
   ```

5. **Continue automation** in Streamlit

6. **Chrome uses generated audio** as microphone input

7. **VMock records your answers**!

---

## ⚙️ Configuration

### Enable/Disable Auto-TTS

Edit `.env`:
```dotenv
# Disable automatic TTS
ENABLE_TTS_RESPONSES=false

# Enable automatic TTS (default)
ENABLE_TTS_RESPONSES=true
```

### Customize Voice

```dotenv
# Change voice (alloy, echo, fable, onyx, nova, shimmer)
OPENAI_TTS_VOICE=nova

# Change quality (tts-1 or tts-1-hd)
OPENAI_TTS_MODEL=tts-1-hd

# Change speed (0.25 to 4.0)
OPENAI_TTS_SPEED=1.1  # Slightly faster
```

### Keywords for Detection

Streamlit detects these keywords:
- interview
- question  
- calibration
- elevator pitch
- mock interview
- tell me about

Add more in `streamlit_app.py`:
```python
interview_keywords = ["interview", "calibration", "your", "custom", "keywords"]
```

---

## 🎯 Advanced Features

### Multiple Audio Files

If multiple questions detected, Streamlit generates multiple audio files:
```
generated_audio/interview_q1.mp3
generated_audio/interview_q2.mp3
generated_audio/interview_q3.mp3
generated_audio/interview_q4.mp3
generated_audio/interview_q5.mp3
```

To cycle through them:
1. Start with `interview_q1.mp3`
2. When first question done, restart Chrome with `interview_q2.mp3`
3. Continue for remaining questions

**Future Enhancement**: Auto-switch audio files during interview

### GPT-5.1 Question Prediction

GPT-5.1 analyzes your prompt and predicts questions like:
- "Tell me about yourself"
- "What are your strengths?"
- "Why do you want this job?"
- "Describe a challenge you faced"
- "Where do you see yourself in 5 years?"

These are generated based on:
- Your prompt content
- Common interview patterns
- The automation task context

---

## 🐛 Troubleshooting

### "No audio generated"
- Check: `ENABLE_TTS_RESPONSES=true` in `.env`
- Check: `OPENAI_API_KEY` is valid
- Check logs: Look for TTS errors in Streamlit

### "Chrome not using audio"
- Verify: Chrome launched with `--use-file-for-fake-audio-capture`
- Check: `ps aux | grep use-file-for-fake-audio`
- Verify: Audio file path is absolute path

### "Questions don't match interview"
- GPT-5.1 predictions are generic
- Manually edit questions in `test_tts_answer.py`
- Re-generate audio with specific questions

### "Audio too fast/slow"
- Edit `.env`: `OPENAI_TTS_SPEED=0.9` (slower) or `1.2` (faster)
- Restart Streamlit
- Re-generate audio

---

## 💡 Tips

1. **Preview audio first** - Use Streamlit player to hear responses before using

2. **Customize answers** - Edit `utils/tts_generator.py` system prompt for better answers

3. **Generate upfront** - Run `python test_tts_answer.py` before automation for specific questions

4. **Use tts-1** for speed - Use `tts-1-hd` only if quality is critical

5. **Monitor Chrome status** - Check sidebar for "Chrome running with audio" indicator

---

## 📊 Cost

**Automatic generation** (per interview):
- GPT-5.1 question prediction: ~$0.003 (100 tokens)
- TTS generation (5 questions): ~$0.045 (3000 characters)
- **Total**: ~**$0.05 per interview** (~5 cents)

---

## 🎉 Success Indicators

You know it's working when you see:

1. **In Streamlit**:
   - ✅ "Audio 1 generated"
   - 🔊 Audio player appears
   - 📁 Files in `generated_audio/`

2. **In Chrome**:
   - ✅ No microphone permission popup
   - 🎤 VMock detects audio input
   - 🔴 Recording indicator shows

3. **In VMock**:
   - ✅ Interview progresses
   - 📹 Video + audio recorded
   - ✅ Interview completes successfully

---

## 🔗 Quick Reference

**Streamlit**: http://localhost:8501
**Generated Audio**: `./generated_audio/`
**Chrome Launcher**: `./launch_chrome_with_audio.sh`
**Test TTS**: `python test_tts_answer.py`
**Configuration**: `.env`

---

## 🚀 Next Steps

Try it out:
1. Open Streamlit
2. Type: `start vmock interview and answer the questions`
3. Wait for audio generation
4. Launch Chrome with audio
5. Watch automation run!

Enjoy your automated interview responses! 🎤✨
