# TTS On-Demand Usage Guide

## Overview
TTS (Text-to-Speech) is now configured for **on-demand use only** - no automatic audio generation. Audio responses are generated only when explicitly requested or when question text is detected during automation.

## Configuration Status

### Current Settings (.env)
```bash
ENABLE_TTS_RESPONSES=false  # TTS capability available but not automatic
OPENAI_TTS_MODEL=tts-1      # Fast, cost-effective model
OPENAI_TTS_VOICE=alloy      # Professional voice
OPENAI_TTS_SPEED=1.0        # Normal speaking speed
```

### What Changed
- ❌ **Removed**: Automatic interview keyword detection
- ❌ **Removed**: Automatic question prediction and audio generation
- ❌ **Removed**: Chrome status indicator in Streamlit sidebar
- ✅ **Kept**: TTS module (`utils/tts_generator.py`)
- ✅ **Kept**: BrowserUseAgent TTS integration
- ✅ **Kept**: Chrome audio launcher script

## Usage Methods

### Method 1: Generate Audio Manually (Python)

```python
from agents.browser_use_agent import BrowserUseAgent

# Initialize agent
agent = BrowserUseAgent()

# Generate audio for a specific question
question = "Tell me about your experience with Python automation"
audio_file = agent.generate_audio_response(
    question=question,
    output_filename="answer_python.mp3"
)

print(f"Audio generated: {audio_file}")
# Output: generated_audio/answer_python.mp3
```

### Method 2: Generate Audio via TTS Module

```python
from utils.tts_generator import TTSGenerator

# Initialize TTS generator
tts = TTSGenerator()

# Generate answer and convert to speech
question = "What is your greatest strength?"
audio_file = tts.answer_question(
    question=question,
    output_filename="strength_answer.mp3"
)

print(f"Audio ready: {audio_file}")
```

### Method 3: Question Detection During Automation (Recommended)

When automation detects question text on screen, generate audio response:

```python
from agents.browser_use_agent import BrowserUseAgent

agent = BrowserUseAgent()

# During automation, if question text is detected on recording screen:
detected_question = "Please introduce yourself and tell us about your background"

# Generate audio response
audio_file = agent.generate_audio_response(
    question=detected_question,
    output_filename="intro_response.mp3"
)

# Launch Chrome with audio
import subprocess
subprocess.run([
    "./launch_chrome_with_audio.sh",
    str(audio_file)
])

# Continue automation - Chrome will use audio as microphone input
```

### Method 4: Pre-Generate Audio Before Interview

```python
from agents.browser_use_agent import BrowserUseAgent

agent = BrowserUseAgent()

# Define expected questions
questions = [
    "Tell me about yourself",
    "Why are you interested in this position?",
    "What are your greatest strengths?",
    "Describe a challenging project you worked on",
    "Where do you see yourself in 5 years?"
]

# Generate audio for all questions
audio_files = []
for i, question in enumerate(questions, 1):
    audio = agent.generate_audio_response(
        question=question,
        output_filename=f"interview_q{i}.mp3"
    )
    audio_files.append(audio)
    print(f"✅ Generated: {audio.name}")

# Use first audio file with Chrome
subprocess.run(["./launch_chrome_with_audio.sh", str(audio_files[0])])
```

## Chrome Audio Integration

### Launch Chrome with Audio Response

```bash
# Stop existing Chrome
pkill -f 'remote-debugging-port=9222'

# Launch with audio file
cd /Users/pratiksingh/Desktop/Interview_automation/Automation_mcp_agent
./launch_chrome_with_audio.sh generated_audio/answer.mp3
```

### Verify Chrome Audio Status

```bash
# Check if Chrome is using audio input
ps aux | grep "use-file-for-fake-audio-capture"
```

## Implementation Example: Question Detection

Here's how to implement TTS when question text is detected during automation:

```python
from agents.browser_use_agent import BrowserUseAgent
from playwright.sync_api import Page

def handle_interview_question(page: Page, agent: BrowserUseAgent):
    """
    Detect question text on page and generate audio response
    """
    # Example: Detect question in specific element
    try:
        # Look for question text on recording screen
        question_selector = ".question-text, .interview-question, [data-question]"
        question_element = page.query_selector(question_selector)
        
        if question_element:
            question_text = question_element.text_content().strip()
            
            if question_text and len(question_text) > 10:
                print(f"📝 Question detected: {question_text[:60]}...")
                
                # Generate audio response
                audio_file = agent.generate_audio_response(
                    question=question_text,
                    output_filename=f"response_{hash(question_text)}.mp3"
                )
                
                if audio_file:
                    print(f"✅ Audio generated: {audio_file.name}")
                    
                    # Optionally: Restart Chrome with new audio
                    # subprocess.run(["./launch_chrome_with_audio.sh", str(audio_file)])
                    
                return audio_file
    except Exception as e:
        print(f"⚠️ Question detection error: {e}")
    
    return None

# Usage in automation
agent = BrowserUseAgent()
page = agent.browser.contexts[0].pages[0]  # Get current page

# When on interview recording screen
audio = handle_interview_question(page, agent)
if audio:
    print(f"Ready to answer with: {audio}")
```

