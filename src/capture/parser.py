"""
Idea Parser Module

Shared parsing utilities for extracting structured ideas from various sources.
Used by text, voice, and screenshot capture modules.
"""

import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass


@dataclass
class ParsedIdea:
    """Structured representation of a parsed idea"""
    concept: str
    elaboration: Optional[str] = None
    content_type: str = 'idea'
    title: str = ''
    tags: List[str] = None
    priority: int = 3
    use_cases: List[str] = None
    source_type: str = 'unknown'
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.use_cases is None:
            self.use_cases = []
        if not self.title:
            self.title = self.concept[:100] if len(self.concept) <= 100 else self.concept[:100].rsplit(' ', 1)[0] + '...'


class IdeaParser:
    """
    Universal parser for extracting ideas from various input sources.
    
    Provides consistent parsing across text, voice, and image inputs.
    """
    
    # Content type detection patterns
    CONTENT_TYPE_PATTERNS = {
        'article': r'\b(article|blog.?post|essay|write.?up|publication)\b',
        'video': r'\b(video|youtube|tutorial|course|screencast|recording)\b',
        'book': r'\b(book|ebook|publication|chapter|manuscript)\b',
        'podcast': r'\b(podcast|episode|interview|audio.?show)\b',
        'tweet': r'\b(tweet|thread|twitter|x\.com|social.?media)\b',
        'code': r'\b(code|script|program|function|snippet)\b',
        'note': r'\b(note|memo|reminder|jotting)\b',
        'idea': r'\b(idea|concept|thought|brainstorm|inspiration)\b',
    }
    
    # Priority detection patterns
    PRIORITY_PATTERNS = {
        5: [r'\burgent\b', r'\bcritical\b', r'\bhigh priority\b', r'\basap\b', 
            r'\bmust do\b', r'!!!', r'\bpriority[:\s]*5\b', r'\bp1\b'],
        4: [r'\bimportant\b', r'\bshould do\b', r'!!', r'\bpriority[:\s]*4\b', r'\bp2\b'],
        2: [r'\blow priority\b', r'\bwhenever\b', r'!', r'\bpriority[:\s]*2\b', r'\bp4\b'],
        1: [r'\bsomeday\b', r'\bmaybe\b', r'\bnice to have\b', r'\beventually\b', 
            r'\bpriority[:\s]*1\b', r'\bp5\b'],
    }
    
    # Topic keywords for auto-tagging
    TOPIC_KEYWORDS = {
        'python': ['python', 'py', 'django', 'flask', 'fastapi'],
        'javascript': ['javascript', 'js', 'node', 'nodejs', 'es6'],
        'typescript': ['typescript', 'ts'],
        'react': ['react', 'reactjs', 'jsx', 'nextjs'],
        'vue': ['vue', 'vuejs', 'nuxt'],
        'angular': ['angular'],
        'ai': ['ai', 'artificial intelligence', 'machine learning', 'ml', 'deep learning'],
        'web': ['web', 'frontend', 'backend', 'fullstack', 'webdev'],
        'devops': ['devops', 'docker', 'kubernetes', 'k8s', 'ci/cd', 'pipeline'],
        'database': ['database', 'sql', 'nosql', 'postgres', 'mongodb', 'redis'],
        'cloud': ['cloud', 'aws', 'azure', 'gcp', 'serverless'],
        'security': ['security', 'cybersecurity', 'encryption', 'auth'],
        'tutorial': ['tutorial', 'guide', 'howto', 'how-to', 'walkthrough'],
        'tips': ['tips', 'tricks', 'best practices', 'patterns'],
        'review': ['review', 'comparison', 'vs', 'versus'],
        'news': ['news', 'update', 'announcement', 'release'],
    }
    
    @classmethod
    def parse(cls, text: str, source_type: str = 'unknown') -> ParsedIdea:
        """
        Parse text to extract structured idea information
        
        Args:
            text: Input text to parse
            source_type: Source of the text (text, voice, image, etc.)
            
        Returns:
            ParsedIdea object with extracted information
        """
        text = text.strip()
        
        # Extract components
        concept = cls._extract_concept(text)
        elaboration = cls._extract_elaboration(text, concept)
        content_type = cls._detect_content_type(text)
        title = cls._extract_title(text, concept)
        tags = cls._extract_tags(text)
        priority = cls._detect_priority(text)
        use_cases = cls._extract_use_cases(text)
        
        return ParsedIdea(
            concept=concept,
            elaboration=elaboration,
            content_type=content_type,
            title=title,
            tags=tags,
            priority=priority,
            use_cases=use_cases,
            source_type=source_type
        )
    
    @classmethod
    def _extract_concept(cls, text: str) -> str:
        """Extract the core concept/idea from text"""
        # Try explicit concept markers
        concept_patterns = [
            r'(?:idea|concept|thought)[:\-]?\s*["\']?([^"\'\n.!?]{5,100})["\']?',
            r'(?:about|regarding|on)[:\-]?\s*["\']?([^"\'\n.!?]{5,100})["\']?',
        ]
        
        for pattern in concept_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        # Use first sentence if reasonably sized
        sentences = re.split(r'[.!?。！？]+', text)
        for sentence in sentences:
            sentence = sentence.strip()
            if 10 <= len(sentence) <= 100:
                return sentence
            elif len(sentence) > 100:
                return sentence[:100].rsplit(' ', 1)[0] + '...'
        
        # Fallback: first 100 chars
        if len(text) <= 100:
            return text
        return text[:100].rsplit(' ', 1)[0] + '...'
    
    @classmethod
    def _extract_elaboration(cls, text: str, concept: str) -> Optional[str]:
        """Extract elaboration/details beyond the core concept"""
        # Remove concept from text to get elaboration
        concept_pos = text.find(concept)
        if concept_pos >= 0:
            after_concept = text[concept_pos + len(concept):].strip()
            # Remove leading punctuation
            after_concept = re.sub(r'^[.!?;:\s]+', '', after_concept)
            if after_concept:
                return after_concept
        
        # If concept is first sentence, rest is elaboration
        sentences = re.split(r'([.!?。！？]+)', text)
        if len(sentences) > 2:
            # Reconstruct sentences (they're split with delimiters)
            rest = ''.join(sentences[2:]).strip()
            if rest:
                return rest
        
        return None
    
    @classmethod
    def _detect_content_type(cls, text: str) -> str:
        """Detect the type of content from text patterns"""
        text_lower = text.lower()
        
        for content_type, pattern in cls.CONTENT_TYPE_PATTERNS.items():
            if re.search(pattern, text_lower):
                return content_type
        
        return 'idea'
    
    @classmethod
    def _extract_title(cls, text: str, concept: str) -> str:
        """Extract a title from the text"""
        # Check for explicit title
        title_match = re.match(r'^(?:title|subject)[:\-]?\s*(.+?)(?:\n|$)', 
                               text, re.IGNORECASE)
        if title_match:
            title = title_match.group(1).strip()
            return title[:100] if len(title) <= 100 else title[:100].rsplit(' ', 1)[0] + '...'
        
        # Use concept as title if it's short enough
        if len(concept) <= 100:
            return concept
        
        # Truncate concept for title
        return concept[:100].rsplit(' ', 1)[0] + '...'
    
    @classmethod
    def _extract_tags(cls, text: str) -> List[str]:
        """Extract tags from text"""
        tags = []
        text_lower = text.lower()
        
        # Extract hashtags
        hashtags = re.findall(r'#(\w+)', text)
        tags.extend(hashtags)
        
        # Extract bracket tags [tag]
        bracket_tags = re.findall(r'\[(\w+)\]', text)
        tags.extend(bracket_tags)
        
        # Match topic keywords
        for tag, keywords in cls.TOPIC_KEYWORDS.items():
            if any(kw in text_lower for kw in keywords):
                if tag not in tags:
                    tags.append(tag)
        
        return list(set(tags))  # Remove duplicates
    
    @classmethod
    def _detect_priority(cls, text: str) -> int:
        """Detect priority level from text"""
        text_lower = text.lower()
        
        # Check patterns from highest to lowest
        for priority in [5, 4, 2, 1]:
            for pattern in cls.PRIORITY_PATTERNS.get(priority, []):
                if re.search(pattern, text_lower):
                    return priority
        
        return 3  # Default medium priority
    
    @classmethod
    def _extract_use_cases(cls, text: str) -> List[str]:
        """Extract use cases or examples from text"""
        use_cases = []
        
        # Patterns for use cases
        patterns = [
            r'(?:use case|example|scenario)[:\-]?\s*(.+?)(?=\n\n|\Z|(?:use case|example|scenario)[:\-]?)',
            r'(?:for example|e\.g\.)[:\-]?\s*(.+?)(?=\n\n|\Z|(?:for example|e\.g\.))',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE | re.DOTALL)
            for match in matches:
                case = match.strip()
                if len(case) > 10:  # Filter out very short matches
                    use_cases.append(case)
        
        return use_cases
    
    @classmethod
    def clean_text(cls, text: str, source_type: str = 'unknown') -> str:
        """
        Clean and normalize text based on source type
        
        Args:
            text: Raw text to clean
            source_type: Source type for source-specific cleaning
            
        Returns:
            Cleaned text
        """
        # Common cleaning
        text = text.strip()
        
        # Source-specific cleaning
        if source_type == 'voice':
            text = cls._clean_voice_text(text)
        elif source_type == 'image':
            text = cls._clean_ocr_text(text)
        
        return text
    
    @classmethod
    def _clean_voice_text(cls, text: str) -> str:
        """Clean transcription artifacts from voice input"""
        # Remove filler words at start
        text = re.sub(r'^(so|um|uh|like|you know|well)\s+', '', text, flags=re.IGNORECASE)
        
        # Remove repeated words (common in transcription)
        text = re.sub(r'\b(\w+)\s+\1\b', r'\1', text, flags=re.IGNORECASE)
        
        # Normalize whitespace
        text = ' '.join(text.split())
        
        return text
    
    @classmethod
    def _clean_ocr_text(cls, text: str) -> str:
        """Clean OCR artifacts from image text"""
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
            '|': 'I',
            '0': 'O',
            '@': 'a',
            '$': 's',
        }
        
        for old, new in replacements.items():
            text = re.sub(rf'(?<=\w){old}(?=\w)', new, text)
        
        # Normalize multiple spaces
        text = ' '.join(text.split())
        
        return text
