import os
import sys
import importlib.util
import logging
from io import StringIO

# Setup logger for module-level functions
logger = logging.getLogger(__name__)


def _relaunch_with_project_venv_if_needed():
    """Re-launch the app with the project venv when Streamlit is unavailable in the current interpreter."""
    if importlib.util.find_spec("streamlit") is not None:
        return

    project_root = os.path.dirname(os.path.abspath(__file__))
    venv_python = os.path.join(project_root, ".venv", "bin", "python")

    if not os.path.exists(venv_python):
        return

    if os.path.abspath(sys.executable) == os.path.abspath(venv_python):
        return

    os.execv(
        venv_python,
        [
            venv_python,
            "-m",
            "streamlit",
            "run",
            os.path.abspath(__file__),
            *sys.argv[1:],
        ],
    )


_relaunch_with_project_venv_if_needed()

try:
    import streamlit as st
except ModuleNotFoundError as exc:
    if exc.name == "streamlit":
        raise SystemExit(
            "Streamlit is not installed in this Python interpreter. "
            "Run the app with the project virtual environment:\n"
            "  .venv/bin/streamlit run streamlit_app.py\n"
            "or\n"
            "  .venv/bin/python -m streamlit run streamlit_app.py"
        )
    raise
import openai
import html
import subprocess
import datetime

# Setup log and screenshot capture for browser-use Agent
class StreamlitLogHandler(logging.Handler):
    """Custom log handler to capture logs in Streamlit session state."""
    def emit(self, record):
        if not hasattr(st.session_state, 'agent_logs'):
            st.session_state.agent_logs = []
        log_entry = self.format(record)
        st.session_state.agent_logs.append(log_entry)

class ScreenshotCapture:
    """Capture and store screenshots during browser automation."""
    def __init__(self):
        self.screenshots = []
        
    def add_screenshot(self, path, step_number, description=""):
        """Add screenshot to collection"""
        self.screenshots.append({
            'path': path,
            'step': step_number,
            'description': description,
            'timestamp': datetime.datetime.now().strftime("%H:%M:%S")
        })
    
    def get_all_screenshots(self):
        """Get all captured screenshots in order by step number"""
        return sorted(self.screenshots, key=lambda x: x['step'])
    
    def clear(self):
        """Clear all screenshots"""
        self.screenshots = []

# Configure logging to capture Agent logs
def setup_log_capture():
    """Setup logging to capture browser-use Agent logs with dual output (terminal + Streamlit UI)."""
    if 'log_capture_setup' not in st.session_state:
        # Create Streamlit handler for UI display
        streamlit_handler = StreamlitLogHandler()
        streamlit_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(levelname)s [%(name)s] %(message)s')
        streamlit_handler.setFormatter(formatter)
        
        # Create console handler for terminal output
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter('%(asctime)s - %(levelname)s [%(name)s] %(message)s')
        console_handler.setFormatter(console_formatter)
        
        # Add to ALL relevant loggers including browser-use internal loggers
        logger_names = [
            'Agent',
            'agents.browser_agent', 
            'agents.browser_use_agent',  # ADDED - this is the actual agent logger
            'tools',
            'BrowserSession',
            'browser_use',  # ADDED - browser-use package logger
            'browser_use.agent',  # ADDED
            'browser_use.browser',  # ADDED
        ]
        
        for logger_name in logger_names:
            logger_obj = logging.getLogger(logger_name)
            # Add both handlers for dual logging
            logger_obj.addHandler(streamlit_handler)
            logger_obj.addHandler(console_handler)
            logger_obj.setLevel(logging.INFO)
        
        # Also add root logger to catch everything
        root_logger = logging.getLogger()
        root_logger.addHandler(streamlit_handler)
        root_logger.addHandler(console_handler)
        root_logger.setLevel(logging.INFO)
        
        st.session_state.log_capture_setup = True
        st.session_state.agent_logs = []
        
        # Print confirmation to terminal
        print("="*80)
        print("🔊 DUAL LOGGING ENABLED - Logs will appear in both terminal and Streamlit UI")
        print("="*80)

# Ensure project root is in Python path for package imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from agents.browser_use_agent import BrowserUseAgent
from agents.api_agent import APIAgent
from agents.file_agent import FileAgent
from orchestrator_agent import OrchestratorAgent, TestPlan
from reporting import Reporting

from llm.llm_interface import get_llm_response

# Optional memory module - requires chromadb and pydantic-settings
try:
    from memory import AgentMemory
    MEMORY_AVAILABLE = True
except ImportError as e:
    MEMORY_AVAILABLE = False
    print(f"⚠️ Memory module not available: {e}")
    print("💡 To enable: pip install pydantic-settings")

from dotenv import load_dotenv

load_dotenv()  # load from .env

openai_key = os.getenv("OPENAI_API_KEY")

def is_allure_installed():
    try:
        result = subprocess.run(["allure", "--version"], capture_output=True, text=True)
        return result.returncode == 0
    except Exception:
        return False

def has_allure_results():
    return os.path.exists("allure-results") and any(
        f.endswith(".json") for f in os.listdir("allure-results")
    )

def has_allure_report():
    return os.path.exists("allure-report/index.html")

def generate_allure_report():
    subprocess.run(["allure", "generate", "allure-results", "-o", "allure-report", "--clean"])

def run_pytest_with_allure():
    """Run pytest with Allure reporting - placeholder for future test integration"""
    logger.warning("Allure test execution not configured - browser_launch.py removed")
    # Future: subprocess.run(["pytest", "test_simple.py", "--alluredir=allure-results"])

# Patch OrchestratorAgent to use browser-use agent
class PatchedOrchestratorAgent(OrchestratorAgent):
    def __init__(self, y4m_path=None, enable_tts=False, tts_voice="alloy", candidate_context=None):
        from agents.browser_use_agent import BrowserUseConfig
        
        # Create config with TTS settings
        config = BrowserUseConfig(
            enable_realtime_tts=enable_tts,
            tts_voice=tts_voice,
            tts_model="tts-1"  # Fast generation
        )
        
        # Initialize browser agent with config
        self.ui_agent = BrowserUseAgent(config=config)
        
        # Set candidate context if TTS is enabled
        if enable_tts and candidate_context and hasattr(self.ui_agent, 'answer_generator'):
            self.ui_agent.answer_generator.set_context(candidate_context)
        
        self.api_agent = APIAgent()
        from agents.sql_agent import SQLAgent
        self.db_agent = SQLAgent()
        
        self.tts_enabled = enable_tts
        self.candidate_context = candidate_context

def parse_action_result(action_text):
    """Parse individual ActionResult from text."""
    import re
    
    # Extract key information using more robust regex patterns
    is_done_match = re.search(r"is_done=([^,]+)", action_text)
    success_match = re.search(r"success=([^,]+)", action_text)
    
    # Handle extracted_content with various quote types and nested content
    extracted_content_match = re.search(r"extracted_content=(?:'([^']*)'|\"([^\"]*)\"|([^,]+))", action_text)
    
    # Handle error with various quote types and nested content  
    error_match = re.search(r"error=(?:'([^']*)'|\"([^\"]*)\"|([^,]+))", action_text)
    
    is_done = is_done_match.group(1) if is_done_match else "Unknown"
    success = success_match.group(1) if success_match else "None"
    
    # Get content from whichever group matched
    if extracted_content_match:
        content = extracted_content_match.group(1) or extracted_content_match.group(2) or extracted_content_match.group(3) or ""
    else:
        content = ""
    
    # Get error from whichever group matched
    if error_match:
        error = error_match.group(1) or error_match.group(2) or error_match.group(3) or ""
    else:
        error = ""
    
    # Clean up None values
    if content == "None":
        content = ""
    if error == "None":
        error = ""
    
    return {
        "is_done": is_done,
        "success": success,
        "content": content,
        "error": error
    }

