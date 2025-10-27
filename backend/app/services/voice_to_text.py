"""
Voice-to-Text Service for IELTS Writing
Converts speech to text with AI-powered transcription
"""

import logging
import base64
import io
from typing import Dict, Any, Optional
import openai
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class VoiceTranscriptionRequest(BaseModel):
    audio_data: str  # Base64 encoded audio
    language: str = "en"
    format: str = "mp3"
    task_type: str = "Task 2"

class VoiceTranscriptionResponse(BaseModel):
    transcript: str
    confidence: float
    word_count: int
    processing_time: float
    language_detected: str
    suggestions: list[str]

class VoiceToTextService:
    """Advanced voice-to-text service with AI transcription"""
    
    def __init__(self, openai_api_key: Optional[str] = None):
        self.openai_client = openai.OpenAI(api_key=openai_api_key) if openai_api_key else None
        self.is_available = bool(openai_api_key)
        
        if not self.is_available:
            logger.warning("⚠️ OpenAI API key not provided, Voice-to-Text service will use fallback")
    
    async def transcribe_audio(self, request: VoiceTranscriptionRequest) -> VoiceTranscriptionResponse:
        """Transcribe audio to text with AI-powered processing"""
        
        if not self.is_available:
            return self._fallback_transcription(request)
        
        try:
            # Decode base64 audio data
            audio_bytes = base64.b64decode(request.audio_data)
            audio_file = io.BytesIO(audio_bytes)
            audio_file.name = f"audio.{request.format}"
            
            # Use OpenAI Whisper for transcription
            transcript_response = self.openai_client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language=request.language,
                response_format="verbose_json"
            )
            
            transcript = transcript_response.text
            confidence = getattr(transcript_response, 'confidence', 0.9)
            language_detected = getattr(transcript_response, 'language', request.language)
            
            # Process transcript for IELTS writing
            processed_transcript = self._process_for_ielts(transcript, request.task_type)
            
            # Generate suggestions for improvement
            suggestions = self._generate_suggestions(processed_transcript, request.task_type)
            
            return VoiceTranscriptionResponse(
                transcript=processed_transcript,
                confidence=confidence,
                word_count=len(processed_transcript.split()),
                processing_time=0.0,  # Will be calculated by caller
                language_detected=language_detected,
                suggestions=suggestions
            )
            
        except Exception as e:
            logger.error(f"❌ Voice transcription failed: {e}")
            return self._fallback_transcription(request)
    
    def _process_for_ielts(self, transcript: str, task_type: str) -> str:
        """Process transcript to make it more suitable for IELTS writing"""
        
        # Basic processing
        processed = transcript.strip()
        
        # Add proper capitalization
        sentences = processed.split('. ')
        capitalized_sentences = []
        
        for sentence in sentences:
            if sentence.strip():
                capitalized_sentences.append(sentence.strip().capitalize())
        
        processed = '. '.join(capitalized_sentences)
        
        # Add proper punctuation if missing
        if not processed.endswith(('.', '!', '?')):
            processed += '.'
        
        # Task-specific processing
        if task_type == "Task 1":
            # Add more formal language for Task 1
            processed = self._make_formal_for_task1(processed)
        elif task_type == "Task 2":
            # Add argumentative structure for Task 2
            processed = self._add_argumentative_structure(processed)
        
        return processed
    
    def _make_formal_for_task1(self, text: str) -> str:
        """Make text more formal for Task 1 (Academic/General)"""
        
        # Replace informal words with formal equivalents
        replacements = {
            "it's": "it is",
            "there's": "there is",
            "can't": "cannot",
            "won't": "will not",
            "don't": "do not",
            "doesn't": "does not",
            "didn't": "did not",
            "hasn't": "has not",
            "haven't": "have not",
            "isn't": "is not",
            "aren't": "are not",
            "wasn't": "was not",
            "weren't": "were not"
        }
        
        for informal, formal in replacements.items():
            text = text.replace(informal, formal)
        
        return text
    
    def _add_argumentative_structure(self, text: str) -> str:
        """Add argumentative structure for Task 2"""
        
        # Check if text has clear structure
        if not any(word in text.lower() for word in ["however", "although", "while", "whereas"]):
            # Add contrast if missing
            sentences = text.split('. ')
            if len(sentences) > 2:
                # Insert contrast in the middle
                middle = len(sentences) // 2
                sentences.insert(middle, "However, there are also opposing views to consider.")
                text = '. '.join(sentences)
        
        return text
    
    def _generate_suggestions(self, transcript: str, task_type: str) -> list[str]:
        """Generate suggestions for improving the transcript"""
        
        suggestions = []
        word_count = len(transcript.split())
        
        # Word count suggestions
        if task_type == "Task 1" and word_count < 150:
            suggestions.append("Consider adding more details to reach the recommended 150 words for Task 1")
        elif task_type == "Task 2" and word_count < 250:
            suggestions.append("Expand your ideas to reach the recommended 250 words for Task 2")
        
        # Structure suggestions
        if task_type == "Task 2":
            if not any(word in transcript.lower() for word in ["first", "second", "third", "moreover", "furthermore"]):
                suggestions.append("Add transition words to improve essay structure")
            
            if not any(word in transcript.lower() for word in ["in conclusion", "to conclude", "overall", "in summary"]):
                suggestions.append("Include a clear conclusion to wrap up your argument")
        
        # Language suggestions
        if "very" in transcript.lower():
            suggestions.append("Replace 'very' with more sophisticated adjectives (e.g., 'extremely', 'highly')")
        
        if any(word in transcript.lower() for word in ["good", "bad", "nice", "big", "small"]):
            suggestions.append("Use more specific and sophisticated vocabulary")
        
        return suggestions[:5]  # Limit to 5 suggestions
    
    def _fallback_transcription(self, request: VoiceTranscriptionRequest) -> VoiceTranscriptionResponse:
        """Fallback transcription when AI is not available"""
        
        # This would typically use a different service or local model
        fallback_text = f"This is a fallback transcription for {request.task_type}. Please use a proper audio transcription service for accurate results."
        
        return VoiceTranscriptionResponse(
            transcript=fallback_text,
            confidence=0.3,
            word_count=len(fallback_text.split()),
            processing_time=0.1,
            language_detected=request.language,
            suggestions=["Use a proper audio transcription service for accurate results"]
        )
    
    def get_supported_formats(self) -> list[str]:
        """Get list of supported audio formats"""
        return ["mp3", "wav", "m4a", "flac", "webm"]
    
    def get_supported_languages(self) -> list[str]:
        """Get list of supported languages"""
        return [
            "en", "es", "fr", "de", "it", "pt", "ru", "ja", "ko", "zh",
            "ar", "hi", "th", "vi", "tr", "pl", "nl", "sv", "da", "no"
        ]


