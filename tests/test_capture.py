"""
Test script for the capture module
"""

import sys
from pathlib import Path

# Add paths
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'content_idea_generator'))
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from capture import TextCapture, VoiceCapture, ScreenshotCapture, IdeaParser

def test_text_capture():
    """Test text capture functionality"""
    print("\n📝 Testing Text Capture...")
    
    capture = TextCapture(db_path=":memory:")
    
    # Test command-style input
    result = capture.capture("/capture Python decorators tutorial for beginners")
    assert result['success'], f"Text capture failed: {result.get('error')}"
    assert result['content_type'] == 'tutorial' or result['content_type'] == 'article'
    assert 'python' in result['tags'] or 'tutorial' in result['tags']
    print(f"  ✅ Command capture: '{result['title'][:50]}...'")
    
    # Test natural language
    result = capture.capture("I have an idea for a blog post about React hooks and state management")
    assert result['success']
    assert 'react' in result['tags']
    print(f"  ✅ Natural language: '{result['title'][:50]}...'")
    
    # Test with priority
    result = capture.capture("URGENT: Need to write about AI safety and ethics ASAP!!!")
    assert result['priority'] == 5
    print(f"  ✅ Priority detection: {result['priority']}/5")
    
    print("  ✅ Text capture tests passed!")

def test_voice_capture():
    """Test voice capture functionality"""
    print("\n🎤 Testing Voice Capture...")
    
    capture = VoiceCapture(db_path=":memory:")
    
    # Test availability check
    status = capture.status
    print(f"  📊 Voice capture status: {status}")
    
    # Test parsing (without actual audio)
    parsed = capture._parse_transcription("Idea: Create a video tutorial about Docker containers and Kubernetes")
    assert parsed['content_type'] == 'video'
    assert 'devops' in parsed['tags']
    print(f"  ✅ Transcription parsing: '{parsed['title'][:50]}...'")
    
    print("  ✅ Voice capture tests passed!")

def test_screenshot_capture():
    """Test screenshot capture functionality"""
    print("\n📸 Testing Screenshot Capture...")
    
    capture = ScreenshotCapture(db_path=":memory:")
    
    # Test availability check
    status = capture.status
    print(f"  📊 Screenshot capture status: {status}")
    
    # Test OCR text parsing
    parsed = capture._parse_ocr_text("TODO: Write an article about Python async/await patterns")
    assert parsed['idea_concept'] is not None
    assert 'python' in parsed['tags']
    print(f"  ✅ OCR parsing: '{parsed['title'][:50]}...'")
    
    print("  ✅ Screenshot capture tests passed!")

def test_idea_parser():
    """Test the universal idea parser"""
    print("\n🔍 Testing Idea Parser...")
    
    # Test basic parsing
    parsed = IdeaParser.parse("Idea: Build a CLI tool for managing content ideas with tags and priorities")
    assert parsed.concept is not None
    assert 'idea' in parsed.tags or 'code' in parsed.tags
    print(f"  ✅ Basic parsing: '{parsed.concept[:50]}...'")
    
    # Test with use cases
    text = """
    Concept: Automated content pipeline
    
    Use case: Capture ideas from voice memos
    Use case: Extract text from screenshots
    Use case: Organize by tags and priority
    """
    parsed = IdeaParser.parse(text)
    assert len(parsed.use_cases) >= 2
    print(f"  ✅ Use case extraction: {len(parsed.use_cases)} use cases found")
    
    # Test priority detection
    parsed = IdeaParser.parse("CRITICAL: Fix the database connection issue ASAP!!! Priority 5")
    assert parsed.priority == 5
    print(f"  ✅ Priority detection: {parsed.priority}/5")
    
    print("  ✅ Idea parser tests passed!")

def test_integration():
    """Test integration with database"""
    print("\n🔗 Testing Database Integration...")
    
    capture = TextCapture(db_path=":memory:")
    
    # Test capture and store
    result = capture.capture_and_store(
        "/capture Tutorial: How to use SQLite FTS5 for full-text search",
        category_id=None,
        tag_ids=[]
    )
    
    assert result['success'], f"Store failed: {result.get('error')}"
    assert 'content_id' in result
    print(f"  ✅ Stored content with ID: {result['content_id']}")
    
    if result.get('idea_id'):
        print(f"  ✅ Created idea with ID: {result['idea_id']}")
    
    print("  ✅ Integration tests passed!")

if __name__ == '__main__':
    print("=" * 60)
    print("Content Idea Generator - Capture Module Tests")
    print("=" * 60)
    
    try:
        test_text_capture()
        test_voice_capture()
        test_screenshot_capture()
        test_idea_parser()
        test_integration()
        
        print("\n" + "=" * 60)
        print("✅ All tests passed!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
