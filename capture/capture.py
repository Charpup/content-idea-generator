"""
Content Idea Generator - Capture Module

Content ingestion and parsing functionality.
"""

import re
from typing import Optional, List, Dict, Any
from pathlib import Path


class TextParser:
    """Parse and clean text content"""
    
    # Common URL pattern
    URL_PATTERN = re.compile(
        r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    )
    
    # Email pattern
    EMAIL_PATTERN = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
    
    def __init__(self):
        self.stop_words = self._load_stop_words()
    
    def _load_stop_words(self) -> set:
        """Load common English stop words"""
        return {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'be',
            'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
            'would', 'could', 'should', 'may', 'might', 'must', 'shall', 'can',
            'need', 'dare', 'ought', 'used', 'this', 'that', 'these', 'those',
            'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her',
            'us', 'them', 'my', 'your', 'his', 'its', 'our', 'their'
        }
    
    def clean_text(self, text: str) -> str:
        """
        Clean text by removing extra whitespace and normalizing
        
        Args:
            text: Raw text content
            
        Returns:
            Cleaned text
        """
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove leading/trailing whitespace
        text = text.strip()
        return text
    
    def extract_urls(self, text: str) -> List[str]:
        """Extract URLs from text"""
        return self.URL_PATTERN.findall(text)
    
    def extract_emails(self, text: str) -> List[str]:
        """Extract email addresses from text"""
        return self.EMAIL_PATTERN.findall(text)
    
    def extract_snippets(self, text: str, min_length: int = 50, 
                        max_length: int = 500) -> List[Dict[str, Any]]:
        """
        Extract potential snippets from text
        
        Args:
            text: Full text content
            min_length: Minimum snippet length
            max_length: Maximum snippet length
            
        Returns:
            List of snippet dictionaries
        """
        snippets = []
        
        # Split into sentences (simple approach)
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        for sentence in sentences:
            sentence = sentence.strip()
            if min_length <= len(sentence) <= max_length:
                # Check if sentence looks like a quote or key insight
                is_quote = sentence.startswith('"') or sentence.startswith("'")
                has_key_words = any(word in sentence.lower() for word in 
                                  ['important', 'key', 'crucial', 'essential', 
                                   'remember', 'note', 'insight'])
                
                score = 0
                if is_quote:
                    score += 2
                if has_key_words:
                    score += 1
                if len(sentence) > 100:
                    score += 1
                
                snippets.append({
                    'text': sentence,
                    'length': len(sentence),
                    'score': score
                })
        
        # Sort by score
        snippets.sort(key=lambda x: x['score'], reverse=True)
        return snippets
    
    def extract_keywords(self, text: str, top_n: int = 10) -> List[str]:
        """
        Extract keywords from text using simple TF scoring
        
        Args:
            text: Text content
            top_n: Number of top keywords to return
            
        Returns:
            List of keywords
        """
        # Clean and tokenize
        text = re.sub(r'[^\w\s]', ' ', text.lower())
        words = text.split()
        
        # Filter stop words and short words
        words = [w for w in words if w not in self.stop_words and len(w) > 2]
        
        # Count frequency
        word_freq = {}
        for word in words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # Return top N
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, _ in sorted_words[:top_n]]
    
    def estimate_reading_time(self, text: str, wpm: int = 200) -> int:
        """
        Estimate reading time in minutes
        
        Args:
            text: Text content
            wpm: Words per minute reading speed
            
        Returns:
            Estimated reading time in minutes
        """
        word_count = len(text.split())
        return max(1, round(word_count / wpm))


class ContentCapture:
    """Capture content from various sources"""
    
    def __init__(self, db):
        """
        Initialize content capture
        
        Args:
            db: Database instance
        """
        self.db = db
        self.parser = TextParser()
    
    def capture_from_text(self, type: str, title: str, content: str,
                         source: Optional[str] = None,
                         author: Optional[str] = None,
                         category: Optional[str] = None,
                         tags: Optional[List[str]] = None,
                         auto_extract: bool = True) -> int:
        """
        Capture content from text
        
        Args:
            type: Content type
            title: Content title
            content: Full content text
            source: Source URL or reference
            author: Content author
            category: Category name
            tags: List of tag names
            auto_extract: Auto-extract snippets
            
        Returns:
            Content item ID
        """
        # Clean content
        cleaned_content = self.parser.clean_text(content)
        
        # Handle category
        category_id = None
        if category:
            cat = self.db.get_category_by_name(category)
            if cat:
                category_id = cat['id']
            else:
                category_id = self.db.create_category(category)
        
        # Handle tags
        tag_ids = []
        if tags:
            for tag_name in tags:
                tag = self.db.get_tag_by_name(tag_name)
                if tag:
                    tag_ids.append(tag['id'])
                else:
                    tag_id = self.db.create_tag(tag_name)
                    tag_ids.append(tag_id)
        
        # Create content item
        content_id = self.db.create_content_item(
            type=type,
            title=title,
            content=cleaned_content,
            source=source,
            author=author,
            category_id=category_id,
            tag_ids=tag_ids
        )
        
        # Auto-extract snippets
        if auto_extract:
            snippets = self.parser.extract_snippets(cleaned_content)
            for snippet in snippets[:5]:  # Top 5 snippets
                self.db.create_text_snippet(
                    content_id=content_id,
                    snippet_text=snippet['text']
                )
        
        return content_id
    
    def capture_from_file(self, file_path: str, type: str, title: Optional[str] = None,
                         **kwargs) -> int:
        """
        Capture content from file
        
        Args:
            file_path: Path to file
            type: Content type
            title: Content title (defaults to filename)
            **kwargs: Additional arguments for capture_from_text
            
        Returns:
            Content item ID
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Read content
        content = path.read_text(encoding='utf-8')
        
        # Use filename as title if not provided
        if title is None:
            title = path.stem
        
        return self.capture_from_text(
            type=type,
            title=title,
            content=content,
            **kwargs
        )


__all__ = [
    'TextParser',
    'ContentCapture'
]
