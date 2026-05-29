# Real-time TTS Usage Guide
## Option C: Hybrid File-Based Approach

## 🎯 Overview

This implementation uses **Chrome's fake microphone** with a **live audio file** that gets updated in real-time. No browser restarts needed!

### Architecture
```
Chrome Launch → Live Audio File (silence)
    ↓
Detect Question (GPT Vision or DOM)
    ↓
Generate Answer (GPT-4)
    ↓
Convert to Speech (OpenAI TTS)
    ↓
Update Audio File In-Place
    ↓
Chrome Automatically Uses New Audio
    ↓
Continue Automation → FULLY AUTOMATED!
```

## 🚀 Quick Start

### 1. Basic TTS Answer Generation

```python
from agents.browser_use_agent import BrowserUseAgent, BrowserUseConfig

# Create agent with TTS enabled
config = BrowserUseConfig(
    enable_realtime_tts=True,
    tts_voice="alloy",  # Options: alloy, echo, fable, onyx, nova, shimmer
    tts_model="tts-1"   # Options: tts-1 (fast) or tts-1-hd (quality)
)

agent = BrowserUseAgent(config=config)

# Set candidate context
context = {
    "candidate_name": "John Doe",
    "position": "Software Engineer",
    "experience_years": 5,
    "skills": ["Python", "React", "AWS"]
}

# Answer a question
question = "Tell me about your experience with cloud technologies."
agent.answer_question_with_tts(question, context)

# Audio file is at: ./generated_audio/live_response.wav
```

### 2. Full Interview Automation with TTS

```python
from agents.browser_use_agent import BrowserUseAgent, BrowserUseConfig

# Configure with TTS
config = BrowserUseConfig(
    enable_realtime_tts=True,
    tts_voice="nova",
    headless=False,  # Show browser for testing
    max_steps=100
)

agent = BrowserUseAgent(config=config)

# Candidate profile
context = {
    "candidate_name": "Sarah Johnson",
    "position": "Senior Developer",
    "experience_years": 7,
    "skills": ["Python", "Docker", "Kubernetes"]
}

# Run interview with automatic TTS answering
result = agent.run_task_with_tts_sync(
    task="Complete the VMock elevator pitch interview",
    start_url="https://vmock.com/elevator-pitch",
    candidate_context=context
)

print(f"Success: {result['success']}")
print(f"Answered Questions: {len(result['answered_questions'])}")
```

### 3. Manual Chrome Launch for Testing

You can test the audio file with Chrome directly:

```bash
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --use-fake-ui-for-media-stream \
  --use-fake-device-for-media-stream \
  --use-file-for-fake-audio-capture="/path/to/Interview_automation/Automation_mcp_agent/generated_audio/live_response.wav" \
  https://vmock.com
```

## 📋 API Reference

### BrowserUseConfig TTS Options

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `enable_realtime_tts` | bool | `False` | Enable real-time TTS answering |
| `tts_voice` | str | `"alloy"` | OpenAI TTS voice (alloy/echo/fable/onyx/nova/shimmer) |
| `tts_model` | str | `"tts-1"` | TTS model (tts-1 or tts-1-hd) |
| `answer_generator_model` | str | `"gpt-4"` | Model for answer generation |

### Methods

#### `answer_question_with_tts(question, context=None)`
Generate answer and update audio file.

**Args:**
- `question` (str): Interview question
- `context` (dict, optional): Candidate context

**Returns:** `bool` - Success status

**Example:**
```python
agent.answer_question_with_tts(
    "What are your strengths?",
    context={"candidate_name": "John", "skills": ["Python", "AWS"]}
)
```

#### `run_task_with_tts_sync(task, start_url=None, candidate_context=None)`
Run automation task with TTS answering.

**Args:**
- `task` (str): Natural language task description
- `start_url` (str, optional): Starting URL
- `candidate_context` (dict, optional): Candidate profile

**Returns:** `dict` - Results with TTS metadata

**Example:**
```python
result = agent.run_task_with_tts_sync(
    task="Answer interview questions on the page",
    start_url="https://interview-platform.com",
    candidate_context={
        "candidate_name": "Alex Chen",
        "position": "DevOps Engineer",
        "experience_years": 6,
        "skills": ["Kubernetes", "Terraform", "Python"]
    }
)
```

## 🎨 TTS Voice Options

| Voice | Description | Best For |
|-------|-------------|----------|
| `alloy` | Neutral, balanced | General use |
| `echo` | Male, clear | Professional settings |
| `fable` | Male, expressive | Storytelling |
| `onyx` | Male, deep | Authority |
| `nova` | Female, clear | Professional female |
| `shimmer` | Female, soft | Friendly female |

## 🧪 Testing

Run the test suite:

