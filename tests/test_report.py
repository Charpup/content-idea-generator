"""
Test suite for Report Generator module.
Content Idea Generator Skill - TDD Implementation

Phase 2.1: RED - Write failing tests first
"""

import pytest
import sys
import os
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional
from unittest.mock import Mock, patch, MagicMock

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from report import (
    ReportGenerator,
    Report,
    ReportStats,
    Suggestion,
    TemplateEngine,
    Cluster,
    Idea,
)


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def sample_ideas():
    """Generate sample ideas for testing."""
    base_date = datetime(2026, 3, 2, 10, 0, 0)
    return [
        Idea(id="idea-001", content="Python decorators tutorial", 
             input_type="text", tags=["python", "tutorial"], 
             created_at=base_date - timedelta(hours=2)),
        Idea(id="idea-002", content="Docker best practices", 
             input_type="text", tags=["devops", "docker"], 
             created_at=base_date - timedelta(hours=4)),
        Idea(id="idea-003", content="List comprehensions guide", 
             input_type="voice", tags=["python", "tutorial"], 
             created_at=base_date - timedelta(hours=6)),
        Idea(id="idea-004", content="CI/CD pipeline setup", 
             input_type="screenshot", tags=["devops", "ci-cd"], 
             created_at=base_date - timedelta(hours=8)),
        Idea(id="idea-005", content="Context managers explained", 
             input_type="text", tags=["python", "advanced"], 
             created_at=base_date - timedelta(hours=10)),
        Idea(id="idea-006", content="Kubernetes basics", 
             input_type="text", tags=["devops", "kubernetes"], 
             created_at=base_date - timedelta(hours=12)),
        Idea(id="idea-007", content="Lambda functions deep dive", 
             input_type="voice", tags=["python", "tutorial"], 
             created_at=base_date - timedelta(hours=14)),
        Idea(id="idea-008", content="GitHub Actions workflows", 
             input_type="text", tags=["devops", "ci-cd"], 
             created_at=base_date - timedelta(hours=16)),
        Idea(id="idea-009", content="Type hints best practices", 
             input_type="text", tags=["python", "tutorial"], 
             created_at=base_date - timedelta(hours=18)),
        Idea(id="idea-010", content="Container security", 
             input_type="screenshot", tags=["devops", "security"], 
             created_at=base_date - timedelta(hours=20)),
    ]


@pytest.fixture
def sample_clusters():
    """Generate sample clusters for suggestion testing."""
    return [
        Cluster(
            id="python-tips",
            theme="Python",
            idea_ids=["idea-001", "idea-003", "idea-005", "idea-007", "idea-009"],
            strength=5
        ),
        Cluster(
            id="devops-guide",
            theme="DevOps",
            idea_ids=["idea-002", "idea-004", "idea-006", "idea-008", "idea-010"],
            strength=5
        ),
        Cluster(
            id="random",
            theme="Misc",
            idea_ids=["idea-random-1", "idea-random-2"],
            strength=2
        ),
    ]


@pytest.fixture
def mock_db():
    """Create a mock database for testing."""
    return Mock()


@pytest.fixture
def report_generator(mock_db):
    """Create a ReportGenerator instance with mock DB."""
    return ReportGenerator(database=mock_db)


@pytest.fixture
def temp_vault(tmp_path):
    """Create a temporary Obsidian vault directory."""
    vault = tmp_path / "test_vault"
    vault.mkdir()
    return vault


# =============================================================================
# TC-001: Daily report with multiple ideas (Integration Test)
# =============================================================================

class TestDailyReportGeneration:
    """Test cases for daily report generation (REP-001)."""
    
    def test_daily_report_with_multiple_ideas(self, report_generator, mock_db, sample_ideas):
        """TC-001: Verify daily report correctly aggregates statistics."""
        # Setup: Seed database with 10 ideas from today, 5 from yesterday
        today = datetime(2026, 3, 2)
        yesterday = today - timedelta(days=1)
        
        # Mock database to return ideas
        mock_db.get_ideas_since.return_value = sample_ideas
        mock_db.get_ideas_for_date.return_value = sample_ideas[:5]  # Yesterday had 5
        
        # Execute
        report = report_generator.generate_daily_report(date=today)
        
        # Verify
        assert report.stats.total_ideas == 10
        assert report.stats.ideas_by_type["text"] == 6
        assert report.stats.ideas_by_type["voice"] == 2
        assert report.stats.ideas_by_type["screenshot"] == 2
        assert report.stats.trend_vs_previous == 100.0  # 10 vs 5 = +100%
        
    def test_daily_report_empty_day(self, report_generator, mock_db):
        """TC-007: Empty database graceful handling."""
        # Setup: Clear all ideas
        mock_db.get_ideas_since.return_value = []
        mock_db.get_ideas_for_date.return_value = []
        
        # Execute
        report = report_generator.generate_daily_report(date=datetime(2026, 3, 2))
        
        # Verify
        assert report.stats.total_ideas == 0
        assert "No new ideas today" in report.insights
        assert any("tip" in insight.lower() or "capture" in insight.lower() 
                   for insight in report.insights)


