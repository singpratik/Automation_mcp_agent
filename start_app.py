#!/usr/bin/env python3
"""
Startup script for the browser automation Streamlit app
"""
import os
import sys
import subprocess
import signal
import time
from dotenv import load_dotenv

def check_requirements():
    """Check if all requirements are met"""
    print("🔍 Checking requirements...")
    
    # Load environment variables
    load_dotenv()
    
    # Check OpenAI API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY not found in .env file")
        print("Please add your OpenAI API key to the .env file:")
        print("OPENAI_API_KEY=your-api-key-here")
        return False
    
    print(f"✅ OpenAI API key found: {api_key[:10]}...")
    
    # Check Y4M file
    y4m_path = "/Users/pratik/Downloads/Assesment/mcp_ai_testAgent/Johnny_1280x720_60.y4m"
    if os.path.exists(y4m_path):
        file_size = os.path.getsize(y4m_path) / (1024*1024)  # MB
        print(f"✅ Y4M file found: {file_size:.1f} MB")
    else:
        print("⚠️  Y4M file not found - camera simulation will be disabled")
    
    return True

def kill_existing_processes():
    """Kill any existing Streamlit processes"""
    try:
        subprocess.run(["pkill", "-f", "streamlit"], check=False)
        time.sleep(2)
        print("🧹 Cleaned up existing processes")
    except:
        pass

def start_streamlit():
    """Start the Streamlit application"""
    print("🚀 Starting Streamlit application...")
    
    # Find available port
    for port in range(8576, 8590):
        try:
            # Check if port is available
            result = subprocess.run(
                ["lsof", "-i", f":{port}"], 
                capture_output=True, 
                text=True
            )
            if result.returncode != 0:  # Port is available
                print(f"🌐 Starting on port {port}")
                
                # Start Streamlit
                cmd = [
                    sys.executable, "-m", "streamlit", "run", 
                    "streamlit_app.py", 
                    "--server.port", str(port),
                    "--server.headless", "true",
                    "--browser.gatherUsageStats", "false"
                ]
                
                process = subprocess.Popen(cmd)
                
                print(f"✅ Streamlit started successfully!")
                print(f"🌍 Open your browser and go to: http://localhost:{port}")
                print("🛑 Press Ctrl+C to stop the application")
                
                try:
                    process.wait()
                except KeyboardInterrupt:
                    print("\n🛑 Stopping application...")
                    process.terminate()
                    process.wait()
                    print("✅ Application stopped")
                
                return True
                
        except Exception as e:
            continue
    
    print("❌ No available ports found")
    return False

def main():
    """Main function"""
    print("🤖 Browser Automation Agent Startup")
    print("=" * 40)
    
    if not check_requirements():
        sys.exit(1)
    
    kill_existing_processes()
    
    if not start_streamlit():
        sys.exit(1)

if __name__ == "__main__":
    main()