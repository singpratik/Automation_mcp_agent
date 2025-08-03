import streamlit as st
import openai
import os
from agents.browser_agent import BrowserAgent
from agents.api_agent import APIAgent
from agents.sql_agent import SQLAgent
from agents.file_agent import FileAgent
from llm.llm_interface import get_llm_response
import inspect
import time
import datetime as dt
import pytz
from dotenv import load_dotenv

# print("✅ Loaded BrowserAgent from:", inspect.getfile(BrowserAgent))

load_dotenv()  # load from .env

openai_key = os.getenv("OPENAI_API_KEY")

def main():
    st.set_page_config(page_title="🕵️ Agent Interface", layout="wide", initial_sidebar_state="expanded")
    
    # Updated modern design CSS matching the images
    st.markdown("""
    <style>
    /* Main app styling */
    .stApp {
        background: #f8f9fa;
        color: #1a1a1a;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }
    
    /* Sidebar styling */
    .stSidebar {
        background: #ffffff;
        border-right: 1px solid #e5e7eb;
    }
    
    .stSidebar .stSelectbox > div > div {
        background: #f8f9fa;
        border: 1px solid #e5e7eb;
        border-radius: 8px;
    }
    
    /* Main header styling */
    .main-header {
        color: #1a1a1a;
        font-size: 2.5rem;
        font-weight: 700;
        text-align: center;
        margin-bottom: 0.5rem;
        letter-spacing: -0.02em;
    }
    
    .subtitle {
        text-align: center;
        color: #6b7280;
        font-size: 1.1rem;
        margin-bottom: 2rem;
        font-weight: 400;
    }
    
    /* Chat container */
    .chat-container {
        max-width: 768px;
        margin: 0 auto;
        padding: 0 16px;
        background: white;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        min-height: 500px;
    }
    
    /* Message styling */
    .message-group {
        margin-bottom: 24px;
        width: 100%;
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
    
    .typing-message {
        display: flex;
        align-items: flex-start;
        margin-bottom: 16px;
        width: 100%;
    }
    
    .typing-bubble {
        background: #f3f4f6;
        color: #6b7280;
        padding: 12px 16px;
        border-radius: 16px;
        border-bottom-left-radius: 4px;
        max-width: 70%;
        font-size: 0.95rem;
        line-height: 1.5;
        font-style: italic;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    }
    
    .message-time {
        font-size: 0.75rem;
        color: #9ca3af;
        margin-top: 4px;
        text-align: right;
        opacity: 0.8;
    }
    
    /* Input container */
    .input-container {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background: white;
        border-top: 1px solid #e5e7eb;
        padding: 16px 20px 20px 20px;
        z-index: 1000;
    }
    
    .input-wrapper {
        max-width: 768px;
        margin: 0 auto;
        position: relative;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    .stChatInput {
        flex: 1;
    }
    
    .stChatInput > div {
        border: 1px solid #d1d5db !important;
        border-radius: 25px !important;
        background: #f8f9fa !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05) !important;
        transition: all 0.2s ease !important;
    }
    
    .stChatInput > div:focus-within {
        border-color: #4f46e5 !important;
        box-shadow: 0 2px 12px rgba(79, 70, 229, 0.15) !important;
        background: white !important;
    }
    
    .stChatInput > div > div > input {
        background: transparent !important;
        border: none !important;
        color: #1a1a1a !important;
        padding: 14px 20px !important;
        font-size: 0.95rem !important;
        font-weight: 400 !important;
        line-height: 1.5 !important;
    }
    
    .stChatInput > div > div > input::placeholder {
        color: #9ca3af !important;
    }
    
    /* Sidebar improvements */
    .sidebar-header {
        padding: 20px;
        border-bottom: 1px solid #e5e7eb;
        background: white;
    }
    
    .new-chat-btn {
        background: #4f46e5;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 12px 16px;
        width: 100%;
        font-weight: 600;
        cursor: pointer;
        margin-bottom: 16px;
        transition: all 0.2s;
    }
    
    .new-chat-btn:hover {
        background: #4338ca;
        transform: translateY(-1px);
    }
    
    .search-box {
        background: #f9fafb;
        border: 1px solid #d1d5db;
        border-radius: 8px;
        padding: 10px 12px;
        width: 100%;
        font-size: 0.9rem;
        margin-bottom: 20px;
    }
    
    .chat-history {
        padding: 0 20px;
        max-height: 60vh;
        overflow-y: auto;
        background: white;
    }
    
    .chat-item {
        padding: 10px 12px;
        border-radius: 8px;
        margin-bottom: 4px;
        cursor: pointer;
        transition: all 0.2s;
        display: flex;
        align-items: center;
        justify-content: space-between;
        border: 1px solid transparent;
    }
    
    .chat-item:hover {
        background: #f8fafc;
        border-color: #e2e8f0;
    }
    
    .chat-item.active {
        background: #ede9fe;
        border-color: #c4b5fd;
    }
    
    .chat-title {
        font-weight: 500;
        font-size: 0.9rem;
        color: #374151;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        line-height: 1.4;
    }
    
    .section-header {
        font-size: 0.75rem;
        font-weight: 700;
        color: #6b7280;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 12px;
        padding: 0 4px;
    }
    
    .sidebar-section {
        padding: 20px;
        border-top: 1px solid #e5e7eb;
        background: white;
    }
    
    .section-title {
        font-weight: 600;
        font-size: 0.9rem;
        color: #374151;
        margin-bottom: 12px;
    }
    
    /* Welcome state styling */
    .welcome-container {
        text-align: center;
        padding: 80px 40px;
        background: white;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        margin: 40px auto;
        max-width: 768px;
    }
    
    .welcome-title {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1a1a1a;
        margin-bottom: 8px;
    }
    
    .welcome-subtitle {
        font-size: 1.1rem;
        color: #6b7280;
        margin-bottom: 40px;
    }
    
    .welcome-description {
        font-size: 1rem;
        color: #4b5563;
        margin-bottom: 32px;
        line-height: 1.6;
    }
    
    .example-buttons {
        display: flex;
        flex-wrap: wrap;
        gap: 12px;
        justify-content: center;
        margin-top: 24px;
    }
    
    .example-btn {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        color: #4b5563;
        padding: 8px 16px;
        border-radius: 20px;
        font-size: 0.9rem;
        cursor: pointer;
        transition: all 0.2s;
    }
    
    .example-btn:hover {
        background: #e2e8f0;
        border-color: #cbd5e1;
        color: #1e293b;
    }
    
    /* Send button styling */
    .send-button {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        background: #4f46e5;
        color: white;
        border: none;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 16px;
        cursor: pointer;
        transition: all 0.2s ease;
        flex-shrink: 0;
    }
    
    .send-button:hover {
        background: #4338ca;
        transform: scale(1.05);
    }
    
    .send-button:disabled {
        background: #f3f4f6;
        color: #9ca3af;
        cursor: not-allowed;
        transform: none;
    }
    
    .stop-button {
        background: #ef4444;
        color: white;
    }
    
    .stop-button:hover {
        background: #dc2626;
    }
    
    /* Deploy button */
    .deploy-button {
        position: fixed;
        top: 20px;
        right: 20px;
        background: #4f46e5;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: 600;
        cursor: pointer;
        z-index: 1000;
        font-size: 0.9rem;
        transition: all 0.2s;
    }
    
    .deploy-button:hover {
        background: #4338ca;
        transform: translateY(-1px);
    }
    
    /* Status indicators */
    .status-indicator {
        padding: 6px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        margin: 8px 0;
    }
    
    .status-success {
        background: #dcfce7;
        color: #166534;
        border: 1px solid #bbf7d0;
    }
    
    .status-error {
        background: #fef2f2;
        color: #dc2626;
        border: 1px solid #fecaca;
    }
    
    .status-warning {
        background: #fefce8;
        color: #a16207;
        border: 1px solid #fde68a;
    }
    
    .status-info {
        background: #eff6ff;
        color: #1d4ed8;
        border: 1px solid #bfdbfe;
    }
    
    /* Modal styling */
    .modal-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.8);
        z-index: 9999;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    .modal-content {
        background: white;
        border-radius: 12px;
        width: 90%;
        max-width: 800px;
        max-height: 90%;
        overflow: hidden;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.5);
    }
    
    .modal-header {
        padding: 20px;
        border-bottom: 1px solid #e5e7eb;
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: #f8fafc;
    }
    
    .modal-body {
        padding: 20px;
        max-height: 60vh;
        overflow-y: auto;
        text-align: center;
    }
    
    .modal-nav {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 16px 20px;
        border-top: 1px solid #e5e7eb;
        background: #f8fafc;
    }
    
    /* Running status indicator */
    .running-indicator {
        position: fixed;
        bottom: 80px;
        left: 50%;
        transform: translateX(-50%);
        background: #fbbf24;
        color: #92400e;
        padding: 8px 16px;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: 600;
        box-shadow: 0 4px 12px rgba(251, 191, 36, 0.3);
        z-index: 1000;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Add Deploy button (top-right)
    st.markdown(
        '<button class="deploy-button" onclick="window.open(\'#\', \'_blank\')">🚀 Deploy</button>',
        unsafe_allow_html=True
    )

    # Initialize session state
    if 'agent' not in st.session_state:
        st.session_state.agent = None
    if 'action_logs' not in st.session_state:
        st.session_state.action_logs = []
    if 'running' not in st.session_state:
        st.session_state.running = False
    if 'screenshots' not in st.session_state:
        st.session_state.screenshots = []
    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = []
    if 'stop_requested' not in st.session_state:
        st.session_state.stop_requested = False
    if 'chat_sessions' not in st.session_state:
        st.session_state.chat_sessions = []
    if 'current_session_id' not in st.session_state:
        st.session_state.current_session_id = None
    if 'search_query' not in st.session_state:
        st.session_state.search_query = ""
    if 'show_action_modal' not in st.session_state:
        st.session_state.show_action_modal = False
    if 'modal_slide_index' not in st.session_state:
        st.session_state.modal_slide_index = 0
    if 'current_action_logs' not in st.session_state:
        st.session_state.current_action_logs = []
    if 'current_screenshots' not in st.session_state:
        st.session_state.current_screenshots = []
    


    # Enhanced Sidebar
    with st.sidebar:
        # Header with New Chat button
        st.markdown('<div class="sidebar-header">', unsafe_allow_html=True)
        if st.button("✨ New Chat", key="new_chat", help="Start a new conversation"):
            # Save current chat if it has messages
            if st.session_state.conversation_history:
                session_id = len(st.session_state.chat_sessions)
                # Generate a better title from first user message
                first_user_msg = next((msg['content'] for msg in st.session_state.conversation_history if msg['role'] == 'user'), "New Chat")
                
                # Create a concise title (like ChatGPT)
                if len(first_user_msg) > 40:
                    title = first_user_msg[:40].strip() + "..."
                else:
                    title = first_user_msg
                
                st.session_state.chat_sessions.append({
                    'id': session_id,
                    'title': title,
                    'messages': st.session_state.conversation_history.copy(),
                    'timestamp': dt.datetime.now().strftime("%H:%M"),
                    'date': dt.datetime.now().strftime('%Y-%m-%d')
                })
            
            # Clear current conversation
            st.session_state.conversation_history = []
            st.session_state.current_session_id = None
            st.rerun()
        
        # Search box
        search_query = st.text_input(
            "Search Chat",
            placeholder="🔍 Search Chat...",
            key="search_input",
            label_visibility="collapsed"
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Chat History Section
        st.markdown('<div class="chat-history">', unsafe_allow_html=True)
        st.markdown('<div class="section-header">RECENT CHAT HISTORY</div>', unsafe_allow_html=True)
        
        if st.session_state.chat_sessions:
            # Filter chats based on search
            filtered_sessions = st.session_state.chat_sessions
            if search_query:
                filtered_sessions = [s for s in st.session_state.chat_sessions 
                                   if search_query.lower() in s['title'].lower()]
            
            # Display recent chats
            for session in reversed(filtered_sessions[-10:]):  # Show last 10 chats
                col1, col2 = st.columns([4, 1])
                with col1:
                    if st.button(
                        session['title'],
                        key=f"chat_{session['id']}",
                        help=f"Switch to chat from {session['timestamp']}",
                        use_container_width=True
                    ):
                        st.session_state.conversation_history = session['messages'].copy()
                        st.session_state.current_session_id = session['id']
                        st.rerun()
                
                with col2:
                    if st.button("🗑️", key=f"del_{session['id']}", help="Delete chat"):
                        st.session_state.chat_sessions = [s for s in st.session_state.chat_sessions if s['id'] != session['id']]
                        if st.session_state.current_session_id == session['id']:
                            st.session_state.conversation_history = []
                            st.session_state.current_session_id = None
                        st.rerun()
        else:
            # Show empty state when no chats
            st.markdown(
                '<div style="padding: 20px; text-align: center; color: #9ca3af; font-size: 0.85rem;">'
                'No conversations yet.<br>Start chatting to see your history here.'
                '</div>',
                unsafe_allow_html=True
            )
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Settings Section
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">SETTINGS</div>', unsafe_allow_html=True)
        
        enable_media = st.checkbox("📹 Camera/Mic", value=True, key="camera_mic")
        
        # File & Browser Operations Section
        st.markdown('<div class="section-title" style="margin-top: 20px;">FILE & BROWSER OPERATIONS</div>', unsafe_allow_html=True)
        
        y4m_file = st.text_input("Y4M File", value="/Users/pratik/Downloads/Assesment/mcp_ai_testAgent/Johnny_1280x720_60.y4m", placeholder="/path/to/video.y4m")
        
        # Y4M file validation with improved status indicators
        if y4m_file.strip():
            if os.path.exists(y4m_file.strip()):
                file_size = os.path.getsize(y4m_file.strip()) / (1024*1024)  # MB
                st.markdown(f'<div class="status-indicator status-success">✅ Y4M file found ({file_size:.1f} MB)</div>', unsafe_allow_html=True)
                
                # Check if it's a valid Y4M file
                try:
                    with open(y4m_file.strip(), 'rb') as f:
                        header = f.read(10).decode('ascii', errors='ignore')
                        if header.startswith('YUV4MPEG2'):
                            st.markdown('<div class="status-indicator status-success">✅ Valid Y4M format detected</div>', unsafe_allow_html=True)
                        else:
                            st.markdown('<div class="status-indicator status-warning">⚠️ File doesn\'t appear to be Y4M format</div>', unsafe_allow_html=True)
                except Exception as e:
                    st.markdown(f'<div class="status-indicator status-error">❌ Cannot read file: {str(e)}</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="status-indicator status-error">❌ Y4M file not found at specified path</div>', unsafe_allow_html=True)
        
        if st.button("🔒 Close Browser", use_container_width=True):
            if st.session_state.agent:
                st.session_state.agent.close_browser()
                st.session_state.agent = None
                st.session_state.running = False
                st.session_state.screenshots = []
            st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Main content area
    if not st.session_state.conversation_history:
        # Welcome screen - centered above chat input
        st.markdown(
            '<div style="display: flex; flex-direction: column; justify-content: center; align-items: center; min-height: 60vh; text-align: center; padding: 20px;">'
            '<div style="font-size: 3rem; font-weight: 700; color: #1a1a1a; margin-bottom: 16px;">🕵️ Agent</div>'
            '<div style="font-size: 1.2rem; color: #6b7280; margin-bottom: 40px;">automation booster</div>'
            '<div style="font-size: 1rem; color: #4b5563; margin-bottom: 32px; line-height: 1.6;">I can help with conversations, web automation, file operations, API calls, and database queries</div>'
            '<div style="display: flex; flex-wrap: wrap; gap: 12px; justify-content: center;">'
            '<div style="background: #f8fafc; border: 1px solid #e2e8f0; color: #4b5563; padding: 8px 16px; border-radius: 20px; font-size: 0.9rem; cursor: pointer;">"What time is it?"</div>'
            '<div style="background: #f8fafc; border: 1px solid #e2e8f0; color: #4b5563; padding: 8px 16px; border-radius: 20px; font-size: 0.9rem; cursor: pointer;">"Browse to google.com"</div>'
            '<div style="background: #f8fafc; border: 1px solid #e2e8f0; color: #4b5563; padding: 8px 16px; border-radius: 20px; font-size: 0.9rem; cursor: pointer;">"Create a file"</div>'
            '<div style="background: #f8fafc; border: 1px solid #e2e8f0; color: #4b5563; padding: 8px 16px; border-radius: 20px; font-size: 0.9rem; cursor: pointer;">"Make API request"</div>'
            '</div>'
            '</div>',
            unsafe_allow_html=True
        )
    
    elif st.session_state.conversation_history:
        # Clean chat interface - only messages
        st.markdown('<div style="max-width: 800px; margin: 0 auto; padding: 20px; padding-bottom: 100px;">', unsafe_allow_html=True)
        
        for i, msg in enumerate(st.session_state.conversation_history):
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
            elif msg["role"] == "assistant":
                if msg.get("typing"):
                    st.markdown(
                        f'<div style="display: flex; align-items: flex-start; margin: 15px 0;">'
                        f'<div style="width: 32px; height: 32px; border-radius: 50%; background: linear-gradient(135deg, #ec4899, #be185d); display: flex; align-items: center; justify-content: center; color: white; font-weight: 600; font-size: 14px; margin-right: 12px; flex-shrink: 0;">AI</div>'
                        f'<div style="background: #f3f4f6; color: #6b7280; padding: 12px 18px; border-radius: 18px; border-bottom-left-radius: 4px; max-width: 70%; font-size: 0.95rem; line-height: 1.5; font-style: italic;">'
                        f'<span style="animation: bubble 1.4s ease-in-out infinite; display: inline-block; margin: 0 1px;">●</span>'
                        f'<span style="animation: bubble 1.4s ease-in-out infinite; animation-delay: 0.2s; display: inline-block; margin: 0 1px;">●</span>'
                        f'<span style="animation: bubble 1.4s ease-in-out infinite; animation-delay: 0.4s; display: inline-block; margin: 0 1px;">●</span>'
                        f' {msg["content"]}'
                        f'</div>'
                        f'</div>',
                        unsafe_allow_html=True
                    )
                else:
                    col1, col2 = st.columns([10, 1])
                    with col1:
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
                    
                    with col2:
                        if msg.get("action_logs"):
                            if st.button("📊", key=f"logs_{i}_{msg['timestamp']}", help="View Steps"):
                                st.session_state.show_action_modal = True
                                st.session_state.modal_slide_index = 0
                                st.session_state.current_action_logs = msg["action_logs"]
                                st.session_state.current_screenshots = msg.get("screenshots", [])
                                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Fixed bottom input
    st.markdown(
        '<div style="position: fixed; bottom: 0; left: 0; right: 0; background: #ffffff; border-top: 1px solid #e5e7eb; padding: 20px; z-index: 1000;">'
        '<div style="max-width: 800px; margin: 0 auto; display: flex; align-items: center; gap: 12px;">',
        unsafe_allow_html=True
    )
    
    # Create columns for input and button
    input_col, button_col = st.columns([6, 1])
    
    with input_col:
        user_input = st.chat_input(
            placeholder="Ask anything...",
            key="chat_input"
        )
    
    with button_col:
        if st.session_state.running:
            if st.button("⏹️", key="stop_btn", help="Stop generating"):
                st.session_state.stop_requested = True
                st.session_state.running = False
                
                if st.session_state.agent:
                    try:
                        st.session_state.agent.stop()
                        st.session_state.agent.close_browser()
                    except:
                        pass
                
                if st.session_state.conversation_history and st.session_state.conversation_history[-1].get("typing"):
                    st.session_state.conversation_history.pop()
                    
                st.session_state.conversation_history.append({
                    "role": "assistant", 
                    "content": "❌ **Response stopped by user.**",
                    "timestamp": dt.datetime.now().strftime("%H:%M:%S")
                })
                
                st.rerun()
    
    st.markdown('</div></div>', unsafe_allow_html=True)
    
    # Running indicator (removed to prevent blocking)
    
    # Handle chat input
    if user_input and not st.session_state.running:
        # Add user message to conversation
        st.session_state.conversation_history.append({
            "role": "user", 
            "content": user_input,
            "timestamp": dt.datetime.now().strftime("%H:%M:%S")
        })
        
        st.session_state.running = True
        st.session_state.stop_requested = False
        
        # Detect explicit browser automation tasks (VMock, complex web tasks)
        automation_keywords = ['vmock', 'login to', 'fill form', 'click button', 'navigate to', 'automation', 'interview']
        should_use_automation = any(keyword in user_input.lower() for keyword in automation_keywords)
        
        if should_use_automation:
            # Launch browser directly without blocking
            try:
                y4m_path = y4m_file.strip() if y4m_file.strip() and os.path.exists(y4m_file.strip()) else None
                
                # Create browser-use script with proper escaping
                script_lines = [
                    "import asyncio",
                    "import os",
                    "import sys",
                    f"sys.path.append('{os.getcwd()}')",
                    "",
                    "from browser_use import Agent",
                    "from browser_use.llm import ChatOpenAI",
                    "",
                    "async def run_vmock_automation():",
                    "    try:",
                    "        print('🚀 Starting VMock automation with browser-use...')",
                    "",
                    "        # Initialize LLM",
                    "        llm = ChatOpenAI(",
                    "            model='gpt-4o-mini',",
                    f"            api_key='{os.getenv('OPENAI_API_KEY')}'",
                    "        )",
                    "",
                    "        # Browser configuration",
                    "        browser_args = [",
                    "            '--no-first-run',",
                    "            '--use-fake-ui-for-media-stream',",
                    "            '--use-fake-device-for-media-stream',",
                    "            '--autoplay-policy=no-user-gesture-required',",
                    "            '--disable-web-security',",
                    "            '--allow-running-insecure-content',",
                    "            '--auto-accept-camera-and-microphone-capture',",
                    "            '--allow-file-access-from-files',",
                    "            '--disable-features=VizDisplayCompositor'",
                    "        ]",
                ]
                
                if y4m_path:
                    script_lines.extend([
                        f"        y4m_path = '{y4m_path}'",
                        "        browser_args.append(f'--use-file-for-fake-video-capture={y4m_path}')",
                        "        print(f'✅ Y4M file configured: {y4m_path}')",
                    ])
                
                script_lines.extend([
                    "",
                    "        # Create the task prompt",
                    "        task = '''Go to https://www.vmock.com/login and complete the following steps:",
                    "1. Click on the Login button if needed",
                    "2. Select 'Login with Email' if prompted",
                    "3. Enter email: _7fresh@mailinator.com",
                    "4. Enter password: Welcome@123",
                    "5. Click the Login button",
                    "6. Wait for the dashboard to load",
                    "7. Click on the 'Interview' tab",
                    "8. Click on 'EP'",
                    "9. Click on 'Start Interview' button'''",
                    "",
                    "        print('🌐 Creating browser agent...')",
                    "",
                    "        # Create agent",
                    "        agent = Agent(",
                    "            task=task,",
                    "            llm=llm,",
                    "            use_vision=True,",
                    "            browser_config={",
                    "                'headless': False,",
                    "                'args': browser_args",
                    "            }",
                    "        )",
                    "",
                    "        print('🤖 Starting automation...')",
                    "",
                    "        # Run the automation",
                    "        result = await agent.run()",
                    "",
                    "        print(f'✅ Automation completed: {result}')",
                    "",
                    "        # Keep browser open for verification",
                    "        input('⏸️  Press Enter to close browser...')",
                    "",
                    "    except Exception as e:",
                    "        print(f'❌ Error: {str(e)}')",
                    "        import traceback",
                    "        traceback.print_exc()",
                    "",
                    "if __name__ == '__main__':",
                    "    asyncio.run(run_vmock_automation())"
                ])
                
                script_content = "\n".join(script_lines)
                
                # Write and launch script
                with open("browser_launch.py", "w") as f:
                    f.write(script_content)
                
                import subprocess
                subprocess.Popen(["python3", "browser_launch.py"])
                
                # Add progress message
                st.session_state.conversation_history.append({
                    "role": "assistant", 
                    "content": "Task in progress",
                    "timestamp": dt.datetime.now().strftime("%H:%M:%S")
                })
                
            except Exception as e:
                st.session_state.conversation_history.append({
                    "role": "assistant", 
                    "content": f"❌ Failed to launch browser: {str(e)}",
                    "timestamp": dt.datetime.now().strftime("%H:%M:%S")
                })
        else:
            # Handle all tasks through browser agent for consistency
            try:
                if not st.session_state.agent:
                    y4m_path = y4m_file.strip() if y4m_file.strip() and os.path.exists(y4m_file.strip()) else None
                    st.session_state.agent = BrowserAgent(
                        enable_media_permissions=enable_media,
                        y4m_file_path=y4m_path
                    )
                
                result = st.session_state.agent.run_task(user_input)
                
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
        
        # Auto-save to chat history after first exchange
        if len(st.session_state.conversation_history) >= 2 and st.session_state.current_session_id is None:
            session_id = len(st.session_state.chat_sessions)
            first_user_msg = st.session_state.conversation_history[0]['content']
            title = first_user_msg[:40] + "..." if len(first_user_msg) > 40 else first_user_msg
            
            new_session = {
                'id': session_id,
                'title': title,
                'messages': st.session_state.conversation_history.copy(),
                'timestamp': dt.datetime.now().strftime("%H:%M"),
                'date': dt.datetime.now().strftime('%Y-%m-%d')
            }
            st.session_state.chat_sessions.append(new_session)
            st.session_state.current_session_id = session_id
        
        # Update existing session
        elif st.session_state.current_session_id is not None:
            for session in st.session_state.chat_sessions:
                if session['id'] == st.session_state.current_session_id:
                    session['messages'] = st.session_state.conversation_history.copy()
                    break
        
        st.session_state.running = False
        st.session_state.stop_requested = False
        st.rerun()

    
    # Action Logs Modal
    if st.session_state.show_action_modal and st.session_state.get('current_action_logs'):
        current_logs = st.session_state.current_action_logs
        current_screenshots = st.session_state.get('current_screenshots', [])
        
        st.markdown(
            '<div class="modal-overlay">'
            '<div class="modal-content">'
            '<div class="modal-header">'
            '<h3 style="margin: 0;">🤖 Browser Automation Steps</h3>'
            '</div>'
            '<div class="modal-body">',
            unsafe_allow_html=True
        )
        
        # Current slide
        if st.session_state.modal_slide_index < len(current_logs):
            current_log = current_logs[st.session_state.modal_slide_index]
            
            # Show screenshot
            if st.session_state.modal_slide_index < len(current_screenshots):
                screenshot_path = current_screenshots[st.session_state.modal_slide_index]
                if os.path.exists(screenshot_path):
                    st.image(screenshot_path, caption=f"Step {st.session_state.modal_slide_index + 1}")
            
            # Show log
            st.markdown(
                f'<div style="background: #f8fafc; padding: 12px; border-radius: 6px; font-family: monospace; font-size: 0.9rem; color: #374151; text-align: left; margin-top: 16px;">'
                f'<strong>Step {st.session_state.modal_slide_index + 1}:</strong><br>'
                f'{current_log}'
                f'</div>',
                unsafe_allow_html=True
            )
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Navigation
        st.markdown('<div class="modal-nav">', unsafe_allow_html=True)
        col1, col2, col3, col4 = st.columns([1, 1, 2, 1])
        
        with col1:
            if st.button("◀ Prev", disabled=st.session_state.modal_slide_index == 0):
                st.session_state.modal_slide_index -= 1
                st.rerun()
        
        with col2:
            if st.button("Next ▶", disabled=st.session_state.modal_slide_index >= len(current_logs) - 1):
                st.session_state.modal_slide_index += 1
                st.rerun()
        
        with col3:
            st.write(f"Slide {st.session_state.modal_slide_index + 1} of {len(current_logs)}")
        
        with col4:
            if st.button("✕ Close"):
                st.session_state.show_action_modal = False
                st.rerun()
        
        st.markdown('</div></div></div>', unsafe_allow_html=True)
    
    # Add CSS animations for typing indicator
    st.markdown(
        '<style>'
        '@keyframes bubble { 0% { opacity: 0.4; } 50% { opacity: 1; } 100% { opacity: 0.4; } }'
        '.bubble-icon { animation: bubble 1.4s ease-in-out infinite; display: inline-block; margin: 0 1px; color: #6b7280; }'
        '.bubble-2 { animation-delay: 0.2s; }'
        '.bubble-3 { animation-delay: 0.4s; }'
        '</style>',
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()