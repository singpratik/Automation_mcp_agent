import streamlit as st
import os
import time
import datetime as dt
import subprocess
import threading
from dotenv import load_dotenv

load_dotenv()

def main():
    st.set_page_config(page_title="🕵️ VMock Automation", layout="wide")
    
    st.markdown("""
    <style>
    .stApp {
        background: #f8f9fa;
        color: #1a1a1a;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }
    
    .status-success {
        background: #dcfce7;
        color: #166534;
        border: 1px solid #bbf7d0;
        padding: 8px 16px;
        border-radius: 8px;
        margin: 8px 0;
    }
    
    .status-error {
        background: #fef2f2;
        color: #dc2626;
        border: 1px solid #fecaca;
        padding: 8px 16px;
        border-radius: 8px;
        margin: 8px 0;
    }
    
    .status-info {
        background: #eff6ff;
        color: #1d4ed8;
        border: 1px solid #bfdbfe;
        padding: 8px 16px;
        border-radius: 8px;
        margin: 8px 0;
    }
    
    .log-container {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 16px;
        font-family: monospace;
        font-size: 0.9rem;
        max-height: 400px;
        overflow-y: auto;
    }
    </style>
    """, unsafe_allow_html=True)

    # Initialize session state
    if 'task_running' not in st.session_state:
        st.session_state.task_running = False
    if 'task_result' not in st.session_state:
        st.session_state.task_result = None
    if 'task_logs' not in st.session_state:
        st.session_state.task_logs = []

    st.title("🕵️ VMock Interview Automation")
    st.markdown("Automate VMock login and interview setup process")

    # Configuration section
    st.header("⚙️ Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        email = st.text_input(
            "📧 Email",
            value="_7fresh@mailinator.com",
            help="VMock login email"
        )
        
        password = st.text_input(
            "🔒 Password",
            value="Welcome@123",
            type="password",
            help="VMock login password"
        )
    
    with col2:
        y4m_file = st.text_input(
            "🎥 Y4M File (Optional)",
            value="/Users/pratik/Downloads/Assesment/mcp_ai_testAgent/Johnny_1280x720_60.y4m",
            help="Path to Y4M video file for camera simulation"
        )
        
        # Y4M file validation
        if y4m_file.strip():
            if os.path.exists(y4m_file.strip()):
                file_size = os.path.getsize(y4m_file.strip()) / (1024*1024)
                st.markdown(f'<div class="status-success">✅ Y4M file found ({file_size:.1f} MB)</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="status-error">❌ Y4M file not found</div>', unsafe_allow_html=True)

    # Action buttons
    st.header("🚀 Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🎯 Start VMock Automation", disabled=st.session_state.task_running):
            if not email or not password:
                st.error("Please provide both email and password")
            else:
                st.session_state.task_running = True
                st.session_state.task_result = None
                st.session_state.task_logs = []
                st.rerun()
    
    with col2:
        if st.button("🧪 Test Simple Browser", disabled=st.session_state.task_running):
            st.session_state.task_running = True
            st.session_state.task_result = None
            st.session_state.task_logs = []
            # Set a flag for simple test
            st.session_state.simple_test = True
            st.rerun()
    
    with col3:
        if st.button("🛑 Stop Task", disabled=not st.session_state.task_running):
            st.session_state.task_running = False
            st.rerun()

    # Status display
    if st.session_state.task_running:
        st.markdown('<div class="status-info">⚡ Task is running... Please wait</div>', unsafe_allow_html=True)
        
        # Progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Run the automation task
        def run_automation():
            try:
                # Create the automation script
                if hasattr(st.session_state, 'simple_test') and st.session_state.simple_test:
                    # Simple browser test
                    script_content = '''
import asyncio
from playwright.async_api import async_playwright

async def simple_test():
    print("LOG: 🚀 Starting simple browser test...")
    
    try:
        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(headless=False)
        page = await browser.new_page()
        
        print("LOG: ✅ Browser launched successfully")
        
        await page.goto("https://www.google.com")
        print("LOG: ✅ Navigated to Google")
        
        await asyncio.sleep(5)
        
        await browser.close()
        print("LOG: ✅ Browser closed")
        print("RESULT: Simple browser test completed successfully")
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        print("RESULT: Simple browser test failed")

if __name__ == "__main__":
    asyncio.run(simple_test())
'''
                    delattr(st.session_state, 'simple_test')
                else:
                    # VMock automation
                    y4m_path = y4m_file.strip() if y4m_file.strip() and os.path.exists(y4m_file.strip()) else None
                    script_content = f'''
import sys
import os
sys.path.append("{os.getcwd()}")

from simple_browser_agent import run_vmock_automation

if __name__ == "__main__":
    try:
        result, logs = run_vmock_automation(
            email="{email}",
            password="{password}",
            y4m_file_path="{y4m_path}" if "{y4m_path}" else None
        )
        
        print(f"RESULT: {{result}}")
        for log in logs:
            print(f"LOG: {{log}}")
            
    except Exception as e:
        print(f"ERROR: {{str(e)}}")
        print("RESULT: VMock automation failed")
'''
                
                # Write script to temp file
                with open("temp_automation.py", "w") as f:
                    f.write(script_content)
                
                # Run the script
                process = subprocess.Popen(
                    ["python3", "temp_automation.py"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    cwd=os.getcwd()
                )
                
                # Monitor progress
                logs = []
                result = "Task started..."
                
                while process.poll() is None:
                    # Read output line by line
                    line = process.stdout.readline()
                    if line:
                        line = line.strip()
                        if line.startswith('LOG:'):
                            logs.append(line[5:])
                        elif line.startswith('RESULT:'):
                            result = line[8:]
                        elif line.startswith('ERROR:'):
                            result = f"Error: {line[7:]}"
                    
                    # Update progress (simulate)
                    progress = min(len(logs) * 10, 90)
                    progress_bar.progress(progress)
                    status_text.text(f"Progress: {len(logs)} steps completed")
                    
                    time.sleep(0.5)
                
                # Get final output
                stdout, stderr = process.communicate()
                
                # Parse remaining output
                for line in stdout.split('\n'):
                    line = line.strip()
                    if line.startswith('LOG:'):
                        logs.append(line[5:])
                    elif line.startswith('RESULT:'):
                        result = line[8:]
                    elif line.startswith('ERROR:'):
                        result = f"Error: {line[7:]}"
                
                if stderr:
                    result += f"\n\nStderr: {stderr}"
                
                # Update session state
                st.session_state.task_result = result
                st.session_state.task_logs = logs
                st.session_state.task_running = False
                
                # Clean up
                try:
                    os.remove("temp_automation.py")
                except:
                    pass
                
                progress_bar.progress(100)
                status_text.text("Task completed!")
                
            except Exception as e:
                st.session_state.task_result = f"Error: {str(e)}"
                st.session_state.task_running = False
        
        # Start the task in a thread
        thread = threading.Thread(target=run_automation)
        thread.daemon = True
        thread.start()
        
        # Auto-refresh while running
        time.sleep(2)
        st.rerun()

    # Results display
    if st.session_state.task_result:
        st.header("📊 Results")
        
        if "Error" in st.session_state.task_result:
            st.markdown(f'<div class="status-error">{st.session_state.task_result}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="status-success">{st.session_state.task_result}</div>', unsafe_allow_html=True)
    
    # Logs display
    if st.session_state.task_logs:
        st.header("📝 Execution Logs")
        
        logs_text = "\n".join(st.session_state.task_logs)
        st.markdown(f'<div class="log-container">{logs_text}</div>', unsafe_allow_html=True)

    # Instructions
    st.header("📋 Instructions")
    st.markdown("""
    **VMock Automation Steps:**
    1. Go to https://www.vmock.com/login
    2. Click on the "Login" button
    3. Select "Login with Email"
    4. Enter email and password
    5. Click the "Login" button
    6. Wait for the dashboard
    7. Click on the "Interview" tab
    8. Click on "EP"
    9. Click on the "Start Interview" button
    
    **Notes:**
    - The browser will open in non-headless mode so you can see the automation
    - Y4M file is optional for camera simulation
    - Press Enter in the terminal when prompted to close the browser
    """)

if __name__ == "__main__":
    main()