def format_automation_result(result):
    """Format automation result for proper display in Streamlit."""
    if result is None:
        return """
        <div style='background: #fef3c7; border-radius: 10px; padding: 20px; margin: 10px 0; border-left: 4px solid #f59e0b;'>
            <h4 style='color: #d97706; margin: 0;'>⚠️ No result returned from automation.</h4>
        </div>
        """
    
    result_str = str(result)
    
    # If it's already formatted HTML, return as-is
    if result_str.strip().startswith('<div') and 'style=' in result_str:
        return result_str
    
    # Check if it's an AgentHistoryList
    if "AgentHistoryList" in result_str and "ActionResult" in result_str:
        return format_agent_history_result(result_str)
    
    # Otherwise, format it nicely as before
    return f"""
    <div style='background: #f8fafc; border-radius: 12px; padding: 24px; margin: 15px 0; border: 1px solid #e2e8f0; box-shadow: 0 2px 8px rgba(0,0,0,0.05);'>
        <h4 style='color: #1e40af; margin: 0 0 15px 0; display: flex; align-items: center; font-size: 18px; font-weight: 600;'>
            🤖 <span style='margin-left: 8px;'>Automation Result</span>
        </h4>
        <div style='background: #ffffff; padding: 20px; border-radius: 8px; border: 1px solid #e5e7eb; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", system-ui, sans-serif;'>
            <pre style='margin: 0; color: #374151; white-space: pre-wrap; word-wrap: break-word; font-size: 14px; line-height: 1.6;'>{html.escape(result_str)}</pre>
        </div>
    </div>
    """

def format_agent_history_result(result_str):
    """Format AgentHistoryList results in a beautiful, readable way."""
    import re
    
    # Simple extraction of ActionResults for basic parsing
    action_results = re.findall(r'ActionResult\([^)]*(?:\([^)]*\))*[^)]*\)', result_str)
    
    if not action_results:
        return f'''<div style="background: #f8fafc; border-radius: 12px; padding: 24px; margin: 15px 0; border: 1px solid #e2e8f0;">
<h4 style="color: #1e40af; margin: 0 0 15px 0;">🤖 Automation Result</h4>
<pre style="margin: 0; color: #374151; white-space: pre-wrap; word-wrap: break-word; font-size: 14px; line-height: 1.6;">{html.escape(result_str)}</pre>
</div>'''
    
    # Count actions by type
    successful_actions = []
    failed_actions = []
    
    for action in action_results[:10]:  # Limit to 10 for performance
        parsed = parse_action_result(action)
        has_error = parsed["error"] and parsed["error"].strip() and parsed["error"] not in ["None", ""]
        has_content = parsed["content"] and parsed["content"].strip() and parsed["content"] not in ["None", ""]
        
        if has_error:
            failed_actions.append(parsed)
        elif has_content:
            successful_actions.append(parsed)
    
    total_actions = len(action_results)
    success_count = len(successful_actions)
    failure_count = len(failed_actions)
    
    # Determine overall status
    if failure_count > 0:
        status_color = "#ef4444"
        status_bg = "#fef2f2"
        status_icon = "❌"
        status_text = "Completed with Errors"
    else:
        status_color = "#22c55e"
        status_bg = "#f0fdf4"
        status_icon = "✅"
        status_text = "Successfully Completed"
    
    # Build the HTML without any leading whitespace
    html_parts = []
    html_parts.append(f'<div style="background: {status_bg}; border-radius: 16px; padding: 28px; margin: 20px 0; border-left: 5px solid {status_color}; box-shadow: 0 6px 20px rgba(0,0,0,0.08); font-family: -apple-system, BlinkMacSystemFont, \\\"Segoe UI\\\", system-ui, sans-serif;">')
    
    # Header section
    html_parts.append(f'<div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 24px; flex-wrap: wrap; gap: 12px;">')
    html_parts.append(f'<h3 style="color: {status_color}; margin: 0; display: flex; align-items: center; font-size: 22px; font-weight: 700;"><span style="font-size: 28px; margin-right: 12px;">{status_icon}</span><span>Browser Automation {status_text}</span></h3>')
    html_parts.append(f'<div style="background: rgba(255,255,255,0.9); padding: 10px 20px; border-radius: 25px; font-size: 14px; font-weight: 600; color: {status_color}; border: 2px solid {status_color};">{total_actions} Actions Executed</div>')
    html_parts.append('</div>')
    
    # Stats grid
    html_parts.append('<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 16px; margin-bottom: 28px;">')
    html_parts.append(f'<div style="background: linear-gradient(135deg, rgba(34, 197, 94, 0.15), rgba(34, 197, 94, 0.05)); padding: 16px; border-radius: 12px; text-align: center; border: 1px solid rgba(34, 197, 94, 0.2);"><div style="font-size: 28px; font-weight: 800; color: #22c55e; margin-bottom: 4px;">{success_count}</div><div style="font-size: 13px; color: #166534; font-weight: 600; text-transform: uppercase;">Successful</div></div>')
    html_parts.append(f'<div style="background: linear-gradient(135deg, rgba(239, 68, 68, 0.15), rgba(239, 68, 68, 0.05)); padding: 16px; border-radius: 12px; text-align: center; border: 1px solid rgba(239, 68, 68, 0.2);"><div style="font-size: 28px; font-weight: 800; color: #ef4444; margin-bottom: 4px;">{failure_count}</div><div style="font-size: 13px; color: #dc2626; font-weight: 600; text-transform: uppercase;">Failed</div></div>')
    html_parts.append(f'<div style="background: linear-gradient(135deg, rgba(245, 158, 11, 0.15), rgba(245, 158, 11, 0.05)); padding: 16px; border-radius: 12px; text-align: center; border: 1px solid rgba(245, 158, 11, 0.2);"><div style="font-size: 28px; font-weight: 800; color: #f59e0b; margin-bottom: 4px;">{total_actions - success_count - failure_count}</div><div style="font-size: 13px; color: #d97706; font-weight: 600; text-transform: uppercase;">Pending</div></div>')
    html_parts.append('</div>')
    
    # Successful actions
    if successful_actions:
        html_parts.append('<details style="margin-bottom: 20px;" open>')
        html_parts.append(f'<summary style="cursor: pointer; font-weight: 700; color: #22c55e; padding: 12px 16px; background: linear-gradient(135deg, rgba(34, 197, 94, 0.1), rgba(34, 197, 94, 0.05)); border-radius: 10px; margin-bottom: 12px; border: 1px solid rgba(34, 197, 94, 0.2); font-size: 16px;"><span style="font-size: 20px; margin-right: 8px;">✅</span>Successful Actions ({len(successful_actions)})</summary>')
        html_parts.append('<div style="margin-left: 20px;">')
        
        for i, action in enumerate(successful_actions[:5]):
            content = action["content"]
            if len(content) > 120:
                content = content[:120] + "..."
            html_parts.append(f'<div style="background: linear-gradient(135deg, #f0fdf4, #f0fdf4); padding: 16px; margin-bottom: 10px; border-radius: 10px; border-left: 4px solid #22c55e; box-shadow: 0 2px 6px rgba(34, 197, 94, 0.1);"><div style="display: flex; align-items: center; margin-bottom: 6px;"><div style="background: #22c55e; color: white; border-radius: 50%; width: 24px; height: 24px; display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: bold; margin-right: 10px;">{i+1}</div><div style="font-weight: 600; color: #166534; font-size: 14px;">Step {i+1} Completed</div></div><div style="color: #374151; font-size: 14px; line-height: 1.5; margin-left: 34px;">{html.escape(content) if content else "Action completed successfully"}</div></div>')
        
        if len(successful_actions) > 5:
            html_parts.append(f'<div style="text-align: center; color: #6b7280; font-style: italic; padding: 12px; background: rgba(34, 197, 94, 0.05); border-radius: 8px; margin: 8px 0;">... and {len(successful_actions) - 5} more successful actions</div>')
        
        html_parts.append('</div></details>')
    
    # Failed actions
    if failed_actions:
        html_parts.append('<details style="margin-bottom: 20px;" open>')
        html_parts.append(f'<summary style="cursor: pointer; font-weight: 700; color: #ef4444; padding: 12px 16px; background: linear-gradient(135deg, rgba(239, 68, 68, 0.1), rgba(239, 68, 68, 0.05)); border-radius: 10px; margin-bottom: 12px; border: 1px solid rgba(239, 68, 68, 0.2); font-size: 16px;"><span style="font-size: 20px; margin-right: 8px;">❌</span>Failed Actions ({len(failed_actions)})</summary>')
        html_parts.append('<div style="margin-left: 20px;">')
        
        for i, action in enumerate(failed_actions):
            error_msg = action["error"]
            if len(error_msg) > 200:
                error_msg = error_msg[:200] + "..."
            html_parts.append(f'<div style="background: linear-gradient(135deg, #fef2f2, #fef2f2); padding: 16px; margin-bottom: 10px; border-radius: 10px; border-left: 4px solid #ef4444; box-shadow: 0 2px 6px rgba(239, 68, 68, 0.1);"><div style="display: flex; align-items: center; margin-bottom: 6px;"><div style="background: #ef4444; color: white; border-radius: 50%; width: 24px; height: 24px; display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: bold; margin-right: 10px;">!</div><div style="font-weight: 600; color: #dc2626; font-size: 14px;">Step {i+1} Failed</div></div><div style="color: #374151; font-size: 14px; line-height: 1.5; margin-left: 34px; background: rgba(255,255,255,0.7); padding: 12px; border-radius: 6px;">{html.escape(error_msg) if error_msg else "Unknown error occurred"}</div></div>')
        
        html_parts.append('</div></details>')
    
    # Add Agent Logs section
    html_parts.append('<details style="margin-bottom: 20px;" open>')
    html_parts.append(f'<summary style="cursor: pointer; font-weight: 700; color: #3b82f6; padding: 12px 16px; background: linear-gradient(135deg, rgba(59, 130, 246, 0.1), rgba(59, 130, 246, 0.05)); border-radius: 10px; margin-bottom: 12px; border: 1px solid rgba(59, 130, 246, 0.2); font-size: 16px;"><span style="font-size: 20px; margin-right: 8px;">🤖</span>LLM Agent Logs</summary>')
    html_parts.append('<div style="margin-left: 20px;">')
    
    # Get logs from session_state
    import streamlit as st
    if hasattr(st, 'session_state') and hasattr(st.session_state, 'agent_logs') and st.session_state.agent_logs:
        log_lines = st.session_state.agent_logs[-100:]  # Last 100 logs
        logs_html = '<div style="background: #1e1e1e; color: #d4d4d4; padding: 16px; border-radius: 8px; font-family: monospace; font-size: 12px; max-height: 400px; overflow-y: auto; line-height: 1.6;">'
        for log in log_lines:
            # Color code logs
            if 'ERROR' in log or 'FAIL' in log:
                logs_html += f'<div style="color: #f87171;">{html.escape(log)}</div>'
            elif 'WARNING' in log:
                logs_html += f'<div style="color: #fbbf24;">{html.escape(log)}</div>'
            elif 'INFO' in log:
                logs_html += f'<div style="color: #60a5fa;">{html.escape(log)}</div>'
            elif 'DEBUG' in log:
                logs_html += f'<div style="color: #a78bfa;">{html.escape(log)}</div>'
            else:
                logs_html += f'<div>{html.escape(log)}</div>'
        logs_html += '</div>'
        html_parts.append(logs_html)
    else:
        html_parts.append('<div style="text-align: center; color: #6b7280; font-style: italic; padding: 20px;">No logs captured</div>')
    
    html_parts.append('</div></details>')
    
    # Add Screenshots section
    html_parts.append('<details style="margin-bottom: 20px;">')
    html_parts.append(f'<summary style="cursor: pointer; font-weight: 700; color: #8b5cf6; padding: 12px 16px; background: linear-gradient(135deg, rgba(139, 92, 246, 0.1), rgba(139, 92, 246, 0.05)); border-radius: 10px; margin-bottom: 12px; border: 1px solid rgba(139, 92, 246, 0.2); font-size: 16px;"><span style="font-size: 20px; margin-right: 8px;">📸</span>Screenshots</summary>')
    html_parts.append('<div style="margin-left: 20px;">')
    
    # Get screenshots from session_state
    if hasattr(st, 'session_state') and hasattr(st.session_state, 'screenshot_capture'):
        screenshots = st.session_state.screenshot_capture.get_all_screenshots()
        if screenshots:
            html_parts.append(f'<div style="color: #6b7280; margin-bottom: 12px;">Captured {len(screenshots)} screenshots during execution</div>')
            html_parts.append('<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 12px;">')
            for screenshot in screenshots[:12]:  # Limit to 12 screenshots
                # Note: We can't embed images in the HTML string directly, we'll just list them
                html_parts.append(f'<div style="background: #f3f4f6; padding: 10px; border-radius: 8px; text-align: center;"><div style="font-weight: 600; color: #374151; margin-bottom: 4px;">Step {screenshot["step"]}</div><div style="font-size: 12px; color: #6b7280;">{screenshot["timestamp"]}</div><div style="font-size: 11px; color: #9ca3af; margin-top: 4px;">{screenshot["description"]}</div></div>')
            html_parts.append('</div>')
            if len(screenshots) > 12:
                html_parts.append(f'<div style="text-align: center; color: #6b7280; font-style: italic; padding: 12px; margin-top: 8px;">... and {len(screenshots) - 12} more screenshots</div>')
        else:
            html_parts.append('<div style="text-align: center; color: #6b7280; font-style: italic; padding: 20px;">No screenshots captured</div>')
    else:
        html_parts.append('<div style="text-align: center; color: #6b7280; font-style: italic; padding: 20px;">Screenshot capture not initialized</div>')
    
    html_parts.append('</div></details>')
    
    html_parts.append('</div>')
    
    return ''.join(html_parts)

