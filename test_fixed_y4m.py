#!/usr/bin/env python3
"""
Test the fixed Y4M configuration
"""
import asyncio
from playwright.async_api import async_playwright
import os

async def test_fixed_y4m():
    """Test Y4M with fixed browser configuration"""
    y4m_path = "/Users/pratik/Downloads/Assesment/mcp_ai_testAgent/Johnny_1280x720_60.y4m"
    
    print("🔧 Testing Fixed Y4M Configuration")
    print("=" * 35)
    
    if not os.path.exists(y4m_path):
        print(f"❌ Y4M file not found: {y4m_path}")
        return
    
    print(f"✅ Y4M file found ({os.path.getsize(y4m_path)/(1024*1024):.1f} MB)")
    
    # Fixed browser args (same as in browser_agent.py)
    browser_args = [
        "--use-fake-ui-for-media-stream",
        "--use-fake-device-for-media-stream", 
        "--autoplay-policy=no-user-gesture-required",
        "--disable-web-security",
        "--allow-running-insecure-content",
        f"--use-file-for-fake-video-capture={y4m_path}"
    ]
    
    print(f"🚀 Browser args: {browser_args}")
    
    async with async_playwright() as p:
        try:
            browser = await p.chromium.launch(
                headless=False,
                args=browser_args
            )
            
            page = await browser.new_page()
            await page.context.grant_permissions(["camera", "microphone"])
            
            # Test camera access
            html = """
            <!DOCTYPE html>
            <html>
            <head><title>Fixed Y4M Test</title></head>
            <body style="font-family: Arial; padding: 20px;">
                <h1>🎥 Fixed Y4M Camera Test</h1>
                <video id="video" width="640" height="480" autoplay muted style="border: 2px solid #333;"></video>
                <div id="status" style="margin: 10px 0; padding: 10px; background: #f0f0f0;">Testing camera...</div>
                <script>
                    async function testCamera() {
                        const status = document.getElementById('status');
                        const video = document.getElementById('video');
                        
                        try {
                            status.textContent = '🔄 Requesting camera access...';
                            const stream = await navigator.mediaDevices.getUserMedia({ video: true });
                            
                            video.srcObject = stream;
                            status.textContent = '✅ Y4M camera active! Video should be playing.';
                            status.style.background = '#d4edda';
                            
                            console.log('Stream active:', stream);
                            console.log('Video tracks:', stream.getVideoTracks());
                            
                        } catch (error) {
                            status.textContent = '❌ Camera error: ' + error.message;
                            status.style.background = '#f8d7da';
                            console.error('Camera error:', error);
                        }
                    }
                    
                    // Auto-start after 1 second
                    setTimeout(testCamera, 1000);
                </script>
            </body>
            </html>
            """
            
            await page.goto(f"data:text/html,{html}")
            await page.wait_for_timeout(3000)
            
            # Check if video is playing
            video_width = await page.evaluate("document.getElementById('video').videoWidth")
            video_height = await page.evaluate("document.getElementById('video').videoHeight")
            
            if video_width > 0 and video_height > 0:
                print(f"✅ SUCCESS: Y4M video playing at {video_width}x{video_height}")
                print("🎬 Y4M camera bypass is working!")
            else:
                print("❌ FAILED: Video not playing")
            
            print("\n📋 Check the browser window - you should see the Y4M video playing")
            input("Press Enter to close browser...")
            
            await browser.close()
            print("✅ Test completed")
            
        except Exception as e:
            print(f"❌ Browser launch failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_fixed_y4m())