#!/bin/bash
echo "🚀 Starting Streamlit with Python 3.12 (latest compatible version)"

cd /Users/pratiksingh/Desktop/Interview_automation/Automation_mcp_agent

# Kill any existing streamlit processes
pkill -9 -f streamlit 2>/dev/null
sleep 1

# Activate Python 3.12 venv and start Streamlit
source /Users/pratiksingh/Desktop/Interview_automation/.venv312/bin/activate
streamlit run streamlit_app.py --server.port 8501 &

echo "✅ Streamlit starting on http://localhost:8501"
echo ""
echo "💡 TIP: Launch Chrome with TTS + video first:"
echo ""
echo '/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \'
echo '  --use-fake-ui-for-media-stream \'
echo '  --use-file-for-fake-audio-capture="/Users/pratiksingh/Desktop/Interview_automation/Automation_mcp_agent/generated_audio/live_response.wav" \'
echo '  --remote-debugging-port=9222 \'
echo '  --user-data-dir=/tmp/chrome-auto-allow'
