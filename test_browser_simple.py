#!/usr/bin/env python3
"""
Simple test script to verify browser agent functionality
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.browser_agent import BrowserAgent

def test_browser_agent():
    """Test basic browser agent functionality"""
    print("🧪 Testing Browser Agent...")
    
    # Check OpenAI API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY not found in environment")
        return False
    
    print(f"✅ OpenAI API key found: {api_key[:10]}...")
    
    try:
        # Create browser agent
        print("🚀 Creating browser agent...")
        agent = BrowserAgent(enable_media_permissions=False)
        print("✅ Browser agent created successfully")
        
        # Test simple task
        print("🌐 Testing simple browser task...")
        result = agent.run_task("Go to google.com")
        
        print(f"📋 Result: {result}")
        
        # Get logs
        logs = agent.get_live_logs()
        print("\n📊 Live Logs:")
        for log in logs:
            print(f"  {log}")
        
        # Close browser
        print("🔒 Closing browser...")
        agent.close_browser()
        print("✅ Test completed successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_browser_agent()
    sys.exit(0 if success else 1)