def create_unified_results_display(browser_result, orchestrator_results, reporting):
    """Create a unified results display that combines browser automation and orchestrator results."""
    
    # Parse browser automation results
    browser_stats = {"successful": 0, "failed": 0, "pending": 0, "total": 0}
    browser_actions = []
    
    if browser_result and "AgentHistoryList" in str(browser_result):
        import re
        action_results = re.findall(r'ActionResult\([^)]*(?:\([^)]*\))*[^)]*\)', str(browser_result))
        browser_stats["total"] = len(action_results)
        
        for action in action_results[:15]:  # Limit for performance
            parsed = parse_action_result(action)
            has_error = parsed["error"] and parsed["error"].strip() and parsed["error"] not in ["None", ""]
            has_content = parsed["content"] and parsed["content"].strip() and parsed["content"] not in ["None", ""]
            
            if has_error:
                browser_stats["failed"] += 1
                browser_actions.append({"type": "failed", "content": parsed["content"], "error": parsed["error"]})
            elif has_content:
                browser_stats["successful"] += 1 
                browser_actions.append({"type": "successful", "content": parsed["content"], "error": ""})
            else:
                browser_stats["pending"] += 1
                browser_actions.append({"type": "pending", "content": "Action in progress...", "error": ""})
    elif browser_result:
        result_text = str(browser_result)
        browser_stats["total"] = 1
        if "❌" in result_text and "✅" not in result_text:
            browser_stats["failed"] = 1
            browser_actions.append({"type": "failed", "content": "", "error": result_text})
        elif "❌" in result_text:
            browser_stats["failed"] = 1
            browser_actions.append({"type": "failed", "content": result_text, "error": result_text})
        else:
            browser_stats["successful"] = 1
            browser_actions.append({"type": "successful", "content": result_text, "error": ""})
    
    # Parse orchestrator results
    orchestrator_tests = []
    for agent, agent_results in orchestrator_results.items():
        for res in agent_results:
            status = "✅" if "✅" in str(res['result']) or "rows" in str(res['result']) else "❌"
            is_passed = status == "✅"
            
            # Parse test steps
            import re
            raw_steps = re.split(r'\.|\band\b|\bthen\b|,', res['test'].replace('\n', ' '))
            prompt_steps = [step.strip() for step in raw_steps if step.strip()]
            
            orchestrator_tests.append({
                "agent": agent.upper(),
                "status": "passed" if is_passed else "failed",
                "steps": prompt_steps,
                "result": str(res['result']),
                "test": res['test']
            })
    
    # Determine overall status
    total_browser_failures = browser_stats["failed"]
    total_orchestrator_failures = len([t for t in orchestrator_tests if t["status"] == "failed"])
    total_failures = total_browser_failures + total_orchestrator_failures
    
    if total_failures > 0:
        overall_status = "completed_with_errors"
        status_color = "#ef4444"
        status_bg = "#fef2f2"
        status_icon = "❌"
        status_text = "Completed with Issues"
    else:
        overall_status = "successful"
        status_color = "#22c55e"
        status_bg = "#f0fdf4"
        status_icon = "✅"
        status_text = "Successfully Completed"
    
    # Build unified HTML
    html_parts = []
    
    # Header section
    html_parts.append(f'<div style="background: {status_bg}; border-radius: 16px; padding: 32px; margin: 20px 0; border-left: 6px solid {status_color}; box-shadow: 0 8px 24px rgba(0,0,0,0.1); font-family: -apple-system, BlinkMacSystemFont, \\\"Segoe UI\\\", system-ui, sans-serif;">')
    
    # Title and summary
    html_parts.append(f'<div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 28px; flex-wrap: wrap; gap: 16px;">')
    html_parts.append(f'<h2 style="color: {status_color}; margin: 0; display: flex; align-items: center; font-size: 26px; font-weight: 800;"><span style="font-size: 32px; margin-right: 16px;">{status_icon}</span><span>Automation {status_text}</span></h2>')
    total_actions = browser_stats["total"] + len(orchestrator_tests)
    html_parts.append(f'<div style="background: rgba(255,255,255,0.9); padding: 12px 24px; border-radius: 30px; font-size: 16px; font-weight: 700; color: {status_color}; border: 3px solid {status_color}; backdrop-filter: blur(10px);">{total_actions} Total Actions</div>')
    html_parts.append('</div>')
    
    # Combined stats grid
    html_parts.append('<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 20px; margin-bottom: 32px;">')
    
    # Browser automation stats
    html_parts.append(f'<div style="background: linear-gradient(135deg, rgba(59, 130, 246, 0.15), rgba(59, 130, 246, 0.05)); padding: 20px; border-radius: 12px; text-align: center; border: 2px solid rgba(59, 130, 246, 0.3);"><div style="font-size: 30px; font-weight: 900; color: #3b82f6; margin-bottom: 6px;">{browser_stats["total"]}</div><div style="font-size: 14px; color: #1e40af; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px;">Browser Actions</div></div>')
    
    # Test results stats  
    orchestrator_passed = len([t for t in orchestrator_tests if t["status"] == "passed"])
    orchestrator_failed = len([t for t in orchestrator_tests if t["status"] == "failed"])
    html_parts.append(f'<div style="background: linear-gradient(135deg, rgba(34, 197, 94, 0.15), rgba(34, 197, 94, 0.05)); padding: 20px; border-radius: 12px; text-align: center; border: 2px solid rgba(34, 197, 94, 0.3);"><div style="font-size: 30px; font-weight: 900; color: #22c55e; margin-bottom: 6px;">{browser_stats["successful"] + orchestrator_passed}</div><div style="font-size: 14px; color: #166534; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px;">Successful</div></div>')
    
    html_parts.append(f'<div style="background: linear-gradient(135deg, rgba(239, 68, 68, 0.15), rgba(239, 68, 68, 0.05)); padding: 20px; border-radius: 12px; text-align: center; border: 2px solid rgba(239, 68, 68, 0.3);"><div style="font-size: 30px; font-weight: 900; color: #ef4444; margin-bottom: 6px;">{browser_stats["failed"] + orchestrator_failed}</div><div style="font-size: 14px; color: #dc2626; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px;">Failed</div></div>')
    
    html_parts.append(f'<div style="background: linear-gradient(135deg, rgba(245, 158, 11, 0.15), rgba(245, 158, 11, 0.05)); padding: 20px; border-radius: 12px; text-align: center; border: 2px solid rgba(245, 158, 11, 0.3);"><div style="font-size: 30px; font-weight: 900; color: #f59e0b; margin-bottom: 6px;">{browser_stats["pending"]}</div><div style="font-size: 14px; color: #d97706; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px;">Pending</div></div>')
    html_parts.append('</div>')
    
    # Browser actions section
    if browser_actions:
        successful_browser = [a for a in browser_actions if a["type"] == "successful"]
        failed_browser = [a for a in browser_actions if a["type"] == "failed"]
        
        if successful_browser:
            html_parts.append('<details style="margin-bottom: 24px;" open>')
            html_parts.append(f'<summary style="cursor: pointer; font-weight: 800; color: #22c55e; padding: 16px 20px; background: linear-gradient(135deg, rgba(34, 197, 94, 0.12), rgba(34, 197, 94, 0.08)); border-radius: 12px; margin-bottom: 16px; border: 2px solid rgba(34, 197, 94, 0.25); font-size: 18px; display: flex; align-items: center;"><span style="font-size: 24px; margin-right: 12px;">🌐</span>Browser Actions - Successful ({len(successful_browser)})</summary>')
            html_parts.append('<div style="margin-left: 24px; space-y: 12px;">')
            
            for i, action in enumerate(successful_browser[:8]):  # Limit display
                content = action["content"]
                if len(content) > 150:
                    content = content[:150] + "..."
                html_parts.append(f'<div style="background: linear-gradient(135deg, #f0fdf4, #f0fdf4); padding: 18px; margin-bottom: 12px; border-radius: 12px; border-left: 5px solid #22c55e; box-shadow: 0 3px 8px rgba(34, 197, 94, 0.12);"><div style="display: flex; align-items: center; margin-bottom: 8px;"><div style="background: #22c55e; color: white; border-radius: 50%; width: 28px; height: 28px; display: flex; align-items: center; justify-content: center; font-size: 14px; font-weight: bold; margin-right: 12px;">{i+1}</div><div style="font-weight: 700; color: #166534; font-size: 16px;">Browser Step {i+1}</div></div><div style="color: #374151; font-size: 15px; line-height: 1.6; margin-left: 40px;">{html.escape(content) if content else "Action completed successfully"}</div></div>')
            
            if len(successful_browser) > 8:
                html_parts.append(f'<div style="text-align: center; color: #6b7280; font-style: italic; padding: 16px; background: rgba(34, 197, 94, 0.08); border-radius: 10px; margin: 12px 0;">... and {len(successful_browser) - 8} more successful browser actions</div>')
            
            html_parts.append('</div></details>')
        
        if failed_browser:
            html_parts.append('<details style="margin-bottom: 24px;" open>')
            html_parts.append(f'<summary style="cursor: pointer; font-weight: 800; color: #ef4444; padding: 16px 20px; background: linear-gradient(135deg, rgba(239, 68, 68, 0.12), rgba(239, 68, 68, 0.08)); border-radius: 12px; margin-bottom: 16px; border: 2px solid rgba(239, 68, 68, 0.25); font-size: 18px; display: flex; align-items: center;"><span style="font-size: 24px; margin-right: 12px;">🚫</span>Browser Actions - Failed ({len(failed_browser)})</summary>')
            html_parts.append('<div style="margin-left: 24px;">')
            
            for i, action in enumerate(failed_browser):
                error_msg = action["error"]
                if len(error_msg) > 250:
                    error_msg = error_msg[:250] + "..."
                html_parts.append(f'<div style="background: linear-gradient(135deg, #fef2f2, #fef2f2); padding: 18px; margin-bottom: 12px; border-radius: 12px; border-left: 5px solid #ef4444; box-shadow: 0 3px 8px rgba(239, 68, 68, 0.12);"><div style="display: flex; align-items: center; margin-bottom: 8px;"><div style="background: #ef4444; color: white; border-radius: 50%; width: 28px; height: 28px; display: flex; align-items: center; justify-content: center; font-size: 14px; font-weight: bold; margin-right: 12px;">!</div><div style="font-weight: 700; color: #dc2626; font-size: 16px;">Browser Error {i+1}</div></div><div style="color: #374151; font-size: 15px; line-height: 1.6; margin-left: 40px; background: rgba(255,255,255,0.8); padding: 14px; border-radius: 8px;">{html.escape(error_msg) if error_msg else "Unknown error occurred"}</div></div>')
            
            html_parts.append('</div></details>')
    
    # Orchestrator tests section
    if orchestrator_tests:
        passed_tests = [t for t in orchestrator_tests if t["status"] == "passed"]
        failed_tests = [t for t in orchestrator_tests if t["status"] == "failed"]
        
        if passed_tests:
            html_parts.append('<details style="margin-bottom: 24px;" open>')
            html_parts.append(f'<summary style="cursor: pointer; font-weight: 800; color: #22c55e; padding: 16px 20px; background: linear-gradient(135deg, rgba(34, 197, 94, 0.12), rgba(34, 197, 94, 0.08)); border-radius: 12px; margin-bottom: 16px; border: 2px solid rgba(34, 197, 94, 0.25); font-size: 18px; display: flex; align-items: center;"><span style="font-size: 24px; margin-right: 12px;">✅</span>System Tests - Passed ({len(passed_tests)})</summary>')
            html_parts.append('<div style="margin-left: 24px;">')
            
            for test in passed_tests:
                steps_html = ""
                for step in test["steps"][:5]:  # Limit steps shown
                    steps_html += f'<li style="margin-bottom: 8px; line-height: 1.6; background: #dcfce7; border-radius: 6px; padding: 6px 10px; color: #166534;">✔️ {step}</li>'
                if len(test["steps"]) > 5:
                    steps_html += f'<li style="margin-bottom: 8px; color: #6b7280; font-style: italic;">... and {len(test["steps"]) - 5} more steps</li>'
                
                html_parts.append(f'<div style="background: #ffffff; border: 2px solid #22c55e; border-radius: 12px; padding: 20px; margin-bottom: 16px; box-shadow: 0 3px 8px rgba(34, 197, 94, 0.1);"><div style="display: flex; align-items: center; margin-bottom: 16px;"><span style="font-size: 24px; margin-right: 12px;">🟢</span><span style="font-weight: 800; color: #22c55e; font-size: 18px; margin-right: 16px;">PASSED</span><span style="background: #e0e7ef; color: #334155; border-radius: 8px; padding: 6px 16px; font-size: 14px; font-weight: 600;">{test["agent"]} Test</span></div><div style="margin-bottom: 16px;"><span style="font-weight: 700; color: #475569; font-size: 16px;">Test Steps:</span><ol style="margin: 8px 0 0 20px; padding: 0;">{steps_html}</ol></div><details><summary style="font-weight: 700; color: #475569; cursor: pointer; font-size: 16px;">View Result Details</summary><pre style="margin: 8px 0 0 0; background: #f8fafc; border-radius: 8px; padding: 16px; color: #1e293b; font-size: 14px; border: 1px solid #e5e7eb; white-space: pre-wrap; word-wrap: break-word;">{html.escape(test["result"])}</pre></details></div>')
            
            html_parts.append('</div></details>')
        
        if failed_tests:
            html_parts.append('<details style="margin-bottom: 24px;" open>')
            html_parts.append(f'<summary style="cursor: pointer; font-weight: 800; color: #ef4444; padding: 16px 20px; background: linear-gradient(135deg, rgba(239, 68, 68, 0.12), rgba(239, 68, 68, 0.08)); border-radius: 12px; margin-bottom: 16px; border: 2px solid rgba(239, 68, 68, 0.25); font-size: 18px; display: flex; align-items: center;"><span style="font-size: 24px; margin-right: 12px;">❌</span>System Tests - Failed ({len(failed_tests)})</summary>')
            html_parts.append('<div style="margin-left: 24px;">')
            
            for test in failed_tests:
                # Find failure point
                fail_idx = None
                error_keywords = ["fail", "error", "not", "unable", "missing", "invalid"]
                for i, step in enumerate(test["steps"]):
                    if any(kw in step.lower() for kw in error_keywords):
                        fail_idx = i
                        break
                if fail_idx is None:
                    fail_idx = len(test["steps"]) - 1 if test["steps"] else None
                
                steps_html = ""
                for idx, step in enumerate(test["steps"][:6]):
                    if idx == fail_idx:
                        steps_html += f'<li style="margin-bottom: 8px; line-height: 1.6; background: #fee2e2; border-radius: 6px; padding: 6px 10px; font-weight: bold; color: #b91c1c; border: 2px solid #ef4444;">❌ {step}</li>'
                    else:
                        steps_html += f'<li style="margin-bottom: 8px; line-height: 1.6; background: #f3f4f6; border-radius: 6px; padding: 6px 10px; color: #334155;">{step}</li>'
                if len(test["steps"]) > 6:
                    steps_html += f'<li style="margin-bottom: 8px; color: #6b7280; font-style: italic;">... and {len(test["steps"]) - 6} more steps</li>'
                
                html_parts.append(f'<div style="background: #ffffff; border: 2px solid #ef4444; border-radius: 12px; padding: 20px; margin-bottom: 16px; box-shadow: 0 3px 8px rgba(239, 68, 68, 0.1);"><div style="display: flex; align-items: center; margin-bottom: 16px;"><span style="font-size: 24px; margin-right: 12px;">🔴</span><span style="font-weight: 800; color: #ef4444; font-size: 18px; margin-right: 16px;">FAILED</span><span style="background: #e0e7ef; color: #334155; border-radius: 8px; padding: 6px 16px; font-size: 14px; font-weight: 600;">{test["agent"]} Test</span></div><div style="margin-bottom: 16px;"><span style="font-weight: 700; color: #475569; font-size: 16px;">Test Steps:</span><ol style="margin: 8px 0 0 20px; padding: 0;">{steps_html}</ol></div><details><summary style="font-weight: 700; color: #475569; cursor: pointer; font-size: 16px;">View Error Details</summary><pre style="margin: 8px 0 0 0; background: #fef2f2; border-radius: 8px; padding: 16px; color: #1e293b; font-size: 14px; border: 1px solid #fecaca; white-space: pre-wrap; word-wrap: break-word;">{html.escape(test["result"])}</pre></details></div>')
            
            html_parts.append('</div></details>')
    
    # Footer with download link
    html_parts.append('<div style="margin-top: 24px; padding-top: 20px; border-top: 2px solid rgba(0,0,0,0.1);"><a href="test_report_fixed.html" download style="display: inline-flex; align-items: center; background: #3b82f6; color: white; padding: 12px 24px; border-radius: 8px; text-decoration: none; font-weight: 600; font-size: 16px; box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3); transition: all 0.2s;"><span style="margin-right: 8px;">⬇️</span>Download Complete Report</a></div>')
    
    html_parts.append('</div>')
    
    return ''.join(html_parts)