# =============================================================================
# TC-002: Discord format respects character limit
# =============================================================================

class TestPlatformFormatting:
    """Test cases for platform-specific formatting (REP-002)."""
    
    def test_discord_format_respects_character_limit(self, report_generator):
        """TC-002: Discord-formatted reports respect 2000 char limit."""
        # Setup: Create report with many suggestions
        report = Report(
            date=datetime(2026, 3, 2),
            type="daily",
            stats=ReportStats(
                total_ideas=50,
                ideas_by_type={"text": 30, "voice": 15, "screenshot": 5},
                top_tags=[("python", 20), ("devops", 15), ("tutorial", 10), 
                         ("advanced", 8), ("tips", 7)],
                trend_vs_previous=25.0
            ),
            suggestions=[
                Suggestion(
                    title=f"Suggestion {i}",
                    type="article",
                    confidence=0.8 + (i * 0.02),
                    related_idea_ids=[f"idea-{j}" for j in range(10)],
                    description=f"This is a very long description for suggestion {i} " * 5
                )
                for i in range(10)
            ],
            insights=["Insight 1", "Insight 2"]
        )
        
        # Execute
        formatted = report_generator.format_for_platform(report, platform="discord")
        
        # Verify
        assert len(formatted) <= 2000
        assert "📊" in formatted or "Stats" in formatted
        assert "..." in formatted or formatted.count("Suggestion") >= 3
        
    def test_telegram_format_respects_character_limit(self, report_generator):
        """Telegram-formatted reports respect 4096 char limit."""
        report = Report(
            date=datetime(2026, 3, 2),
            type="daily",
            stats=ReportStats(
                total_ideas=50,
                ideas_by_type={"text": 30, "voice": 15, "screenshot": 5},
                top_tags=[("python", 20)],
                trend_vs_previous=25.0
            ),
            suggestions=[],
            insights=[]
        )
        
        formatted = report_generator.format_for_platform(report, platform="telegram")
        
        assert len(formatted) <= 4096
        assert "<b>" in formatted or "📊" in formatted


# =============================================================================
# TC-003: Obsidian export creates valid markdown
# =============================================================================

class TestObsidianExport:
    """Test cases for Obsidian markdown export (REP-003)."""
    
    def test_obsidian_daily_export(self, report_generator, temp_vault):
        """TC-003: Obsidian export creates valid markdown with frontmatter."""
        # Setup
        report = Report(
            date=datetime(2026, 3, 2),
            type="daily",
            stats=ReportStats(
                total_ideas=12,
                ideas_by_type={"text": 7, "voice": 3, "screenshot": 2},
                top_tags=[("python", 5), ("devops", 3), ("tutorial", 2)],
                trend_vs_previous=50.0
            ),
            suggestions=[
                Suggestion(
                    title="Python Tips Series",
                    type="series",
                    confidence=0.92,
                    related_idea_ids=["idea-001", "idea-004", "idea-007"],
                    description="Create a weekly Python tips series"
                )
            ],
            insights=["Great progress!"]
        )
        
        # Execute
        export_path = report_generator.export_to_obsidian(report, str(temp_vault))
        
        # Verify
        expected_file = temp_vault / "Daily Notes" / "2026-03-02.md"
        assert Path(export_path) == expected_file
        assert expected_file.exists()
        
        content = expected_file.read_text()
        assert "---" in content  # YAML frontmatter
        assert "date: 2026-03-02" in content
        assert "type: daily-report" in content
        assert "[[idea-001]]" in content or "idea-001" in content  # Wiki links
        
    def test_obsidian_weekly_export(self, report_generator, temp_vault):
        """Weekly summary markdown export with aggregated data."""
        report = Report(
            date=datetime(2026, 2, 24),
            type="weekly",
            stats=ReportStats(
                total_ideas=35,
                ideas_by_type={"text": 20, "voice": 10, "screenshot": 5},
                top_tags=[("python", 12), ("devops", 8)],
                trend_vs_previous=25.0
            ),
            suggestions=[],
            insights=["Weekly highlight"]
        )
        
        export_path = report_generator.export_to_obsidian(report, str(temp_vault))
        
        expected_file = temp_vault / "Weekly Notes" / "2026-02-24.md"
        assert Path(export_path) == expected_file
        assert expected_file.exists()


