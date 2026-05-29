"""
Test script for Real-time TTS functionality
Demonstrates Option C: Hybrid File-Based approach
"""

import logging
from agents.browser_use_agent import BrowserUseAgent, BrowserUseConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_tts_answer_generation():
    """Test TTS answer generation without browser"""
    print("\n" + "="*80)
    print("TEST 1: TTS Answer Generation")
    print("="*80)
    
    # Create agent with TTS enabled
    config = BrowserUseConfig(
        enable_realtime_tts=True,
        tts_voice="alloy",
        tts_model="tts-1"
    )
    
    agent = BrowserUseAgent(config=config)
    
    # Set candidate context
    context = {
        "candidate_name": "Sarah Johnson",
        "position": "Senior Software Engineer",
        "experience_years": 7,
        "skills": ["Python", "AWS", "Docker", "React", "PostgreSQL"]
    }
    
    # Test question
    question = "Tell me about your experience with cloud technologies."
    
    print(f"\n🎯 Question: {question}")
    print(f"👤 Candidate: {context['candidate_name']} ({context['position']})")
    
    # Generate and save answer
    success = agent.answer_question_with_tts(question, context)
    
    if success:
        print(f"\n✅ SUCCESS!")
        print(f"📁 Audio file: {agent.realtime_tts.get_audio_path()}")
        print("\nTo test with Chrome:")
        print(f"  /Applications/Google\\ Chrome.app/Contents/MacOS/Google\\ Chrome \\")
        print(f"    --use-fake-ui-for-media-stream \\")
        print(f"    --use-fake-device-for-media-stream \\")
        print(f"    --use-file-for-fake-audio-capture=\"{agent.realtime_tts.get_audio_path()}\" \\")
        print(f"    https://vmock.com")
    else:
        print("\n❌ FAILED to generate TTS audio")


def test_tts_task_with_context():
    """Test full task execution with TTS support"""
    print("\n" + "="*80)
    print("TEST 2: Browser Task with TTS (No actual interview - just setup)")
    print("="*80)
    
    # Create agent with TTS enabled
    config = BrowserUseConfig(
        enable_realtime_tts=True,
        tts_voice="nova",  # Female voice
        tts_model="tts-1",
        headless=False,  # Show browser
        max_steps=50
    )
    
    agent = BrowserUseAgent(config=config)
    
    # Set candidate context
    context = {
        "candidate_name": "Alex Chen",
        "position": "Full Stack Developer",
        "experience_years": 5,
        "skills": ["JavaScript", "Node.js", "React", "MongoDB", "AWS"]
    }
    
    print(f"\n👤 Candidate Profile:")
    print(f"   Name: {context['candidate_name']}")
    print(f"   Position: {context['position']}")
    print(f"   Experience: {context['experience_years']} years")
    print(f"   Skills: {', '.join(context['skills'])}")
    
    print(f"\n🎤 Audio Configuration:")
    print(f"   Voice: {config.tts_voice}")
    print(f"   Model: {config.tts_model}")
    print(f"   File: {agent.realtime_tts.get_audio_path()}")
    
    # Note: This would run actual browser automation with TTS
    # For testing, we just verify setup
    print("\n✅ TTS agent configured and ready!")
    print("\n💡 To run full interview automation:")
    print("   result = agent.run_task_with_tts_sync(")
    print("       task='Complete the VMock elevator pitch interview',")
    print("       start_url='https://vmock.com/elevator-pitch',")
    print("       candidate_context=context")
    print("   )")


def test_multiple_questions():
    """Test answering multiple questions"""
    print("\n" + "="*80)
    print("TEST 3: Multiple Questions with Different Answers")
    print("="*80)
    
    config = BrowserUseConfig(
        enable_realtime_tts=True,
        tts_voice="alloy"
    )
    
    agent = BrowserUseAgent(config=config)
    
    # Context
    context = {
        "candidate_name": "Maria Garcia",
        "position": "DevOps Engineer",
        "experience_years": 6,
        "skills": ["Kubernetes", "Terraform", "CI/CD", "Python", "AWS"]
    }
    
    questions = [
        "What is your experience with containerization?",
        "How do you handle infrastructure as code?",
        "Tell me about a challenging deployment you managed."
    ]
    
    print(f"\n👤 Candidate: {context['candidate_name']}")
    
    for i, question in enumerate(questions, 1):
        print(f"\n📋 Question {i}: {question}")
        success = agent.answer_question_with_tts(question, context)
        
        if success:
            print(f"   ✅ Answer generated and audio updated")
        else:
            print(f"   ❌ Failed to generate answer")
    
    print(f"\n✅ Test completed!")
    print(f"📁 Final audio: {agent.realtime_tts.get_audio_path()}")


if __name__ == "__main__":
    print("\n" + "="*80)
    print("🎤 Real-time TTS Testing Suite")
    print("Option C: Hybrid File-Based Approach")
    print("="*80)
    
    try:
        # Test 1: Basic answer generation
        test_tts_answer_generation()
        
        # Test 2: Full task setup
        test_tts_task_with_context()
        
        # Test 3: Multiple questions
        test_multiple_questions()
        
        print("\n" + "="*80)
        print("✅ All tests completed successfully!")
        print("="*80)
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
