#!/bin/bash
# Launch Chrome with automatic media permission grants
# This bypasses permission prompts entirely

echo "🚀 Launching Chrome with automatic camera/microphone permissions..."
echo ""
echo "✅ Flags enabled:"
echo "   - Auto-grant media permissions (no popups)"
echo "   - Fake media devices available"
echo "   - Remote debugging on port 9222"
echo ""
echo "⏳ Chrome will start in 2 seconds..."
sleep 2

/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --use-fake-ui-for-media-stream \
  --use-fake-device-for-media-stream \
  --enable-usermedia-screen-capturing \
  --auto-accept-camera-and-microphone-capture \
  --remote-debugging-port=9222 \
  --user-data-dir=/tmp/chrome-auto-allow \
  --disable-blink-features=AutomationControlled \
  2>/dev/null &

CHROME_PID=$!

echo "✅ Chrome launched with PID: $CHROME_PID"
echo ""
echo "📋 Next steps:"
echo "   1. Keep this terminal open"
echo "   2. Open a NEW terminal"
echo "   3. Run: cd Automation_mcp_agent && ./start_streamlit.sh"
echo ""
echo "💡 Chrome will now automatically grant camera/microphone permissions!"
echo ""
echo "Press Ctrl+C to stop Chrome when done."

# Wait for Chrome process
wait $CHROME_PID
