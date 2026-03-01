"""
Content Capture Module for Content Idea Generator Skill

Handles text, voice, and screenshot input capture.
"""

import os
import re
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from enum import Enum


class ContentType(Enum):
    """Types of content that can be captured."""
    TEXT = "text"
    VOICE = "voice"
    SCREENSHOT = "screenshot"


class IdeaType(Enum):
    """Types of ideas based on content analysis."""
    BLOG_POST = "blog_post"
    VIDEO_SCRIPT = "video_script"
    SOCIAL_POST = "social_post"
    TUTORIAL = "tutorial"
    NOTE = "note"
    THREAD = "thread"
    NEWSLETTER = "newsletter"


@dataclass
class CapturedIdea:
    """Represents a captured idea."""
    content: str
    content_type: ContentType
    idea_type: IdeaType
    source: str
    tags: List[str]
    confidence: float = 1.0
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class TextCapture:
    """Capture ideas from text input."""
    
    KEYWORDS = {
        "tutorial": IdeaType.TUTORIAL,
        "guide": IdeaType.BLOG_POST,
        "tips": IdeaType.SOCIAL_POST,
        "thread": IdeaType.THREAD,
        "video": IdeaType.VIDEO_SCRIPT,
        "newsletter": IdeaType.NEWSLETTER,
        "blog": IdeaType.BLOG_POST,
        "post": IdeaType.SOCIAL_POST,
    }
    
    @classmethod
    def capture(cls, text: str, source: str = "manual") -> CapturedIdea:
        """Capture idea from text input."""
        text_lower = text.lower()
        
        # Detect idea type from keywords
        idea_type = IdeaType.NOTE
        for keyword, itype in cls.KEYWORDS.items():
            if keyword in text_lower:
                idea_type = itype
                break
        
        # Extract tags
        tags = cls._extract_tags(text)
        
        # Clean content
        clean_content = cls._clean_content(text)
        
        return CapturedIdea(
            content=clean_content,
            content_type=ContentType.TEXT,
            idea_type=idea_type,
            source=source,
            tags=tags,
            confidence=1.0
        )
    
    @classmethod
    def _extract_tags(cls, text: str) -> List[str]:
        """Extract tags from text."""
        hashtags = re.findall(r'#(\w+)', text)
        brackets = re.findall(r'\[(\w+)\]', text)
        return list(set(hashtags + brackets))
    
    @classmethod
    def _clean_content(cls, text: str) -> str:
        """Clean content by removing command prefixes."""
        if text.startswith('/capture'):
            text = text[8:].strip()
        text = re.sub(r'#\w+', '', text)
        return text.strip()


class VoiceCapture:
    """Capture ideas from voice/audio input using whisper.cpp."""
    
    WHISPER_MODEL = "base"
    WHISPER_PATH = os.environ.get("WHISPER_CPP_PATH", "whisper-cli")
    
    @classmethod
    def capture(cls, audio_path: str, source: str = "voice") -> CapturedIdea:
        """Capture idea from voice/audio file."""
        transcription = cls._transcribe(audio_path)
        
        if not transcription["text"]:
            return CapturedIdea(
                content="",
                content_type=ContentType.VOICE,
                idea_type=IdeaType.NOTE,
                source=source,
                tags=[],
                confidence=0.0,
                metadata={"error": "No transcription"}
            )
        
        idea = TextCapture.capture(transcription["text"], source)
        idea.content_type = ContentType.VOICE
        idea.confidence = transcription.get("confidence", 0.8)
        idea.metadata["transcription"] = transcription
        
        return idea
    
    @classmethod
    def _transcribe(cls, audio_path: str) -> Dict[str, Any]:
        """Transcribe audio using whisper.cpp."""
        try:
            if not cls._whisper_available():
                return {"text": "", "confidence": 0.0, "error": "whisper.cpp not available"}
            
            cmd = [
                cls.WHISPER_PATH,
                "-m", f"models/ggml-{cls.WHISPER_MODEL}.bin",
                "-f", audio_path,
                "-l", "auto"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                return {"text": "", "confidence": 0.0, "error": result.stderr}
            
            return {
                "text": result.stdout.strip(),
                "confidence": 0.8,
                "language": "auto"
            }
            
        except subprocess.TimeoutExpired:
            return {"text": "", "confidence": 0.0, "error": "Transcription timeout"}
        except Exception as e:
            return {"text": "", "confidence": 0.0, "error": str(e)}
    
    @classmethod
    def _whisper_available(cls) -> bool:
        """Check if whisper.cpp is installed."""
        try:
            subprocess.run([cls.WHISPER_PATH, "--help"], capture_output=True, timeout=5)
            return True
        except:
            return False


class ScreenshotCapture:
    """Capture ideas from screenshots using OCR."""
    
    @classmethod
    def capture(cls, image_path: str, source: str = "screenshot") -> List[CapturedIdea]:
        """Capture ideas from screenshot/image."""
        ocr_result = cls._ocr(image_path)
        
        if not ocr_result["text"]:
            return [CapturedIdea(
                content="",
                content_type=ContentType.SCREENSHOT,
                idea_type=IdeaType.NOTE,
                source=source,
                tags=[],
                confidence=0.0,
                metadata={"error": "No text found"}
            )]
        
        ideas_text = cls._split_ideas(ocr_result["text"])
        
        ideas = []
        for idea_text in ideas_text:
            idea = TextCapture.capture(idea_text, source)
            idea.content_type = ContentType.SCREENSHOT
            idea.confidence = ocr_result.get("confidence", 0.7)
            idea.metadata["ocr"] = ocr_result
            ideas.append(idea)
        
        return ideas
    
    @classmethod
    def _ocr(cls, image_path: str) -> Dict[str, Any]:
        """Perform OCR on image."""
        try:
            import pytesseract
            from PIL import Image
            
            image = Image.open(image_path)
            text = pytesseract.image_to_string(image)
            
            return {
                "text": text.strip(),
                "confidence": 0.7
            }
            
        except ImportError:
            return {"text": "", "confidence": 0.0, "error": "pytesseract not installed"}
        except Exception as e:
            return {"text": "", "confidence": 0.0, "error": str(e)}
    
    @classmethod
    def _split_ideas(cls, text: str) -> List[str]:
        """Split OCR text into multiple ideas."""
        # Split by bullet points or numbers
        ideas = re.split(r'\n[\-\*\d\.]\s+', text)
        return [idea.strip() for idea in ideas if idea.strip()]


class CaptureService:
    """Main service for capturing content ideas."""
    
    @classmethod
    def capture_text(cls, text: str) -> CapturedIdea:
        """Capture idea from text."""
        return TextCapture.capture(text)
    
    @classmethod
    def capture_voice(cls, audio_path: str) -> CapturedIdea:
        """Capture idea from voice."""
        return VoiceCapture.capture(audio_path)
    
    @classmethod
    def capture_screenshot(cls, image_path: str) -> List[CapturedIdea]:
        """Capture ideas from screenshot."""
        return ScreenshotCapture.capture(image_path)
