#!/usr/bin/env python3
"""
Final Y4M test with proper error handling
"""
import asyncio
from playwright.async_api import async_playwright
import os

async def final_y4m_test():
    """Final test for Y4M functionality"""
    y4m_path = "/Users/pratik/Downloads/Assesment/mcp_ai_testAgent/Johnny_1280x720_60.y4m"
    
    print("🎯 Final Y4M Test")
    print("=" * 20)
    
    if not os.path.exists(y4m_path):
        print(f"❌ Y4M file not found")
        return False
    
    print(f"✅ Y4M file ready")
    
    browser_args = [
        "--use-fake-ui-for-media-stream",
        "--use-fake-device-for-media-stream",
        "--autoplay-policy=no-user-gesture-required", 
        "--disable-web-security",
        "--allow-running-insecure-content",
        f"--use-file-for-fake-video-capture={y4m_path}"
    ]
    
    async with async_playwright() as p:
        try:
            browser = await p.chromium.launch(headless=False, args=browser_args)
            page = await browser.new_page()
            await page.context.grant_permissions(["camera", "microphone"])
            
            # Simple camera test
            await page.goto("data:text/html,<h1>Y4M Test</h1><video id='v' width='320' height='240' autoplay></video><script>navigator.mediaDevices.getUserMedia({video:true}).then(s=>{document.getElementById('v').srcObject=s;console.log('SUCCESS')}).catch(e=>console.log('ERROR:',e))</script>")
            
            await page.wait_for_timeout(2000)
            
            # Check video
            try:
                video_width = await page.evaluate("document.getElementById('v') ? document.getElementById('v').videoWidth : 0")
                if video_width > 0:
                    print("✅ Y4M WORKING - Camera bypass successful!")
                    return True
                else:
                    print("❌ Y4M NOT WORKING - No video stream")
                    return False
            except:
                print("❌ Y4M NOT WORKING - Video check failed")
                return False
            finally:
                await browser.close()
                
        except Exception as e:
            print(f"❌ Browser error: {e}")
            return False

if __name__ == "__main__":
    result = asyncio.run(final_y4m_test())
    print(f"\n🎯 Result: {'SUCCESS' if result else 'FAILED'}")