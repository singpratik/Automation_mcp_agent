import asyncio
import os
import sys
sys.path.append('/Users/pratik/Downloads/Assesment/mcp_ai_testAgent')

from browser_use import Agent
from browser_use.llm import ChatOpenAI

async def run_vmock_automation():
    try:
        print('🚀 Starting VMock automation with browser-use...')

        # Initialize LLM
        llm = ChatOpenAI(
            model='gpt-4o-mini',
            api_key=os.getenv('OPENAI_API_KEY')
        )

        # Browser configuration
        browser_args = [
            '--no-first-run',
            '--use-fake-ui-for-media-stream',
            '--use-fake-device-for-media-stream',
            '--autoplay-policy=no-user-gesture-required',
            '--disable-web-security',
            '--allow-running-insecure-content',
            '--auto-accept-camera-and-microphone-capture',
            '--allow-file-access-from-files',
            '--disable-features=VizDisplayCompositor'
        ]
        y4m_path = '/Users/pratik/Downloads/Assesment/mcp_ai_testAgent/Johnny_1280x720_60.y4m'
        browser_args.append(f'--use-file-for-fake-video-capture={y4m_path}')
        print(f'✅ Y4M file configured: {y4m_path}')

        # Create the task prompt
        task = '''Go to https://www.vmock.com/login and complete the following steps:
1. Click on the Login button if needed
2. Select 'Login with Email' if prompted
3. Enter email: _7fresh@mailinator.com
4. Enter password: Welcome@123
5. Click the Login button
6. Wait for the dashboard to load
7. Click on the 'Interview' tab
8. Click on 'EP'
9. Click on 'Start Interview' button'''

        print('🌐 Creating browser agent...')

        # Create agent
        agent = Agent(
            task=task,
            llm=llm,
            use_vision=True,
            browser_config={
                'headless': False,
                'args': browser_args
            }
        )

        print('🤖 Starting automation...')

        # Run the automation
        result = await agent.run()

        print(f'✅ Automation completed: {result}')

        # Keep browser open for verification
        input('⏸️  Press Enter to close browser...')

    except Exception as e:
        print(f'❌ Error: {str(e)}')
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    asyncio.run(run_vmock_automation())