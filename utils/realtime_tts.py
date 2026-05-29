"""
Real-time TTS Module for Browser Automation
Uses OpenAI TTS API with in-place audio file updates for Chrome fake microphone
"""

import os
import logging
import time
from pathlib import Path
from typing import Optional
import wave
import struct

logger = logging.getLogger(__name__)

class RealtimeTTS:
    """
    Real-time Text-to-Speech with file-based audio updates
    
    Chrome's --use-file-for-fake-audio-capture continuously reads the audio file.
    This class updates the file in-place, and Chrome automatically picks up changes.
    """
    
    def __init__(self, api_key: Optional[str] = None, audio_dir: str = "./generated_audio"):
        """
        Initialize RealtimeTTS
        
        Args:
            api_key: OpenAI API key (reads from env if not provided)
            audio_dir: Directory for audio files
        """
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        except TypeError as e:
            # Fallback for version compatibility issues
            logger.warning(f"OpenAI initialization error: {e}. Trying alternative method...")
            from openai import OpenAI
            import httpx
            # Create httpx client with compatible settings
            http_client = httpx.Client(timeout=httpx.Timeout(60.0))
            self.client = OpenAI(
                api_key=api_key or os.getenv("OPENAI_API_KEY"),
                http_client=http_client
            )
        
        self.audio_dir = Path(audio_dir)
        self.audio_dir.mkdir(parents=True, exist_ok=True)
        
        # Main audio file that Chrome reads
        self.live_audio_file = self.audio_dir / "live_response.wav"
        
        # Create initial silence (1 second)
        self._create_silence(duration_seconds=1)
        
        logger.info(f"✅ RealtimeTTS initialized - Audio file: {self.live_audio_file}")
    
    def _create_silence(self, duration_seconds: float = 1.0):
        """
        Create a silent WAV file
        
        Args:
            duration_seconds: Duration of silence
        """
        sample_rate = 16000
        num_samples = int(sample_rate * duration_seconds)
        
        with wave.open(str(self.live_audio_file), 'wb') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(sample_rate)
            
            # Write silent samples (zeros)
            for _ in range(num_samples):
                wav_file.writeframes(struct.pack('<h', 0))
        
        logger.debug(f"Created {duration_seconds}s silence: {self.live_audio_file}")
    
    def generate_and_update(self, text: str, voice: str = "alloy", model: str = "tts-1") -> bool:
        """
        Generate TTS audio and update the live file
        
        Args:
            text: Text to convert to speech
            voice: OpenAI TTS voice (alloy, echo, fable, onyx, nova, shimmer)
            model: TTS model (tts-1 or tts-1-hd)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"🎤 Generating TTS for: {text[:100]}...")
            
            # Generate audio
            response = self.client.audio.speech.create(
                model=model,
                voice=voice,
                input=text,
                response_format="wav"  # WAV for better Chrome compatibility
            )
            
            # Save to temporary file first
            temp_file = self.audio_dir / "temp_response.wav"
            response.stream_to_file(str(temp_file))
            
            # Atomic replace - Chrome will pick up the new file
            temp_file.replace(self.live_audio_file)
            
            logger.info(f"✅ Audio updated successfully - Chrome will use new audio")
            return True
            
        except Exception as e:
            logger.error(f"❌ TTS generation failed: {e}")
            return False
    
    def get_audio_path(self) -> str:
        """Get absolute path to live audio file"""
        return str(self.live_audio_file.absolute())
    
    def reset_to_silence(self):
        """Reset audio to silence"""
        self._create_silence(duration_seconds=1)
        logger.debug("Audio reset to silence")


class QuestionDetector:
    """
    Detect interview questions using GPT Vision or DOM inspection
    """
    
    @staticmethod
    def detect_from_screenshot(screenshot_path: str, llm_client) -> Optional[str]:
        """
        Detect question text from screenshot using GPT Vision
        
        Args:
            screenshot_path: Path to screenshot
            llm_client: OpenAI client for vision
            
        Returns:
            Detected question text or None
        """
        try:
            import base64
            
            # Read and encode screenshot
            with open(screenshot_path, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode('utf-8')
            
            # Use GPT Vision to detect question
            response = llm_client.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Look at this interview page. If there's a question being asked, extract ONLY the question text. If no question is visible, respond with 'NO_QUESTION'. Be concise."
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=300
            )
            
            result = response.choices[0].message.content.strip()
            
            if result == "NO_QUESTION" or not result:
                return None
            
            logger.info(f"📋 Detected question: {result[:100]}...")
            return result
            
        except Exception as e:
            logger.error(f"Question detection failed: {e}")
            return None
    
    @staticmethod
    def detect_from_dom(page_content: str, question_selectors: list) -> Optional[str]:
        """
        Detect question from DOM content using CSS selectors
        
        Args:
            page_content: HTML page content
            question_selectors: List of CSS selectors to try
            
        Returns:
            Detected question or None
        """
        from bs4 import BeautifulSoup
        
        try:
            soup = BeautifulSoup(page_content, 'html.parser')
            
            for selector in question_selectors:
                element = soup.select_one(selector)
                if element and element.text.strip():
                    question = element.text.strip()
                    logger.info(f"📋 Detected question via DOM: {question[:100]}...")
                    return question
            
            return None
            
        except Exception as e:
            logger.error(f"DOM question detection failed: {e}")
            return None


class AnswerGenerator:
    """
    Generate natural answers to interview questions using GPT
    """
    
    def __init__(self, llm_client, model: str = "gpt-4"):
        """
        Initialize answer generator
        
        Args:
            llm_client: OpenAI client
            model: GPT model to use
        """
        self.client = llm_client
        self.model = model
        
        # Default interview context
        self.context = {
            "candidate_name": "John Doe",
            "position": "Software Engineer",
            "experience_years": 5,
            "skills": ["Python", "JavaScript", "React", "Node.js", "AWS"]
        }
    
    def set_context(self, context: dict):
        """Update candidate context"""
        self.context.update(context)
    
    def generate_answer(self, question: str, max_tokens: int = 200) -> str:
        """
        Generate natural answer to interview question
        
        Args:
            question: Interview question
            max_tokens: Maximum response length
            
        Returns:
            Generated answer
        """
        try:
            system_prompt = f"""You are {self.context['candidate_name']}, a {self.context['position']} with {self.context['experience_years']} years of experience.
Your skills: {', '.join(self.context['skills'])}.

Answer the interview question naturally and concisely. Keep it professional but conversational.
Speak in first person. Keep answers under 30 seconds when spoken aloud."""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": question}
                ],
                max_tokens=max_tokens,
                temperature=0.7
            )
            
            answer = response.choices[0].message.content.strip()
            logger.info(f"✅ Generated answer: {answer[:100]}...")
            return answer
            
        except Exception as e:
            logger.error(f"Answer generation failed: {e}")
            return "I'm sorry, I didn't quite understand the question. Could you please rephrase it?"
