#!/usr/bin/env python3
"""
Simple camera test to verify Y4M file works
"""
import asyncio
from playwright.async_api import async_playwright
import os

async def simple_camera_test():
    """Simple test to check if Y4M camera works"""
    y4m_path = "/Users/pratik/Downloads/Assesment/mcp_ai_testAgent/sample.y4m"
    
    print("🎥 Simple Y4M Camera Test")
    print("=" * 30)
    
    if not os.path.exists(y4m_path):
        print(f"❌ Y4M file not found: {y4m_path}")
        return
    
    print(f"✅ Y4M file found: {os.path.basename(y4m_path)}")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            args=[
                "--use-fake-ui-for-media-stream",
                "--use-fake-device-for-media-stream",
                f"--use-file-for-fake-video-capture={y4m_path}",
                "--disable-web-security",
                "--allow-running-insecure-content"
            ]
        )
        
        page = await browser.new_page()
        await page.context.grant_permissions(["camera", "microphone"])
        
        # Create a simple HTML page to test camera
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Y4M Camera Test</title>
            <style>
                body { font-family: Arial; padding: 20px; background: #f0f0f0; }
                video { border: 2px solid #333; margin: 10px 0; }
                button { padding: 10px 20px; font-size: 16px; margin: 5px; }
                .status { padding: 10px; margin: 10px 0; border-radius: 5px; }
                .success { background: #d4edda; color: #155724; }
                .error { background: #f8d7da; color: #721c24; }
            </style>
        </head>
        <body>
            <h1>🎥 Y4M Camera Test</h1>
            <button onclick="startCamera()">Start Camera</button>
            <button onclick="stopCamera()">Stop Camera</button>
            <div id="status" class="status">Click 'Start Camera' to test Y4M simulation</div>
            <br>
            <video id="video" width="640" height="480" autoplay muted></video>
            
            <script>
                let stream = null;
                
                async function startCamera() {
                    const statusDiv = document.getElementById('status');
                    const video = document.getElementById('video');
                    
                    try {
                        statusDiv.textContent = '🔄 Requesting camera access...';
                        statusDiv.className = 'status';
                        
                        stream = await navigator.mediaDevices.getUserMedia({ 
                            video: true, 
                            audio: false 
                        });
                        
                        video.srcObject = stream;
                        statusDiv.textContent = '✅ Y4M camera simulation active!';
                        statusDiv.className = 'status success';
                        
                        console.log('Camera stream:', stream);
                        console.log('Video tracks:', stream.getVideoTracks());
                        
                    } catch (error) {
                        statusDiv.textContent = '❌ Camera error: ' + error.message;
                        statusDiv.className = 'status error';
                        console.error('Camera error:', error);
                    }
                }
                
                function stopCamera() {
                    if (stream) {
                        stream.getTracks().forEach(track => track.stop());
                        document.getElementById('video').srcObject = null;
                        document.getElementById('status').textContent = '⏹️ Camera stopped';
                        document.getElementById('status').className = 'status';
                    }
                }
                
                // Auto-start camera after 2 seconds
                setTimeout(startCamera, 2000);
            </script>
        </body>
        </html>
        """
        
        await page.goto(f"data:text/html,{html}")
        
        print("🌐 Camera test page loaded")
        print("⏰ Camera will auto-start in 2 seconds...")
        
        # Wait for camera to start
        await page.wait_for_timeout(5000)
        
        # Check if video is playing
        try:
            video_width = await page.evaluate("document.getElementById('video').videoWidth")
            video_height = await page.evaluate("document.getElementById('video').videoHeight")
            
            if video_width > 0 and video_height > 0:
                print(f"✅ SUCCESS: Video playing at {video_width}x{video_height}")
                print("🎬 Y4M file is being used as camera input!")
            else:
                print("❌ FAILED: Video not playing")
                
        except Exception as e:
            print(f"❌ Error checking video: {e}")
        
        print("\n📋 Instructions:")
        print("1. Look at the browser window")
        print("2. You should see your Y4M video playing")
        print("3. This confirms Y4M camera simulation is working")
        
        input("\nPress Enter to close browser...")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(simple_camera_test())