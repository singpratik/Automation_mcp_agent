import asyncio
import importlib
import inspect
import logging
import os
import re
import threading
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import nest_asyncio
    nest_asyncio.apply()
except Exception:
    pass  # uvloop or other incompatible loop — thread-based fallback will be used instead
try:
    # Preferred: local module api_monitor.py (same directory / project root)
    NetworkAPIMonitor = importlib.import_module("api_monitor").NetworkAPIMonitor
except Exception:  # noqa: BLE001
    try:
        # Fallback: package-style import when project is installed as Automation_mcp_agent
        NetworkAPIMonitor = importlib.import_module("Automation_mcp_agent.api_monitor").NetworkAPIMonitor
    except Exception:  # noqa: BLE001
        # Final fallback: disable API monitoring entirely instead of crashing
        NetworkAPIMonitor = None
        logging.getLogger(__name__).warning(
            "API monitor module not found (api_monitor / Automation_mcp_agent.api_monitor); "
            "network API monitoring will be disabled."
        )

# Setup logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Suppress noisy browser-use cleanup errors (Python 3.13 + uvloop incompatibility)
bubus_logger = logging.getLogger("bubus")
bubus_logger.setLevel(logging.CRITICAL)  # Only show CRITICAL, suppress ERROR spam

class BrowserRetryConfig:
    """Configuration for browser action retries"""
    def __init__(self, max_retries: int = 3, backoff_factor: float = 1.5, timeout: int = 30):
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.timeout = timeout

