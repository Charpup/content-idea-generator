"""
Content Idea Generator - Capture Module

Handles multi-modal content capture:
- Text input from chat/commands
- Voice/audio transcription
- Screenshot/image OCR
"""

from .text import TextCapture, CapturedText
from .voice import VoiceCapture, CapturedAudio
from .screenshot import ScreenshotCapture, CapturedImage
from .parser import IdeaParser, ParsedIdea

__all__ = [
    'TextCapture',
    'CapturedText',
    'VoiceCapture',
    'CapturedAudio',
    'ScreenshotCapture',
    'CapturedImage',
    'IdeaParser',
    'ParsedIdea'
]

# Version
__version__ = '1.0.0'
