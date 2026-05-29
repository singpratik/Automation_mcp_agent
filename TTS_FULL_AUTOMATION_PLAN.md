# OpenAI TTS + Fake Microphone - Full Automation Implementation Plan

## ✅ TTS Cleanup Complete

All previous TTS integrations have been removed:
- ❌ Removed TTS configuration from BrowserUseConfig
- ❌ Removed TTS generator initialization from agent
- ❌ Removed `generate_audio_response()` method
- ❌ Removed `get_audio_response_instructions()` method
- ❌ Removed task prompt enhancement
- ❌ Removed TTS config from .env
- ❌ Removed automatic detection from Streamlit

**Status**: Agent is now clean and ready for new implementation ✅

---

## 🎯 New Approach: OpenAI TTS + Fake Microphone (Full Automation)

### Concept
Instead of pre-generating audio before automation, we'll create **real-time TTS integration** where the agent:

1. **Runs automation** normally
2. **Detects interview questions** on screen during execution
3. **Generates audio response** using OpenAI TTS immediately
4. **Injects audio as microphone** into the browser session
5. **Continues automation** seamlessly

This is **fully automated** - no manual steps needed!

---

## Architecture Design

### Option A: Browser Extension with TTS (Recommended ⭐)
```
Browser Automation (browser-use)
  ↓
Detects Question on Page (GPT-5.1 Vision)
  ↓
Extract Question Text
  ↓
Generate Answer (GPT-5.1 Text)
  ↓
Convert to Audio (OpenAI TTS)
  ↓
Save to Temp File
  ↓
Inject via Chrome Extension (MediaStream API)
  ↓
Continue Automation
```

**Pros:**
- ✅ Fully automated
- ✅ No browser restart needed
- ✅ Real-time audio injection
- ✅ Can handle multiple questions sequentially

**Cons:**
- ⚠️ Requires Chrome extension development
- ⚠️ More complex implementation

### Option B: Dynamic Browser Restart (Simpler)
```
Browser Automation (browser-use)
  ↓
Detects Question on Page
  ↓
Generate Audio Response
  ↓
PAUSE: Save current state
  ↓
RESTART: Chrome with new audio file
  ↓
RESUME: Continue from saved state
  ↓
Complete Automation
```

**Pros:**
- ✅ Uses existing `--use-file-for-fake-audio-capture` flag
- ✅ Simpler implementation
- ✅ No extension needed

**Cons:**
- ⚠️ Browser restart required per question
- ⚠️ Slower (restart overhead)
- ⚠️ State management complexity

### Option C: Hybrid Approach (Best Balance)
```
START: Launch Chrome with placeholder audio
  ↓
Automation Begins
  ↓
Question Detected
  ↓
Generate TTS in Background (async)
  ↓
Update Audio File in Place
  ↓
Chrome picks up new audio automatically
  ↓
Continue Automation
```

**Pros:**
- ✅ No browser restart
- ✅ Simple implementation
- ✅ Uses existing Chrome flags
- ✅ Fast response time

**Cons:**
- ⚠️ Requires audio file monitoring
- ⚠️ Timing coordination needed

---

## Recommended Implementation: **Option C (Hybrid)**

### Step-by-Step Implementation

#### 1. Create Real-Time TTS Module (`utils/realtime_tts.py`)

```python
import os
from openai import OpenAI
from pathlib import Path
import threading
import time

class RealtimeTTS:
    """
    Real-time TTS that updates audio file in-place for Chrome
    """
    def __init__(self, api_key=None):
        self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        self.audio_file = Path("./generated_audio/live_response.mp3")
        self.audio_file.parent.mkdir(exist_ok=True)
        
        # Create initial silence (Chrome needs file to exist)
        self._create_silence()
    
    def _create_silence(self):
        """Create initial silent audio file"""
        # Generate 1 second of silence using TTS
        response = self.client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input="..."  # Minimal audio
        )
        response.stream_to_file(str(self.audio_file))
    
    def update_audio(self, text: str):
        """
        Update audio file with new TTS response
        Chrome will pick up the new audio automatically
        """
        response = self.client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=text,
            speed=1.0
        )
        response.stream_to_file(str(self.audio_file))
        print(f"✅ Audio updated: {self.audio_file}")
    
    def get_audio_path(self):
        """Get path to live audio file"""
        return str(self.audio_file.absolute())
```

#### 2. Integrate with Browser Agent

```python
# In browser_use_agent.py

async def run_task_with_tts(self, task: str, start_url: Optional[str] = None):
    """
    Run task with real-time TTS support
    """
    from utils.realtime_tts import RealtimeTTS
    
    # Initialize real-time TTS
    tts = RealtimeTTS()
    
    # Launch Chrome with live audio file
    audio_path = tts.get_audio_path()
    browser = self._launch_chrome_with_audio(audio_path)
    
    # Create agent with question detection callback
    agent = Agent(
        task=task,
        llm=self.llm,
        browser=browser,
        ...
    )
    
    # Run with TTS monitoring
    result = await agent.run()
    
    return result

def _launch_chrome_with_audio(self, audio_path):
    """Launch Chrome with fake microphone"""
    from browser_use import Browser
    
    browser = Browser(
        headless=False,
        channel='chrome',
        cdp_url=None,  # Force new instance
        extra_chromium_args=[
            '--use-fake-ui-for-media-stream',
            '--use-fake-device-for-media-stream',
            f'--use-file-for-fake-audio-capture={audio_path}',
            '--enable-usermedia-screen-capturing',
            '--auto-accept-camera-and-microphone-capture'
        ]
    )
    
    return browser
```

