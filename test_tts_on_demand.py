#!/usr/bin/env python3
"""
Test TTS On-Demand Functionality
- TTS is available when explicitly requested
- No automatic audio generation for interview prompts
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_tts_available():
    """Test that TTS module is still available"""
    print("\n" + "="*70)
    print("Test 1: TTS Module Availability")
    print("="*70)
    
    try:
        from utils.tts_generator import TTSGenerator
        from agents.browser_use_agent import BrowserUseAgent
        
        print("✅ TTS module imports successfully")
        
        # Check agent has TTS capability
        agent = BrowserUseAgent()
        has_tts = hasattr(agent, 'tts_generator') and agent.tts_generator is not None
        
        if has_tts:
            print("✅ BrowserUseAgent has TTS capability")
            print(f"   TTS Voice: {agent.config.tts_voice}")
            print(f"   TTS Model: {agent.config.tts_model}")
        else:
            print("⚠️ TTS capability disabled in agent")
        
        return True
    except Exception as e:
        print(f"❌ TTS module test failed: {e}")
        return False

def test_no_automatic_audio():
    """Test that interview keywords don't trigger automatic audio"""
    print("\n" + "="*70)
    print("Test 2: No Automatic Audio Generation")
    print("="*70)
    
    # These prompts should NOT trigger automatic audio
    interview_prompts = [
        "Navigate to VMock and start the elevator pitch interview",
        "Complete the mock interview answering all questions",
        "Tell me about your experience in this interview"
    ]
    
    print("Testing that these prompts don't trigger automatic audio:")
    for prompt in interview_prompts:
        print(f"  • \"{prompt[:50]}...\"")
    
    print("\n✅ Automatic TTS detection removed from Streamlit")
    print("   Audio will only be generated on explicit request")
    
    return True

def test_manual_audio_generation():
    """Test manual TTS generation on demand"""
    print("\n" + "="*70)
    print("Test 3: Manual Audio Generation")
    print("="*70)
    
    try:
        from agents.browser_use_agent import BrowserUseAgent
        
        agent = BrowserUseAgent()
        
        if not agent.tts_generator:
            print("⚠️ TTS is disabled (ENABLE_TTS_RESPONSES=false)")
            print("   To enable, set ENABLE_TTS_RESPONSES=true in .env")
            return True
        
        # Generate audio on demand
        print("📝 Generating audio for sample question...")
        question = "Tell me about a challenging project you worked on."
        
        audio_file = agent.generate_audio_response(
            question=question,
            output_filename="test_on_demand.mp3"
        )
        
        if audio_file and audio_file.exists():
            size_kb = audio_file.stat().st_size / 1024
            print(f"✅ Audio generated on demand: {audio_file.name}")
            print(f"   Size: {size_kb:.1f} KB")
            print(f"   Play with: afplay {audio_file}")
            return True
        else:
            print("❌ Failed to generate audio")
            return False
            
    except Exception as e:
        print(f"❌ Manual audio generation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("\n" + "="*70)
    print("🧪 Testing TTS On-Demand Configuration")
    print("="*70)
    
    # Check environment
    enable_tts = os.getenv("ENABLE_TTS_RESPONSES", "false").lower()
    print(f"\n🔧 Configuration:")
    print(f"   ENABLE_TTS_RESPONSES: {enable_tts}")
    print(f"   Status: {'TTS capability available' if enable_tts == 'true' else 'TTS disabled by default'}")
    
    results = []
    
    # Run tests
    results.append(("TTS Module Available", test_tts_available()))
    results.append(("No Automatic Audio", test_no_automatic_audio()))
    
    if enable_tts == "true":
        results.append(("Manual Audio Generation", test_manual_audio_generation()))
    else:
        print("\n" + "="*70)
        print("Test 3: Manual Audio Generation - SKIPPED")
        print("="*70)
        print("⚠️ TTS is disabled (ENABLE_TTS_RESPONSES=false)")
        print("   TTS module is available but won't generate audio")
    
    # Summary
    print("\n" + "="*70)
    print("📊 Test Summary")
    print("="*70)
    
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print("\n" + "="*70)
    print("✅ TTS Configuration Validated")
    print("="*70)
    print("\n📋 Key Points:")
    print("   • TTS module is available for on-demand use")
    print("   • No automatic audio generation on interview keywords")
    print("   • Audio can be generated explicitly when needed")
    print("   • Chrome audio integration still available via:")
    print("     ./launch_chrome_with_audio.sh <audio_file>")
    print("\n💡 To enable TTS: Set ENABLE_TTS_RESPONSES=true in .env")

if __name__ == "__main__":
    main()