# =============================================================================
# TC-004: Custom Jinja2 template rendering
# =============================================================================

class TestTemplateRendering:
    """Test cases for Jinja2 template rendering (REP-004)."""
    
    def test_default_template_rendering(self):
        """TC-004: Default template is used and rendered correctly."""
        engine = TemplateEngine()
        
        report = Report(
            date=datetime(2026, 3, 2),
            type="daily",
            stats=ReportStats(
                total_ideas=10,
                ideas_by_type={"text": 6, "voice": 2, "screenshot": 2},
                top_tags=[("python", 5), ("devops", 3)],
                trend_vs_previous=50.0
            ),
            suggestions=[],
            insights=[]
        )
        
        result = engine.render("daily_report", {"report": report})
        
        assert "daily" in result.lower() or "Daily" in result
        assert "10" in result
        
    def test_custom_template_rendering(self, tmp_path):
        """Custom template can be loaded and rendered with report data."""
        engine = TemplateEngine()
        
        # Create custom template
        template_dir = tmp_path / "templates"
        template_dir.mkdir()
        template_file = template_dir / "custom.j2"
        template_file.write_text("""
# {{ report.type }} Report
Ideas: {{ report.stats.total_ideas }}
{% for tag, count in report.stats.top_tags %}
- {{ tag }}: {{ count }}
{% endfor %}
""")
        
        report = Report(
            date=datetime(2026, 3, 2),
            type="daily",
            stats=ReportStats(
                total_ideas=10,
                ideas_by_type={},
                top_tags=[("python", 5), ("devops", 3)],
                trend_vs_previous=0.0
            ),
            suggestions=[],
            insights=[]
        )
        
        template = engine.load_template(str(template_file))
        result = engine.render_template(template, {"report": report})
        
        assert "daily Report" in result or "Report" in result
        assert "Ideas: 10" in result
        assert "python: 5" in result
        assert "devops: 3" in result
        
    def test_template_variable_access(self):
        """Template variables are replaced with actual report data."""
        engine = TemplateEngine()
        
        report = Report(
            date=datetime(2026, 3, 2),
            type="daily",
            stats=ReportStats(
                total_ideas=42,
                ideas_by_type={},
                top_tags=[("tag1", 10)],
                trend_vs_previous=15.5
            ),
            suggestions=[],
            insights=[]
        )
        
        template_str = "Total: {{ report.stats.total_ideas }}, Trend: {{ report.stats.trend_vs_previous }}%"
        result = engine.render_string(template_str, {"report": report})
        
        assert "Total: 42" in result
        assert "Trend: 15.5%" in result


# =============================================================================
# TC-005: Content suggestion confidence calculation
# =============================================================================

class TestContentSuggestions:
    """Test cases for content suggestions with confidence scores (REP-005)."""
    
    def test_suggestion_generation_with_confidence(self, report_generator, sample_clusters):
        """TC-005: Suggestions are generated with confidence scores."""
        # Execute
        suggestions = report_generator.generate_suggestions(sample_clusters)
        
        # Verify
        assert len(suggestions) >= 2
        
        # Find Python suggestion (strong cluster)
        python_suggestion = next(
            (s for s in suggestions if "python" in s.title.lower()), None
        )
        assert python_suggestion is not None
        assert python_suggestion.confidence >= 0.8
        assert len(python_suggestion.related_idea_ids) == 5
        
    def test_high_confidence_suggestion(self, report_generator):
        """Strong thematic cluster produces high confidence suggestion."""
        strong_cluster = Cluster(
            id="python-mastery",
            theme="Python",
            idea_ids=[f"idea-{i}" for i in range(8)],  # 8 ideas
            strength=8
        )
        
        suggestions = report_generator.generate_suggestions([strong_cluster])
        
        assert len(suggestions) == 1
        assert suggestions[0].confidence >= 0.8
        
    def test_low_confidence_filtering(self, report_generator):
        """Low confidence suggestions are excluded or marked as 'explore'."""
        weak_cluster = Cluster(
            id="weak-theme",
            theme="Misc",
            idea_ids=["idea-1", "idea-2"],  # Only 2 ideas
            strength=2
        )
        
        suggestions = report_generator.generate_suggestions([weak_cluster])
        
        # Either filtered out or has low confidence
        if suggestions:
            assert all(s.confidence < 0.5 or "explore" in s.title.lower() 
                      for s in suggestions)


