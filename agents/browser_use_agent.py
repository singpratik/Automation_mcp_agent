"""
Browser-Use Agent - AI-powered browser automation
Wraps browser-use/web-ui library for robust web automation with LLM intelligence
"""

import os
import asyncio
import logging
import re
import time
from typing import Optional, Dict, Any, List
from pathlib import Path
from dataclasses import dataclass
import sys

# Add parent directory to path for utils import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


# Wrapper class to add 'provider' attribute to LangChain LLMs
class LLMWrapper:
    """Wrapper to add provider attribute to LangChain LLMs for browser-use compatibility"""
    def __init__(self, llm, provider_name: str):
        object.__setattr__(self, '_llm', llm)
        object.__setattr__(self, 'provider', provider_name)
        # Also expose common attributes directly for browser-use checks
        if hasattr(llm, 'model_name'):
            object.__setattr__(self, 'model', llm.model_name)
        elif hasattr(llm, 'model'):
            object.__setattr__(self, 'model', llm.model)
        
    def __getattr__(self, name):
        # Forward all other attributes to the wrapped LLM
        return getattr(object.__getattribute__(self, '_llm'), name)
    
    def __setattr__(self, name, value):
        if name in ('_llm', 'provider', 'model'):
            object.__setattr__(self, name, value)
        else:
            setattr(object.__getattribute__(self, '_llm'), name, value)


@dataclass
class BrowserUseConfig:
    """Configuration for browser-use agent"""
    llm_provider: str = "openai"  # openai, anthropic, google, ollama, deepseek
    model_name: str = "gpt-4o"
    api_key: Optional[str] = None
    max_steps: int = 100
    headless: bool = False
    enable_recording: bool = True
    enable_screenshots: bool = True  # Capture screenshots at each step
    screenshot_dir: str = "./browser_screenshots"
    persistent_session: bool = True
    browser_path: Optional[str] = None
    user_data_dir: Optional[str] = None
    disable_security: bool = False  # Disable web security features
    timeout: int = 15000  # milliseconds - FASTER (15s instead of 30s)
    # On-demand TTS toggle (pre-generated audio via utils.tts_generator.TTSGenerator)
    # This is separate from enable_realtime_tts which controls live fake-mic audio.
    enable_tts: bool = False
    
    # Real-time TTS configuration
    enable_realtime_tts: bool = False
    tts_voice: str = "alloy"  # alloy, echo, fable, onyx, nova, shimmer
    tts_model: str = "tts-1"  # tts-1 or tts-1-hd
    answer_generator_model: str = "gpt-4"


