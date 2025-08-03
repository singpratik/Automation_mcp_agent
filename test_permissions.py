#!/usr/bin/env python3
"""
Test camera/microphone permissions with Y4M
"""
import asyncio
from playwright.async_api import async_playwright
import os

async def test_permissions():
    """Test camera permissions with Y4M bypass"""
    y4m_path = "/Users/pratik/Downloads/Assesment/mcp_ai_testAgent/Johnny_1280x720_60.y4m"
    
    browser_args = [
        "--use-fake-ui-for-media-stream",
        "--use-fake-device-for-media-stream", 
        f"--use-file-for-fake-video-capture={y4m_path}",
        "--disable-web-security",
        "--allow-running-insecure-content",
        "--autoplay-policy=no-user-gesture-required",
        "--allow-file-access-from-files",
        "--disable-features=VizDisplayCompositor"
    ]
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, args=browser_args)
        
        # Create context with permissions
        context = await browser.new_context(
            permissions=["camera", "microphone"]
        )
        
        page = await context.new_page()
        
        # Test camera access
        html = """
        <html><body>
        <h1>Camera Permission Test</h1>
        <video id="video" width="640" height="480" autoplay></video>
        <div id="status">Testing...</div>
        <script>
        navigator.mediaDevices.getUserMedia({video: true, audio: true})
        .then(stream => {
            document.getElementById('video').srcObject = stream;
            document.getElementById('status').textContent = '✅ Camera/Mic ALLOWED - Y4M Active';
        })
        .catch(err => {
            document.getElementById('status').textContent = '❌ Permission DENIED: ' + err.message;
        });
        </script>
        </body></html>
        """
        
        await page.goto(f"data:text/html,{html}")
        await page.wait_for_timeout(3000)
        
        # Check result
        status = await page.evaluate("document.getElementById('status').textContent")
        print(f"Result: {status}")
        
        input("Press Enter to close...")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_permissions())