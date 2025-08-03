#!/usr/bin/env python3
"""
Test media devices detection with different browser configurations
"""
import asyncio
from playwright.async_api import async_playwright
import os

async def test_media_devices():
    """Test different configurations for media device detection"""
    y4m_path = "/Users/pratik/Downloads/Assesment/mcp_ai_testAgent/sample.y4m"
    
    if not os.path.exists(y4m_path):
        print(f"❌ Y4M file not found: {y4m_path}")
        return
    
    print("🎥 Testing Media Device Detection")
    print("=" * 40)
    print(f"✅ Y4M file: {y4m_path}")
    print(f"📊 Size: {os.path.getsize(y4m_path) / (1024*1024):.1f} MB")
    
    async with async_playwright() as p:
        # Test configuration 1: Basic fake devices
        print("\n🧪 Test 1: Basic fake devices")
        browser1 = await p.chromium.launch(
            headless=False,
            args=[
                "--use-fake-ui-for-media-stream",
                "--use-fake-device-for-media-stream"
            ]
        )
        
        page1 = await browser1.new_page()
        await page1.goto("data:text/html,<html><body><h1>Test 1: Basic Fake Devices</h1><script>navigator.mediaDevices.enumerateDevices().then(devices => { console.log('Devices:', devices); document.body.innerHTML += '<p>Devices: ' + devices.length + '</p>'; devices.forEach(d => document.body.innerHTML += '<p>' + d.kind + ': ' + d.label + '</p>'); });</script></body></html>")
        await page1.wait_for_timeout(3000)
        await browser1.close()
        
        # Test configuration 2: With Y4M file
        print("\n🧪 Test 2: With Y4M file")
        browser2 = await p.chromium.launch(
            headless=False,
            args=[
                "--use-fake-ui-for-media-stream",
                "--use-fake-device-for-media-stream",
                f"--use-file-for-fake-video-capture={y4m_path}",
                "--disable-web-security"
            ]
        )
        
        page2 = await browser2.new_page()
        await page2.goto("data:text/html,<html><body><h1>Test 2: With Y4M File</h1><script>navigator.mediaDevices.enumerateDevices().then(devices => { console.log('Devices:', devices); document.body.innerHTML += '<p>Devices: ' + devices.length + '</p>'; devices.forEach(d => document.body.innerHTML += '<p>' + d.kind + ': ' + d.label + '</p>'); });</script></body></html>")
        await page2.wait_for_timeout(3000)
        await browser2.close()
        
        # Test configuration 3: Try to access camera directly
        print("\n🧪 Test 3: Direct camera access")
        browser3 = await p.chromium.launch(
            headless=False,
            args=[
                "--use-fake-ui-for-media-stream",
                "--use-fake-device-for-media-stream",
                f"--use-file-for-fake-video-capture={y4m_path}",
                "--disable-web-security",
                "--allow-running-insecure-content"
            ]
        )
        
        page3 = await browser3.new_page()
        await page3.context.grant_permissions(["camera", "microphone"])
        
        html_content = """
        <html>
        <body>
            <h1>Test 3: Direct Camera Access</h1>
            <video id="video" width="320" height="240" autoplay></video>
            <p id="status">Requesting camera...</p>
            <script>
                navigator.mediaDevices.getUserMedia({ video: true, audio: false })
                    .then(stream => {
                        document.getElementById('video').srcObject = stream;
                        document.getElementById('status').textContent = '✅ Camera stream active';
                        console.log('Camera stream:', stream);
                    })
                    .catch(err => {
                        document.getElementById('status').textContent = '❌ Camera error: ' + err.message;
                        console.error('Camera error:', err);
                    });
            </script>
        </body>
        </html>
        """
        
        await page3.goto(f"data:text/html,{html_content}")
        await page3.wait_for_timeout(5000)
        
        # Check if video is playing
        video_playing = await page3.evaluate("document.getElementById('video').videoWidth > 0")
        if video_playing:
            print("✅ Video is playing - Y4M simulation working!")
        else:
            print("❌ Video not playing - Y4M simulation failed")
        
        input("\nPress Enter to close browser and continue...")
        await browser3.close()

if __name__ == "__main__":
    asyncio.run(test_media_devices())