#### 3. Add Question Detection

```python
def detect_and_respond_to_questions(self, page, tts: RealtimeTTS):
    """
    Monitor page for interview questions and generate responses
    """
    # Use GPT-5.1 vision to detect questions
    screenshot = page.screenshot()
    
    # Ask GPT if there's a question visible
    question = self._extract_question_from_screen(screenshot)
    
    if question:
        print(f"📝 Question detected: {question[:60]}...")
        
        # Generate answer
        answer = self._generate_answer(question)
        
        # Update audio in real-time
        tts.update_audio(answer)
        
        # Wait for audio to update
        time.sleep(1)
        
        print(f"✅ Audio ready for: {question[:40]}...")
```

#### 4. Streamlit Integration

```python
# In streamlit_app.py

if context["ui_tests"]:
    st.info("🚀 Starting automation with real-time TTS...")
    
    # Create agent with TTS
    agent = BrowserUseAgent()
    
    # Run with TTS enabled
    browser_result = agent.run_task_with_tts_sync(user_input)
    
    st.success("✅ Automation completed with TTS responses!")
```

---

## Implementation Phases

### Phase 1: Setup (30 min)
- [ ] Create `utils/realtime_tts.py`
- [ ] Test audio file updates
- [ ] Verify Chrome picks up new audio

### Phase 2: Integration (1 hour)
- [ ] Add `run_task_with_tts()` method
- [ ] Implement Chrome launch with audio
- [ ] Test basic TTS injection

### Phase 3: Question Detection (1 hour)
- [ ] Implement question detection logic
- [ ] Add GPT-5.1 vision analysis
- [ ] Test on actual interview page

### Phase 4: Answer Generation (30 min)
- [ ] Create answer generation prompts
- [ ] Optimize for natural speech
- [ ] Test different question types

### Phase 5: End-to-End Testing (1 hour)
- [ ] Test full automation flow
- [ ] Verify audio timing
- [ ] Handle edge cases

---

## Technical Considerations

### Chrome Audio File Monitoring

Chrome's `--use-file-for-fake-audio-capture` flag **continuously reads** from the audio file. When you update the file, Chrome picks up the new audio on the next read cycle.

**Key Points:**
- ✅ File can be updated while Chrome is running
- ✅ Chrome automatically uses new audio
- ✅ No restart needed
- ⚠️ Timing matters - update before recording starts

### Audio File Requirements

- **Format**: MP3, WAV, or OGG
- **Sample Rate**: 16kHz or 48kHz recommended
- **Channels**: Mono or Stereo
- **Bitrate**: 128kbps+ for quality

### Timing Coordination

```python
# Pseudo-code for timing
1. Agent detects question appears (GPT vision)
2. Generate TTS immediately (async)
3. Wait for "Start Recording" button
4. Audio is ready before click
5. Click button - Chrome uses new audio
```

---

## Testing Strategy

### Unit Tests
```bash
# Test TTS generation
python test_realtime_tts.py

# Test audio file updates
python test_audio_updates.py

# Test Chrome audio pickup
python test_chrome_audio.py
```

### Integration Tests
```bash
# Test full automation
streamlit run streamlit_app.py
# Enter: "Complete VMock interview with TTS"
```

### Manual Verification
1. Launch Chrome with placeholder audio
2. Update audio file manually
3. Verify Chrome uses new audio
4. Test with actual interview page

---

## Alternative: Chrome Extension Approach

If file-based approach has issues, we can build a Chrome extension:

```javascript
// content.js
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.type === 'UPDATE_AUDIO') {
    // Create MediaStream from audio file
    const audio = new Audio(request.audioUrl);
    const stream = audio.captureStream();
    
    // Replace microphone stream
    navigator.mediaDevices.getUserMedia = async () => stream;
    
    sendResponse({success: true});
  }
});
```

This allows:
- ✅ Dynamic audio switching
- ✅ No file monitoring needed
- ✅ Better timing control
- ⚠️ Requires extension installation

---

## Next Steps

1. **Choose approach**: Hybrid (Option C) or Extension (Alternative)?
2. **Create prototype**: Implement Phase 1
3. **Test audio updates**: Verify Chrome behavior
4. **Full integration**: Connect all pieces
5. **Test with VMock**: Real interview scenario

## Questions Before Implementation

1. **Which approach do you prefer?**
   - [ ] Option C: Hybrid (file-based, simpler)
   - [ ] Extension: More control, more complex

2. **Question detection strategy?**
   - [ ] GPT Vision (screenshots)
   - [ ] DOM inspection (text selectors)
   - [ ] Both (hybrid detection)

3. **Answer generation?**
   - [ ] Predefined templates
   - [ ] GPT-5.1 dynamic answers
   - [ ] Hybrid (templates + GPT enhancement)

4. **Priority?**
   - [ ] Implement now (I'll code it)
   - [ ] Review plan first
   - [ ] Test concept separately

Let me know your preferences and I'll start implementation! 🚀
