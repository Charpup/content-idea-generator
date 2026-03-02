"""
Screenshot/Image Capture Module

Handles image input capture and OCR text extraction using pytesseract.
Supports screenshots, photos, and scanned documents.
"""

import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List, Union, Tuple
from dataclasses import dataclass
from io import BytesIO
import sys

# Add content_idea_generator path for database import
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent / 'content_idea_generator'))
from database import ContentIdeaDatabase, DatabaseError

# Optional imports - handle gracefully if not available
try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False


@dataclass
class CapturedImage:
    """Represents captured image input"""
    image_path: Optional[str]
    image_data: Optional[bytes] = None
    format: str = 'png'
    timestamp: datetime = None
    metadata: Dict[str, Any] = None
    ocr_text: Optional[str] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.metadata is None:
            self.metadata = {}


class ScreenshotCapture:
    """
    Captures and processes image/screenshot input for content ideas.
    
    Uses pytesseract for OCR text extraction.
    Supports various image formats and preprocessing for better OCR.
    
    Features:
    - Screenshot OCR
    - Photo text extraction
    - Document scanning
    - Image preprocessing (contrast, deskew, etc.)
    - Multi-language OCR support
    """
    
    # Supported image formats
    SUPPORTED_FORMATS = ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp']
    
    # OCR engine modes
    OCR_MODES = {
        'fast': '1',      # Fast LSTM only
        'standard': '3',  # Default, based on what is available
        'legacy': '2',    # Legacy + LSTM
        'legacy_only': '0',  # Legacy engine only
    }
    
    def __init__(self, 
                 db: Optional[ContentIdeaDatabase] = None, 
                 db_path: str = "content_ideas.db",
                 tesseract_cmd: Optional[str] = None,
                 language: str = 'eng',
                 ocr_mode: str = 'standard'):
        """
        Initialize screenshot capture module
        
        Args:
            db: Existing database instance or None to create new
            db_path: Database path if creating new instance
            tesseract_cmd: Path to tesseract executable
            language: OCR language code(s), e.g., 'eng', 'eng+chi_sim'
            ocr_mode: OCR engine mode ('fast', 'standard', 'legacy')
        """
        self.db = db or ContentIdeaDatabase(db_path)
        self.language = language
        self.ocr_mode = self.OCR_MODES.get(ocr_mode, '3')
        
        # Configure tesseract if path provided
        if tesseract_cmd and TESSERACT_AVAILABLE:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
        
        self._pil_available = PIL_AVAILABLE
        self._tesseract_available = TESSERACT_AVAILABLE and self._check_tesseract()
    
    def _check_tesseract(self) -> bool:
        """Check if tesseract is available and working"""
        if not TESSERACT_AVAILABLE:
            return False
        
        try:
            version = pytesseract.get_tesseract_version()
            return version is not None
        except:
            return False
    
    @property
    def is_available(self) -> bool:
        """Check if screenshot capture is available"""
        return self._pil_available and self._tesseract_available
    
    @property
    def status(self) -> Dict[str, bool]:
        """Get detailed availability status"""
        return {
            'pil_available': self._pil_available,
            'tesseract_available': self._tesseract_available,
            'fully_available': self.is_available
        }
    
    def capture(self, image_path: Optional[str] = None,
                image_data: Optional[bytes] = None,
                preprocess: bool = True,
                metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Capture and OCR an image
        
        Args:
            image_path: Path to image file (optional if image_data provided)
            image_data: Raw image bytes (optional if image_path provided)
            preprocess: Whether to apply image preprocessing
            metadata: Additional metadata
            
        Returns:
            Dict with OCR result and extracted information
        """
        # Validate inputs
        if not image_path and not image_data:
            return {
                'success': False,
                'error': 'Either image_path or image_data must be provided'
            }
        
        # Check availability
        if not self._pil_available:
            return {
                'success': False,
                'error': 'PIL (Pillow) not installed. Run: pip install Pillow'
            }
        
        if not self._tesseract_available:
            return {
                'success': False,
                'error': (
                    'Tesseract OCR not available. Install:\n'
                    'Ubuntu/Debian: sudo apt-get install tesseract-ocr\n'
                    'macOS: brew install tesseract\n'
                    'Windows: https://github.com/UB-Mannheim/tesseract/wiki\n'
                    'Then: pip install pytesseract'
                )
            }
        
        try:
            # Load image
            if image_data:
                image = Image.open(BytesIO(image_data))
                format_from_data = image.format.lower() if image.format else 'png'
            else:
                image_path = Path(image_path)
                if not image_path.exists():
                    return {
                        'success': False,
                        'error': f"Image file not found: {image_path}"
                    }
                
                if image_path.suffix.lower() not in self.SUPPORTED_FORMATS:
                    return {
                        'success': False,
                        'error': f"Unsupported format: {image_path.suffix}. "
                                f"Supported: {', '.join(self.SUPPORTED_FORMATS)}"
                    }
                
                image = Image.open(image_path)
                format_from_data = image_path.suffix.lstrip('.').lower()
            
            # Create captured image object
            captured = CapturedImage(
                image_path=str(image_path) if image_path else None,
                image_data=image_data,
                format=format_from_data,
                metadata=metadata or {}
            )
            
            # Preprocess if requested
            if preprocess:
                image = self._preprocess_image(image)
            
            # Perform OCR
            ocr_result = self._perform_ocr(image)
            
            if not ocr_result['success']:
                return {
                    'success': False,
                    'error': ocr_result.get('error', 'OCR failed'),
                    'captured': captured
                }
            
            captured.ocr_text = ocr_result['text']
            
            # Parse extracted text
            parsed = self._parse_ocr_text(ocr_result['text'])
            
            return {
                'success': True,
                'captured': captured,
                'ocr': ocr_result,
                'parsed': parsed,
                'content_type': parsed.get('content_type', 'note'),
                'title': parsed.get('title', ''),
                'content': ocr_result['text'],
                'tags': parsed.get('tags', []),
                'priority': parsed.get('priority', 3),
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Image capture failed: {e}"
            }
    
    def capture_and_store(self, image_path: Optional[str] = None,
                         image_data: Optional[bytes] = None,
                         preprocess: bool = True,
                         category_id: Optional[int] = None,
                         tag_ids: Optional[List[int]] = None,
                         metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Capture image and store directly to database
        
        Args:
            image_path: Path to image file
            image_data: Raw image bytes
            preprocess: Whether to apply preprocessing
            category_id: Optional category ID
            tag_ids: Optional list of tag IDs
            metadata: Additional metadata
            
        Returns:
            Dict with capture result and database ID
        """
        try:
            # First capture and OCR
            result = self.capture(image_path, image_data, preprocess, metadata)
            
            if not result['success']:
                return result
            
            parsed = result['parsed']
            ocr_text = result['ocr']['text']
            
            # Generate title if not extracted
            title = parsed.get('title') or f"Screenshot - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            
            # Store to database
            content_id = self.db.create_content_item(
                type=parsed.get('content_type', 'note'),
                title=title,
                content=ocr_text,
                source=f"image://{image_path}" if image_path else "image://upload",
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
                'ocr': result['ocr'],
                'parsed': parsed,
                'message': f"Captured image and stored as content #{content_id}"
            }
            
        except DatabaseError as e:
            return {
                'success': False,
                'error': f"Database error: {e}",
                'ocr': result.get('ocr') if 'result' in locals() else None
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"Screenshot capture failed: {e}"
            }
    
    def _preprocess_image(self, image: 'Image.Image') -> 'Image.Image':
        """
        Apply preprocessing to improve OCR accuracy
        
        Args:
            image: PIL Image object
            
        Returns:
            Preprocessed PIL Image
        """
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Resize if image is very large (helps with OCR)
        max_dimension = 3000
        width, height = image.size
        if width > max_dimension or height > max_dimension:
            ratio = min(max_dimension / width, max_dimension / height)
            new_size = (int(width * ratio), int(height * ratio))
            image = image.resize(new_size, Image.Resampling.LANCZOS)
        
        # Enhance contrast
        from PIL import ImageEnhance
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1.5)
        
        # Enhance sharpness
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(1.5)
        
        return image
    
    def _perform_ocr(self, image: 'Image.Image') -> Dict[str, Any]:
        """
        Perform OCR on the image
        
        Args:
            image: PIL Image object
            
        Returns:
            Dict with OCR results
        """
        try:
            # Configure OCR options
            config = f'--oem {self.ocr_mode} --psm 6'
            
            # Perform OCR
            text = pytesseract.image_to_string(
                image, 
                lang=self.language,
                config=config
            )
            
            # Get detailed data including bounding boxes
            data = pytesseract.image_to_data(
                image,
                lang=self.language,
                config=config,
                output_type=pytesseract.Output.DICT
            )
            
            # Extract confidence scores
            confidences = [int(c) for c in data['conf'] if int(c) > 0]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            # Count words
            words = [w for w in data['text'] if w.strip()]
            
            return {
                'success': True,
                'text': text.strip(),
                'word_count': len(words),
                'confidence': avg_confidence,
                'language': self.language,
                'raw_data': data
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"OCR error: {e}"
            }
    
    def _parse_ocr_text(self, text: str) -> Dict[str, Any]:
        """
        Parse OCR text to extract structured information
        
        Args:
            text: OCR extracted text
            
        Returns:
            Dict with parsed information
        """
        result = {
            'content_type': 'note',
            'title': '',
            'tags': [],
            'priority': 3,
            'idea_concept': None,
            'elaboration': None,
            'use_cases': [],
        }
        
        # Clean up OCR artifacts
        text = self._clean_ocr_text(text)
        
        # Detect content type
        text_lower = text.lower()
        content_types = {
            'article': ['article', 'blog', 'essay', 'write up'],
            'book': ['book', 'chapter', 'publication'],
            'video': ['video', 'youtube', 'watch'],
            'tweet': ['tweet', 'twitter', 'thread'],
            'idea': ['idea', 'concept', 'thought'],
            'code': ['code', 'function', 'class', 'def ', 'import '],
        }
        
        for ctype, keywords in content_types.items():
            if any(kw in text_lower for kw in keywords):
                result['content_type'] = ctype
                break
        
        # Extract title - first non-empty line or sentence
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        if lines:
            # Use first line if it's reasonably short
            first_line = lines[0]
            if len(first_line) <= 100:
                result['title'] = first_line
            else:
                # Truncate at word boundary
                result['title'] = first_line[:100].rsplit(' ', 1)[0] + '...'
        
        # Extract idea concept
        # Look for patterns like "Idea: X" or similar
        concept_patterns = [
            r'(?:idea|concept|thought)[:\-]?\s*["\']?([^"\'\n.!?]+)["\']?',
            r'(?:todo|task|action)[:\-]?\s*["\']?([^"\'\n.!?]+)["\']?',
        ]
        
        for pattern in concept_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                result['idea_concept'] = match.group(1).strip()
                # Rest of text is elaboration
                rest_start = text.find(match.group(0)) + len(match.group(0))
                result['elaboration'] = text[rest_start:].strip()
                break
        
        # If no concept found, use first paragraph
        if not result['idea_concept'] and lines:
            result['idea_concept'] = lines[0][:100]
            result['elaboration'] = '\n'.join(lines[1:]) if len(lines) > 1 else text
        
        # Extract tags
        result['tags'] = self._extract_tags(text)
        
        # Detect priority
        result['priority'] = self._detect_priority(text)
        
        return result
    
    def _clean_ocr_text(self, text: str) -> str:
        """Clean up common OCR artifacts"""
        # Remove excessive whitespace
        text = '\n'.join(line.strip() for line in text.split('\n'))
        
        # Remove isolated single characters (common OCR noise)
        lines = []
        for line in text.split('\n'):
            if len(line.strip()) > 1 or line.strip().isalnum():
                lines.append(line)
        text = '\n'.join(lines)
        
        # Fix common OCR errors
        replacements = {
            '|': 'I',  # Pipe to I
            '0': 'O',  # Zero to O in words
            '@': 'a',  # @ to a
            '$': 's',  # $ to s
        }
        
        # Only replace within words, not as standalone
        for old, new in replacements.items():
            text = re.sub(rf'(?<=\w){old}(?=\w)', new, text)
        
        # Normalize multiple spaces
        text = ' '.join(text.split())
        
        return text.strip()
    
    def _extract_tags(self, text: str) -> List[str]:
        """Extract tags from OCR text"""
        tags = []
        text_lower = text.lower()
        
        # Extract hashtags
        hashtags = re.findall(r'#(\w+)', text)
        tags.extend(hashtags)
        
        # Topic keywords
        topic_keywords = {
            'python': ['python', 'py'],
            'javascript': ['javascript', 'js'],
            'code': ['code', 'programming', 'development'],
            'design': ['design', 'ui', 'ux'],
            'tutorial': ['tutorial', 'how to', 'guide'],
            'tips': ['tips', 'tricks'],
        }
        
        for tag, keywords in topic_keywords.items():
            if any(kw in text_lower for kw in keywords):
                if tag not in tags:
                    tags.append(tag)
        
        return list(set(tags))
    
    def _detect_priority(self, text: str) -> int:
        """Detect priority from OCR text"""
        text_lower = text.lower()
        
        high_indicators = ['urgent', 'important', 'critical', 'asap', '!!!', 'priority: high']
        low_indicators = ['low priority', 'whenever', 'someday', 'maybe']
        
        if any(ind in text_lower for ind in high_indicators):
            return 5
        if any(ind in text_lower for ind in low_indicators):
            return 1
        
        return 3
    
    def capture_region(self, x: int, y: int, width: int, height: int) -> Dict[str, Any]:
        """
        Capture a specific screen region (requires platform-specific implementation)
        
        Args:
            x: X coordinate
            y: Y coordinate
            width: Region width
            height: Region height
            
        Returns:
            Dict with capture result
        """
        # This is a placeholder - actual implementation would require
        # platform-specific screen capture libraries
        return {
            'success': False,
            'error': (
                'Screen region capture not implemented. '
                'Use capture() with a saved screenshot file instead.'
            )
        }
    
    def batch_capture(self, image_paths: List[str], 
                     preprocess: bool = True) -> List[Dict[str, Any]]:
        """
        Capture and OCR multiple images
        
        Args:
            image_paths: List of image file paths
            preprocess: Whether to apply preprocessing
            
        Returns:
            List of capture results
        """
        results = []
        for path in image_paths:
            result = self.capture(image_path=path, preprocess=preprocess)
            results.append(result)
        return results