```bash
cd Automation_mcp_agent
python test_realtime_tts.py
```

This will:
1. Test TTS answer generation
2. Verify browser task setup with TTS
3. Test multiple question handling

## 📁 File Structure

```
Automation_mcp_agent/
├── agents/
│   └── browser_use_agent.py     # Main agent with TTS support
├── utils/
│   └── realtime_tts.py          # TTS module (RealtimeTTS, QuestionDetector, AnswerGenerator)
├── generated_audio/
│   └── live_response.wav        # Live audio file (auto-created)
└── test_realtime_tts.py         # Test suite
```

## 🔧 How It Works

### 1. Chrome Audio Capture
Chrome is launched with `--use-file-for-fake-audio-capture` pointing to a WAV file:
```python
chrome_args = [
    '--use-fake-ui-for-media-stream',
    '--use-fake-device-for-media-stream',
    '--use-file-for-fake-audio-capture=/path/to/live_response.wav'
]
```

### 2. Audio File Updates
When a question is detected:
```python
# 1. Generate answer with GPT
answer = answer_generator.generate_answer(question)

# 2. Convert to speech with OpenAI TTS
audio_response = openai.audio.speech.create(
    model="tts-1",
    voice="alloy",
    input=answer
)

# 3. Save to temporary file
audio_response.stream_to_file("temp.wav")

# 4. Atomic replace - Chrome picks up instantly
temp_file.replace("live_response.wav")
```

### 3. Chrome Behavior
Chrome continuously reads from the audio file. When the file is updated, Chrome automatically uses the new audio on the next read cycle. **No restart needed!**

## 🎯 Use Cases

### 1. VMock Elevator Pitch
```python
agent.run_task_with_tts_sync(
    task="Complete elevator pitch interview",
    start_url="https://vmock.com/elevator-pitch",
    candidate_context={...}
)
```

### 2. Custom Interview Platform
```python
# Answer specific questions
agent.answer_question_with_tts("Tell me about yourself")
agent.answer_question_with_tts("What are your strengths?")
```

### 3. Pre-recorded Answers
```python
# Generate answers without browser
questions = [
    "What is your experience?",
    "Why this role?",
    "What are your goals?"
]

for question in questions:
    agent.answer_question_with_tts(question, context)
    # Audio file updated each time
```

## 🐛 Troubleshooting

### Audio Not Working in Chrome
- **Check file exists:** `ls generated_audio/live_response.wav`
- **Verify format:** Must be WAV, 16kHz, mono
- **Check permissions:** File must be readable by Chrome

### TTS Generation Fails
- **Verify OpenAI API key:** Check `OPENAI_API_KEY` in `.env`
- **Check quota:** OpenAI TTS has rate limits
- **Inspect logs:** Look for error messages

### Chrome Not Picking Up Audio Changes
- **Ensure atomic updates:** Using `temp_file.replace()` for atomic operations
- **Check file modification time:** `stat generated_audio/live_response.wav`
- **Restart Chrome:** Close and relaunch with fresh session

## 📚 Advanced Usage

### Custom Question Detection
```python
from utils.realtime_tts import QuestionDetector

detector = QuestionDetector()

# From screenshot
question = detector.detect_from_screenshot(
    screenshot_path="page.png",
    llm_client=openai_client
)

# From DOM
question = detector.detect_from_dom(
    page_content=html,
    question_selectors=[
        ".question-text",
        "#interview-question",
        "[data-question]"
    ]
)
```

### Custom Answer Templates
```python
from utils.realtime_tts import AnswerGenerator

generator = AnswerGenerator(
    llm_client=openai_client,
    model="gpt-4"
)

# Provide detailed context
generator.set_context({
    "candidate_name": "Jane Smith",
    "position": "AI Engineer",
    "experience_years": 8,
    "skills": ["Machine Learning", "PyTorch", "MLOps"],
    "achievements": ["Led ML team", "Published papers"],
    "company": "TechCorp"
})

answer = generator.generate_answer("What's your biggest achievement?")
```

## 🎓 Best Practices

1. **Always set candidate context** before running interviews
2. **Use appropriate voice** for candidate profile
3. **Test audio file** with manual Chrome launch first
4. **Monitor logs** for TTS generation errors
5. **Keep answers concise** (under 30 seconds spoken)

## 🔐 Security Notes

- Audio files stored in `generated_audio/` directory
- No sensitive data in audio files (only interview answers)
- OpenAI TTS API calls use encrypted HTTPS
- Audio files automatically overwritten (not accumulated)

## 📞 Support

For issues or questions:
1. Check logs: `logger.setLevel(logging.DEBUG)`
2. Run test suite: `python test_realtime_tts.py`
3. Review TTS_FULL_AUTOMATION_PLAN.md for architecture details