def main():
    # Setup log capture before anything else
    setup_log_capture()
    
    st.set_page_config(page_title="🕵️ Agent Interface", layout="wide", initial_sidebar_state="expanded")
    st.markdown("""
    <style>
    .stApp { background: #f8f9fa; color: #1a1a1a; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }
    </style>
    """, unsafe_allow_html=True)

    # --- Memory Management UI (Optional) ---
    if MEMORY_AVAILABLE:
        if 'agent_memory' not in st.session_state:
            st.session_state.agent_memory = AgentMemory()

        st.sidebar.header("Memory Management")

    # Short-term memory controls
    st.sidebar.subheader("Short-term Memory")
    short_vec_str = st.sidebar.text_input("Short-term Vector (comma-separated)", key="short_vec")
    short_text = st.sidebar.text_input("Short-term Text", key="short_text")
    if st.sidebar.button("Add to Short-term Memory"):
        try:
            vec = [float(x) for x in short_vec_str.split(",") if x.strip()]
            st.session_state.agent_memory.add_short_term(vec, short_text)
            st.sidebar.success("Added to short-term memory.")
        except Exception as e:
            st.sidebar.error(f"Error: {e}")
    if st.sidebar.button("View Short-term Memory"):
        with st.expander("Short-term Memory Contents"):
            st.write(st.session_state.agent_memory.get_short_term())
    if st.sidebar.button("Clear Short-term Memory"):
        st.session_state.agent_memory.clear_short_term()
        st.sidebar.success("Short-term memory cleared.")

    # Long-term memory controls
    st.sidebar.subheader("Long-term Memory")
    long_vec_str = st.sidebar.text_input("Long-term Vector (comma-separated)", key="long_vec")
    long_text = st.sidebar.text_input("Long-term Text", key="long_text")
    if st.sidebar.button("Add to Long-term Memory"):
        try:
            vec2 = [float(x) for x in long_vec_str.split(",") if x.strip()]
            st.session_state.agent_memory.add_long_term(vec2, long_text)
            st.sidebar.success("Added to long-term memory.")
        except Exception as e:
            st.sidebar.error(f"Error: {e}")
    search_vec_str = st.sidebar.text_input("Search Vector (comma-separated)", key="search_vec")
    if st.sidebar.button("Search Long-term Memory"):
        try:
            search_vec = [float(x) for x in search_vec_str.split(",") if x.strip()]
            with st.expander("Long-term Memory Search Results"):
                st.write(st.session_state.agent_memory.search_long_term(search_vec))
        except Exception as e:
            st.sidebar.error(f"Error: {e}")
    del_text = st.sidebar.text_input("Delete Long-term Text", key="del_text")
    if st.sidebar.button("Delete from Long-term Memory"):
        st.session_state.agent_memory.delete_long_term(del_text)
        st.sidebar.success("Deleted from long-term memory.")
    else:
        # Memory module not available - show info
        st.sidebar.info("💡 Memory features disabled. Install: pip install pydantic-settings")

    # === TTS CONFIGURATION ===
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🎤 Real-time TTS Configuration")
    
    # Initialize TTS session state
    if 'enable_tts' not in st.session_state:
        st.session_state.enable_tts = False
    if 'tts_voice' not in st.session_state:
        st.session_state.tts_voice = "alloy"
    if 'candidate_context' not in st.session_state:
        st.session_state.candidate_context = {
            "candidate_name": "John Doe",
            "position": "Software Engineer",
            "experience_years": 5,
            "skills": ["Python", "JavaScript", "React"]
        }
    
    # TTS Enable/Disable
    st.session_state.enable_tts = st.sidebar.checkbox(
        "Enable Real-time TTS", 
        value=st.session_state.enable_tts,
        help="Auto-generate and speak answers to interview questions"
    )
    
    if st.session_state.enable_tts:
        # Voice selection
        voice_options = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
        voice_descriptions = {
            "alloy": "Neutral, balanced",
            "echo": "Male, clear",
            "fable": "Male, expressive",
            "onyx": "Male, deep",
            "nova": "Female, clear",
            "shimmer": "Female, soft"
        }
        
        st.session_state.tts_voice = st.sidebar.selectbox(
            "TTS Voice",
            options=voice_options,
            index=voice_options.index(st.session_state.tts_voice),
            format_func=lambda x: f"{x.title()} - {voice_descriptions[x]}",
            help="Select voice for TTS responses"
        )
        
        # Candidate context
        with st.sidebar.expander("👤 Candidate Profile", expanded=False):
            st.session_state.candidate_context["candidate_name"] = st.text_input(
                "Name",
                value=st.session_state.candidate_context["candidate_name"],
                key="tts_name"
            )
            st.session_state.candidate_context["position"] = st.text_input(
                "Position",
                value=st.session_state.candidate_context["position"],
                key="tts_position"
            )
            st.session_state.candidate_context["experience_years"] = st.number_input(
                "Years of Experience",
                min_value=0,
                max_value=50,
                value=st.session_state.candidate_context["experience_years"],
                key="tts_experience"
            )
            skills_str = ", ".join(st.session_state.candidate_context["skills"])
            new_skills = st.text_input(
                "Skills (comma-separated)",
                value=skills_str,
                key="tts_skills"
            )
            st.session_state.candidate_context["skills"] = [s.strip() for s in new_skills.split(",") if s.strip()]
        
        # Audio file location
        audio_file = os.path.abspath("./generated_audio/live_response.wav")
        if os.path.exists(audio_file):
            file_size = os.path.getsize(audio_file) / 1024  # KB
            st.sidebar.success(f"✅ Audio ready ({file_size:.1f} KB)")
            
            # Show Chrome command
            with st.sidebar.expander("🌐 Chrome Launch Command", expanded=False):
                chrome_cmd = f'''
/Applications/Google\\ Chrome.app/Contents/MacOS/Google\\ Chrome \\
  --use-fake-ui-for-media-stream \\
  --use-fake-device-for-media-stream \\
  --use-file-for-fake-audio-capture="{audio_file}" \\
  https://vmock.com
                '''.strip()
                st.code(chrome_cmd, language="bash")
                st.caption("Copy and run this to test audio in Chrome")
        else:
            st.sidebar.info("🎤 Audio will be generated on first question")
    
    st.sidebar.markdown("---")
    
    # Initialize session state
    if 'agent' not in st.session_state:
        st.session_state.agent = None
    if 'action_logs' not in st.session_state:
        st.session_state.action_logs = []
    if 'running' not in st.session_state:
        st.session_state.running = False
    if 'screenshots' not in st.session_state:
        st.session_state.screenshots = []
    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = []
    if 'stop_requested' not in st.session_state:
        st.session_state.stop_requested = False
    if 'chat_sessions' not in st.session_state:
        st.session_state.chat_sessions = []
    if 'current_session_id' not in st.session_state:
        st.session_state.current_session_id = None
    if 'search_query' not in st.session_state:
        st.session_state.search_query = ""
    if 'show_action_modal' not in st.session_state:
        st.session_state.show_action_modal = False
    if 'modal_slide_index' not in st.session_state:
        st.session_state.modal_slide_index = 0
    if 'current_action_logs' not in st.session_state:
        st.session_state.current_action_logs = []
    if 'current_screenshots' not in st.session_state:
        st.session_state.current_screenshots = []

    with st.sidebar:
        st.markdown('<div class="sidebar-header">', unsafe_allow_html=True)
        if st.button("✨ New Chat", key="new_chat", help="Start a new conversation"):
            if st.session_state.conversation_history:
                session_id = len(st.session_state.chat_sessions)
                first_user_msg = next((msg['content'] for msg in st.session_state.conversation_history if msg['role'] == 'user'), "New Chat")
                title = first_user_msg[:40].strip() + "..." if len(first_user_msg) > 40 else first_user_msg
                st.session_state.chat_sessions.append({
                    'id': session_id,
                    'title': title,
                    'messages': st.session_state.conversation_history.copy(),
                    'timestamp': datetime.datetime.now().strftime("%H:%M"),
                    'date': datetime.datetime.now().strftime('%Y-%m-%d')
                })
            st.session_state.conversation_history = []
            st.session_state.current_session_id = None
            st.rerun()
        
        search_query = st.text_input("Search Chat", placeholder="🔍 Search Chat...", key="search_input", label_visibility="collapsed")
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('<div class="chat-history">', unsafe_allow_html=True)
        st.markdown('<div class="section-header">RECENT CHAT HISTORY</div>', unsafe_allow_html=True)
        if st.session_state.chat_sessions:
            filtered_sessions = st.session_state.chat_sessions
            if search_query:
                filtered_sessions = [s for s in st.session_state.chat_sessions if search_query.lower() in s['title'].lower()]
            for session in reversed(filtered_sessions[-10:]):
                col1, col2 = st.columns([4, 1])
                with col1:
                    if st.button(session['title'], key=f"chat_{session['id']}", help=f"Switch to chat from {session['timestamp']}", use_container_width=True):
                        st.session_state.conversation_history = session['messages'].copy()
                        st.session_state.current_session_id = session['id']
                        st.rerun()
                with col2:
                    if st.button("🗑️", key=f"del_{session['id']}", help="Delete chat"):
                        st.session_state.chat_sessions = [s for s in st.session_state.chat_sessions if s['id'] != session['id']]
                        if st.session_state.current_session_id == session['id']:
                            st.session_state.conversation_history = []
                            st.session_state.current_session_id = None
                        st.rerun()
        else:
            st.markdown('<div style="padding: 20px; text-align: center; color: #9ca3af; font-size: 0.85rem;">No conversations yet.<br>Start chatting to see your history here.</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">SETTINGS</div>', unsafe_allow_html=True)
        enable_media = st.checkbox("📹 Camera/Mic", value=True, key="camera_mic")
