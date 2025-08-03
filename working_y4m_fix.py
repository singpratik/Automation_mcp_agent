#!/usr/bin/env python3
"""
Working Y4M fix with Chrome compatibility
"""
import asyncio
from playwright.async_api import async_playwright
import os

async def working_y4m_fix():
    """Working Y4M implementation"""
    y4m_path = "/Users/pratik/Downloads/Assesment/mcp_ai_testAgent/Johnny_1280x720_60.y4m"
    
    print("🔧 Working Y4M Fix")
    print("=" * 20)
    
    # Chrome-compatible args for Y4M
    browser_args = [
        "--use-fake-ui-for-media-stream",
        "--use-fake-device-for-media-stream",
        f"--use-file-for-fake-video-capture={y4m_path}",
        "--disable-web-security",
        "--allow-running-insecure-content",
        "--autoplay-policy=no-user-gesture-required",
        "--disable-blink-features=AutomationControlled"
    ]
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            args=browser_args
        )
        
        context = await browser.new_context(
            permissions=["camera", "microphone"]
        )
        
        page = await context.new_page()
        
        # Test with webcam test site
        await page.goto("https://webcamtests.com/")
        await page.wait_for_timeout(3000)
        
        try:
            # Click test button if available
            test_btn = page.locator("text=Test my cam")
            if await test_btn.is_visible():
                await test_btn.click()
                await page.wait_for_timeout(3000)
                print("✅ Clicked test button")
        except:
            pass
        
        # Check for video elements
        video_count = await page.locator("video").count()
        print(f"📹 Found {video_count} video elements")
        
        if video_count > 0:
            print("✅ Y4M should be working - check browser window")
        else:
            print("❌ No video elements found")
        
        input("Press Enter to close...")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(working_y4m_fix())