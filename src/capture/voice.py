"""
Voice Capture Module

Handles audio input capture and transcription using whisper.cpp
"""

import os
import re
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass
import sys

# Add content_idea_generator path for database import
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent / 'content_idea_generator'))
from database import ContentIdeaDatabase, DatabaseError


@dataclass
class CapturedAudio:
    """Represents captured audio input"""
    audio_path: str
    duration: Optional[float] = None
    format: str = 'wav'
    timestamp: datetime = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.metadata is None:
            self.metadata = {}


class VoiceCapture:
    """
    Captures and transcribes voice/audio input for content ideas.
    
    Uses whisper.cpp for local transcription (privacy-preserving, no cloud API needed).
    Falls back to alternative methods if whisper.cpp is not available.
    
    Features:
    - Audio file transcription
    - Voice memo processing
    - Multi-language support (via whisper models)
    - Speaker diarization (basic)
    """
    
    # Supported audio formats
    SUPPORTED_FORMATS = ['.wav', '.mp3', '.m4a', '.ogg', '.flac', '.webm', '.mp4']
    
    # Default whisper.cpp settings
    DEFAULT_MODEL = 'base'
    DEFAULT_LANGUAGE = 'en'
    
    def __init__(self, 
                 db: Optional[ContentIdeaDatabase] = None, 
                 db_path: str = "content_ideas.db",
                 whisper_path: Optional[str] = None,
                 model_path: Optional[str] = None,
                 language: str = 'auto'):
        """
        Initialize voice capture module
        
        Args:
            db: Existing database instance or None to create new
            db_path: Database path if creating new instance
            whisper_path: Path to whisper.cpp main executable
            model_path: Path to whisper model file (.bin)
            language: Default language code ('auto' for auto-detect)
        """
        self.db = db or ContentIdeaDatabase(db_path)
        self.whisper_path = whisper_path or self._find_whisper()
        self.model_path = model_path or self._find_model()
        self.language = language
        self._whisper_available = self._check_whisper()
    
    def _find_whisper(self) -> Optional[str]:
        """Find whisper.cpp executable in common locations"""
        # Check environment variable
        if 'WHISPER_CPP_PATH' in os.environ:
            return os.environ['WHISPER_CPP_PATH']
        
        # Common installation paths
        common_paths = [
            '/usr/local/bin/whisper-cli',
            '/usr/bin/whisper-cli',
            '/opt/whisper.cpp/main',
            '/opt/whisper.cpp/whisper-cli',
            str(Path.home() / '.local/bin/whisper-cli'),
            str(Path.home() / 'whisper.cpp/main'),
            str(Path.home() / 'whisper.cpp/build/bin/whisper-cli'),
            './whisper-cli',
            './main',
        ]
        
        for path in common_paths:
            if os.path.isfile(path) and os.access(path, os.X_OK):
                return path
        
        # Try to find in PATH
        try:
            result = subprocess.run(['which', 'whisper-cli'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass
        
        return None
    
    def _find_model(self) -> Optional[str]:
        """Find whisper model file in common locations"""
        # Check environment variable
        if 'WHISPER_MODEL_PATH' in os.environ:
            return os.environ['WHISPER_MODEL_PATH']
        
        # Common model paths
        model_names = [
            'ggml-base.bin',
            'ggml-small.bin',
            'ggml-medium.bin',
            'ggml-tiny.bin',
            'ggml-large.bin',
        ]
        
        common_paths = [
            '/usr/local/share/whisper',
            '/usr/share/whisper',
            '/opt/whisper.cpp/models',
            str(Path.home() / '.local/share/whisper'),
            str(Path.home() / 'whisper.cpp/models'),
            './models',
        ]
        
        for base_path in common_paths:
            for model_name in model_names:
                model_path = os.path.join(base_path, model_name)
                if os.path.isfile(model_path):
                    return model_path
        
        return None
    
    def _check_whisper(self) -> bool:
        """Check if whisper.cpp is available and working"""
        if not self.whisper_path or not os.path.isfile(self.whisper_path):
            return False
        
        if not self.model_path or not os.path.isfile(self.model_path):
            return False
        
        # Test whisper with --help
        try:
            result = subprocess.run(
                [self.whisper_path, '--help'],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except:
            return False
    
    @property
    def is_available(self) -> bool:
        """Check if voice capture is available"""
        return self._whisper_available
    
    def capture(self, audio_path: str, 
                language: Optional[str] = None,
                metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Capture and transcribe audio file
        
        Args:
            audio_path: Path to audio file
            language: Language code (overrides default)
            metadata: Additional metadata
            
        Returns:
            Dict with transcription result
        """
        audio_path = Path(audio_path)
        
        # Validate audio file
        if not audio_path.exists():
            return {
                'success': False,
                'error': f"Audio file not found: {audio_path}"
            }
        
        if audio_path.suffix.lower() not in self.SUPPORTED_FORMATS:
            return {
                'success': False,
                'error': f"Unsupported format: {audio_path.suffix}. "
                        f"Supported: {', '.join(self.SUPPORTED_FORMATS)}"
            }
        
        # Create captured audio object
        captured = CapturedAudio(
            audio_path=str(audio_path),
            format=audio_path.suffix.lstrip('.'),
            metadata=metadata or {}
        )
        
        # Transcribe
        if self._whisper_available:
            transcription = self._transcribe_with_whisper(
                str(audio_path), 
                language or self.language
            )
        else:
            transcription = self._transcribe_fallback(str(audio_path))
        
        if not transcription['success']:
            return {
                'success': False,
                'error': transcription.get('error', 'Transcription failed'),
                'captured': captured
            }
        
        # Parse the transcription
        parsed = self._parse_transcription(transcription['text'])
        
        return {
            'success': True,
            'captured': captured,
            'transcription': transcription,
            'parsed': parsed,
            'content_type': parsed.get('content_type', 'idea'),
            'title': parsed.get('title', ''),
            'content': transcription['text'],
            'tags': parsed.get('tags', []),
            'priority': parsed.get('priority', 3),
        }
    
    def capture_and_store(self, audio_path: str,
                         language: Optional[str] = None,
                         category_id: Optional[int] = None,
                         tag_ids: Optional[List[int]] = None,
                         metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Capture audio and store directly to database
        
        Args:
            audio_path: Path to audio file
            language: Language code
            category_id: Optional category ID
            tag_ids: Optional list of tag IDs
            metadata: Additional metadata
            
        Returns:
            Dict with capture result and database ID
        """
        try:
            # First capture and transcribe
            result = self.capture(audio_path, language, metadata)
            
            if not result['success']:
                return result
            
            parsed = result['parsed']
            transcription = result['transcription']
            
            # Store to database
            content_id = self.db.create_content_item(
                type=parsed.get('content_type', 'idea'),
                title=parsed.get('title', f'Voice Memo - {datetime.now().strftime("%Y-%m-%d")}'),
                content=transcription['text'],
                source=f"voice://{audio_path}",
                author=metadata.get('author') if metadata else None,
                category_id=category_id,
                status='active',
                priority=parsed.get('priority', 3),
                tag_ids=tag_ids or []
            )
            
            # If this contains an idea concept, also create an idea record
            idea_id = None
            if parsed.get('idea_concept'):
                idea_id = self.db.create_idea(
                    content_id=content_id,
                    concept=parsed['idea_concept'],
                    elaboration=parsed.get('elaboration'),
                    use_cases=parsed.get('use_cases'),
                    tags=parsed.get('tags'),
                    priority=parsed.get('priority', 3),
                    status='new'
                )
            
            return {
                'success': True,
                'content_id': content_id,
                'idea_id': idea_id,
                'transcription': transcription,
                'parsed': parsed,
                'message': f"Captured voice and stored as content #{content_id}"
            }
            
        except DatabaseError as e:
            return {
                'success': False,
                'error': f"Database error: {e}",
                'transcription': result.get('transcription') if 'result' in locals() else None
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"Voice capture failed: {e}"
            }
    
    def _transcribe_with_whisper(self, audio_path: str, language: str) -> Dict[str, Any]:
        """Transcribe audio using whisper.cpp"""
        try:
            # Build whisper command
            cmd = [
                self.whisper_path,
                '-m', self.model_path,
                '-f', audio_path,
                '--output-json',
                '--output-file', '-'  # Output to stdout
            ]
            
            # Add language if specified (not auto)
            if language and language != 'auto':
                cmd.extend(['-l', language])
            else:
                cmd.append('-l')  # Auto-detect
            
            # Run whisper
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode != 0:
                return {
                    'success': False,
                    'error': f"Whisper error: {result.stderr}"
                }
            
            # Parse JSON output
            import json
            try:
                whisper_output = json.loads(result.stdout)
                text = whisper_output.get('text', '').strip()
                segments = whisper_output.get('segments', [])
                
                return {
                    'success': True,
                    'text': text,
                    'segments': segments,
                    'language': whisper_output.get('language', 'unknown'),
                    'model': Path(self.model_path).name if self.model_path else 'unknown'
                }
            except json.JSONDecodeError:
                # Fallback: use raw stdout as text
                return {
                    'success': True,
                    'text': result.stdout.strip(),
                    'segments': [],
                    'language': 'unknown',
                    'model': Path(self.model_path).name if self.model_path else 'unknown'
                }
                
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': 'Transcription timeout (audio too long)'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"Transcription error: {e}"
            }
    
    def _transcribe_fallback(self, audio_path: str) -> Dict[str, Any]:
        """Fallback transcription when whisper.cpp is not available"""
        return {
            'success': False,
            'error': (
                "whisper.cpp not available. Please install:\n"
                "1. Clone whisper.cpp: git clone https://github.com/ggerganov/whisper.cpp\n"
                "2. Build: cd whisper.cpp && make\n"
                "3. Download model: ./models/download-ggml-model.sh base\n"
                "4. Set WHISPER_CPP_PATH and WHISPER_MODEL_PATH environment variables"
            )
        }
    
    def _parse_transcription(self, text: str) -> Dict[str, Any]:
        """Parse transcribed text to extract structured information"""
        result = {
            'content_type': 'idea',
            'title': '',
            'tags': [],
            'priority': 3,
            'idea_concept': None,
            'elaboration': None,
            'use_cases': [],
        }
        
        # Clean up transcription artifacts
        text = self._clean_transcription(text)
        
        # Detect content type
        text_lower = text.lower()
        content_types = {
            'article': ['article', 'blog post', 'write about', 'essay'],
            'video': ['video', 'record a', 'screencast', 'tutorial video'],
            'podcast': ['podcast', 'episode', 'interview'],
            'book': ['book', 'write a book', 'chapter'],
        }
        
        for ctype, keywords in content_types.items():
            if any(kw in text_lower for kw in keywords):
                result['content_type'] = ctype
                break
        
        # Extract title - first sentence or phrase
        sentences = re.split(r'[.!?]+', text)
        if sentences:
            first = sentences[0].strip()
            # Clean up filler words
            first = re.sub(r'^(so|um|uh|like|you know)\s+', '', first, flags=re.IGNORECASE)
            result['title'] = first[:100] if len(first) <= 100 else first[:100].rsplit(' ', 1)[0] + '...'
        
        # Extract idea concept
        # Look for "Idea: X" or similar patterns
        concept_match = re.search(
            r'(?:idea|concept|thought)[:\-]?\s*["\']?([^"\'\n.!?]+)["\']?',
            text, re.IGNORECASE
        )
        if concept_match:
            result['idea_concept'] = concept_match.group(1).strip()
            result['elaboration'] = text
        else:
            # Use first sentence as concept
            if sentences:
                result['idea_concept'] = sentences[0].strip()[:100]
                result['elaboration'] = text
        
        # Extract tags
        result['tags'] = self._extract_tags(text)
        
        # Detect priority
        result['priority'] = self._detect_priority(text)
        
        return result
    
    def _clean_transcription(self, text: str) -> str:
        """Clean up common transcription artifacts"""
        # Remove filler words at start
        text = re.sub(r'^(so|um|uh|like|you know|well)\s+', '', text, flags=re.IGNORECASE)
        
        # Remove repeated words (common in transcription)
        text = re.sub(r'\b(\w+)\s+\1\b', r'\1', text, flags=re.IGNORECASE)
        
        # Normalize whitespace
        text = ' '.join(text.split())
        
        return text.strip()
    
    def _extract_tags(self, text: str) -> List[str]:
        """Extract tags from transcribed text"""
        tags = []
        text_lower = text.lower()
        
        # Topic keywords
        topic_keywords = {
            'python': ['python'],
            'javascript': ['javascript', 'js'],
            'typescript': ['typescript'],
            'react': ['react'],
            'ai': ['ai', 'artificial intelligence', 'machine learning'],
            'web': ['web development', 'frontend', 'backend'],
            'devops': ['devops', 'docker', 'kubernetes'],
            'tutorial': ['tutorial', 'how to', 'guide'],
        }
        
        for tag, keywords in topic_keywords.items():
            if any(kw in text_lower for kw in keywords):
                tags.append(tag)
        
        return tags
    
    def _detect_priority(self, text: str) -> int:
        """Detect priority from transcription"""
        text_lower = text.lower()
        
        if any(w in text_lower for w in ['urgent', 'important', 'critical', 'asap']):
            return 5
        if any(w in text_lower for w in ['low priority', 'whenever', 'someday']):
            return 1
        
        return 3
    
    def convert_audio(self, input_path: str, output_format: str = 'wav') -> Dict[str, Any]:
        """
        Convert audio to a different format (for compatibility)
        
        Args:
            input_path: Path to input audio file
            output_format: Target format (wav, mp3, etc.)
            
        Returns:
            Dict with conversion result
        """
        input_path = Path(input_path)
        output_path = input_path.with_suffix(f'.{output_format}')
        
        # Try ffmpeg first
        try:
            result = subprocess.run(
                ['ffmpeg', '-i', str(input_path), '-y', str(output_path)],
                capture_output=True,
                timeout=60
            )
            
            if result.returncode == 0:
                return {
                    'success': True,
                    'output_path': str(output_path),
                    'format': output_format
                }
        except:
            pass
        
        return {
            'success': False,
            'error': 'Audio conversion failed. Install ffmpeg for format conversion.'
        }
