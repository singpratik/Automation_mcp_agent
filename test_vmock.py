#!/usr/bin/env python3
"""
Test script to verify VMock login automation
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.browser_agent import BrowserAgent

def test_vmock_login():
    """Test VMock login automation"""
    print("🧪 Testing VMock Login Automation...")
    
    # Check OpenAI API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY not found in environment")
        return False
    
    print(f"✅ OpenAI API key found: {api_key[:10]}...")
    
    try:
        # Create browser agent with Y4M file
        y4m_path = "/Users/pratik/Downloads/Assesment/mcp_ai_testAgent/Johnny_1280x720_60.y4m"
        print(f"🎥 Using Y4M file: {y4m_path}")
        
        agent = BrowserAgent(
            enable_media_permissions=True,
            y4m_file_path=y4m_path if os.path.exists(y4m_path) else None
        )
        print("✅ Browser agent created successfully")
        
        # Test VMock login task
        task = """Go to https://www.vmock.com/login and login with:
        Email: _7fresh@mailinator.com
        Password: Welcome@123
        Then navigate to Interview > EP > Start Interview"""
        
        print("🌐 Starting VMock login task...")
        result = agent.run_task(task)
        
        print(f"📋 Result: {result}")
        
        # Get logs
        logs = agent.get_live_logs()
        print("\n📊 Live Logs:")
        for log in logs:
            print(f"  {log}")
        
        # Keep browser open for manual verification
        input("\n⏸️  Press Enter to close browser...")
        
        # Close browser
        print("🔒 Closing browser...")
        agent.close_browser()
        print("✅ Test completed")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_vmock_login()
    sys.exit(0 if success else 1)