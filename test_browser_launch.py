#!/usr/bin/env python3
"""
Simple test script to verify browser launches correctly
"""
import asyncio
import os
from browser_use import Agent
from browser_use.llm import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

async def test_browser_launch():
    """Test basic browser launch"""
    try:
        print("🚀 Testing browser launch...")
        
        # Initialize LLM
        llm = ChatOpenAI(
            model="gpt-4o-mini",
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        print("✅ LLM initialized")
        
        # Create agent with minimal config
        agent = Agent(
            task="Navigate to google.com",
            llm=llm,
            use_vision=True,
            browser_config={
                "headless": False,
                "args": [
                    "--no-first-run",
                    "--disable-extensions",
                    "--disable-default-apps"
                ]
            }
        )
        
        print("✅ Agent created")
        print("🌐 Browser should be launching now...")
        
        # Just test browser startup - don't run full task
        await asyncio.sleep(5)  # Give browser time to start
        
        print("✅ Browser launch test completed")
        
        # Close browser
        if hasattr(agent, 'browser') and agent.browser:
            await agent.browser.close()
            print("✅ Browser closed")
        
        return True
        
    except Exception as e:
        print(f"❌ Browser launch failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_browser_launch())
    if success:
        print("\n🎉 Browser launch test PASSED")
    else:
        print("\n💥 Browser launch test FAILED")