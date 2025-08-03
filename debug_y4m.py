#!/usr/bin/env python3
"""
Debug Y4M camera bypass functionality
"""
import asyncio
from playwright.async_api import async_playwright
import os

async def debug_y4m():
    """Debug Y4M camera functionality"""
    y4m_path = "/Users/pratik/Downloads/Assesment/mcp_ai_testAgent/Johnny_1280x720_60.y4m"
    
    print("🔍 Y4M Debug Test")
    print("=" * 30)
    
    # Check file
    if os.path.exists(y4m_path):
        size_mb = os.path.getsize(y4m_path) / (1024*1024)
        print(f"✅ Y4M file exists: {size_mb:.1f} MB")
        
        # Check header
        with open(y4m_path, 'rb') as f:
            header = f.read(50).decode('ascii', errors='ignore')
            print(f"📄 Header: {header}")
    else:
        print(f"❌ Y4M file not found: {y4m_path}")
        return
    
    async with async_playwright() as p:
        # Test current browser args
        browser_args = [
            "--no-first-run",
            "--use-fake-ui-for-media-stream",
            "--use-fake-device-for-media-stream",
            "--autoplay-policy=no-user-gesture-required",
            "--disable-web-security",
            "--allow-running-insecure-content",
            "--auto-accept-camera-and-microphone-capture",
            "--allow-file-access-from-files",
            "--disable-features=VizDisplayCompositor",
            f"--use-file-for-fake-video-capture={y4m_path}"
        ]
        
        print(f"🚀 Browser args: {len(browser_args)} arguments")
        for arg in browser_args:
            print(f"  {arg}")
        
        browser = await p.chromium.launch(
            headless=False,
            args=browser_args
        )
        
        page = await browser.new_page()
        await page.context.grant_permissions(["camera", "microphone"])
        
        # Simple camera test
        html = """
        <!DOCTYPE html>
        <html>
        <head><title>Y4M Debug Test</title></head>
        <body>
            <h1>🎥 Y4M Debug Test</h1>
            <video id="video" width="640" height="480" autoplay muted></video>
            <div id="status">Starting camera test...</div>
            <script>
                async function testCamera() {
                    try {
                        const stream = await navigator.mediaDevices.getUserMedia({ 
                            video: true, 
                            audio: false 
                        });
                        document.getElementById('video').srcObject = stream;
                        document.getElementById('status').textContent = '✅ Camera active';
                        console.log('Stream:', stream);
                        console.log('Video tracks:', stream.getVideoTracks());
                    } catch (error) {
                        document.getElementById('status').textContent = '❌ Error: ' + error.message;
                        console.error('Camera error:', error);
                    }
                }
                setTimeout(testCamera, 1000);
            </script>
        </body>
        </html>
        """
        
        await page.goto(f"data:text/html,{html}")
        await page.wait_for_timeout(3000)
        
        # Check if video is playing
        try:
            video_width = await page.evaluate("document.getElementById('video').videoWidth")
            video_height = await page.evaluate("document.getElementById('video').videoHeight")
            
            if video_width > 0 and video_height > 0:
                print(f"✅ SUCCESS: Video playing at {video_width}x{video_height}")
            else:
                print("❌ FAILED: Video not playing")
                
            # Get video element properties
            video_props = await page.evaluate("""
                const video = document.getElementById('video');
                return {
                    videoWidth: video.videoWidth,
                    videoHeight: video.videoHeight,
                    readyState: video.readyState,
                    currentTime: video.currentTime,
                    duration: video.duration,
                    paused: video.paused
                };
            """)
            print(f"📊 Video properties: {video_props}")
            
        except Exception as e:
            print(f"❌ Error checking video: {e}")
        
        input("\nPress Enter to close browser...")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(debug_y4m())