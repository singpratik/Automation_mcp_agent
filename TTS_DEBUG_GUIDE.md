# TTS Debugging Guide - Question Not Detected Issue

## Current Status
- ✅ Monitoring code is running (logs show checks happening)
- ✅ Disk space cleaned up (71 GB free)
- ✅ TTS components initialized
- ❌ Questions are NOT being detected by selectors
- ❌ No TTS audio being generated

## Root Cause
The monitoring is working, but the **question detection selectors** are not finding any questions on the VMock page. This means either:
1. Page structure has changed since selectors were created
2. Questions are in an iframe
3. You're not on the actual question page yet
4. Page is still loading when checks happen

## Immediate Debugging Steps

### Step 1: Run Debug Script (MOST IMPORTANT)
While on a VMock interview page with Chrome running on port 9222:

```bash
cd /Users/pratiksingh/Desktop/Interview_automation/Automation_mcp_agent
/Users/pratiksingh/Desktop/Interview_automation/.venv312/bin/python debug_tts.py
```

This will show:
- ✅ What selectors are finding elements
- ✅ What text is on the page
- ✅ Whether questions exist but aren't matched by selectors
- ✅ Page structure details

### Step 2: Check Current Logs
The monitoring logs should show something like:
```
INFO [agents.browser_use_agent] 🔍 VMock monitor check #1: https://vmock.com/...
INFO [agents.browser_use_agent] ℹ️ No VMock question detected on this check
```

If you're seeing these, monitoring IS working - it just can't find questions.

### Step 3: Manual Page Inspection
1. Open Chrome DevTools (F12) on the VMock interview page
2. Look at the Elements tab
3. Search for question text (Ctrl+F in DevTools)
4. Check if it's in an `<iframe>` (this would require special handling)
5. Look at the class names and IDs used for question elements

## Common Issues & Solutions

### Issue 1: Questions in Iframe
**Symptom**: Page has questions but debug script can't find them
**Solution**: We need to add iframe detection to the code

### Issue 2: Page Not Loaded
**Symptom**: Monitor checks happen before page fully loads
**Solution**: Add wait for specific element before checking

### Issue 3: Different Selectors Needed
**Symptom**: VMock changed their HTML structure
**Solution**: Update selectors based on debug script output

### Issue 4: Not on Question Page Yet
**Symptom**: Monitoring runs but you're still on login/navigation pages
**Solution**: Monitoring only activates on 'vmock' domain, but waits for questions to appear

## Expected vs Actual Behavior

### Expected (Working):
```
🔍 VMock monitor check #5: https://practice.vmock.com/interview/12345
❓ Detected VMock question: Please tell me about yourself...
🤔 Generating answer...
💬 Answer (523 chars): My name is John Doe...
✅ Audio file updated - Chrome will play TTS audio!
```

### Actual (Not Working):
```
🔍 VMock monitor check #5: https://practice.vmock.com/interview/12345
ℹ️ No VMock question detected on this check
```

## Quick Fix Options

### Option A: Add Wait Before First Check
If questions appear after page loads, add a delay:

```python
# In monitor_vmock_questions(), before while loop:
await asyncio.sleep(10)  # Wait 10s for page to fully load
```

### Option B: Add Iframe Support
If questions are in iframe:

```python
# Check iframes for questions
frames = page.frames
for frame in frames:
    try:
        questions = await frame.locator('[class*="question"]').all()
        # ... check questions
    except:
        pass
```

### Option C: Add Dynamic Selector Discovery
Let the agent inspect page and find question elements:

```python
# Use browser-use AI to identify question elements
# More robust but slower
```

## Next Steps

1. **RUN THE DEBUG SCRIPT FIRST** - This will tell us exactly what's on the page
2. Based on debug output, we can:
   - Update selectors to match actual page structure
   - Add iframe support if needed
   - Add longer wait times if needed
   - Add dynamic element discovery

3. If debug script shows questions exist but current selectors don't match:
   - I'll update the selectors immediately
   
4. If questions are in an iframe:
   - I'll add iframe traversal to the monitoring code

5. If page needs more time to load:
   - I'll add progressive wait logic

## Running Debug Script Now

To help me fix this immediately, please:

1. Make sure Chrome is running with debugging port 9222 (it should be based on terminal history)
2. Navigate to an actual VMock interview question page
3. Run the debug script:
   ```bash
   cd /Users/pratiksingh/Desktop/Interview_automation/Automation_mcp_agent
   /Users/pratiksingh/Desktop/Interview_automation/.venv312/bin/python debug_tts.py
   ```
4. Share the output with me

The output will show exactly what's on the page and why questions aren't being detected, allowing me to fix the selectors or add iframe support immediately.