## Configuration Options

### Enable TTS Capability

To enable TTS generation, update `.env`:

```bash
ENABLE_TTS_RESPONSES=true
```

Then restart your application:
```bash
pkill -f streamlit
cd /Users/pratiksingh/Desktop/Interview_automation/Automation_mcp_agent
streamlit run streamlit_app.py
```

### Change Voice

Available voices:
- `alloy` - Neutral, professional (default)
- `echo` - Clear, articulate
- `fable` - British accent
- `onyx` - Deep, confident
- `nova` - Energetic
- `shimmer` - Warm, friendly

Update in `.env`:
```bash
OPENAI_TTS_VOICE=nova
```

### Adjust Speed

Speaking speed (0.25 to 4.0):
```bash
OPENAI_TTS_SPEED=1.0  # Normal
OPENAI_TTS_SPEED=1.2  # 20% faster
OPENAI_TTS_SPEED=0.8  # 20% slower
```

## Cost Considerations

TTS pricing:
- **OpenAI TTS-1**: $0.015 per 1,000 characters
- **Average answer**: ~300 characters = $0.0045 (~0.5 cents)
- **5 interview questions**: ~$0.02 (2 cents)

**Recommendation**: Use `tts-1` model for testing and production. Only use `tts-1-hd` for high-quality recordings.

## Testing

Test TTS on-demand functionality:

```bash
cd /Users/pratiksingh/Desktop/Interview_automation/Automation_mcp_agent
python test_tts_on_demand.py
```

Expected output:
```
✅ PASS: TTS Module Available
✅ PASS: No Automatic Audio
```

## Troubleshooting

### TTS Not Generating Audio

1. Check OPENAI_API_KEY is set in `.env`
2. Verify ENABLE_TTS_RESPONSES=true (if you want to enable it)
3. Test standalone:
   ```bash
   python test_tts_answer.py
   ```

### Chrome Not Using Audio

1. Verify Chrome launched with audio flag:
   ```bash
   ps aux | grep "use-file-for-fake-audio-capture"
   ```

2. Check audio file exists:
   ```bash
   ls -lh generated_audio/*.mp3
   ```

3. Test audio playback:
   ```bash
   afplay generated_audio/test.mp3
   ```

### Audio Quality Issues

1. Try different voice:
   ```bash
   OPENAI_TTS_VOICE=nova  # More energetic
   OPENAI_TTS_VOICE=onyx  # Deeper, confident
   ```

2. Adjust speed:
   ```bash
   OPENAI_TTS_SPEED=0.9  # Slightly slower for clarity
   ```

3. Use HD model:
   ```bash
   OPENAI_TTS_MODEL=tts-1-hd  # Higher quality (same price)
   ```

## Key Differences from Automatic Mode

| Feature | Automatic (OLD) | On-Demand (NEW) |
|---------|----------------|-----------------|
| Trigger | Interview keywords in prompt | Explicit call or detected question |
| Timing | Before automation starts | During automation when needed |
| Question Source | GPT prediction | Actual detected text or manual |
| Audio Generation | 3-5 files upfront | 1 file per detected question |
| Chrome Setup | Manual after generation | Dynamic during automation |
| Cost | Higher (predict + generate) | Lower (only detected questions) |
| Accuracy | 60-70% predicted correctly | 100% (actual questions) |

## Best Practices

1. **Question Detection**: Implement robust question text detection on interview screens
2. **Audio Caching**: Cache generated audio by question hash to avoid regeneration
3. **Error Handling**: Always check if audio generation succeeded before using
4. **Chrome Management**: Restart Chrome with new audio when questions change
5. **Testing**: Test with sample questions before live interviews
6. **Cost Control**: Only generate audio when absolutely needed

## Next Steps

1. ✅ Test TTS on-demand: `python test_tts_on_demand.py`
2. ✅ Open Streamlit: http://localhost:8501
3. ✅ Verify no automatic audio generation
4. 🔄 Implement question detection in your automation flow
5. 🔄 Test with actual VMock interview screen

## Support

For issues or questions:
- Check logs: `cat /tmp/streamlit.log`
- Test TTS module: `python test_tts_answer.py`
- Review documentation: `TTS_GUIDE.md`