<<<<<<< HEAD
        
        # File & Browser Operations Section
        st.markdown('<div class="section-title" style="margin-top: 20px;">FILE & BROWSER OPERATIONS</div>', unsafe_allow_html=True)
        
        y4m_file = st.text_input("Y4M File", value="/Users/pratik/Downloads/Assesment/mcp_ai_testAgent/Johnny_1280x720_60.y4m", placeholder="/path/to/video.y4m")
        audio_file = st.text_input("Audio File", value="/Users/pratik/Downloads/Assesment/Ui_Automation/Resources/sample_audio.wav", placeholder="/path/to/audio.wav")

        # Y4M file validation with improved status indicators
        if y4m_file.strip():
            if os.path.exists(y4m_file.strip()):
                file_size = os.path.getsize(y4m_file.strip()) / (1024*1024)  # MB
                st.markdown(f'<div class="status-indicator status-success">✅ Y4M file found ({file_size:.1f} MB)</div>', unsafe_allow_html=True)
                
                # Check if it's a valid Y4M file
                try:
                    with open(y4m_file.strip(), 'rb') as f:
                        header = f.read(10).decode('ascii', errors='ignore')
                        if header.startswith('YUV4MPEG2'):
                            st.markdown('<div class="status-indicator status-success">✅ Valid Y4M format detected</div>', unsafe_allow_html=True)
                        else:
                            st.markdown('<div class="status-indicator status-warning">⚠️ File doesn\'t appear to be Y4M format</div>', unsafe_allow_html=True)
                except Exception as e:
                    st.markdown(f'<div class="status-indicator status-error">❌ Cannot read file: {str(e)}</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="status-indicator status-error">❌ Y4M file not found at specified path</div>', unsafe_allow_html=True)

        # Audio file validation
        if audio_file.strip():
            if os.path.exists(audio_file.strip()):
                file_size = os.path.getsize(audio_file.strip()) / (1024*1024)  # MB
                st.markdown(f'<div class="status-indicator status-success">✅ Audio file found ({file_size:.1f} MB)</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="status-indicator status-error">❌ Audio file not found at specified path</div>', unsafe_allow_html=True)
        
        if st.button("🔒 Close Browser", use_container_width=True):
            if st.session_state.agent:
                st.session_state.agent.close_browser()
                st.session_state.agent = None
                st.session_state.running = False
                st.session_state.screenshots = []
            st.rerun()
        
