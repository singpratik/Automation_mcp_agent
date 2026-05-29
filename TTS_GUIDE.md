# 🎤 OpenAI TTS Integration - Intelligent Audio Responses

## ✅ What's New?

Your agent can now **generate intelligent spoken answers** to interview questions in real-time!

**How it works:**
1. **GPT-5.1** reads the question on screen: "Please tell me something about yourself"
2. **GPT-5.1** generates intelligent text answer: "I'm a passionate software engineer with 5 years of experience..."
3. **OpenAI TTS** converts text to natural speech (MP3 audio)
4. **Chrome** uses the audio file as fake microphone input
5. **VMock** records the audio as your answer!

---

## 🚀 Quick Start

### Option 1: Automatic (Recommended for Testing)

Test the TTS generation:
```bash
cd Automation_mcp_agent
python test_tts_answer.py
```

This will generate 3 sample audio files and you can hear them!

### Option 2: With Chrome Automation

**Step 1:** Generate an answer for a specific question
```bash
cd Automation_mcp_agent
python -c "
from utils.tts_generator import TTSGenerator
from dotenv import load_dotenv
load_dotenv()

tts = TTSGenerator()
audio = tts.answer_question('Please tell me something about yourself.', 'my_answer.mp3')
print(f'Audio: {audio}')
"
```

**Step 2:** Launch Chrome with the audio file
```bash
./launch_chrome_with_audio.sh generated_audio/my_answer.mp3
```

**Step 3:** Run your automation
```bash
./start_streamlit.sh
```

In Streamlit, use your normal prompt:
```
Navigate to VMock interview, start the interview, and when asked questions, the Chrome will use the pre-generated audio
```

---

## ⚙️ Configuration (.env)

```dotenv
# OpenAI TTS Settings
OPENAI_TTS_MODEL=tts-1          # tts-1 (fast) or tts-1-hd (high quality)
OPENAI_TTS_VOICE=alloy          # alloy, echo, fable, onyx, nova, shimmer
OPENAI_TTS_SPEED=1.0            # 0.25 to 4.0 (1.0 = normal)
ENABLE_TTS_RESPONSES=true       # Enable auto-responses
```

### Voice Options:
- **alloy** - Neutral, balanced (good for professional)
- **echo** - Male, articulate
- **fable** - Expressive, storytelling
- **onyx** - Deep, authoritative male
- **nova** - Female, warm
- **shimmer** - Female, bright, energetic

Try different voices:
```bash
export OPENAI_TTS_VOICE=nova
python test_tts_answer.py
```

---

## 📊 Cost Information

OpenAI TTS pricing: **$0.015 per 1,000 characters**

Typical interview answer (600 characters):
- **Cost**: ~$0.009 (less than 1 cent per answer)
- **Audio**: ~900 KB MP3 file
- **Duration**: ~60 seconds

For a 5-question interview: **~$0.045 (4.5 cents total)**

---

## 🎯 Advanced Usage

### Generate Custom Answers Programmatically

```python
from utils.tts_generator import TTSGenerator
from dotenv import load_dotenv

load_dotenv()

tts = TTSGenerator()

# Option 1: Let GPT generate the answer
audio_file = tts.answer_question(
    "What are your strengths?",
    "strengths_answer.mp3"
)

# Option 2: Use your own text
audio_file = tts.text_to_speech(
    "I'm excellent at automation testing and Python development",
    "custom_answer.mp3"
)

print(f"Audio saved: {audio_file}")
```

### Multiple Questions in Sequence

```python
questions = [
    "Tell me about yourself",
    "What are your strengths?",
    "Why do you want this job?"
]

for i, q in enumerate(questions, 1):
    audio = tts.answer_question(q, f"answer_{i}.mp3")
    print(f"Q{i}: {audio}")
```

---

## 🔧 Integration with Browser Automation

### Manual Control (Current)

1. Generate audio for expected questions
2. Launch Chrome with audio file
3. Run automation - Chrome uses audio as mic input

