"""
Simple TTS module test without browser agent dependencies
Tests the core TTS functionality directly
"""

import logging
import sys
import os
from pathlib import Path

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
from dotenv import load_dotenv
env_file = Path(__file__).parent / ".env"
if env_file.exists():
    load_dotenv(env_file)
    print(f"✅ Loaded environment from {env_file}")
else:
    print(f"⚠️ No .env file found at {env_file}")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def test_tts_module():
    """Test TTS module directly"""
    print("\n" + "="*80)
    print("🎤 Testing RealtimeTTS Module")
    print("="*80)
    
    from utils.realtime_tts import RealtimeTTS
    
    # Initialize TTS
    print("\n1. Initializing RealtimeTTS...")
    tts = RealtimeTTS()
    print(f"   ✅ Audio file: {tts.get_audio_path()}")
    print(f"   ✅ File exists: {os.path.exists(tts.get_audio_path())}")
    
    # Generate test audio
    print("\n2. Generating TTS audio...")
    test_text = "Hello, I am a test of the real-time text to speech system. This audio will be used for Chrome's fake microphone."
    
    success = tts.generate_and_update(test_text, voice="alloy", model="tts-1")
    
    if success:
        print(f"   ✅ Audio generated successfully!")
        print(f"   📁 File: {tts.get_audio_path()}")
        
        # Check file size
        file_size = os.path.getsize(tts.get_audio_path())
        print(f"   📊 File size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
        
        return True
    else:
        print(f"   ❌ Failed to generate audio")
        return False


def test_answer_generator():
    """Test answer generation"""
    print("\n" + "="*80)
    print("🤖 Testing AnswerGenerator")
    print("="*80)
    
    from utils.realtime_tts import AnswerGenerator
    from openai import OpenAI
    import httpx
    
    # Initialize with httpx client (compatibility fix)
    print("\n1. Initializing AnswerGenerator...")
    http_client = httpx.Client(timeout=httpx.Timeout(60.0))
    client = OpenAI(http_client=http_client)
    generator = AnswerGenerator(llm_client=client, model="gpt-4o-mini")
    
    # Set context
    context = {
        "candidate_name": "Test Candidate",
        "position": "Software Engineer",
        "experience_years": 5,
        "skills": ["Python", "JavaScript", "AWS"]
    }
    generator.set_context(context)
    print(f"   ✅ Context set: {context['candidate_name']} - {context['position']}")
    
    # Generate answer
    print("\n2. Generating answer...")
    question = "Tell me about your experience with cloud technologies."
    answer = generator.generate_answer(question)
    
    print(f"\n   📋 Question: {question}")
    print(f"   💬 Answer: {answer}")
    
    return True


def test_full_pipeline():
    """Test complete pipeline: question → answer → audio"""
    print("\n" + "="*80)
    print("🚀 Testing Full Pipeline")
    print("="*80)
    
    from utils.realtime_tts import RealtimeTTS, AnswerGenerator
    from openai import OpenAI
    import httpx
    
    # Initialize components
    print("\n1. Initializing components...")
    tts = RealtimeTTS()
    http_client = httpx.Client(timeout=httpx.Timeout(60.0))
    client = OpenAI(http_client=http_client)
    generator = AnswerGenerator(llm_client=client, model="gpt-4o-mini")
    
    # Set context
    context = {
        "candidate_name": "Alex Chen",
        "position": "DevOps Engineer",
        "experience_years": 6,
        "skills": ["Kubernetes", "Terraform", "Python"]
    }
    generator.set_context(context)
    print(f"   ✅ Components ready")
    print(f"   👤 Candidate: {context['candidate_name']} ({context['position']})")
    
    # Process question
    print("\n2. Processing question...")
    question = "What's your experience with container orchestration?"
    print(f"   📋 Question: {question}")
    
    # Generate answer
    answer = generator.generate_answer(question)
    print(f"   💬 Answer: {answer[:150]}...")
    
    # Convert to audio
    print("\n3. Converting to audio...")
    success = tts.generate_and_update(answer, voice="echo", model="tts-1")
    
    if success:
        print(f"   ✅ Audio generated!")
        print(f"   📁 File: {tts.get_audio_path()}")
        print(f"   📊 Size: {os.path.getsize(tts.get_audio_path())/1024:.1f} KB")
        print("\n   🎤 Chrome can now use this audio as fake microphone input!")
        return True
    else:
        print(f"   ❌ Audio generation failed")
        return False


def show_chrome_command():
    """Show how to launch Chrome with the audio file"""
    print("\n" + "="*80)
    print("🌐 Launch Chrome with Fake Microphone")
    print("="*80)
    
    from utils.realtime_tts import RealtimeTTS
    tts = RealtimeTTS()
    audio_path = tts.get_audio_path()
    
    print("\nCopy and run this command to test with Chrome:\n")
    print(f'/Applications/Google\\ Chrome.app/Contents/MacOS/Google\\ Chrome \\')
    print(f'  --use-fake-ui-for-media-stream \\')
    print(f'  --use-fake-device-for-media-stream \\')
    print(f'  --use-file-for-fake-audio-capture="{audio_path}" \\')
    print(f'  https://vmock.com')
    
    print("\n💡 The audio file will automatically be used as microphone input!")


if __name__ == "__main__":
    print("\n" + "="*80)
    print("🎤 Real-time TTS Module Test Suite")
    print("Testing core functionality without browser dependencies")
    print("="*80)
    
    try:
        # Test 1: TTS module
        if not test_tts_module():
            print("\n❌ TTS module test failed")
            sys.exit(1)
        
        # Test 2: Answer generator
        if not test_answer_generator():
            print("\n❌ Answer generator test failed")
            sys.exit(1)
        
        # Test 3: Full pipeline
        if not test_full_pipeline():
            print("\n❌ Full pipeline test failed")
            sys.exit(1)
        
        # Show Chrome command
        show_chrome_command()
        
        print("\n" + "="*80)
        print("✅ All tests passed successfully!")
        print("="*80)
        print("\n💡 Next steps:")
        print("   1. Run the Chrome command above to test audio")
        print("   2. Navigate to an interview page")
        print("   3. The audio will play as microphone input")
        print("   4. Use Streamlit UI to run full automation with TTS")
        print("="*80 + "\n")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