class BrowserAgent:
    """
    UI Agent (browser-use with Chrome channel)
    - Handles UI flows (automated browser actions)
    - Uses browser-use session/runtime (no direct Playwright orchestration)
    - Defaults to Chrome channel for stable local browser execution
    - DOM validation with retry logic and selector fallback
    - Visual checks with screenshot-on-error capabilities
    - Supports fake camera/mic for automated media stream testing
    """
    
    # Selector fallback chains for common UI elements
    SELECTOR_FALLBACKS = {
        "search_box": [
            "input[name='q']",
            "input[type='search']",
            "input[type='text']",
            "input[aria-label*='search' i]",
            "input[placeholder*='search' i]",
            "[role='searchbox']"
        ],
        "button": [
            "button:has-text('{text}')",
            "[role='button']:has-text('{text}')",
            "a:has-text('{text}')",
            "[onclick]:has-text('{text}')"
        ],
        "submit": [
            "button[type='submit']",
            "input[type='submit']",
            "button:has-text('submit')",
            "button:has-text('search')"
        ]
    }
    
    def __init__(self, 
                 y4m_file_path: Optional[str] = None, 
                 wav_file_path: Optional[str] = None,
                 browser_channel: str = "chrome",
                 browser_engine: str = "browser-use",
                 retry_config: Optional[BrowserRetryConfig] = None,
                 screenshot_dir: str = "browser_screenshots",
                 api_report_dir: str = "reports/browser_api_monitor"):
        """
        Initialize BrowserAgent
        
        Args:
            y4m_file_path: Path to Y4M video file for fake camera
            wav_file_path: Path to WAV file for fake microphone
            browser_channel: Browser channel ('chrome', 'chromium', or 'firefox')
            retry_config: Retry configuration for browser actions
            screenshot_dir: Directory to save screenshots on errors
        """
        default_y4m: str = os.path.join("Resources", "Johnny_1280x720_60.y4m")
        default_wav: str = os.path.join("Resources", "sample.wav")
        
        self.y4m_file_path: str = y4m_file_path or default_y4m
        self.wav_file_path: str = wav_file_path or default_wav
        self.browser_channel: str = browser_channel or "chrome"
        self.browser_engine: str = browser_engine or "browser-use"
        self.retry_config: BrowserRetryConfig = retry_config or BrowserRetryConfig()
        self.screenshot_dir: str = screenshot_dir
        self.api_report_dir: str = api_report_dir
        self.page = None
        self.browser = None
        self.browser_session = None
        self.api_monitor: Optional[Any] = None
        self.last_api_report: Dict[str, str] = {}
        
        # Create screenshot directory
        Path(self.screenshot_dir).mkdir(parents=True, exist_ok=True)
        
        logger.info(
            "BrowserAgent initialized with engine=%s channel=%s retries=%s",
            self.browser_engine,
            self.browser_channel,
            self.retry_config.max_retries,
        )

    def _run_async_blocking(self, coro):
        """Run async coroutine from sync context safely.
        
        Strategy: always run in a dedicated non-daemon thread with its own event loop.
        This avoids conflicts with uvloop (used by Streamlit/uvicorn) and nest_asyncio
        incompatibilities. The thread is non-daemon so Chrome CDP connections stay alive.
        """
        result_container: Dict[str, Any] = {}
        error_container: Dict[str, BaseException] = {}

        def _runner():
            try:
                new_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(new_loop)
                try:
                    result_container["value"] = new_loop.run_until_complete(coro)
                finally:
                    # Suppress cleanup errors from browser-use event bus
                    try:
                        new_loop.close()
                    except Exception:
                        pass
            except BaseException as exc:  # noqa: BLE001
                error_container["error"] = exc

        thread = threading.Thread(target=_runner, daemon=False)
        thread.start()
        thread.join(timeout=180)
        if not thread.is_alive() and "error" in error_container:
            raise error_container["error"]
        return result_container.get("value")

    def _enhance_prompt_for_agent(self, prompt: str) -> str:
        """Senior Engineer Pattern: Break down complex prompts for better LLM comprehension."""
        # Add explicit guidance for login workflows
        if "log in" in prompt.lower() or "login" in prompt.lower():
            prompt = prompt.replace("Log in with", "IMPORTANT: First locate and click the Login/Sign In button to open login form, then carefully find the Email field and type")
            prompt = prompt.replace("Fill in password", "After email is entered, locate the Password field and type")
        
        # Add explicit wait guidance for uploads
        if "upload" in prompt.lower() and "wait" in prompt.lower():
            prompt = prompt.replace("upload", "click the upload button and select")
            prompt += " CRITICAL: After file selection, wait at least 30 seconds for processing progress bar to complete before proceeding."
        
        # Add explicit element identification for form fields  
        if "email" in prompt.lower() and "@" in prompt:
            email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', prompt)
            if email_match:
                email = email_match.group(0)
                prompt = prompt.replace(email, f"EXACT_EMAIL[{email}]")
        
        # Add step numbering for clarity
        if "," in prompt and len(prompt.split(",")) > 3:
            steps = [s.strip() for s in prompt.split(",")]
            numbered = "\\n".join([f"Step {i+1}: {step}" for i, step in enumerate(steps)])
            logger.info(f"Complex workflow detected, breaking into {len(steps)} steps")
            return f"Execute this multi-step workflow carefully:\\n{numbered}"
        
        return prompt

    def _extract_url_and_action(self, prompt: str) -> Dict[str, Optional[str]]:
        """Extract coarse action + URL for deterministic browser-use fallback mode."""
        action = "open"
        lowered = prompt.lower()
        if "click" in lowered:
            action = "click"
        elif "search" in lowered or "type" in lowered:
            action = "search"

        url = None
        match = re.search(r"(https?://[^\s]+)", prompt)
        if match:
            url = match.group(1)
        else:
            match = re.search(r"\b([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})\b", prompt)
            if match:
                url = "https://" + match.group(1)

        return {"action": action, "url": url}

    def _get_browser_profile(self):
        """Build browser-use profile and force chrome channel by default."""
        import importlib

        browser_use_module = importlib.import_module("browser_use")
        BrowserProfile = getattr(browser_use_module, "BrowserProfile")

        requested = (self.browser_channel or "chrome").lower().strip()
        allowed = {
            "chromium",
            "chrome",
            "chrome-beta",
            "chrome-dev",
            "chrome-canary",
            "msedge",
            "msedge-beta",
            "msedge-dev",
            "msedge-canary",
        }
        channel = requested if requested in allowed else "chrome"
        if channel != requested:
            logger.warning("Unsupported channel '%s', forcing 'chrome'", requested)

        headless = os.getenv("BROWSER_HEADLESS", "false").lower() in {"1", "true", "yes"}
        return BrowserProfile(
            channel=channel,
            headless=headless,
            minimum_wait_page_load_time=0.25,
            wait_for_network_idle_page_load_time=0.75,
            wait_between_actions=0.2,
            highlight_elements=True,
            enable_default_extensions=False,  # skip extension downloads (avoids SSL hang)
            captcha_solver=False,
        )

    def _build_llm_for_browser_use(self):
        """Provide a browser-use compatible model if Browser Use cloud key is not configured."""
        if os.getenv("BROWSER_USE_API_KEY"):
            return None

        openai_key = os.getenv("OPENAI_API_KEY")
        if not openai_key:
            return None

        import importlib

        openai_chat_module = importlib.import_module("browser_use.llm.openai.chat")
        ChatOpenAI = getattr(openai_chat_module, "ChatOpenAI")

        return ChatOpenAI(
            model=os.getenv("BROWSER_USE_MODEL", "gpt-4o-mini"),
            api_key=openai_key,
            base_url=os.getenv("OPENAI_BASE_URL") or None,
            timeout=60.0,
        )

    def _initialize_api_monitoring(self):
        """Start collecting network activity for the active page."""
        if not self.page:
            return

        # If NetworkAPIMonitor could not be imported, skip API monitoring gracefully
        if NetworkAPIMonitor is None:
            logger.info("API monitoring disabled: NetworkAPIMonitor not available")
            self.api_monitor = None
            self.last_api_report = {}
            return

        if not hasattr(self.page, "on"):
            logger.info("API monitoring skipped: current browser-use page does not expose Playwright event hooks")
            self.api_monitor = None
            self.last_api_report = {}
            return

        self.api_monitor = NetworkAPIMonitor(report_dir=self.api_report_dir)
        self.last_api_report = {}
        monitor = self.api_monitor
        if not monitor:
            return
        self.page.on("request", monitor.on_playwright_request)
        self.page.on("response", monitor.on_playwright_response)
        self.page.on("requestfailed", monitor.on_playwright_request_failed)
        logger.info("API monitoring enabled for current browser session")

    def _finalize_api_report(self, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, str]:
        """Write API monitoring reports once per browser session."""
        if not self.api_monitor:
            return self.last_api_report
        if self.last_api_report:
            return self.last_api_report

        try:
            self.last_api_report = self.api_monitor.generate_reports(metadata=metadata)
            logger.info("API monitoring reports generated: %s", self.last_api_report)
        except Exception as e:
            logger.error(f"Failed to generate API monitoring report: {e}")
            self.last_api_report = {}
        return self.last_api_report

    def _close_browser_with_reporting(self, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, str]:
        """Close the browser and then persist captured network activity."""
        if self.browser_session:
            try:
                # Suppress event loop cleanup errors during browser-use shutdown
                import warnings
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    self._run_async_blocking(self.browser_session.stop())
                logger.info("browser-use session stopped successfully")
            except (AssertionError, RuntimeError) as e:
                # Ignore event loop cleanup errors from browser-use internals
                logger.debug(f"Suppressed browser-use cleanup error: {e}")
            except Exception as e:
                logger.error(f"Error stopping browser-use session: {e}")
            finally:
                self.browser_session = None
                self.browser = None
                self.page = None
        elif self.browser:
            try:
                self.browser.close()
                logger.info("Browser closed successfully")
            except Exception as e:
                logger.error(f"Error closing browser: {e}")
            finally:
                self.browser = None
                self.page = None

        report_paths = self._finalize_api_report(metadata=metadata)
        self.api_monitor = None
        return report_paths

    def _take_screenshot(self, label: str = "error") -> str:
        """Take a screenshot and save to file"""
        if not self.page:
            return ""
        
        try:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"{self.screenshot_dir}/screenshot_{label}_{timestamp}.png"
            capture = self.page.screenshot(path=filename)
            if inspect.isawaitable(capture):
                self._run_async_blocking(capture)
            logger.info(f"Screenshot saved: {filename}")
            return filename
        except Exception as e:
            logger.error(f"Failed to take screenshot: {e}")
            return ""

    def _safe_page_title(self) -> str:
        """Return page title when available without raising if the page is already closed."""
        if not self.page:
            return "Unavailable"

        try:
            title_call = self.page.title()
            if inspect.isawaitable(title_call):
                return self._run_async_blocking(title_call) or "Unavailable"
            return title_call
        except Exception as e:
            logger.warning(f"Could not read page title: {e}")
            return "Unavailable"

    def _find_element_with_fallback(self, selectors: List[str], action_type: str = "find"):
        """
        Find element using fallback selector chain
        
        Args:
            selectors: List of selectors to try in order
            action_type: Type of action for logging
            
        Returns:
            Found element or None
        """
        for i, selector in enumerate(selectors):
            try:
                page = self.page
                if not page:
                    return None
                element = page.query_selector(selector)
                if inspect.isawaitable(element):
                    element = self._run_async_blocking(element)
                if element:
                    logger.info(f"✅ Found element with selector (attempt {i+1}/{len(selectors)}): {selector}")
                    return element
            except Exception as e:
                logger.debug(f"Selector attempt {i+1} failed: {selector} - {str(e)}")
                continue
        
        logger.warning(f"❌ No element found after trying {len(selectors)} selectors")
        return None

    def _retry_action(self, action_func, action_name: str = "action", *args, **kwargs):
        """
        Execute an action with retry logic and exponential backoff
        
        Args:
            action_func: Function to execute
            action_name: Name of action for logging
            *args, **kwargs: Arguments to pass to action_func
            
        Returns:
            Result of action or None if all retries failed
        """
        wait_time = 1
        
        for attempt in range(1, self.retry_config.max_retries + 1):
            try:
                logger.info(f"[Attempt {attempt}/{self.retry_config.max_retries}] Executing: {action_name}")
                result = action_func(*args, **kwargs)
                logger.info(f"✅ {action_name} succeeded")
                return result
            except Exception as e:
                logger.warning(f"❌ {action_name} failed (attempt {attempt}): {str(e)}")
                
                if attempt < self.retry_config.max_retries:
                    logger.info(f"⏳ Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                    wait_time *= self.retry_config.backoff_factor
                else:
                    screenshot = self._take_screenshot(f"{action_name}_failed")
                    logger.error(f"❌ {action_name} failed after {self.retry_config.max_retries} attempts (screenshot: {screenshot})")
                    return None
        
        return None

    def run_task(self, prompt: str) -> str:
        """Execute browser task using browser-use with Chrome channel."""
        if not prompt or not str(prompt).strip():
            return "❌ Prompt cannot be empty."

        if self.browser_engine.lower() != "browser-use":
            logger.warning("Unsupported browser_engine '%s', forcing browser-use", self.browser_engine)

        try:
            llm = self._build_llm_for_browser_use()
            has_cloud_key = bool(os.getenv("BROWSER_USE_API_KEY"))
            enable_agent_mode = os.getenv("BROWSER_USE_ENABLE_AGENT", "false").lower() in {"1", "true", "yes"}

            if enable_agent_mode and (llm is not None or has_cloud_key):
                logger.info("browser-use agent mode enabled")
                result = self._run_async_blocking(self._run_browser_use_agent_task(prompt=prompt, llm=llm))
                return str(result)

            logger.info("Using scripted browser-use execution mode (stable default for Streamlit)")
            result = self._run_async_blocking(self._run_browser_use_scripted_task(prompt=prompt))
            return str(result)
        except Exception as e:
            logger.error("browser-use automation failed: %s", e, exc_info=True)
            if self.page:
                self._take_screenshot("automation_error")
            report_paths = self._close_browser_with_reporting(
                {"prompt": prompt, "status": "failed", "error": str(e)}
            )
            msg = f"❌ browser-use automation failed: {e}"
            if report_paths:
                msg += (
                    f"\n📄 API monitoring report (HTML): {report_paths.get('html', 'n/a')}"
                    f"\n📄 API monitoring report (JSON): {report_paths.get('json', 'n/a')}"
                )
            return msg

    async def _run_browser_use_agent_task(self, prompt: str, llm=None) -> str:
        import importlib

        browser_use_module = importlib.import_module("browser_use")
        Agent = getattr(browser_use_module, "Agent")
        BrowserSession = getattr(browser_use_module, "BrowserSession")

        # Senior Engineer Enhancement: Preprocess complex prompts for better success
        enhanced_prompt = self._enhance_prompt_for_agent(prompt)
        
        parsed = self._extract_url_and_action(enhanced_prompt)
        profile = self._get_browser_profile()
        session = BrowserSession(browser_profile=profile)
        self.browser_session = session
        self.browser = session
        self.last_api_report = {}

        await session.start()
        self.page = await session.get_current_page()
        if not self.page:
            self.page = await session.new_page()
        self._initialize_api_monitoring()

        agent_kwargs: Dict[str, Any] = {
            "task": prompt,
            "browser_session": session,
            "max_failures": int(os.getenv("BROWSER_USE_MAX_FAILURES", "8")),
            "step_timeout": int(os.getenv("BROWSER_USE_STEP_TIMEOUT", "45")),
            "use_vision": True,
        }
        if llm is not None:
            agent_kwargs["llm"] = llm

        max_steps = int(os.getenv("BROWSER_USE_MAX_STEPS", "50"))
        timeout_secs = int(os.getenv("BROWSER_USE_TIMEOUT", "600"))
        
        logger.info(f"🚀 Starting agent with max_steps={max_steps}, timeout={timeout_secs}s, max_failures={agent_kwargs['max_failures']}")
        try:
            agent_instance = Agent(**agent_kwargs)
            history = await asyncio.wait_for(
                agent_instance.run(max_steps=max_steps),
                timeout=timeout_secs,
            )
            logger.info(f"✅ Agent completed {len(history.history)} steps")
        except asyncio.TimeoutError:
            logger.error("browser-use agent timed out after %ss", timeout_secs)
            await session.stop()
            return f"❌ browser-use agent timed out after {timeout_secs}s. Complex workflows need more time. Current: {timeout_secs}s, Steps attempted: ~{max_steps}. Try breaking into smaller tasks or increase BROWSER_USE_TIMEOUT/BROWSER_USE_MAX_STEPS in .env"

        try:
            page_title = await session.get_current_page_title()
        except Exception:
            page_title = self._safe_page_title()

        await session.stop()
        self.browser_session = None
        self.browser = None
        self.page = None

        report_paths = self._finalize_api_report(
            {
                "prompt": prompt,
                "url": parsed.get("url"),
                "title": page_title,
                "mode": "browser-use-agent",
                "status": "completed" if history.is_successful() else "failed",
            }
        )
        self.api_monitor = None

        final_text = history.final_result() or ""
        errors = [e for e in history.errors() if e]
        if not final_text and errors:
            final_text = " | ".join(errors)
        if not final_text:
            final_text = "Task finished but no final textual summary was returned."

        if history.is_successful() is False:
            result_msg = f"❌ browser-use agent task failed.\nDetails: {final_text}\n"
            result_msg += f"Steps completed: {len(history.history)}/{max_steps}\n"
            result_msg += f"\n💡 SENIOR ENGINEER TIP: Complex workflow detected.\n"
            result_msg += f"   Current limits: max_steps={max_steps}, timeout={timeout_secs}s, max_failures={agent_kwargs['max_failures']}\n"
            result_msg += f"   Solutions:\n"
            result_msg += f"   1. Break into smaller prompts (e.g., login first, then upload, then feedback)\n"
            result_msg += f"   2. Increase limits in .env: BROWSER_USE_MAX_STEPS=50, BROWSER_USE_TIMEOUT=600\n"
            result_msg += f"   3. Simplify task: Remove steps after first failure point\n"
        else:
            result_msg = f"✅ browser-use (chrome) completed {len(history.history)} steps.\nSummary: {final_text}\nPage title: {page_title}"

        if report_paths:
            result_msg += (
                f"\n📄 API monitoring report (HTML): {report_paths.get('html', 'n/a')}"
                f"\n📄 API monitoring report (JSON): {report_paths.get('json', 'n/a')}"
            )
        return result_msg

    async def _run_browser_use_scripted_task(self, prompt: str) -> str:
        """No-LLM deterministic mode using browser-use BrowserSession + Chrome channel.
        Uses session.navigate_to() (the correct browser-use navigation API) and
        page.evaluate() for DOM interaction — avoids CDP tab-detachment issues.
        """
        browser_use_module = importlib.import_module("browser_use")
        BrowserSession = getattr(browser_use_module, "BrowserSession")

        extracted = self._extract_url_and_action(prompt)
        action = extracted["action"]
        url = extracted["url"]
        if not url:
            return "❌ Could not parse a URL from prompt. Add a full URL like https://example.com"

        profile = self._get_browser_profile()
        session = BrowserSession(browser_profile=profile)
        self.browser_session = session
        self.last_api_report = {}

        logger.info("🌐 browser-use scripted: launching Chrome → %s", url)
        await session.start()

        # navigate_to is the proper browser-use session-level navigation API
        await session.navigate_to(url)
        await asyncio.sleep(1.5)

        try:
            page_title = await session.get_current_page_title()
        except Exception:
            page_title = url
        result_msg = f"✅ Navigated to {url}, page title: {page_title}"

        # get underlying browser-use Page for DOM interaction
        bu_page = await session.get_current_page()

        if action == "search" and bu_page:
            search_match = re.search(r"search for ([\w\s]+)", prompt, re.IGNORECASE)
            query = search_match.group(1).strip() if search_match else "test"
            js = f"""
                () => {{
                    const inputs = ['input[name=q]','input[type=search]','input[type=text]','[role=searchbox]'];
                    for (const sel of inputs) {{
                        const el = document.querySelector(sel);
                        if (el) {{ el.value = {repr(query)}; el.form && el.form.submit(); return true; }}
                    }}
                    return false;
                }}
            """
            try:
                found = await bu_page.evaluate(js)
                await asyncio.sleep(1.5)
                result_msg += f"\n{'✅' if found else '❌'} Searched for '{query}'"
            except Exception as e:
                result_msg += f"\n❌ Search failed: {e}"

        elif action == "click" and bu_page:
            click_match = re.search(r"click\s+(?:on\s+)?(?:the\s+)?([\"']?[^\"']+[\"']?)", prompt, re.IGNORECASE)
            btn_text = click_match.group(1).strip().strip("\"'") if click_match else ""
            btn_text = re.sub(r"^on\s+", "", btn_text, flags=re.IGNORECASE).strip()
            if btn_text:
                safe_text = btn_text.replace("'", "\\'")
                js = f"""
                    () => {{
                        const tags = ['a','button','[role=button]','input[type=submit]'];
                        for (const tag of tags) {{
                            const els = document.querySelectorAll(tag);
                            for (const el of els) {{
                                if (el.textContent.toLowerCase().includes('{safe_text.lower()}')) {{
                                    el.click(); return true;
                                }}
                            }}
                        }}
                        return false;
                    }}
                """
                try:
                    clicked = await bu_page.evaluate(js)
                    await asyncio.sleep(1.0)
                    result_msg += f"\n{'✅' if clicked else '❌'} Click '{btn_text}'"
                except Exception as e:
                    result_msg += f"\n❌ Click failed: {e}"
            else:
                result_msg += "\n❌ No click target found in prompt."

        await session.stop()
        self.browser_session = None
        self.browser = None
        self.page = None

        report_paths = self._finalize_api_report(
            {
                "prompt": prompt,
                "url": url,
                "title": page_title,
                "mode": "browser-use-scripted-chrome",
                "status": "completed",
            }
        )
        self.api_monitor = None

        if report_paths:
            result_msg += (
                f"\n📄 API monitoring report (HTML): {report_paths.get('html', 'n/a')}"
                f"\n📄 API monitoring report (JSON): {report_paths.get('json', 'n/a')}"
            )
        return result_msg

    def run_ui_tests(self, ui_tests: List[str]) -> List[Dict[str, Any]]:
        """
        Run a list of UI test prompts and return their results with enhanced error handling.
        Each test in ui_tests should be a string prompt describing the UI flow or check.
        
        Args:
            ui_tests: List of test prompts
            
        Returns:
            List of test results with status and details
        """
        results = []
        for i, test in enumerate(ui_tests, 1):
            try:
                logger.info(f"Running UI test {i}/{len(ui_tests)}: {test[:50]}...")
                result = self.run_task(test)
                results.append({
                    "test": test,
                    "result": result,
                    "status": "pass" if "✅" in result else "fail"
                })
            except Exception as e:
                logger.error(f"UI test {i} raised exception: {e}", exc_info=True)
                results.append({
                    "test": test,
                    "result": f"❌ Test failed with exception: {str(e)}",
                    "status": "error"
                })
        
        return results

    def get_live_logs(self) -> List[str]:
        """Get live execution logs"""
        return []

    def close_browser(self):
        """Close browser if open"""
        self._close_browser_with_reporting({"status": "closed_by_cleanup"})

    def __del__(self):
        """Cleanup on deletion"""
        self.close_browser()
