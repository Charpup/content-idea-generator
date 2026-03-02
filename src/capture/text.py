"""
Text Capture Module

Handles text input capture from chat/commands and converts to content ideas.
"""

import re
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
from pathlib import Path
import sys

# Add content_idea_generator path for database import
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent / 'content_idea_generator'))
from database import ContentIdeaDatabase, DatabaseError


@dataclass
class CapturedText:
    """Represents captured text input"""
    raw_text: str
    source: str = 'chat'
    timestamp: datetime = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.metadata is None:
            self.metadata = {}


class TextCapture:
    """
    Captures and processes text input for content ideas.
    
    Supports:
    - Command-style input: "/capture Python decorators tutorial"
    - Natural language: "I have an idea for a blog post about..."
    - Quick notes: "Note: remember to cover async/await"
    """
    
    # Command patterns
    COMMAND_PATTERNS = {
        'capture': r'^/capture\s+(.+)$',
        'idea': r'^/idea\s+(.+)$',
        'note': r'^/note\s+(.+)$',
        'bookmark': r'^/bookmark\s+(.+)$',
    }
    
    # Content type detection patterns
    CONTENT_TYPE_PATTERNS = {
        'article': r'\b(article|blog|post|essay|write.?up)\b',
        'video': r'\b(video|youtube|tutorial|course|screencast)\b',
        'book': r'\b(book|ebook|publication|chapter)\b',
        'podcast': r'\b(podcast|episode|interview|audio)\b',
        'tweet': r'\b(tweet|thread|twitter|x\.com)\b',
        'idea': r'\b(idea|concept|thought|brainstorm)\b',
    }
    
    def __init__(self, db: Optional[ContentIdeaDatabase] = None, db_path: str = "content_ideas.db"):
        """
        Initialize text capture module
        
        Args:
            db: Existing database instance or None to create new
            db_path: Database path if creating new instance
        """
        self.db = db or ContentIdeaDatabase(db_path)
    
    def capture(self, text: str, source: str = 'chat', 
                metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Capture text input and extract idea information
        
        Args:
            text: Raw text input
            source: Source of input (chat, command, import, etc.)
            metadata: Additional metadata
            
        Returns:
            Dict with capture result and extracted information
        """
        captured = CapturedText(
            raw_text=text,
            source=source,
            metadata=metadata or {}
        )
        
        # Parse the input
        parsed = self._parse_input(captured)
        
        return {
            'success': True,
            'captured': captured,
            'parsed': parsed,
            'content_type': parsed.get('content_type', 'idea'),
            'title': parsed.get('title', ''),
            'content': parsed.get('content', ''),
            'tags': parsed.get('tags', []),
            'priority': parsed.get('priority', 3),
        }
    
    def capture_and_store(self, text: str, source: str = 'chat',
                         category_id: Optional[int] = None,
                         tag_ids: Optional[List[int]] = None,
                         metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Capture text and store directly to database
        
        Args:
            text: Raw text input
            source: Source of input
            category_id: Optional category ID
            tag_ids: Optional list of tag IDs
            metadata: Additional metadata
            
        Returns:
            Dict with capture result and database ID
        """
        try:
            # First capture and parse
            result = self.capture(text, source, metadata)
            
            if not result['success']:
                return result
            
            parsed = result['parsed']
            
            # Store to database
            content_id = self.db.create_content_item(
                type=parsed.get('content_type', 'idea'),
                title=parsed.get('title', 'Untitled'),
                content=parsed.get('content', text),
                source=source,
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
                'parsed': parsed,
                'message': f"Captured and stored as content #{content_id}"
            }
            
        except DatabaseError as e:
            return {
                'success': False,
                'error': f"Database error: {e}",
                'parsed': result.get('parsed') if 'result' in locals() else None
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"Capture failed: {e}"
            }
    
    def _parse_input(self, captured: CapturedText) -> Dict[str, Any]:
        """
        Parse captured text to extract structured information
        
        Args:
            captured: CapturedText object
            
        Returns:
            Dict with parsed information
        """
        text = captured.raw_text.strip()
        result = {
            'original_text': text,
            'command_type': None,
            'content_type': 'idea',
            'title': '',
            'content': text,
            'tags': [],
            'priority': 3,
            'idea_concept': None,
            'elaboration': None,
            'use_cases': [],
        }
        
        # Check for command patterns
        for cmd_type, pattern in self.COMMAND_PATTERNS.items():
            match = re.match(pattern, text, re.IGNORECASE)
            if match:
                result['command_type'] = cmd_type
                text = match.group(1).strip()
                result['content'] = text
                break
        
        # Detect content type
        result['content_type'] = self._detect_content_type(text)
        
        # Extract title
        result['title'] = self._extract_title(text)
        
        # Extract tags
        result['tags'] = self._extract_tags(text)
        
        # Extract idea concept and elaboration
        concept_data = self._extract_idea_concept(text)
        result['idea_concept'] = concept_data['concept']
        result['elaboration'] = concept_data['elaboration']
        result['use_cases'] = concept_data['use_cases']
        
        # Detect priority
        result['priority'] = self._detect_priority(text)
        
        return result
    
    def _detect_content_type(self, text: str) -> str:
        """Detect content type from text patterns"""
        text_lower = text.lower()
        
        for content_type, pattern in self.CONTENT_TYPE_PATTERNS.items():
            if re.search(pattern, text_lower):
                return content_type
        
        return 'idea'
    
    def _extract_title(self, text: str, max_length: int = 100) -> str:
        """Extract a title from the text"""
        # Try to find a clear title pattern
        # Pattern: "Title: content" or "about Title" or first sentence
        
        # Check for explicit title marker
        title_match = re.match(r'^(?:title|about|re:)\s*[:\-]?\s*(.+?)(?:\n|$)', 
                               text, re.IGNORECASE)
        if title_match:
            title = title_match.group(1).strip()
            return title[:max_length]
        
        # Use first sentence or first N characters
        # Split by sentence endings
        sentences = re.split(r'[.!?。！？]+', text)
        if sentences and sentences[0].strip():
            title = sentences[0].strip()
            # If first sentence is too long, truncate at word boundary
            if len(title) > max_length:
                title = title[:max_length].rsplit(' ', 1)[0] + '...'
            return title
        
        # Fallback: first N characters
        return text[:max_length].strip()
    
    def _extract_tags(self, text: str) -> List[str]:
        """Extract hashtags and keyword tags from text"""
        tags = []
        
        # Extract hashtags
        hashtags = re.findall(r'#(\w+)', text)
        tags.extend(hashtags)
        
        # Extract bracket tags [tag]
        bracket_tags = re.findall(r'\[(\w+)\]', text)
        tags.extend(bracket_tags)
        
        # Extract common topic keywords
        topic_keywords = {
            'python': ['python', 'py'],
            'javascript': ['javascript', 'js', 'node', 'nodejs'],
            'typescript': ['typescript', 'ts'],
            'react': ['react', 'reactjs'],
            'ai': ['ai', 'artificial intelligence', 'machine learning', 'ml'],
            'web': ['web', 'frontend', 'backend', 'fullstack'],
            'devops': ['devops', 'docker', 'kubernetes', 'k8s', 'ci/cd'],
            'database': ['database', 'sql', 'nosql', 'postgres', 'mongodb'],
            'tutorial': ['tutorial', 'guide', 'howto', 'how-to'],
            'tips': ['tips', 'tricks', 'best practices'],
        }
        
        text_lower = text.lower()
        for tag, keywords in topic_keywords.items():
            if any(kw in text_lower for kw in keywords):
                if tag not in tags:
                    tags.append(tag)
        
        return list(set(tags))  # Remove duplicates
    
    def _extract_idea_concept(self, text: str) -> Dict[str, Any]:
        """Extract core idea concept and elaboration"""
        result = {
            'concept': None,
            'elaboration': None,
            'use_cases': []
        }
        
        # Try to extract a concise concept
        # Look for patterns like "Idea: X" or "Concept: X"
        concept_match = re.search(
            r'(?:idea|concept|thought)[:\-]?\s*["\']?([^"\'\n.!?]+)["\']?',
            text, re.IGNORECASE
        )
        
        if concept_match:
            result['concept'] = concept_match.group(1).strip()
            # Rest of text is elaboration
            rest = text[concept_match.end():].strip()
            if rest:
                result['elaboration'] = rest
        else:
            # Use first sentence as concept if it's short
            sentences = re.split(r'[.!?。！？]+', text)
            if sentences:
                first = sentences[0].strip()
                if len(first) <= 100:
                    result['concept'] = first
                    if len(sentences) > 1:
                        result['elaboration'] = '. '.join(s.strip() for s in sentences[1:] if s.strip())
                else:
                    # Truncate for concept
                    result['concept'] = first[:100].rsplit(' ', 1)[0] + '...'
                    result['elaboration'] = text
        
        # Extract use cases
        use_case_patterns = [
            r'(?:use case|example|scenario)[:\-]?\s*(.+?)(?=\n\n|\Z)',
            r'(?:for example|e\.g\.)[:\-]?\s*(.+?)(?=\n\n|\Z)',
        ]
        
        for pattern in use_case_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE | re.DOTALL)
            result['use_cases'].extend(m.strip() for m in matches if len(m.strip()) > 10)
        
        return result
    
    def _detect_priority(self, text: str) -> int:
        """Detect priority level from text cues"""
        text_lower = text.lower()
        
        # High priority indicators
        high_priority = ['urgent', 'important', 'critical', 'high priority', 
                        'must do', 'asap', 'priority 5', '!!!']
        if any(indicator in text_lower for indicator in high_priority):
            return 5
        
        # Low priority indicators
        low_priority = ['low priority', 'whenever', 'someday', 'maybe', 
                       'nice to have', 'priority 1', 'eventually']
        if any(indicator in text_lower for indicator in low_priority):
            return 1
        
        # Medium-high
        med_high = ['priority 4', 'should do', '!!']
        if any(indicator in text_lower for indicator in med_high):
            return 4
        
        # Medium-low
        med_low = ['priority 2', '!']
        if any(indicator in text_lower for indicator in med_low):
            return 2
        
        return 3  # Default medium priority
    
    def batch_capture(self, texts: List[str], source: str = 'import') -> List[Dict[str, Any]]:
        """
        Capture multiple text inputs at once
        
        Args:
            texts: List of text strings
            source: Source identifier
            
        Returns:
            List of capture results
        """
        results = []
        for text in texts:
            result = self.capture(text, source)
            results.append(result)
        return results
