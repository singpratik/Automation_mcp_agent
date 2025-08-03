#!/usr/bin/env python3
"""
Direct Playwright test with Y4M file for camera simulation
"""
import asyncio
from playwright.async_api import async_playwright

async def test_y4m_camera():
    """Test Y4M file with direct Playwright"""
    print("🎥 Y4M Camera Simulation Test")
    print("=" * 40)
    y4m_path = "/Users/pratik/Downloads/Assesment/mcp_ai_testAgent/sample.y4m"
    
    async with async_playwright() as p:
        # Check if Y4M file exists
        import os
        if not os.path.exists(y4m_path):
            print(f"❌ Y4M file not found: {y4m_path}")
            return
        
        print(f"✅ Y4M file found: {y4m_path}")
        print(f"📊 File size: {os.path.getsize(y4m_path) / (1024*1024):.1f} MB")
        
        browser = await p.chromium.launch(
            headless=False,
            args=[
                "--use-fake-ui-for-media-stream",
                "--use-fake-device-for-media-stream",
                f"--use-file-for-fake-video-capture={y4m_path}",
                "--use-file-for-fake-audio-capture=/System/Library/Sounds/Ping.aiff",
                "--allow-running-insecure-content",
                "--disable-web-security",
                "--disable-features=VizDisplayCompositor",
                "--autoplay-policy=no-user-gesture-required",
                "--allow-file-access-from-files",
                "--disable-blink-features=AutomationControlled",
                "--enable-usermedia-screen-capturing",
                "--allow-http-screen-capture"
            ]
        )
        
        page = await browser.new_page()
        
        # Grant camera permissions
        context = browser.contexts[0]
        await context.grant_permissions(["camera", "microphone"])
        
        # Test with a simpler camera test page first
        await page.goto("https://www.onlinemictest.com/webcam-test/")
        
        print("🌐 Navigated to webcam test page")
        await page.wait_for_timeout(3000)
        
        print("✅ Browser opened with Y4M camera simulation")
        print("🎥 Y4M file should be active as camera input")
        
        # Wait for page to load
        await page.wait_for_timeout(3000)
        
        # Try to start webcam test
        try:
            # Look for start test button
            start_button = page.locator("button:has-text('Start webcam test'), button:has-text('Test webcam'), .start-test")
            if await start_button.first.is_visible(timeout=5000):
                await start_button.first.click()
                print("✅ Clicked start webcam test")
                await page.wait_for_timeout(3000)
            
            # Check if video element is present
            video_element = page.locator("video")
            if await video_element.is_visible(timeout=5000):
                print("✅ Video element found - Y4M should be playing")
            else:
                print("⚠️ No video element found")
                
        except Exception as e:
            print(f"⚠️ Error during test: {e}")
            
        # Also try the original site
        print("\n🔄 Trying webcamtests.com...")
        await page.goto("https://webcamtests.com/")
        await page.wait_for_timeout(3000)
        
        try:
            test_button = page.locator("text=Test my cam")
            if await test_button.is_visible():
                await test_button.click()
                print("✅ Clicked Test my cam button")
                await page.wait_for_timeout(3000)
        except:
            pass
        
        # Check for any video elements
        video_elements = await page.locator("video").count()
        print(f"\n📹 Found {video_elements} video element(s)")
        
        if video_elements > 0:
            print("✅ Video elements detected - Y4M simulation may be working")
        else:
            print("❌ No video elements found - Y4M simulation may not be working")
            
        # Wait for user to check
        input("\n📷 Check if Y4M video is playing in the camera test. Press Enter to close browser...")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_y4m_camera())