=======
>>>>>>> 17e4131 (Add interview automation agents, docs, and Streamlit/TTS app)
        st.markdown('</div>', unsafe_allow_html=True)

    # === ENHANCED CHAT INTERFACE: Use st.chat_message for GPT-like chat ===
    if not st.session_state.conversation_history:
        st.markdown('<div style="display: flex; flex-direction: column; justify-content: center; align-items: center; min-height: 60vh; text-align: center; padding: 20px;">'
            '<div style="font-size: 3rem; font-weight: 700; color: #1a1a1a; margin-bottom: 16px;">🕵️ Agent</div>'
            '<div style="font-size: 1.2rem; color: #6b7280; margin-bottom: 40px;">automation booster</div>'
            '<div style="font-size: 1rem; color: #4b5563; margin-bottom: 32px; line-height: 1.6;">I can help with conversations, web automation, file operations, API calls, and database queries</div>'
            '<div style="display: flex; flex-wrap: wrap; gap: 12px; justify-content: center;">'
            '<div style="background: #f8fafc; border: 1px solid #e2e8f0; color: #4b5563; padding: 8px 16px; border-radius: 20px; font-size: 0.9rem; cursor: pointer;">"What time is it?"</div>'
            '<div style="background: #f8fafc; border: 1px solid #e2e8f0; color: #4b5563; padding: 8px 16px; border-radius: 20px; font-size: 0.9rem; cursor: pointer;">"Browse to google.com"</div>'
            '<div style="background: #f8fafc; border: 1px solid #e2e8f0; color: #4b5563; padding: 8px 16px; border-radius: 20px; font-size: 0.9rem; cursor: pointer;">"Create a file"</div>'
            '<div style="background: #f8fafc; border: 1px solid #e2e8f0; color: #4b5563; padding: 8px 16px; border-radius: 20px; font-size: 0.9rem; cursor: pointer;">"Make API request"</div>'
            '</div>'
            '</div>', unsafe_allow_html=True)
    elif st.session_state.conversation_history:
        # --- Enhanced GPT-like chat display ---
        for msg in st.session_state.conversation_history:
            if msg["role"] == "user":
                with st.chat_message("user"):
                    st.markdown(msg["content"])
            elif msg["role"] == "assistant":
                with st.chat_message("assistant"):
                    # Check if content contains HTML - improved detection
                    content = msg["content"]
                    # Remove leading/trailing whitespace for checking
                    content_stripped = content.strip()
                    
                    # Multiple ways to detect HTML content
                    is_html = (
                        content_stripped.startswith("<div") or 
                        content_stripped.startswith("<") or
                        "style=" in content or 
                        "background:" in content or
                        "border-radius:" in content or
                        "margin:" in content or
                        "padding:" in content or
                        "<details" in content or
                        "<summary" in content
                    )
                    
                    if is_html:
                        st.markdown(content, unsafe_allow_html=True)
                    else:
                        st.markdown(content)

    # === Allure Report Integration (ONLY Allure) ===
    allure_installed = is_allure_installed()
    results_exist = has_allure_results()
    report_exists = has_allure_report()
    allure_port = 8080

    st.sidebar.markdown("---")
    st.sidebar.markdown("### Allure Test Report")

    if not allure_installed:
        st.sidebar.error("Allure CLI is not installed. Please install Allure to enable reporting.")
    elif not results_exist:
        st.sidebar.warning("No Allure results found. Run a test to generate results.")
    else:
        # Always generate a fresh report after results
        generate_allure_report()
        # Do NOT start the HTTP server here; start it manually ONCE outside Streamlit
        if st.sidebar.button("Open Allure Report in Browser"):
            import webbrowser
            webbrowser.open(f"http://localhost:{allure_port}/index.html")

    input_col, button_col = st.columns([6, 1])
    with input_col:
        user_input = st.chat_input(placeholder="Ask anything...", key="chat_input")
    with button_col:
        if st.session_state.running:
            if st.button("⏹️", key="stop_btn", help="Stop generating"):
                st.session_state.stop_requested = True
                st.session_state.running = False
                if st.session_state.agent:
                    try:
                        st.session_state.agent.stop()
                        st.session_state.agent.close_browser()
                    except Exception as e:
                        print(f"Error stopping agent: {e}")
                if st.session_state.conversation_history and st.session_state.conversation_history[-1].get("typing"):
                    st.session_state.conversation_history.pop()
                st.session_state.conversation_history.append({
                    "role": "assistant", 
                    "content": "❌ **Response stopped by user.**",
                    "timestamp": datetime.datetime.now().strftime("%H:%M:%S")
                })
                st.rerun()
    st.markdown('</div></div>', unsafe_allow_html=True)

    if user_input and not st.session_state.running:
        # Reset browser action execution flag for new input
        st.session_state.browser_action_executed = False
        st.session_state.conversation_history.append({
            "role": "user", 
            "content": user_input,
            "timestamp": datetime.datetime.now().strftime("%H:%M:%S")
        })
        st.session_state.running = True
        st.session_state.stop_requested = False