# =============================================================================
# TC-006: Weekly summary aggregation
# =============================================================================

class TestWeeklySummary:
    """Test cases for weekly summary reports (REP-006)."""
    
    def test_weekly_summary_generation(self, report_generator, mock_db):
        """TC-006: Weekly summary correctly aggregates 7 days of data."""
        # Setup: 14 days of data
        week_start = datetime(2026, 2, 24)
        
        # Mock current week (35 ideas) and previous week (28 ideas)
        current_week_ideas = [Mock() for _ in range(35)]
        previous_week_ideas = [Mock() for _ in range(28)]
        
        mock_db.get_ideas_between.return_value = current_week_ideas
        mock_db.get_ideas_between.side_effect = [
            current_week_ideas,      # Current week
            previous_week_ideas      # Previous week
        ]
        
        # Execute
        report = report_generator.generate_weekly_report(week_start=week_start)
        
        # Verify
        assert report.stats.total_ideas == 35
        assert report.stats.trend_vs_previous == 25.0  # (35-28)/28 * 100
        assert len(report.insights) > 0
        
    def test_weekly_comparison(self, report_generator, mock_db):
        """Report includes week-over-week percentage changes."""
        week_start = datetime(2026, 2, 24)
        
        mock_db.get_ideas_between.side_effect = [
            [Mock() for _ in range(40)],  # Current week
            [Mock() for _ in range(32)]   # Previous week
        ]
        
        report = report_generator.generate_weekly_report(week_start=week_start)
        
        # 40 vs 32 = +25%
        assert report.stats.trend_vs_previous == 25.0


# =============================================================================
# TC-008: Template sandbox security
# =============================================================================

class TestTemplateSecurity:
    """Test cases for template security (REP-NF-005)."""
    
    def test_template_sandbox_security(self):
        """TC-008: Jinja2 templates run in sandboxed environment."""
        engine = TemplateEngine()
        
        # Attempt to use system command
        malicious_template = "{{ __import__('os').system('ls') }}"
        
        with pytest.raises((Exception,)) as exc_info:
            engine.render_string(malicious_template, {})
        
        # Should raise an error, not execute the command
        assert exc_info.value is not None
        
    def test_user_input_escaped(self):
        """User input is properly escaped in rendered output."""
        engine = TemplateEngine()
        
        template = "Hello {{ name }}"
        context = {"name": "<script>alert('xss')</script>"}
        
        result = engine.render_string(template, context)
        
        # Should escape HTML
        assert "<script>" not in result or "&lt;script&gt;" in result


# =============================================================================
# Data Structure Tests
# =============================================================================

class TestDataStructures:
    """Test report data structures."""
    
    def test_report_creation(self):
        """Report dataclass can be created with all fields."""
        report = Report(
            date=datetime(2026, 3, 2),
            type="daily",
            stats=ReportStats(
                total_ideas=10,
                ideas_by_type={"text": 6, "voice": 2, "screenshot": 2},
                top_tags=[("python", 5)],
                trend_vs_previous=50.0
            ),
            suggestions=[],
            insights=["Great day!"]
        )
        
        assert report.type == "daily"
        assert report.stats.total_ideas == 10
        
    def test_suggestion_creation(self):
        """Suggestion dataclass can be created with all fields."""
        suggestion = Suggestion(
            title="Test Series",
            type="series",
            confidence=0.85,
            related_idea_ids=["idea-1", "idea-2"],
            description="A test suggestion"
        )
        
        assert suggestion.confidence == 0.85
        assert len(suggestion.related_idea_ids) == 2


# =============================================================================
# Error Handling Tests
# =============================================================================

class TestErrorHandling:
    """Test error handling (REP-NF-002)."""
    
    def test_database_error_handling(self, report_generator, mock_db):
        """Graceful handling of database errors."""
        mock_db.get_ideas_since.side_effect = Exception("DB Connection Error")
        
        # Should not crash
        report = report_generator.generate_daily_report()
        
        assert report.stats.total_ideas == 0
        assert any("error" in insight.lower() for insight in report.insights)
        
    def test_template_error_handling(self):
        """Template syntax errors are caught and reported."""
        engine = TemplateEngine()
        
        invalid_template = "{{ unclosed"
        
        with pytest.raises(Exception):
            engine.render_string(invalid_template, {})


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
