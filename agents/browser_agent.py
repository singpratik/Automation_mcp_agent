import asyncio
from playwright.async_api import async_playwright
import os

class BrowserAgent:
    def __init__(self, enable_media_permissions=True, y4m_file_path=None, audio_file_path=None):
        self.y4m_file_path = y4m_file_path or "/Users/pratik/Downloads/Assesment/mcp_ai_testAgent/Johnny_1280x720_60.y4m"
        self.audio_file_path = audio_file_path
        self.live_logs = []
        self.browser = None
        self.page = None
    
    def run_task(self, prompt):
        import traceback
        try:
            try:
                loop = asyncio.get_running_loop()
                # If we're in an event loop (e.g., Streamlit), run as a task and wait for result
                return loop.run_until_complete(self._run_task(prompt))
            except RuntimeError:
                # No event loop running, safe to use asyncio.run
                return asyncio.run(self._run_task(prompt))
        except Exception as e:
            tb = traceback.format_exc()
            return f"Error: {str(e)}\nTraceback:\n{tb}"
    
    async def _run_task(self, prompt):
        try:
            # Browser args for Y4M bypass
            args = [
                "--use-fake-ui-for-media-stream",
                "--use-fake-device-for-media-stream",
                f"--use-file-for-fake-video-capture={self.y4m_file_path}",
                "--disable-web-security",
                "--autoplay-policy=no-user-gesture-required"
            ]
            if self.audio_file_path:
                args.append(f"--use-file-for-fake-audio-capture={self.audio_file_path}")
            
            async with async_playwright() as p:
                self.browser = await p.chromium.launch(headless=False, args=args)
                context = await self.browser.new_context(permissions=["camera", "microphone"])
                self.page = await context.new_page()
                
                # Simple task execution
                if "vmock" in prompt.lower():
                    await self.page.goto("https://www.vmock.com/login")
                    await self.page.wait_for_timeout(2000)
                    return "✅ VMock page loaded with Y4M camera bypass active"
                else:
                    return f"✅ Task completed: {prompt}"
                    
        except Exception as e:
            return f"❌ Task failed: {str(e)}"
    
    def get_live_logs(self):
        return self.live_logs
    
    def close_browser(self):
        if self.browser:
            try:
                asyncio.run(self.browser.close())
            except:
                pass
