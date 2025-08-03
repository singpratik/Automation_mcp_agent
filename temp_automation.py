
import sys
import os
sys.path.append("/Users/pratik/Downloads/Assesment/mcp_ai_testAgent")

from simple_browser_agent import run_vmock_automation

if __name__ == "__main__":
    try:
        result, logs = run_vmock_automation(
            email="_7fresh@mailinator.com",
            password="Welcome@123",
            y4m_file_path="/Users/pratik/Downloads/Assesment/mcp_ai_testAgent/Johnny_1280x720_60.y4m" if "/Users/pratik/Downloads/Assesment/mcp_ai_testAgent/Johnny_1280x720_60.y4m" else None
        )
        
        print(f"RESULT: {result}")
        for log in logs:
            print(f"LOG: {log}")
            
    except Exception as e:
        print(f"ERROR: {str(e)}")
        print("RESULT: VMock automation failed")