class BrowserUseAgent:
    """
    Enhanced browser agent using browser-use/web-ui library
    
    Features:
    - AI-driven element detection
    - Natural language task execution
    - Persistent browser sessions
    - Screen recording
    - Multi-LLM support (OpenAI, Anthropic, Google, Ollama)
    """
    
    def __init__(self, config: Optional[BrowserUseConfig] = None):
        """
        Initialize BrowserUseAgent
        
        Args:
            config: Configuration for browser-use agent
        """
        self.config = config or self._load_config_from_env()
        self.agent = None
        self.browser = None
        self.context = None
        self.llm = None
        
        # Real-time TTS components (live fake-mic audio)
        self.realtime_tts = None
        self.question_detector = None
        self.answer_generator = None
        self.last_answered_question = None
        # Track all questions answered in a session (normalized text) so we don't
        # regenerate audio for the same prompt multiple times.
        self.answered_questions: List[str] = []
        # Soft limit on how many questions to auto-answer per interview.
        self.max_tts_questions: int = int(os.getenv("VMOCK_MAX_TTS_QUESTIONS", "5"))
        # How long to wait (in seconds) after updating the audio file so that
        # Chrome can "speak" the answer before we move on.
        self.per_question_play_seconds: int = int(os.getenv("VMOCK_TTS_PLAY_SECONDS", "40"))
        # Optional vision-based fallback (GPT‑4 vision) for question detection.
        self.enable_vision_question_detection: bool = os.getenv("VMOCK_TTS_VISION", "false").lower() in {"1", "true", "yes"}
        
        # On-demand TTS generator (pre-generated MP3 files)
        self.tts_generator = None
        
        # Validate dependencies
        self._validate_dependencies()
        
        # Initialize LLM
        self._initialize_llm()
        
        # Initialize real-time TTS (live fake-mic audio) if enabled
        if self.config.enable_realtime_tts:
            self._initialize_realtime_tts()
        
        # Initialize on-demand TTS generator for pre-recorded audio files
        self._initialize_on_demand_tts()
        
        logger.info(f"BrowserUseAgent initialized with {self.config.llm_provider}/{self.config.model_name}")
    
    def _load_config_from_env(self) -> BrowserUseConfig:
        """Load configuration from environment variables"""
        # Load from existing .env file
        env_file = Path(__file__).parent.parent / ".env"
        if env_file.exists():
            from dotenv import load_dotenv
            load_dotenv(env_file)
        
        return BrowserUseConfig(
            llm_provider=os.getenv("BROWSER_USE_LLM_PROVIDER", "openai"),
            model_name=os.getenv("BROWSER_USE_MODEL", "gpt-4o-mini"),
            api_key=os.getenv("OPENAI_API_KEY"),  # Use existing OPENAI_API_KEY
            max_steps=int(os.getenv("BROWSER_USE_MAX_STEPS", "100")),  # Increased for complex tasks
            headless=os.getenv("BROWSER_USE_HEADLESS", "false").lower() == "true",
            enable_recording=os.getenv("BROWSER_USE_ENABLE_RECORDING", "true").lower() == "true",
            enable_screenshots=os.getenv("BROWSER_USE_ENABLE_SCREENSHOTS", "true").lower() == "true",
            screenshot_dir=os.getenv("BROWSER_USE_SAVE_RECORDING_PATH", "./browser_screenshots"),
            persistent_session=os.getenv("USE_PERSISTENT_BROWSER", "true").lower() == "true",
            browser_path=os.getenv("BROWSER_PATH"),
            user_data_dir=os.getenv("BROWSER_USER_DATA"),
            timeout=int(os.getenv("BROWSER_USE_TIMEOUT", "300")) * 1000,  # Convert seconds to milliseconds - FASTER
            # On-demand TTS configuration (separate from real-time TTS)
            enable_tts=os.getenv("ENABLE_TTS_RESPONSES", "false").lower() == "true",
            tts_voice=os.getenv("OPENAI_TTS_VOICE", "alloy"),
            tts_model=os.getenv("OPENAI_TTS_MODEL", "tts-1"),
        )
    
    def _validate_dependencies(self):
        """Validate that required packages are installed"""
        try:
            import browser_use
            logger.info(f"✅ browser-use version: {browser_use.__version__ if hasattr(browser_use, '__version__') else 'unknown'}")
        except ImportError:
            raise ImportError(
                "browser-use library not found. Install with:\n"
                "pip install browser-use\n"
                "Or for full web-ui features:\n"
                "git clone https://github.com/browser-use/web-ui.git && cd web-ui && pip install -r requirements.txt"
            )
        
        try:
            from playwright.async_api import async_playwright
        except ImportError:
            raise ImportError("Playwright not found. Install with: playwright install --with-deps")
    
    def _initialize_realtime_tts(self):
        """Initialize real-time TTS components"""
        try:
            from utils.realtime_tts import RealtimeTTS, QuestionDetector, AnswerGenerator
            
            self.realtime_tts = RealtimeTTS(api_key=self.config.api_key)
            self.question_detector = QuestionDetector()
            self.answer_generator = AnswerGenerator(
                llm_client=self.llm,
                model=self.config.answer_generator_model
            )
            
            logger.info("✅ Real-time TTS initialized")
            logger.info(f"   Voice: {self.config.tts_voice}")
            logger.info(f"   Model: {self.config.tts_model}")
            logger.info(f"   Audio file: {self.realtime_tts.get_audio_path()}")
            
        except Exception as e:
            logger.error(f"Failed to initialize real-time TTS: {e}")
            self.config.enable_realtime_tts = False

    def _initialize_on_demand_tts(self):
        """Initialize on-demand TTS generator (separate from real-time TTS).

        This uses utils.tts_generator.TTSGenerator to generate standalone MP3
        files that can be played manually or via launch_chrome_with_audio.sh.
        """
        if not self.config.enable_tts:
            # Explicitly disabled in config / .env
            logger.info("On-demand TTS is disabled (ENABLE_TTS_RESPONSES!=true)")
            self.tts_generator = None
            return

        try:
            from utils.tts_generator import TTSGenerator

            self.tts_generator = TTSGenerator(api_key=self.config.api_key)
            logger.info("✅ On-demand TTS generator initialized")
            logger.info(f"   Voice: {self.config.tts_voice}")
            logger.info(f"   Model: {self.config.tts_model}")
        except Exception as e:
            logger.error(f"Failed to initialize on-demand TTS generator: {e}")
            self.tts_generator = None
    
    def _initialize_llm(self):
        """Initialize the LLM based on provider configuration"""
        provider = self.config.llm_provider.lower()
        
        try:
            if provider == "openai":
                # Use browser-use's native ChatOpenAI for better compatibility
                try:
                    from browser_use import ChatOpenAI as BrowserUseChatOpenAI
                    self.llm = BrowserUseChatOpenAI(
                        model=self.config.model_name,
                        api_key=self.config.api_key or os.getenv("OPENAI_API_KEY"),
                        temperature=0.7
                    )
                    logger.info("✅ OpenAI LLM initialized (browser-use native)")
                except ImportError:
                    # Fallback to LangChain if browser-use doesn't have ChatOpenAI
                    from langchain_openai import ChatOpenAI
                    llm = ChatOpenAI(
                        model=self.config.model_name,
                        api_key=self.config.api_key or os.getenv("OPENAI_API_KEY"),
                        temperature=0.7
                    )
                    # browser-use expects a 'provider' attribute - wrap LLM to add it
                    self.llm = LLMWrapper(llm, "openai")
                    logger.info("✅ OpenAI LLM initialized (LangChain wrapper)")
            
            elif provider == "anthropic":
                # Use browser-use's ChatAnthropic for Anthropic models
                from browser_use import ChatAnthropic
                self.llm = ChatAnthropic(
                    model=self.config.model_name or "claude-sonnet-4-6",
                    api_key=self.config.api_key or os.getenv("ANTHROPIC_API_KEY")
                )
                logger.info("✅ Anthropic LLM initialized")
            
            elif provider == "google":
                # Use browser-use's ChatGoogle for Google models
                from browser_use import ChatGoogle
                self.llm = ChatGoogle(
                    model=self.config.model_name or "gemini-3-flash-preview",
                    api_key=self.config.api_key or os.getenv("GOOGLE_API_KEY")
                )
                logger.info("✅ Google LLM initialized")
            
            elif provider == "browser-use":
                # Use browser-use's cloud models (bu-latest, bu-1-0, bu-2-0)
                from browser_use import ChatBrowserUse
                self.llm = ChatBrowserUse(
                    model=self.config.model_name or "bu-latest",
                    api_key=self.config.api_key or os.getenv("BROWSER_USE_API_KEY")
                )
                logger.info("✅ Browser-Use Cloud LLM initialized")
            
            elif provider == "ollama":
                # Use LangChain's ChatOllama for local Ollama models
                try:
                    from langchain_ollama import ChatOllama
                    llm = ChatOllama(
                        model=self.config.model_name or "llama3.1:8b",
                        base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
                        temperature=0.7
                    )
                    self.llm = LLMWrapper(llm, "ollama")
                    logger.info("✅ Ollama LLM initialized")
                except ImportError:
                    logger.error("langchain-ollama not installed. Install with: pip install langchain-ollama")
                    raise
            
            elif provider == "deepseek":
                # Use LangChain's ChatOpenAI with DeepSeek API
                from langchain_openai import ChatOpenAI
                llm = ChatOpenAI(
                    model=self.config.model_name or "deepseek-chat",
                    api_key=self.config.api_key or os.getenv("DEEPSEEK_API_KEY"),
                    base_url="https://api.deepseek.com"
                )
                self.llm = LLMWrapper(llm, "deepseek")
                logger.info("✅ DeepSeek LLM initialized")
            
            else:
                raise ValueError(f"Unsupported LLM provider: {provider}")
        
        except Exception as e:
            logger.error(f"Failed to initialize LLM: {e}")
            raise
    
    async def run_task(self, task: str, start_url: Optional[str] = None) -> Dict[str, Any]:
        """
        Execute a browser automation task using natural language
        
        Args:
            task: Natural language description of the task
            start_url: Optional starting URL
            
        Returns:
            Dictionary with task results
        """
        try:
            from browser_use import Agent, Browser
            
            # Audio-only mode: Using default webcam + TTS audio (no Y4M video file)
            logger.info("🎤 Audio-only mode enabled (default webcam + TTS audio)")
            
            # Try to connect to pre-launched Chrome on port 9222
            # If Chrome is already running with permissions, browser-use will connect to it
            logger.info("🌐 Checking for pre-launched Chrome with permissions...")
            
            import socket
            chrome_running = False
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                result = sock.connect_ex(('127.0.0.1', 9222))
                sock.close()
                if result == 0:
                    chrome_running = True
                    logger.info("✅ Found Chrome on port 9222 - will connect to it")
                    logger.info("💡 Using pre-launched Chrome with automatic permissions!")
            except:
                pass
            
            if chrome_running:
                # Connect to existing Chrome instance using cdp_url
                try:
                    logger.info("🔌 Attempting to connect to Chrome on port 9222...")
                    # First, get the browser websocket URL
                    import requests
                    import json
                    
                    try:
                        response = requests.get("http://127.0.0.1:9222/json/version", timeout=2)
                        version_info = response.json()
                        ws_url = version_info.get("webSocketDebuggerUrl")
                        logger.info(f"📍 Chrome WebSocket URL: {ws_url}")
                    except Exception as e:
                        logger.warning(f"Could not get WebSocket URL: {e}")
                        ws_url = None
                    
                    # Try connecting with CDP URL
                    browser = Browser.from_system_chrome(
                        cdp_url="http://127.0.0.1:9222"
                    )
                    logger.info("✅ Connected to pre-launched Chrome with auto-permissions")
                except Exception as e:
                    logger.error(f"❌ Failed to connect to Chrome on port 9222: {e}")
                    logger.error(f"Error type: {type(e).__name__}")
                    logger.info("💡 Falling back to launching new Chrome instance...")
                    browser = Browser(
                        headless=self.config.headless,
                        channel='chrome'
                    )
            else:
                # Launch new Chrome (permissions will need manual grant)
                logger.info("⚠️  No pre-launched Chrome found on port 9222")
                logger.info("💡 Starting new Chrome - you may need to grant permissions manually")
                logger.info("💡 TIP: Run './launch_chrome_with_permissions.sh' first for auto-permissions")
                
                browser = Browser(
                    headless=self.config.headless,
                    channel='chrome'
                )
            
            # Create screenshot directory if needed
            screenshot_dir = "./browser_screenshots"
            os.makedirs(screenshot_dir, exist_ok=True)
            logger.info(f"📸 Screenshot directory: {os.path.abspath(screenshot_dir)}")
            
            # Create agent
            agent = Agent(
                task=task,
                llm=self.llm,
                browser=browser,
                use_vision=True,
                max_failures=5,
                max_actions_per_step=self.config.max_steps,
                step_timeout=self.config.timeout,
                directly_open_url=True if start_url else False,
                save_recording_path=screenshot_dir  # Enable screenshot capture
            )
            
            logger.info(f"🚀 Starting browser-use agent task: {task}")
            if start_url:
                logger.info(f"📍 Starting URL: {start_url}")
            
            # Include URL in task if needed
            if start_url and start_url not in task:
                full_task = f"Navigate to {start_url} and then: {task}"
                agent.task = full_task
            
            # TTS Integration: Run agent with VMock monitoring if TTS enabled
            if self.config.enable_realtime_tts and self.realtime_tts:
                result = await self._run_agent_with_tts_monitoring(agent, browser)
            else:
                # Run the agent directly - browser starts automatically
                result = await agent.run()
            
            logger.info("✅ Browser-use agent task completed")
            
            # Extract results from AgentHistoryList
            return {
                "success": True,
                "result": result,
                "final_result": str(result),
                "history": result if isinstance(result, list) else [],
                "recording_path": "./browser_screenshots" if self.config.enable_screenshots else None
            }
        
        except Exception as e:
            logger.error(f"❌ Browser-use agent task failed: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "result": None
            }
    
    def run_task_sync(self, task: str, start_url: Optional[str] = None) -> Dict[str, Any]:
        """
        Synchronous wrapper for run_task
        
        Args:
            task: Natural language description of the task
            start_url: Optional starting URL
            
        Returns:
            Dictionary with task results
        """
        try:
            # Check if we're already in an event loop
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # We're in an async context, create a new loop
                import nest_asyncio
                nest_asyncio.apply()
                return loop.run_until_complete(self.run_task(task, start_url))
            else:
                return asyncio.run(self.run_task(task, start_url))
        except RuntimeError:
            # No event loop, create one
            return asyncio.run(self.run_task(task, start_url))
    
    async def _run_agent_with_tts_monitoring(self, agent, browser):
        """
        Run browser-use agent with parallel VMock question monitoring
        
        This runs the agent task while simultaneously monitoring for VMock questions
        in the background. When questions are detected, TTS answers are generated.
        
        Args:
            agent: browser-use Agent instance
            browser: Browser instance
            
        Returns:
            Agent execution result
        """
        logger.info("🎤 Starting agent with VMock TTS monitoring...")
        
        # Create a flag to stop monitoring when agent finishes
        monitoring_active = asyncio.Event()
        monitoring_active.set()  # Start active
        
        answered_questions = [0]  # Use list to allow modification in nested function
        
        async def monitor_vmock_questions():
            """Background task to monitor for VMock questions"""
            check_count = 0
            max_checks = 120  # Monitor for up to 10 minutes (5s intervals)
            
            while monitoring_active.is_set() and check_count < max_checks:
                try:
                    page = await browser.get_current_page()
                    if not page:
                        pages = await browser.get_pages()
                        if pages:
                            page = pages[0]

                    if page:
                        current_url = page.url or ""
                        logger.info(f"🔍 VMock monitor check #{check_count + 1}: {current_url or 'no URL yet'}")

                        # Check if we're in an interview context (recording active, video present)
                        # Look for indicators: video elements, recording UI, calibration done
                        is_interview_context = False
                        try:
                            # Check for video recording elements (common across all interview types)
                            video_count = await page.locator("video").count()
                            recording_indicator = await page.locator("text=/recording|rec|timer|00:/i").count()
                            
                            # Check if on VMock domain (any interview type: elevator-pitch, mock-interview, etc.)
                            is_vmock_domain = 'vmock' in current_url.lower()
                            
                            # Original strict context: require video/timer markers
                            is_interview_context = is_vmock_domain and (video_count > 0 or recording_indicator > 0)

                            # Relaxation: if we're on any vmock page but no video/timer
                            # markers are detected, still treat it as interview context
                            # and let detect_and_answer_vmock_questions() decide based
                            # on the presence of the questions panel. This matches the
                            # new UI where the highlighted question is visible in the
                            # sidebar even if <video> isn't.
                            if is_vmock_domain and not is_interview_context:
                                is_interview_context = True
                                logger.info(
                                    f"📹 Using relaxed interview context (vmock domain, video={video_count}, rec={recording_indicator})"
                                )
                            elif is_interview_context:
                                logger.info(
                                    f"📹 Interview context detected (video={video_count}, recording_ui={recording_indicator})"
                                )
                            else:
                                logger.debug(
                                    f"Not in interview context yet (vmock={is_vmock_domain}, video={video_count}, rec={recording_indicator})"
                                )
                        except Exception as e:
                            logger.debug(f"Context check error: {e}")
                            # Fallback: if on VMock domain, still try to detect questions
                            is_interview_context = 'vmock' in current_url.lower()

                        if is_interview_context:
                            questions_answered = await self.detect_and_answer_vmock_questions(page)
                            answered_questions[0] += questions_answered

                            if questions_answered > 0:
                                logger.info(f"✅ Answered {questions_answered} question(s) - Total: {answered_questions[0]}")
                            else:
                                logger.info("ℹ️ No VMock question detected on this check")
                        else:
                            logger.info("ℹ️ Waiting for interview context (calibration/recording not started yet)")
                    else:
                        logger.info(f"ℹ️ VMock monitor check #{check_count + 1}: no active page available yet")
                    
                    # Wait before next check
                    await asyncio.sleep(5)
                    check_count += 1
                    
                except Exception as e:
                    logger.debug(f"Monitoring check error: {e}")
                    await asyncio.sleep(5)
            
            logger.info(f"🔍 VMock monitoring stopped (Total answered: {answered_questions[0]})")
        
        # Start monitoring task in background
        monitoring_task = asyncio.create_task(monitor_vmock_questions())
        
        try:
            # Run the agent (main task)
            logger.info("🚀 Running browser-use agent...")
            result = await agent.run()
            logger.info("✅ Agent task completed")
            
            # Stop monitoring
            monitoring_active.clear()
            
            # Wait for monitoring to finish (with timeout)
            try:
                await asyncio.wait_for(monitoring_task, timeout=5.0)
            except asyncio.TimeoutError:
                logger.debug("Monitoring task cancelled due to timeout")
                monitoring_task.cancel()
            
            logger.info(f"🎤 TTS Session Summary: {answered_questions[0]} question(s) answered")
            
            return result
            
        except Exception as e:
            # Stop monitoring on error
            monitoring_active.clear()
            monitoring_task.cancel()
            raise
    
    async def detect_and_answer_vmock_questions(self, page) -> int:
        """
        Detect VMock interview questions on page and answer with TTS
        
        Args:
            page: Playwright page object
            
        Returns:
            Number of questions answered
        """
        if not self.config.enable_realtime_tts:
            return 0

        if not self.answer_generator or not self.realtime_tts:
            logger.warning("TTS monitoring is enabled but TTS components are not initialized")
            return 0
        
        answered_count = 0
        answer_generator = self.answer_generator
        realtime_tts = self.realtime_tts

        def normalize_question(text: str) -> str:
            return re.sub(r'\s+', ' ', (text or '')).strip().lower()

        async def answer_question(question_text: str) -> bool:
            question_clean = question_text.strip()
            normalized_question = normalize_question(question_clean)

            if len(question_clean) <= 10:
                return False

            # Avoid re-answering the same logical question
            if normalized_question in self.answered_questions:
                logger.info("⏭️ Skipping already-answered VMock question: %s", question_clean[:120])
                return False

            # Respect a soft cap on the number of questions per session
            if len(self.answered_questions) >= self.max_tts_questions:
                logger.info(
                    "⏹️ Reached max TTS questions for this session (%s); skipping '%s'",
                    self.max_tts_questions,
                    question_clean[:120],
                )
                return False

            logger.info(f"❓ Detected VMock question: {question_clean[:100]}...")
            logger.info("🤔 Generating answer...")
            answer = answer_generator.generate_answer(question_clean)
            logger.info(f"💬 Answer ({len(answer)} chars): {answer[:100]}...")

            success = realtime_tts.generate_and_update(
                text=answer,
                voice=self.config.tts_voice,
                model=self.config.tts_model
            )

            if success:
                self.last_answered_question = normalized_question
                self.answered_questions.append(normalized_question)
                logger.info(
                    "✅ Audio file updated - Chrome will play TTS audio! "
                    "(answered %s question(s) this session)",
                    len(self.answered_questions),
                )
                # Give Chrome time to stream the audio as fake microphone input.
                if self.per_question_play_seconds > 0:
                    logger.info(
                        "⏱️ Waiting %s seconds for TTS playback before continuing...",
                        self.per_question_play_seconds,
                    )
                    await asyncio.sleep(self.per_question_play_seconds)
                return True

            logger.warning("⚠️ TTS audio generation failed for detected VMock question")
            return False
        
        try:
            # ------------------------------------------------------------------
            # 0) Recording-screen question text (primary on calibration/interview
            #    screens). This targets the prominent question shown above the
            #    video area, which changes dynamically each time.
            # ------------------------------------------------------------------
            try:
                recording_selectors = [
                    "main h1", "main h2",
                    "div[role='main'] h1", "div[role='main'] h2",
                    "div[class*='elevator'] h1", "div[class*='elevator'] h2",
                    "div[class*='calibration'] h1", "div[class*='calibration'] h2",
                    "div[class*='question'] h1", "div[class*='question'] h2",
                ]

                for selector in recording_selectors:
                    loc = page.locator(selector)
                    if await loc.count() == 0:
                        continue
                    text = (await loc.first.text_content() or "").strip()
                    if not text:
                        continue

                    logger.info(
                        "🎯 Recording-screen question candidate (%s): %s",
                        selector,
                        text[:160],
                    )
                    if await answer_question(text):
                        answered_count += 1
                        return answered_count
            except Exception as e:
                logger.debug(f"Recording-screen question detection failed: {e}")

            # ------------------------------------------------------------------
            # 1) Directly target VMock's current "Interview Questions" markup
            #    Example snippet:
            #    <div class="interview-questions-view-body" role="tablist">
            #      <div class="... interview-questions-view-body-item" tabindex="0" role="tab">
            #        <div class="interview-questions-view-body-item-count">1.</div>
            #        <div class="interview-questions-view-body-item-content">Question text...</div>
            #      </div>
            #    </div>
            # ------------------------------------------------------------------
            try:
                # Simplest and most robust: take the first visible question text
                # from the interview-questions-view-body panel. In the current
                # VMock UI, the active question is rendered at the top and uses
                # the "interview-questions-view-body-item-content" class.
                body_panel = page.locator("div.interview-questions-view-body")
                contents = body_panel.locator(".interview-questions-view-body-item-content")

                if await contents.count() > 0:
                    highlighted_text = await contents.first.text_content()
                    logger.info("🧩 VMock sidebar question candidate: %s", (highlighted_text or "").strip()[:120])
                    if highlighted_text and await answer_question(highlighted_text):
                        answered_count += 1
                        return answered_count
            except Exception as e:
                logger.debug(f"Direct interview-questions-view-body detection failed: {e}")

            # ------------------------------------------------------------------
            # 2) Prefer the currently highlighted question in the "Interview
            #    Questions" sidebar on the recording screen (generic header-based
            #    detection for older layouts).
            # ------------------------------------------------------------------
            try:
                sidebar = page.locator("text=/Interview Questions/i")
                if await sidebar.count() > 0:
                    sidebar_header = sidebar.first
                    panel_root = sidebar_header.locator("xpath=../..")

                    active_selectors = [
                        "[aria-current='true']",
                        "[aria-selected='true']",
                        "[class*='active']",
                        "[class*='selected']",
                    ]
                    active_element = None
                    for sel in active_selectors:
                        cand = panel_root.locator(sel)
                        if await cand.count() > 0:
                            active_element = cand.first
                            break

                    if active_element is None:
                        card_candidates = panel_root.locator(
                            "xpath=.//li | .//div[@role='listitem'] | .//div[contains(@class,'question')]"
                        )
                        if await card_candidates.count() > 0:
                            active_element = card_candidates.first

                    if active_element is not None:
                        try:
                            highlighted_text = await active_element.text_content()
                            if highlighted_text and await answer_question(highlighted_text):
                                answered_count += 1
                                return answered_count
                        except Exception as e:
                            logger.debug(f"Error reading highlighted sidebar question: {e}")
            except Exception as e:
                logger.debug(f"Sidebar question panel detection failed: {e}")

            # ------------------------------------------------------------------
            # 3) Generic VMock question selectors (fallback)
            #    Covers: elevator-pitch, mock-interview, practice interviews
            # ------------------------------------------------------------------
            question_selectors = [
                'text=/^Q\\.|Question/i',  # Questions starting with "Q." or "Question"
                'text=/Please tell/i',      # "Please tell me about yourself"
                'text=/Describe/i',         # "Describe your experience"
                'text=/What.*about/i',      # "What can you tell us about..."
                'text=/Tell me about/i',    # "Tell me about yourself"
                'text=/introduce yourself/i',  # "Introduce yourself"
                'text=/elevator pitch/i',      # Elevator pitch specific
                'text=/30 seconds/i',          # Time-based prompts
                '[class*="question"]',      # Elements with "question" in class
                '[class*="prompt"]',        # Prompt text
                '[data-testid*="question"]', # Data attributes
                'h1, h2, h3, h4',           # Headers often contain questions
                '[role="heading"]'          # ARIA headings
            ]
            
            # Check each selector
            for selector in question_selectors:
                try:
                    elements = await page.locator(selector).all()
                    
                    for element in elements[:3]:  # Check up to 3 matches per selector
                        try:
                            question_text = await element.text_content()
                            if question_text and await answer_question(question_text):
                                answered_count += 1
                                break  # One question at a time
                                    
                        except Exception as e:
                            logger.debug(f"Error processing element: {e}")
                            continue
                            
                    if answered_count > 0:
                        break  # Found and answered a question

                except Exception as e:
                    logger.debug(f"Selector {selector} failed: {e}")
                    continue

            # ------------------------------------------------------------------
            # 4) Fallback: body-text regex search for question-like sentences
            # ------------------------------------------------------------------
            if answered_count == 0:
                try:
                    body_text = await page.locator("body").inner_text(timeout=2000)
                    body_text = re.sub(r'\s+', ' ', body_text or '').strip()

                    fallback_patterns = [
                        r'(please tell me about yourself[^.?!]{0,250}[.?!]?)',
                        r'(tell me about yourself[^.?!]{0,250}[.?!]?)',
                        r'(describe your experience[^.?!]{0,250}[.?!]?)',
                        r'(what can you tell us about[^.?!]{0,250}[.?!]?)',
                        r'((?:q\.?|question)\s*[:\-]?\s*[^.?!]{10,250}[.?!]?)',
                    ]

                    for pattern in fallback_patterns:
                        match = re.search(pattern, body_text, re.IGNORECASE)
                        if match and await answer_question(match.group(1)):
                            answered_count += 1
                            break

                except Exception as e:
                    logger.debug(f"Fallback body-text question detection failed: {e}")

            # ------------------------------------------------------------------
            # 5) Optional GPT‑4 Vision fallback (screenshot-based question
            #    detection). This is controlled via VMOCK_TTS_VISION env flag
            #    to avoid unnecessary cost.
            # ------------------------------------------------------------------
            if (
                answered_count == 0
                and self.enable_vision_question_detection
                and self.question_detector is not None
            ):
                try:
                    screenshot_dir = Path(self.config.screenshot_dir)
                    screenshot_dir.mkdir(parents=True, exist_ok=True)
                    screenshot_path = screenshot_dir / f"vmock_q_{int(time.time())}.png"
                    await page.screenshot(path=str(screenshot_path), full_page=False)
                    logger.info(
                        "🖼️ Captured screenshot for vision-based question detection: %s",
                        screenshot_path,
                    )

                    from openai import OpenAI

                    client = OpenAI(api_key=self.config.api_key or os.getenv("OPENAI_API_KEY"))
                    vision_question = self.question_detector.detect_from_screenshot(
                        str(screenshot_path),
                        client,
                    )
                    if vision_question and await answer_question(vision_question):
                        answered_count += 1
                except Exception as e:
                    logger.warning(f"Vision-based question detection failed: {e}")
                    
        except Exception as e:
            logger.error(f"Error detecting VMock questions: {e}")
        
        return answered_count
    
    async def run_task_with_tts(
        self,
        task: str,
        start_url: Optional[str] = None,
        candidate_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Run task with real-time TTS question answering for VMock interviews
        
        This is a wrapper around run_task() that adds VMock question monitoring.
        For now, we just run the regular task and note that monitoring happens via
        browser-use's action callbacks in the future.
        
        Args:
            task: Natural language task description
            start_url: Starting URL
            candidate_context: Candidate info for answer generation (name, position, skills, etc.)
            
        Returns:
            Task results with TTS metadata
        """
        if not self.config.enable_realtime_tts:
            logger.warning("Real-time TTS not enabled, falling back to regular task")
            return await self.run_task(task, start_url)
        
        # Set candidate context if provided
        if candidate_context:
            self.answer_generator.set_context(candidate_context)
        
        logger.info("🎤 Starting VMock interview with real-time TTS answering")
        logger.info(f"   Audio file: {self.realtime_tts.get_audio_path()}")
        logger.info(f"   Voice: {self.config.tts_voice}")
        logger.info("💡 Note: TTS audio ready for VMock questions!")
        logger.info("💡 Browser-use will handle navigation and actions")
        
        try:
            # Run the regular task - browser-use handles all automation
            result = await self.run_task(task, start_url)
            
            # Add TTS metadata to result
            if isinstance(result, dict):
                result['tts_enabled'] = True
                result['audio_file'] = self.realtime_tts.get_audio_path()
                result['tts_voice'] = self.config.tts_voice
            
            return result
            
        except Exception as e:
            logger.error(f"Task with TTS failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "result": None
            }
    
    def run_task_with_tts_sync(
        self,
        task: str,
        start_url: Optional[str] = None,
        candidate_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Synchronous wrapper for run_task_with_tts"""
        return asyncio.run(self.run_task_with_tts(task, start_url, candidate_context))
    
    # ------------------------------------------------------------------
    # On-demand TTS helper methods (used by test_agent_tts, test_tts_on_demand,
    # and external scripts described in TTS_ON_DEMAND_GUIDE.md)
    # ------------------------------------------------------------------

    def generate_audio_response(self, question: str, output_filename: str = "interview_answer.mp3"):
        """Generate an audio response for a question using on-demand TTS.

        Returns the Path to the generated audio file, or None if TTS is
        disabled or generation fails.
        """
        if not self.config.enable_tts or not self.tts_generator:
            logger.warning("On-demand TTS is not enabled or tts_generator is unavailable")
            return None

        try:
            audio_path = self.tts_generator.answer_question(
                question=question,
                output_filename=output_filename,
            )
            return audio_path
        except Exception as e:
            logger.error(f"Failed to generate on-demand TTS audio: {e}")
            return None

    def get_audio_response_instructions(self, audio_file) -> str:
        """Return human-readable instructions for using the generated audio.

        This matches the guidance in TTS_ON_DEMAND_GUIDE.md and references the
        launch_chrome_with_audio.sh helper script.
        """
        try:
            from pathlib import Path as _Path

            audio_path = _Path(audio_file)
            rel_path = audio_path.as_posix()
        except Exception:
            rel_path = str(audio_file)

        instructions = [
            "To use this audio as microphone input in Chrome:",
            "",
            "1. Open a terminal",
            "2. Navigate to the Automation_mcp_agent directory",
            "3. Run:",
            f"   ./launch_chrome_with_audio.sh {rel_path}",
        ]
        return "\n".join(instructions)
    
    def answer_question_with_tts(self, question: str, context: Optional[Dict[str, Any]] = None) -> bool:
        """
        Generate answer to question and update audio file
        
        Args:
            question: Interview question text
            context: Optional context for answer generation
            
        Returns:
            True if successful
        """
        if not self.config.enable_realtime_tts:
            logger.error("Real-time TTS not enabled")
            return False
        
        try:
            # Set context if provided
            if context:
                self.answer_generator.set_context(context)
            
            # Generate answer
            logger.info(f"🤔 Generating answer for: {question[:100]}...")
            answer = self.answer_generator.generate_answer(question)
            
            # Convert to audio and update file
            logger.info(f"💬 Answer: {answer[:100]}...")
            success = self.realtime_tts.generate_and_update(
                text=answer,
                voice=self.config.tts_voice,
                model=self.config.tts_model
            )
            
            if success:
                logger.info("✅ Audio file updated - Chrome will use new audio")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to answer question: {e}")
            return False
    
    async def close(self):
        """Clean up browser resources"""
        if self.browser:
            try:
                # browser-use handles cleanup internally
                logger.info("Browser cleanup handled by browser-use")
            except Exception as e:
                logger.error(f"Error during cleanup: {e}")
            finally:
                self.browser = None
                self.context = None


class BrowserFactory:
    """
    Factory for creating browser agents
    Supports both Playwright-based and browser-use agents
    """
    
    @staticmethod
    def create_agent(engine: str = "playwright", **kwargs) -> Any:
        """
        Create a browser agent based on engine type
        
        Args:
            engine: 'playwright' or 'browser-use'
            **kwargs: Configuration parameters
            
        Returns:
            Browser agent instance
        """
        if engine == "browser-use":
            config = BrowserUseConfig(**kwargs) if kwargs else None
            return BrowserUseAgent(config=config)
        elif engine == "playwright":
            from Automation_mcp_agent.agents.browser_agent import BrowserAgent
            return BrowserAgent(**kwargs)
        else:
            raise ValueError(f"Unsupported browser engine: {engine}. Choose 'playwright' or 'browser-use'")


# Example usage
if __name__ == "__main__":
    import sys
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Example 1: Simple navigation
    print("=" * 80)
    print("Example 1: Navigate to Google and search")
    print("=" * 80)
    
    agent = BrowserUseAgent()
    result = agent.run_task_sync(
        task="Go to google.com and search for 'VMock'",
        start_url="https://www.google.com"
    )
    
    print(f"Success: {result['success']}")
    print(f"Result: {result.get('final_result', result.get('error'))}")
    
    # Example 2: Using factory pattern
    print("\n" + "=" * 80)
    print("Example 2: Using factory pattern")
    print("=" * 80)
    
    # Choose engine dynamically
    engine = "browser-use" if "--use-ai" in sys.argv else "playwright"
    agent = BrowserFactory.create_agent(engine=engine)
    
    print(f"Created agent with engine: {engine}")
    print(f"Agent type: {type(agent).__name__}")