### Future: Automatic Detection (Coming Soon)

The agent will:
1. Detect question text on page
2. Generate answer using GPT-5.1
3. Convert to speech with TTS
4. Inject audio in real-time

---

## 📝 Example Workflow

**Complete interview automation:**

```bash
# Terminal 1: Generate answers
cd Automation_mcp_agent
python -c "
from utils.tts_generator import TTSGenerator
from dotenv import load_dotenv
load_dotenv()

tts = TTSGenerator()

questions = [
    'Please tell me something about yourself.',
    'What are your key strengths?',
    'Why do you want to work here?'
]

for i, q in enumerate(questions, 1):
    audio = tts.answer_question(q, f'interview_q{i}.mp3')
    print(f'Generated: {audio}')
"

# Terminal 2: Launch Chrome with first answer
./launch_chrome_with_audio.sh generated_audio/interview_q1.mp3

# Terminal 3: Run Streamlit
./start_streamlit.sh
```

Then in Streamlit UI:
```
Navigate to VMock, start interview, the Chrome will answer using pre-generated audio
```

---

## 🎤 Listen to Generated Audio

Play any generated audio:
```bash
afplay generated_audio/test_answer_1.mp3
```

Or open in Finder:
```bash
open generated_audio/
```

---

## 🐛 Troubleshooting

### "Audio file not found"
- Check path: `ls generated_audio/`
- Regenerate: `python test_tts_answer.py`

### "OpenAI API key not set"
- Verify: `grep OPENAI_API_KEY .env`
- Make sure `.env` file is in `Automation_mcp_agent/` directory

### "Chrome not using audio"
- Check Chrome is launched with: `ps aux | grep use-file-for-fake-audio`
- Verify audio file path is absolute
- Check logs: `cat /tmp/chrome_audio.log`

### "Audio quality poor"
- Use `tts-1-hd` model instead of `tts-1`
- Adjust speed: `OPENAI_TTS_SPEED=0.9`
- Try different voice: `OPENAI_TTS_VOICE=nova`

---

## 📊 Generated Files

Audio files are saved to:
```
Automation_mcp_agent/generated_audio/
├── interview_answer.mp3      # Default filename
├── test_answer_1.mp3         # Test questions
├── test_answer_2.mp3
└── test_answer_3.mp3
```

Cleanup old files (keeps latest 5):
```python
tts.cleanup_old_audio(keep_latest=5)
```

---

## ✅ Verification

Test that everything works:

```bash
cd Automation_mcp_agent

# 1. Test TTS generation
python test_tts_answer.py

# 2. Verify audio files created
ls -lh generated_audio/

# 3. Play one
afplay generated_audio/test_answer_1.mp3

# 4. Test Chrome with audio
./launch_chrome_with_audio.sh generated_audio/test_answer_1.mp3
```

You should see:
- ✅ Audio files generated (~900 KB each)
- ✅ Chrome launches on port 9222
- ✅ Chrome shows "🎤 Fake audio" in logs

---

## 🎯 Next Steps

**Current Capabilities:**
- ✅ GPT-5.1 generates intelligent text answers
- ✅ OpenAI TTS converts to natural speech
- ✅ Chrome can use audio file as fake microphone
- ✅ Multiple voice options
- ✅ Configurable speed and quality

**Future Enhancements:**
- 🔄 Auto-detect questions on page
- 🔄 Real-time audio generation during interview
- 🔄 Question-answer history tracking
- 🔄 Custom voice training

---

## 💡 Tips

1. **Generate answers before interview** for faster execution
2. **Use `tts-1`** for speed, `tts-1-hd` for quality
3. **Test different voices** to find the best match
4. **Keep answers 30-60 seconds** for natural flow
5. **Cleanup old audio** to save disk space

---

## 📞 Support

If you have issues:
1. Check logs: `cat /tmp/chrome_audio.log`
2. Verify API key: `echo $OPENAI_API_KEY`
3. Test TTS: `python test_tts_answer.py`
4. Check Chrome: `ps aux | grep 9222`
