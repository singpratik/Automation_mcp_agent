#!/bin/bash

# Complete automation setup with Chrome + TTS + Y4M video
# This script shows both terminals needed

echo "🎥🎤 VMock Interview Automation with TTS + Video"
echo "================================================"
echo ""
echo "STEP 1: Launch Chrome with fake video + audio"
echo "----------------------------------------------"
echo "Run this in Terminal 1:"
echo ""
echo '/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \\'
echo '  --use-fake-ui-for-media-stream \\'
echo '  --use-fake-device-for-media-stream \\'
echo '  --use-file-for-fake-video-capture="/Users/pratiksingh/Desktop/Interview_automation/Recources/Johnny_1280x720_60.y4m" \\'
echo '  --use-file-for-fake-audio-capture="/Users/pratiksingh/Desktop/Interview_automation/Automation_mcp_agent/generated_audio/live_response.wav" \\'
echo '  --remote-debugging-port=9222 \\'
echo '  --user-data-dir=/tmp/chrome-auto-allow'
echo ""
echo "STEP 2: Navigate to VMock and start interview"
echo "----------------------------------------------"
echo "In the Chrome window that opened:"
echo "1. Go to: https://vmock.com/elevator-pitch"
echo "2. Login if needed"
echo "3. Start the calibration/interview"
echo ""
echo "STEP 3: Enable TTS in Streamlit (if running)"
echo "----------------------------------------------"
echo "If Streamlit is running:"
echo "1. Open: http://localhost:8501 or 8502"
echo "2. Enable '🎤 Real-time TTS' in sidebar"
echo "3. Configure candidate profile"
echo "4. The browser automation will speak through TTS!"
echo ""
echo "✅ Chrome will:"
echo "   - Show Johnny video (not green screen)"
echo "   - Speak TTS-generated answers"
echo "   - Auto-grant camera/microphone permissions"
echo ""
