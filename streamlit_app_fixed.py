import streamlit as st
import openai
import os
import time
import datetime as dt
import subprocess
import threading
from dotenv import load_dotenv

load_dotenv()

def main():
    st.set_page_config(page_title="🕵️ Agent Interface", layout="wide", initial_sidebar_state="expanded")
    
    # Modern CSS styling
    st.markdown("""
    <style>
    .stApp {
        background: #f8f9fa;
        color: #1a1a1a;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }
    
    .main-header {
        color: #1a1a1a;
        font-size: 2.5rem;
        font-weight: 700;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    
    .chat-container {
        max-width: 768px;
        margin: 0 auto;
        padding: 0 16px;
        background: white;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        min-height: 500px;
    }
    
    .user-message {
        display: flex;
        justify-content: flex-end;
        margin-bottom: 16px;
        width: 100%;
    }
    
    .user-bubble {
        background: #4f46e5;
        color: white;
        padding: 12px 16px;
        border-radius: 16px;
        border-bottom-right-radius: 4px;
        max-width: 70%;
        font-size: 0.95rem;
        line-height: 1.4;
        word-wrap: break-word;
        box-shadow: 0 2px 8px rgba(79, 70, 229, 0.3);
    }
    
    .agent-message {
        display: flex;
        align-items: flex-start;
        margin-bottom: 16px;
        width: 100%;
    }
    
    .agent-avatar {
        width: 32px;
        height: 32px;
        border-radius: 50%;
        background: linear-gradient(135deg, #ec4899, #be185d);
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: 600;
        font-size: 14px;
        margin-right: 12px;
        flex-shrink: 0;
        margin-top: 2px;
    }
    
    .agent-bubble {
        background: #f3f4f6;
        color: #1a1a1a;
        padding: 12px 16px;
        border-radius: 16px;
        border-bottom-left-radius: 4px;
        max-width: 70%;
        font-size: 0.95rem;
        line-height: 1.5;
        word-wrap: break-word;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    }
    
    .status-success {
        background: #dcfce7;
        color: #166534;
        border: 1px solid #bbf7d0;
        padding: 6px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        margin: 8px 0;
    }
    
    .status-error {
        background: #fef2f2;
        color: #dc2626;
        border: 1px solid #fecaca;
        padding: 6px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        margin: 8px 0;
    }
    
    .status-warning {
        background: #fefce8;
        color: #a16207;
        border: 1px solid #fde68a;
        padding: 6px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        margin: 8px 0;
    }
    </style>
    """, unsafe_allow_html=True)

    # Initialize session state
    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = []
    if 'running' not in st.session_state:
        st.session_state.running = False
    if 'browser_process' not in st.session_state:
        st.session_state.browser_process = None
    if 'task_status' not in st.session_state:
        st.session_state.task_status = None

    # Sidebar
    with st.sidebar:
        st.markdown("### 🤖 Browser Agent Settings")
        
        enable_media = st.checkbox("📹 Camera/Mic", value=True)
        
        y4m_file = st.text_input(
            "Y4M File", 
            value="/Users/pratik/Downloads/Assesment/mcp_ai_testAgent/Johnny_1280x720_60.y4m",
            placeholder="/path/to/video.y4m"
        )
        
        # Y4M file validation
        if y4m_file.strip():
            if os.path.exists(y4m_file.strip()):
                file_size = os.path.getsize(y4m_file.strip()) / (1024*1024)
                st.markdown(f'<div class="status-success">✅ Y4M file found ({file_size:.1f} MB)</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="status-error">❌ Y4M file not found</div>', unsafe_allow_html=True)
        
        if st.button("🔒 Stop All Tasks"):
            st.session_state.running = False
            st.session_state.task_status = "stopped"
            if st.session_state.browser_process:
                try:
                    st.session_state.browser_process.terminate()
                    st.session_state.browser_process = None
                except:
                    pass
            st.rerun()

    # Main content
    if not st.session_state.conversation_history:
        # Welcome screen
        st.markdown(
            '<div style="display: flex; flex-direction: column; justify-content: center; align-items: center; min-height: 60vh; text-align: center; padding: 20px;">'
            '<div style="font-size: 3rem; font-weight: 700; color: #1a1a1a; margin-bottom: 16px;">🕵️ Agent</div>'
            '<div style="font-size: 1.2rem; color: #6b7280; margin-bottom: 40px;">Browser Automation Assistant</div>'
            '<div style="font-size: 1rem; color: #4b5563; margin-bottom: 32px; line-height: 1.6;">I can help with web automation, login tasks, and browser interactions</div>'
            '</div>',
            unsafe_allow_html=True
        )
    else:
        # Chat messages
        st.markdown('<div style="max-width: 800px; margin: 0 auto; padding: 20px; padding-bottom: 100px;">', unsafe_allow_html=True)
        
        for msg in st.session_state.conversation_history:
            if msg["role"] == "user":
                st.markdown(
                    f'<div style="display: flex; justify-content: flex-end; margin: 15px 0;">'
                    f'<div style="max-width: 70%; display: flex; flex-direction: column; align-items: flex-end;">'
                    f'<div style="background: #4f46e5; color: white; padding: 12px 18px; border-radius: 18px; border-bottom-right-radius: 4px; font-size: 0.95rem; line-height: 1.4;">'
                    f'{msg["content"]}'
                    f'</div>'
                    f'<div style="font-size: 0.75rem; color: #9ca3af; margin-top: 4px; opacity: 0.8;">{msg["timestamp"]}</div>'
                    f'</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f'<div style="display: flex; align-items: flex-start; margin: 15px 0;">'
                    f'<div style="width: 32px; height: 32px; border-radius: 50%; background: linear-gradient(135deg, #ec4899, #be185d); display: flex; align-items: center; justify-content: center; color: white; font-weight: 600; font-size: 14px; margin-right: 12px; flex-shrink: 0;">AI</div>'
                    f'<div style="max-width: 70%; display: flex; flex-direction: column;">'
                    f'<div style="background: #f3f4f6; color: #1a1a1a; padding: 12px 18px; border-radius: 18px; border-bottom-left-radius: 4px; font-size: 0.95rem; line-height: 1.5;">'
                    f'{msg["content"]}'
                    f'</div>'
                    f'<div style="font-size: 0.75rem; color: #9ca3af; margin-top: 4px; opacity: 0.8;">{msg["timestamp"]}</div>'
                    f'</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )
        
        st.markdown('</div>', unsafe_allow_html=True)

    # Fixed bottom input
    st.markdown(
        '<div style="position: fixed; bottom: 0; left: 0; right: 0; background: #ffffff; border-top: 1px solid #e5e7eb; padding: 20px; z-index: 1000;">'
        '<div style="max-width: 800px; margin: 0 auto; display: flex; align-items: center; gap: 12px;">',
        unsafe_allow_html=True
    )
    
    # Input and button
    input_col, button_col = st.columns([6, 1])
    
    with input_col:
        user_input = st.chat_input(
            placeholder="Ask me to automate any browser task...",
            key="chat_input",
            disabled=st.session_state.running
        )
    
    with button_col:
        if st.session_state.running:
            if st.button("⏹️", key="stop_btn", help="Stop task"):
                st.session_state.running = False
                st.session_state.task_status = "stopped"
                st.rerun()
    
    st.markdown('</div></div>', unsafe_allow_html=True)
    
    # Running indicator
    if st.session_state.running:
        st.markdown(
            '<div style="position: fixed; bottom: 80px; left: 50%; transform: translateX(-50%); background: #fbbf24; color: #92400e; padding: 8px 16px; border-radius: 20px; font-size: 0.9rem; font-weight: 600; box-shadow: 0 4px 12px rgba(251, 191, 36, 0.3); z-index: 1000;">'
            '⚡ Running browser automation task...'
            '</div>',
            unsafe_allow_html=True
        )

    # Handle user input
    if user_input and not st.session_state.running:
        # Add user message
        st.session_state.conversation_history.append({
            "role": "user",
            "content": user_input,
            "timestamp": dt.datetime.now().strftime("%H:%M:%S")
        })
        
        # Check if it's a browser task
        browser_keywords = ['browse', 'go to', 'navigate', 'click', 'login', 'visit', 'open', 'website', 'vmock']
        is_browser_task = any(keyword in user_input.lower() for keyword in browser_keywords)
        
        if is_browser_task:
            st.session_state.running = True
            
            # Add initial response
            st.session_state.conversation_history.append({
                "role": "assistant",
                "content": "🚀 Starting browser automation task...",
                "timestamp": dt.datetime.now().strftime("%H:%M:%S")
            })
            
            st.rerun()
            
            # Run browser task in subprocess to avoid blocking
            def run_browser_task():
                try:
                    # Create a simple Python script to run the browser task
                    script_content = f'''
import sys
import os
sys.path.append("{os.getcwd()}")

from agents.browser_agent import BrowserAgent
import asyncio

async def main():
    try:
        y4m_path = "{y4m_file.strip()}" if "{y4m_file.strip()}" and os.path.exists("{y4m_file.strip()}") else None
        agent = BrowserAgent(
            enable_media_permissions={enable_media},
            y4m_file_path=y4m_path
        )
        
        result = agent.run_task("""{user_input}""")
        print(f"RESULT: {{result}}")
        
        # Get logs
        logs = agent.get_live_logs()
        for log in logs:
            print(f"LOG: {{log}}")
            
    except Exception as e:
        print(f"ERROR: {{str(e)}}")

if __name__ == "__main__":
    asyncio.run(main())
'''
                    
                    # Write script to temp file
                    with open("temp_browser_task.py", "w") as f:
                        f.write(script_content)
                    
                    # Run the script
                    process = subprocess.Popen(
                        ["python3", "temp_browser_task.py"],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        cwd=os.getcwd()
                    )
                    
                    st.session_state.browser_process = process
                    
                    # Wait for completion with timeout
                    try:
                        stdout, stderr = process.communicate(timeout=300)  # 5 minute timeout
                        
                        # Parse output
                        result_lines = [line for line in stdout.split('\n') if line.startswith('RESULT:')]
                        log_lines = [line[5:] for line in stdout.split('\n') if line.startswith('LOG:')]
                        
                        if result_lines:
                            result = result_lines[0][8:]  # Remove "RESULT: "
                        else:
                            result = "Task completed"
                        
                        if stderr:
                            result += f"\n\nErrors: {stderr}"
                        
                        # Update the last message with result
                        if st.session_state.conversation_history:
                            st.session_state.conversation_history[-1] = {
                                "role": "assistant",
                                "content": f"✅ {result}",
                                "timestamp": dt.datetime.now().strftime("%H:%M:%S")
                            }
                        
                    except subprocess.TimeoutExpired:
                        process.kill()
                        if st.session_state.conversation_history:
                            st.session_state.conversation_history[-1] = {
                                "role": "assistant",
                                "content": "⏰ Task timed out after 5 minutes",
                                "timestamp": dt.datetime.now().strftime("%H:%M:%S")
                            }
                    
                    # Clean up
                    try:
                        os.remove("temp_browser_task.py")
                    except:
                        pass
                    
                except Exception as e:
                    if st.session_state.conversation_history:
                        st.session_state.conversation_history[-1] = {
                            "role": "assistant",
                            "content": f"❌ Error: {str(e)}",
                            "timestamp": dt.datetime.now().strftime("%H:%M:%S")
                        }
                
                finally:
                    st.session_state.running = False
                    st.session_state.browser_process = None
            
            # Start the task in a thread
            thread = threading.Thread(target=run_browser_task)
            thread.daemon = True
            thread.start()
            
        else:
            # Handle non-browser tasks with OpenAI
            try:
                client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are a helpful AI assistant."},
                        {"role": "user", "content": user_input}
                    ],
                    max_tokens=500
                )
                
                result = response.choices[0].message.content
                
                st.session_state.conversation_history.append({
                    "role": "assistant",
                    "content": result,
                    "timestamp": dt.datetime.now().strftime("%H:%M:%S")
                })
                
            except Exception as e:
                st.session_state.conversation_history.append({
                    "role": "assistant",
                    "content": f"Error: {str(e)}",
                    "timestamp": dt.datetime.now().strftime("%H:%M:%S")
                })
        
        st.rerun()

    # Auto-refresh when running
    if st.session_state.running:
        time.sleep(2)
        st.rerun()

if __name__ == "__main__":
    main()