<<<<<<< HEAD
        
        # Detect explicit browser automation tasks (VMock, complex web tasks)
        automation_keywords = ['vmock', 'login to', 'fill form', 'click button', 'navigate to', 'automation', 'interview']
        should_use_automation = any(keyword in user_input.lower() for keyword in automation_keywords)
        
        if should_use_automation:
            # Run BrowserAgent with Y4M and audio file support
            try:
                from agents.browser_agent import BrowserAgent
                browser_agent = BrowserAgent(
                    y4m_file_path=y4m_file.strip(),
                    audio_file_path=audio_file.strip()
                )
                result = browser_agent.run_task(user_input)
                # Format AgentHistoryList or similar objects for user-friendly output
                display_content = None
                if hasattr(result, "all_results"):
                    # Try to extract the last extracted_content that is not None
                    for action in reversed(getattr(result, "all_results", [])):
                        if hasattr(action, "extracted_content") and action.extracted_content:
                            display_content = action.extracted_content
                            break
                elif isinstance(result, dict) and "all_results" in result:
                    for action in reversed(result["all_results"]):
                        if "extracted_content" in action and action["extracted_content"]:
                            display_content = action["extracted_content"]
                            break
                if not display_content:
                    display_content = str(result)
                st.session_state.conversation_history.append({
                    "role": "assistant", 
                    "content": f"{display_content}",
                    "timestamp": dt.datetime.now().strftime("%H:%M:%S")
                })
            except Exception as e:
                st.session_state.conversation_history.append({
                    "role": "assistant", 
                    "content": f"❌ Failed to run BrowserAgent: {str(e)}",
                    "timestamp": dt.datetime.now().strftime("%H:%M:%S")
                })
        else:
            # Handle all tasks through browser-use Agent for consistency
            try:
                async def run_browser_use_agent(task):
                    llm = ChatOpenAI(
                        model="gpt-4o-mini",
                        api_key=os.getenv("OPENAI_API_KEY")
                    )
                    agent = Agent(
                        task=task,
                        llm=llm,
                        use_vision=True
                    )
                    result = await agent.run(max_steps=10)
                    return result

                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(run_browser_use_agent(user_input))
                loop.close()

                # Format AgentHistoryList or similar objects for user-friendly output
                display_content = None
                if hasattr(result, "all_results"):
                    for action in reversed(getattr(result, "all_results", [])):
                        if hasattr(action, "extracted_content") and action.extracted_content:
                            display_content = action.extracted_content
                            break
                elif isinstance(result, dict) and "all_results" in result:
                    for action in reversed(result["all_results"]):
                        if "extracted_content" in action and action["extracted_content"]:
                            display_content = action["extracted_content"]
                            break
                if not display_content:
                    display_content = str(result)
                st.session_state.conversation_history.append({
                    "role": "assistant", 
                    "content": f"{display_content}",
                    "timestamp": dt.datetime.now().strftime("%H:%M:%S")
                })
            except Exception as e:
                st.session_state.conversation_history.append({
                    "role": "assistant", 
                    "content": f"Error: {str(e)}",
                    "timestamp": dt.datetime.now().strftime("%H:%M:%S")
                })
        
        # Auto-save to chat history after first exchange
