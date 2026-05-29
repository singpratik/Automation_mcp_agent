"""
OpenAI TTS (Text-to-Speech) Generator
Generates audio responses for interview questions using OpenAI TTS API
"""

import os
import logging
from openai import OpenAI
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

class TTSGenerator:
    """Generate audio responses using OpenAI TTS API"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize TTS generator
        
        Args:
            api_key: OpenAI API key (defaults to env variable)
        """
        self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        self.audio_dir = Path("./generated_audio")
        self.audio_dir.mkdir(exist_ok=True)
        
        # TTS configuration
        self.model = os.getenv("OPENAI_TTS_MODEL", "tts-1")  # tts-1 or tts-1-hd
        self.voice = os.getenv("OPENAI_TTS_VOICE", "alloy")  # alloy, echo, fable, onyx, nova, shimmer
        self.speed = float(os.getenv("OPENAI_TTS_SPEED", "1.0"))  # 0.25 to 4.0
        
        logger.info(f"🎤 TTS initialized: model={self.model}, voice={self.voice}, speed={self.speed}")
    
    def generate_answer(self, question: str, llm_client=None) -> str:
        """
        Generate intelligent answer to interview question using GPT
        
        Args:
            question: Interview question text
            llm_client: LLM client to use (optional, will create new if not provided)
            
        Returns:
            Generated answer text
        """
        try:
            if not llm_client:
                from openai import OpenAI
                llm_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            
            # Create interview answer prompt
            system_prompt = """You are a confident, articulate professional being interviewed. 
Generate natural, conversational answers to interview questions. 
Keep answers concise (30-60 seconds when spoken), specific, and professional.
Use first person and show enthusiasm."""
            
            logger.info(f"💭 Generating answer for question: {question[:50]}...")
            
            response = llm_client.chat.completions.create(
                model=os.getenv("BROWSER_USE_MODEL", "gpt-4o"),
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Interview question: {question}\n\nProvide a natural, spoken answer:"}
                ],
                max_completion_tokens=300,
                temperature=0.8
            )
            
            answer = response.choices[0].message.content.strip()
            logger.info(f"✅ Generated answer: {answer[:100]}...")
            return answer
            
        except Exception as e:
            logger.error(f"Failed to generate answer: {e}")
            # Fallback generic answer
            return "I'm a passionate professional with strong technical skills and experience in automation testing. I'm excited about this opportunity."
    
    def text_to_speech(self, text: str, output_filename: str = "response.mp3") -> Optional[Path]:
        """
        Convert text to speech using OpenAI TTS
        
        Args:
            text: Text to convert to speech
            output_filename: Output audio filename
            
        Returns:
            Path to generated audio file or None on failure
        """
        try:
            output_path = self.audio_dir / output_filename
            
            logger.info(f"🎵 Converting text to speech: {text[:50]}...")
            logger.info(f"📊 Text length: {len(text)} characters")
            
            # Call OpenAI TTS API
            response = self.client.audio.speech.create(
                model=self.model,
                voice=self.voice,
                input=text,
                speed=self.speed
            )
            
            # Save audio file
            response.stream_to_file(str(output_path))
            
            file_size = output_path.stat().st_size / 1024  # KB
            logger.info(f"✅ Audio generated: {output_path} ({file_size:.1f} KB)")
            
            return output_path
            
        except Exception as e:
            logger.error(f"❌ TTS generation failed: {e}")
            return None
    
    def answer_question(self, question: str, output_filename: str = "interview_answer.mp3", llm_client=None) -> Optional[Path]:
        """
        Complete pipeline: Generate answer + Convert to speech
        
        Args:
            question: Interview question text
            output_filename: Output audio filename
            llm_client: LLM client to use (optional)
            
        Returns:
            Path to generated audio file or None on failure
        """
        try:
            # Step 1: Generate intelligent answer
            answer_text = self.generate_answer(question, llm_client)
            
            # Step 2: Convert to speech
            audio_path = self.text_to_speech(answer_text, output_filename)
            
            return audio_path
            
        except Exception as e:
            logger.error(f"❌ Failed to answer question: {e}")
            return None
    
    def cleanup_old_audio(self, keep_latest: int = 5):
        """
        Clean up old generated audio files
        
        Args:
            keep_latest: Number of latest files to keep
        """
        try:
            audio_files = sorted(self.audio_dir.glob("*.mp3"), key=lambda p: p.stat().st_mtime, reverse=True)
            
            if len(audio_files) > keep_latest:
                for old_file in audio_files[keep_latest:]:
                    old_file.unlink()
                    logger.info(f"🗑️ Cleaned up old audio: {old_file.name}")
                    
        except Exception as e:
            logger.error(f"Failed to cleanup audio files: {e}")


if __name__ == "__main__":
    # Test TTS generation
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    
    tts = TTSGenerator()
    
    # Test question
    test_question = "Please tell me something about yourself."
    
    print(f"\n🎤 Testing TTS with question: {test_question}\n")
    
    audio_file = tts.answer_question(test_question, "test_answer.mp3")
    
    if audio_file:
        print(f"\n✅ Success! Audio file generated: {audio_file}")
        print(f"📊 File size: {audio_file.stat().st_size / 1024:.1f} KB")
        print(f"\n🔊 Play it with: afplay {audio_file}")
    else:
        print("\n❌ Failed to generate audio")
