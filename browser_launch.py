import asyncio
import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

import allure

try:
    from Automation_mcp_agent.session_memory import SessionMemory
    from Automation_mcp_agent.agents.browser_agent import BrowserAgent
except ImportError:
    from session_memory import SessionMemory
    from agents.browser_agent import BrowserAgent

def get_browser_agentic_task(task_prompt=None):
    """
    Use BrowserAgent (browser-use with Chrome channel) for browser automation.
    """
    agent = BrowserAgent(browser_channel="chrome", browser_engine="browser-use")
    return agent, SessionMemory()

# Unified agentic function for both Streamlit and Allure reporting
def run_browser_agentic_task(task_prompt=None):
    try:
        if not task_prompt:
            task_prompt = "open https://example.com"
        agent, session_memory = get_browser_agentic_task(task_prompt)
        allure.attach(str(task_prompt), name="User Prompt", attachment_type=allure.attachment_type.TEXT)
        allure.attach("Agent initialized", name="Agent", attachment_type=allure.attachment_type.TEXT)

        result = agent.run_task(task_prompt)
        session_memory.log_action("result", {"prompt": task_prompt}, result=result)
        allure.attach(str(result), name="Automation Result", attachment_type=allure.attachment_type.TEXT)

        if agent.last_api_report:
            allure.attach(
                json.dumps(agent.last_api_report, indent=2),
                name="API Monitoring Report Paths",
                attachment_type=allure.attachment_type.JSON,
            )

        if "❌" in result:
            allure.attach(f"Automation crashed: {result}", name="Automation Crash", attachment_type=allure.attachment_type.TEXT)
        else:
            allure.attach("Automation succeeded", name="Automation Success", attachment_type=allure.attachment_type.TEXT)

        with allure.step("Close browser"):
            allure.attach("Browser closed (auto or not exposed)", name="Browser", attachment_type=allure.attachment_type.TEXT)

        allure.dynamic.title("Agentic browser-use automation test")
        allure.dynamic.description("This test launches Chrome via browser-use, performs agentic automation, and closes the browser.")
        return result

    except Exception as e:
        allure.attach(str(e), name="Error", attachment_type=allure.attachment_type.TEXT)
        import traceback
        allure.attach(traceback.format_exc(), name="Traceback", attachment_type=allure.attachment_type.TEXT)
        raise

# Synchronous entry point for manual runs
if __name__ == "__main__":
    import sys
    prompt = sys.argv[1] if len(sys.argv) > 1 else None
    run_browser_agentic_task(prompt)