=======

        # === Agentic action routing: use advanced prompt parser for intent detection ===
        from prompt_parser import parse_prompt_for_action

        intent = parse_prompt_for_action(user_input)
        context = {"ui_tests": [], "api_tests": [], "db_tests": []}

        # Robust browser automation trigger: always treat browser prompts as UI actions
        browser_keywords = ["go to", "open", "navigate", "click", "search", "scrape", "fill", "browser", "webcam", "website", "page"]
        is_browser_prompt = any(kw in user_input.lower() for kw in browser_keywords)

        # === ENHANCED: Only use LLM for non-browser tasks ===
        if not is_browser_prompt and not (intent.get("is_url") and intent.get("is_browser_action")):
            llm_response = get_llm_response(user_input)
            st.session_state.conversation_history.append({
                "role": "assistant",
                "content": llm_response,
                "timestamp": datetime.datetime.now().strftime("%H:%M:%S")
            })

        if intent["should_act"] or is_browser_prompt:
            # Only route to one test type based on priority: UI > API
            if (intent.get("is_url") and intent.get("is_browser_action")) or intent.get("llm_intent") == "browser" or is_browser_prompt:
                context["ui_tests"] = [user_input]
            elif "api" in user_input.lower() or intent.get("llm_intent") == "api":
                context["api_tests"] = [user_input]
            elif intent.get("llm_intent") == "db" or intent.get("is_sql"):
                context["db_tests"] = [user_input]

            # If UI agentic action, call browser agentic task directly with the user prompt
            browser_result = None
            all_screenshots = []
            if context["ui_tests"]:
                st.info("🚀 Starting FAST browser automation...")
                
                # Clear previous logs and screenshots
                st.session_state.agent_logs = []
                if 'screenshot_capture' not in st.session_state:
                    st.session_state.screenshot_capture = ScreenshotCapture()
                st.session_state.screenshot_capture.clear()
                
                # Create placeholders for live updates
                status_placeholder = st.empty()
                progress_bar = st.progress(0)
                
                # Use BrowserUseAgent directly
                prompt_with_y4m = user_input
                # Prevent repeated execution for the same input
                if not st.session_state.get("browser_action_executed", False):
                    try:
                        status_placeholder.info("🔄 Initializing browser automation...")
                        progress_bar.progress(10)
                        
                        # Create config with TTS if enabled
                        from agents.browser_use_agent import BrowserUseConfig
                        config = BrowserUseConfig(
                            enable_realtime_tts=st.session_state.get('enable_tts', False),
                            tts_voice=st.session_state.get('tts_voice', 'alloy'),
                            tts_model="tts-1"
                        )
                        
                        # Run browser automation using BrowserUseAgent with TTS
                        browser_agent = BrowserUseAgent(config=config)
                        
                        # Set candidate context if TTS enabled
                        if config.enable_realtime_tts and st.session_state.get('candidate_context'):
                            if hasattr(browser_agent, 'answer_generator') and browser_agent.answer_generator:
                                browser_agent.answer_generator.set_context(st.session_state.candidate_context)
                        
                        if config.enable_realtime_tts:
                            status_placeholder.info("🎤 TTS enabled - Ready to answer questions!")
                        
                        status_placeholder.info("🌐 Browser launched, executing tasks...")
                        progress_bar.progress(30)
                        
                        # Use TTS-enabled task if enabled
                        if config.enable_realtime_tts:
                            browser_result = browser_agent.run_task_with_tts_sync(
                                task=prompt_with_y4m,
                                candidate_context=st.session_state.get('candidate_context')
                            )
                        else:
                            browser_result = browser_agent.run_task_sync(prompt_with_y4m)
                        
                        st.session_state.browser_action_executed = True
                        progress_bar.progress(100)
                        status_placeholder.success("✅ All tasks completed!")
                        
                        # Collect screenshots from browser_screenshots directory
                        screenshot_dir = "./browser_screenshots"
                        if os.path.exists(screenshot_dir):
                            screenshot_files = sorted([
                                os.path.join(screenshot_dir, f) 
                                for f in os.listdir(screenshot_dir) 
                                if f.endswith(('.png', '.jpg', '.jpeg'))
                            ])
                            if screenshot_files:
                                if not hasattr(st.session_state, 'screenshot_capture'):
                                    st.session_state.screenshot_capture = ScreenshotCapture()
                                for idx, screenshot_path in enumerate(screenshot_files):
                                    st.session_state.screenshot_capture.add_screenshot(
                                        screenshot_path, 
                                        idx + 1, 
                                        f"Browser automation step {idx + 1}"
                                    )
                        
                        # Display results section with tabs
                        tab1, tab2, tab3 = st.tabs(["📊 Results", "🤖 Agent Logs", "📸 Screenshots"])
                        
                        with tab1:
                            if browser_result:
                                st.success("✅ Browser automation completed successfully!")
                                st.json({"status": "success", "tasks_completed": "all"})
                            else:
                                st.warning("⚠️ Browser automation completed with warnings")
                        
                        with tab2:
                            # Display captured logs
                            if st.session_state.agent_logs:
                                st.markdown("### 🤖 AI Agent Logs (LLM Reasoning)")
                                log_text = "\n".join(st.session_state.agent_logs[-200:])  # Last 200 logs
                                st.code(log_text, language="log", line_numbers=True)
                            else:
                                st.info("No logs captured")
                        
                        with tab3:
                            # Display screenshots
                            if hasattr(st.session_state, 'screenshot_capture'):
                                screenshots = st.session_state.screenshot_capture.get_all_screenshots()
                                if screenshots:
                                    st.markdown(f"### 📸 Captured {len(screenshots)} Screenshots")
                                    cols = st.columns(3)
                                    for idx, screenshot in enumerate(screenshots):
                                        with cols[idx % 3]:
                                            st.image(screenshot['path'], caption=f"Step {screenshot['step']} - {screenshot['timestamp']}")
                                            if screenshot['description']:
                                                st.caption(screenshot['description'])
                                else:
                                    st.info("No screenshots captured during execution")
                            else:
                                st.info("Screenshot capture not initialized")
                        
                    except Exception as e:
                        st.error(f"❌ Browser automation failed: {e}")
                        browser_result = f"Browser automation failed: {str(e)}"
                    
                    # After execution, generate Allure report (no pytest run)
                    generate_allure_report()
                    # Do NOT start the server again here; start it manually ONCE outside Streamlit
                else:
                    st.warning("⚠️ Browser automation already executed for this input. Please enter a new prompt to run again.")

                # Avoid running the same UI prompt a second time through the orchestrator.
                context["ui_tests"] = []

            # Use OrchestratorAgent directly (BrowserUseAgent handles config)
            reporting = Reporting()
            results = {}
            no_tests_ran = False

            if context["ui_tests"] or context["api_tests"] or context["db_tests"]:
                orchestrator = PatchedOrchestratorAgent(
                    enable_tts=st.session_state.get('enable_tts', False),
                    tts_voice=st.session_state.get('tts_voice', 'alloy'),
                    candidate_context=st.session_state.get('candidate_context', None)
                )
                
                # Run each test type using actual orchestrator methods
                test_plan = TestPlan(
                    ui_tests=context.get("ui_tests", []),
                    api_tests=context.get("api_tests", []),
                    db_tests=context.get("db_tests", [])
                )
                
                if test_plan.has_tests():
                    results = orchestrator.execute_test_plan(test_plan)
                else:
                    no_tests_ran = True
                
                reporting.add_run(results)
                reporting.generate_fixed_html_report("test_report_fixed.html", no_tests_ran=no_tests_ran)

            # Create display for browser-only or mixed runs.
            if browser_result and not results:
                unified_result = format_automation_result(browser_result)
            else:
                unified_result = create_unified_results_display(browser_result, results, reporting)

            st.session_state.conversation_history.append({
                "role": "assistant",
                "content": unified_result,
                "timestamp": datetime.datetime.now().strftime("%H:%M:%S")
            })

>>>>>>> 17e4131 (Add interview automation agents, docs, and Streamlit/TTS app)
        if len(st.session_state.conversation_history) >= 2 and st.session_state.current_session_id is None:
            session_id = len(st.session_state.chat_sessions)
            first_user_msg = st.session_state.conversation_history[0]['content']
            title = first_user_msg[:40] + "..." if len(first_user_msg) > 40 else first_user_msg
            new_session = {
                'id': session_id,
                'title': title,
                'messages': st.session_state.conversation_history.copy(),
                'timestamp': datetime.datetime.now().strftime("%H:%M"),
                'date': datetime.datetime.now().strftime('%Y-%m-%d')
            }
            st.session_state.chat_sessions.append(new_session)
            st.session_state.current_session_id = session_id
        elif st.session_state.current_session_id is not None:
            for session in st.session_state.chat_sessions:
                if session['id'] == st.session_state.current_session_id:
                    session['messages'] = st.session_state.conversation_history.copy()
                    break
        st.session_state.running = False
        st.session_state.stop_requested = False
        st.rerun()

if __name__ == "__main__":
    main()
