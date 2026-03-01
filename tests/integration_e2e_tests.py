"""
TDD Test Suite for Content Idea Generator Skill - Part 2
Integration Tests & End-to-End Tests

This completes the test suite started by the subagent.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import json


# ═══════════════════════════════════════════════════════════════════════════════
# Integration Tests
# ═══════════════════════════════════════════════════════════════════════════════

class TestVoiceToStorageIntegration:
    """Integration tests: Voice → STT → Storage flow"""
    
    def test_voice_message_complete_flow(self):
        """✅ E2E: Voice message → transcribed → stored with metadata"""
        # Arrange
        audio_data = b"fake_audio_data"
        expected_transcription = "I have an idea for a Python tutorial"
        
        with patch('whisper_cpp.transcribe') as mock_stt, \
             patch('IdeaRepository.create') as mock_create:
            
            mock_stt.return_value = {
                "text": expected_transcription,
                "confidence": 0.95,
                "language": "en"
            }
            mock_create.return_value = {"id": "idea-001", "status": "success"}
            
            # Act
            result = VoiceCaptureService().process(audio_data)
            
            # Assert
            assert result["transcription"] == expected_transcription
            assert result["stored"] is True
            assert result["idea_id"] == "idea-001"
    
    def test_voice_low_confidence_fallback(self):
        """✅ Low confidence transcription triggers manual review"""
        with patch('whisper_cpp.transcribe') as mock_stt:
            mock_stt.return_value = {
                "text": "unclear audio",
                "confidence": 0.45,
                "language": "en"
            }
            
            result = VoiceCaptureService().process(b"audio")
            
            assert result["status"] == "needs_review"
            assert result["confidence"] < 0.5


class TestScreenshotToStorageIntegration:
    """Integration tests: Screenshot → OCR → Storage flow"""
    
    def test_screenshot_complete_flow(self):
        """✅ E2E: Screenshot → OCR → extract ideas → stored"""
        image_data = b"fake_image_data"
        expected_text = "TODO:\n- Write blog post about Docker\n- Create video script"
        
        with patch('pytesseract.image_to_string') as mock_ocr, \
             patch('IdeaRepository.create') as mock_create:
            
            mock_ocr.return_value = expected_text
            mock_create.return_value = {"id": "idea-002"}
            
            result = ScreenshotCaptureService().process(image_data)
            
            assert len(result["extracted_ideas"]) == 2
            assert result["stored_count"] == 2
    
    def test_screenshot_no_text_found(self):
        """✅ Screenshot with no readable text handled gracefully"""
        with patch('pytesseract.image_to_string') as mock_ocr:
            mock_ocr.return_value = ""
            
            result = ScreenshotCaptureService().process(b"image")
            
            assert result["status"] == "no_text_found"
            assert result["stored_count"] == 0


class TestDailyAnalysisToReportIntegration:
    """Integration tests: Daily analysis → Report generation"""
    
    def test_daily_analysis_generates_report(self):
        """✅ Daily analysis runs and generates chat-formatted report"""
        with patch('AnalysisEngine.analyze') as mock_analyze, \
             patch('ReportGenerator.generate') as mock_report:
            
            mock_analyze.return_value = {
                "clusters": [{"name": "Python", "ideas": 3}],
                "suggestions": ["Create a Python series"]
            }
            mock_report.return_value = "📊 Daily Report:\n\n3 Python ideas found..."
            
            result = DailyAnalysisService().run()
            
            assert "📊" in result
            assert "Python" in result
    
    def test_empty_library_report(self):
        """✅ Empty library produces encouraging message"""
        with patch('IdeaRepository.get_all') as mock_get:
            mock_get.return_value = []
            
            result = DailyAnalysisService().run()
            
            assert "No ideas yet" in result or "Start capturing" in result


# ═══════════════════════════════════════════════════════════════════════════════
# End-to-End Tests
# ═══════════════════════════════════════════════════════════════════════════════

class TestCompleteUserWorkflow:
    """End-to-end: Complete user workflows"""
    
    def test_user_captures_idea_via_text(self):
        """✅ E2E: User sends text → stored → confirmed"""
        # User: "/capture Python decorators tutorial"
        user_input = "/capture Python decorators tutorial"
        
        with patch('ChatHandler.parse_command') as mock_parse, \
             patch('IdeaRepository.create') as mock_create, \
             patch('ChatHandler.send_response') as mock_send:
            
            mock_parse.return_value = {
                "command": "capture",
                "content": "Python decorators tutorial",
                "tags": ["python"]
            }
            mock_create.return_value = {"id": "idea-001", "title": "Python decorators tutorial"}
            
            # Execute workflow
            ChatHandler().handle_message(user_input)
            
            # Verify
            mock_create.assert_called_once()
            mock_send.assert_called_with("✅ Idea saved: Python decorators tutorial")
    
    def test_user_requests_daily_report(self):
        """✅ E2E: User requests report → analysis runs → report delivered"""
        user_input = "/report"
        
        with patch('DailyAnalysisService.run') as mock_analysis, \
             patch('ChatHandler.send_response') as mock_send:
            
            mock_analysis.return_value = "📊 Daily Report:\n- 5 new ideas\n- Top: Python"
            
            ChatHandler().handle_message(user_input)
            
            mock_analysis.assert_called_once()
            mock_send.assert_called_with("📊 Daily Report:\n- 5 new ideas\n- Top: Python")
    
    def test_user_searches_ideas(self):
        """✅ E2E: User searches → results returned → can select"""
        user_input = "/search python"
        
        with patch('IdeaRepository.search') as mock_search, \
             patch('ChatHandler.send_response') as mock_send:
            
            mock_search.return_value = [
                {"id": "1", "title": "Python tips"},
                {"id": "2", "title": "Python tutorial"}
            ]
            
            ChatHandler().handle_message(user_input)
            
            assert mock_send.call_count == 1
            response = mock_send.call_args[0][0]
            assert "Python tips" in response
            assert "Python tutorial" in response


class TestDailyReportDelivery:
    """End-to-end: Daily report delivery"""
    
    def test_daily_report_auto_delivered(self):
        """✅ E2E: Cron triggers → report generated → sent to user"""
        with patch('CronService.should_run') as mock_cron, \
             patch('DailyAnalysisService.run') as mock_analysis, \
             patch('NotificationService.send') as mock_notify:
            
            mock_cron.return_value = True
            mock_analysis.return_value = "📊 Your daily inspiration report..."
            
            CronJobRunner().check_and_run()
            
            mock_analysis.assert_called_once()
            mock_notify.assert_called_with("📊 Your daily inspiration report...")
    
    def test_user_interacts_with_suggestion(self):
        """✅ E2E: Report suggestion → user clicks → action taken"""
        # User clicks "Create draft" on a suggestion
        user_action = {"action": "create_draft", "idea_ids": ["1", "2"]}
        
        with patch('DraftGenerator.generate') as mock_draft, \
             patch('ChatHandler.send_response') as mock_send:
            
            mock_draft.return_value = "Draft content here..."
            
            ActionHandler().handle(user_action)
            
            mock_draft.assert_called_with(["1", "2"])
            mock_send.assert_called_with("📝 Draft created:\nDraft content here...")


class TestContentSuggestionInteraction:
    """End-to-end: Content suggestion interactions"""
    
    def test_user_accepts_suggestion(self):
        """✅ E2E: Suggestion shown → user accepts → idea created"""
        suggestion = {"type": "series", "message": "Create Python series", "ideas": ["1", "2"]}
        
        with patch('IdeaRepository.create') as mock_create, \
             patch('ChatHandler.send_response') as mock_send:
            
            mock_create.return_value = {"id": "series-001"}
            
            SuggestionHandler().accept(suggestion)
            
            mock_create.assert_called_once()
            mock_send.assert_called_with("✅ Series idea created!")
    
    def test_user_dismisses_suggestion(self):
        """✅ E2E: Suggestion shown → user dismisses → marked ignored"""
        suggestion_id = "sugg-001"
        
        with patch('SuggestionRepository.mark_dismissed') as mock_dismiss:
            
            SuggestionHandler().dismiss(suggestion_id)
            
            mock_dismiss.assert_called_with(suggestion_id)


# ═══════════════════════════════════════════════════════════════════════════════
# Test Fixtures (Additional)
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.fixture
def mock_whisper_result():
    """Mock whisper.cpp transcription result"""
    return {
        "text": "I have an idea for a blog post",
        "confidence": 0.95,
        "language": "en",
        "segments": [
            {"start": 0.0, "end": 2.5, "text": "I have an idea"}
        ]
    }

@pytest.fixture
def mock_ocr_result():
    """Mock OCR result from screenshot"""
    return {
        "text": "TODO:\n- Write about Python\n- Create video",
        "confidence": 0.92,
        "boxes": [
            {"text": "TODO:", "bbox": [10, 10, 100, 30]},
            {"text": "- Write about Python", "bbox": [10, 40, 200, 60]}
        ]
    }

@pytest.fixture
def mock_analysis_result():
    """Mock daily analysis result"""
    return {
        "total_ideas": 5,
        "new_ideas": 3,
        "clusters": [
            {"name": "Python", "count": 2, "ideas": ["1", "2"]},
            {"name": "Docker", "count": 1, "ideas": ["3"]}
        ],
        "suggestions": [
            {
                "type": "series",
                "message": "Create a Python tutorial series",
                "confidence": 0.85,
                "related_ideas": ["1", "2"]
            }
        ],
        "trends": {
            "most_active_day": "Wednesday",
            "avg_ideas_per_day": 2.5
        }
    }


# ═══════════════════════════════════════════════════════════════════════════════
# Mock Service Classes
# ═══════════════════════════════════════════════════════════════════════════════

class VoiceCaptureService:
    """Mock voice capture service"""
    def process(self, audio_data):
        # In real implementation: call whisper.cpp
        return {
            "transcription": "mock transcription",
            "confidence": 0.95,
            "stored": True,
            "idea_id": "idea-001"
        }

class ScreenshotCaptureService:
    """Mock screenshot capture service"""
    def process(self, image_data):
        # In real implementation: call OCR
        return {
            "extracted_ideas": [{"title": "Idea 1"}, {"title": "Idea 2"}],
            "stored_count": 2
        }

class DailyAnalysisService:
    """Mock daily analysis service"""
    def run(self):
        # In real implementation: run analysis pipeline
        return "📊 Daily Report:\n- 5 ideas\n- Top: Python"

class ChatHandler:
    """Mock chat handler"""
    def handle_message(self, message):
        pass
    
    def send_response(self, response):
        pass
    
    def parse_command(self, message):
        return {"command": "capture", "content": message}

class CronJobRunner:
    """Mock cron job runner"""
    def check_and_run(self):
        pass

class NotificationService:
    """Mock notification service"""
    @staticmethod
    def send(message):
        pass

class ActionHandler:
    """Mock action handler"""
    def handle(self, action):
        pass

class SuggestionHandler:
    """Mock suggestion handler"""
    def accept(self, suggestion):
        pass
    
    def dismiss(self, suggestion_id):
        pass

class DraftGenerator:
    """Mock draft generator"""
    @staticmethod
    def generate(idea_ids):
        return "Draft content..."

class SuggestionRepository:
    """Mock suggestion repository"""
    @staticmethod
    def mark_dismissed(suggestion_id):
        pass
