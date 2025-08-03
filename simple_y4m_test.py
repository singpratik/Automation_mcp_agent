#!/usr/bin/env python3
"""
Simple Y4M test with minimal browser args
"""
import asyncio
from playwright.async_api import async_playwright
import os

async def simple_y4m_test():
    """Test Y4M with minimal configuration"""
    y4m_path = "/Users/pratik/Downloads/Assesment/mcp_ai_testAgent/Johnny_1280x720_60.y4m"
    
    print("🎥 Simple Y4M Test")
    print("=" * 20)
    
    if not os.path.exists(y4m_path):
        print(f"❌ Y4M file not found: {y4m_path}")
        return
    
    print(f"✅ Y4M file found")
    
    async with async_playwright() as p:
        # Minimal browser args that work
        browser_args = [
            "--use-fake-ui-for-media-stream",
            "--use-fake-device-for-media-stream",
            f"--use-file-for-fake-video-capture={y4m_path}"
        ]
        
        print(f"🚀 Using minimal args: {browser_args}")
        
        try:
            browser = await p.chromium.launch(
                headless=False,
                args=browser_args
            )
            
            page = await browser.new_page()
            
            # Simple test page
            await page.goto("data:text/html,<h1>Y4M Test - Check Console</h1><script>navigator.mediaDevices.getUserMedia({video:true}).then(s=>console.log('SUCCESS:',s)).catch(e=>console.log('ERROR:',e))</script>")
            
            await page.wait_for_timeout(3000)
            print("✅ Browser launched successfully")
            
            input("Press Enter to close...")
            await browser.close()
            
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(simple_y4m_test())