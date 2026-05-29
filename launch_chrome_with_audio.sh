#!/bin/bash
# Launch Chrome with fake audio input for answering interview questions
#
# This is a **minimal, stable** launch configuration tested with newer macOS +
# Chrome builds. It avoids experimental flags that can trigger crashes.

# Get audio file path (default to the shared live_response.wav used by RealtimeTTS)
AUDIO_FILE="${1:-/Users/pratiksingh/Desktop/Interview_automation/Automation_mcp_agent/generated_audio/live_response.wav}"

# Convert to absolute path
AUDIO_FILE=$(cd "$(dirname "$AUDIO_FILE")" && pwd)/$(basename "$AUDIO_FILE")

echo "🎤 Launching Chrome with fake audio input"
echo "📁 Audio file: $AUDIO_FILE"

# Check if audio file exists
if [ ! -f "$AUDIO_FILE" ]; then
    echo "⚠️  Warning: Audio file not found: $AUDIO_FILE"
    echo "   Chrome will still start, but no TTS audio will be played."
fi

# Kill existing Chrome instances that are using the remote debugging port
pkill -f "remote-debugging-port=9222" 2>/dev/null || true
sleep 1

# Launch Chrome with **only** the essential flags:
# - use-fake-ui-for-media-stream: auto-accept mic/camera prompt UI
# - use-file-for-fake-audio-capture: feed audio from the specified file
# - remote-debugging-port: allow browser-use/Streamlit to attach
# - user-data-dir: isolate this instance so flags are actually applied
#
# IMPORTANT: We deliberately do **NOT** use --use-fake-device-for-media-stream
# here, so that Chrome uses your **real webcam** for video while still taking
# microphone input from the TTS audio file.
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --use-fake-ui-for-media-stream \
  --use-file-for-fake-audio-capture="$AUDIO_FILE" \
  --remote-debugging-port=9222 \
  --user-data-dir=/tmp/chrome-auto-allow \
  > /tmp/chrome_audio.log 2>&1 &

CHROME_PID=$!

echo "✅ Chrome launched with PID: $CHROME_PID"
echo "🌐 Remote debugging on: http://localhost:9222"
echo "🎥 Video source: your normal webcam (no fake device flags)"
echo "🎤 Fake audio (TTS): $AUDIO_FILE"
echo ""
echo "💡 Chrome will use this audio file as microphone input"
echo "📝 Logs: /tmp/chrome_audio.log"
echo ""
echo "🛑 To stop: pkill -f 'remote-debugging-port=9222'"
