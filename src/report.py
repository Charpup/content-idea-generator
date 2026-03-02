"""
Content Idea Generator - Report Generator

Generates daily/weekly reports with statistics and suggestions.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from collections import Counter


@dataclass
class ReportStats:
    """Statistics for a report period"""
    total_ideas: int = 0
    new_ideas_today: int = 0
    text_inputs: int = 0
    voice_inputs: int = 0
    screenshot_inputs: int = 0
    top_tags: List[tuple] = None
    trend_vs_yesterday: float = 0.0
    
    def __post_init__(self):
        if self.top_tags is None:
            self.top_tags = []


@dataclass
class Suggestion:
    """Content suggestion"""
    title: str = ""
    description: str = ""
    confidence: float = 0.0
    related_ideas: List[str] = None
    suggested_tags: List[str] = None
    
    def __post_init__(self):
        if self.related_ideas is None:
            self.related_ideas = []
        if self.suggested_tags is None:
            self.suggested_tags = []


@dataclass
class Idea:
    """Idea data class"""
    id: str = ""
    title: str = ""
    content: str = ""
    tags: List[str] = None
    created_at: Optional[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []


@dataclass
class Cluster:
    """Cluster data class"""
    id: int = 0
    ideas: List[Idea] = None
    keywords: List[str] = None
    
    def __post_init__(self):
        if self.ideas is None:
            self.ideas = []
        if self.keywords is None:
            self.keywords = []


@dataclass
class Report:
    """Report data class"""
    date: str = ""
    period: str = "daily"
    stats: ReportStats = None
    suggestions: List[Suggestion] = None
    highlights: List[str] = None
    
    def __post_init__(self):
        if self.stats is None:
            self.stats = ReportStats()
        if self.suggestions is None:
            self.suggestions = []
        if self.highlights is None:
            self.highlights = []


class TemplateEngine:
    """Template engine for report rendering"""
    
    def __init__(self, template_dir: Optional[str] = None):
        self.template_dir = template_dir or "templates"
        self.templates: Dict[str, str] = {}
    
    def load_template(self, name: str) -> str:
        """Load a template by name"""
        return self.templates.get(name, "")
    
    def render(self, template_name: str, context: Dict) -> str:
        """Render a template with context"""
        template = self.load_template(template_name)
        # Simple string replacement for now
        for key, value in context.items():
            template = template.replace(f"{{{{ {key} }}}}", str(value))
        return template


class ReportGenerator:
    """Generates formatted reports for content ideas"""
    
    def __init__(self, timezone: str = 'UTC'):
        self.timezone = timezone
        self.template_engine = TemplateEngine()
        
    def generate_daily_report(self, ideas: List[Dict], suggestions: List[Suggestion] = None, date: Optional[str] = None) -> Report:
        """Generate daily report"""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        if suggestions is None:
            suggestions = []
            
        # Calculate stats
        today = datetime.strptime(date, '%Y-%m-%d')
        yesterday = today - timedelta(days=1)
        
        today_ideas = [i for i in ideas if i.get('created_at', '').startswith(date)]
        yesterday_ideas = [i for i in ideas if i.get('created_at', '').startswith(yesterday.strftime('%Y-%m-%d'))]
        
        # Count input types
        text_count = sum(1 for i in today_ideas if i.get('input_type') == 'text')
        voice_count = sum(1 for i in today_ideas if i.get('input_type') == 'voice')
        screenshot_count = sum(1 for i in today_ideas if i.get('input_type') == 'screenshot')
        
        # Top tags
        all_tags = []
        for idea in today_ideas:
            all_tags.extend(idea.get('tags', []))
        top_tags = Counter(all_tags).most_common(5)
        
        # Trend calculation
        trend = 0.0
        if yesterday_ideas:
            trend = ((len(today_ideas) - len(yesterday_ideas)) / len(yesterday_ideas)) * 100
            
        stats = ReportStats(
            total_ideas=len(ideas),
            new_ideas_today=len(today_ideas),
            text_inputs=text_count,
            voice_inputs=voice_count,
            screenshot_inputs=screenshot_count,
            top_tags=top_tags,
            trend_vs_yesterday=trend
        )
        
        return Report(
            date=date,
            period='daily',
            stats=stats,
            suggestions=suggestions,
            highlights=[]
        )
    
    def format_for_discord(self, report: Report) -> str:
        """Format report for Discord (2000 char limit)"""
        lines = [
            f"📊 **Daily Inspiration Report - {report.date}**",
            "",
            f"📈 **Stats:**",
            f"• {report.stats.new_ideas_today} new ideas today",
            f"• {report.stats.text_inputs} text, {report.stats.voice_inputs} voice, {report.stats.screenshot_inputs} screenshot",
        ]
        
        if report.stats.top_tags:
            top_tags_str = ", ".join([f"#{tag} ({count})" for tag, count in report.stats.top_tags[:3]])
            lines.append(f"• Top tags: {top_tags_str}")
            
        if report.stats.trend_vs_yesterday != 0:
            trend_emoji = "📈" if report.stats.trend_vs_yesterday > 0 else "📉"
            lines.append(f"• {trend_emoji} {abs(report.stats.trend_vs_yesterday):.1f}% vs yesterday")
            
        lines.append("")
        
        if report.suggestions:
            lines.append("💡 **Suggestions:**")
            for i, sug in enumerate(report.suggestions[:3], 1):
                confidence_emoji = "🟢" if sug.confidence >= 0.7 else "🟡" if sug.confidence >= 0.5 else "🔴"
                lines.append(f"{i}. {confidence_emoji} {sug.title} ({sug.confidence*100:.0f}%)")
        else:
            lines.append("💡 No suggestions today. Keep capturing ideas!")
            
        return "\n".join(lines)
    
    def format_for_telegram(self, report: Report) -> str:
        """Format report for Telegram (HTML)"""
        lines = [
            f"📊 <b>Daily Inspiration Report - {report.date}</b>",
            "",
            f"📈 <b>Stats:</b>",
            f"• {report.stats.new_ideas_today} new ideas today",
            f"• {report.stats.text_inputs} text, {report.stats.voice_inputs} voice, {report.stats.screenshot_inputs} screenshot",
        ]
        
        if report.stats.top_tags:
            top_tags_str = ", ".join([f"#{tag}" for tag, count in report.stats.top_tags[:3]])
            lines.append(f"• Top tags: {top_tags_str}")
            
        lines.append("")
        
        if report.suggestions:
            lines.append("💡 <b>Suggestions:</b>")
            for i, sug in enumerate(report.suggestions[:3], 1):
                lines.append(f"{i}. {sug.title}")
        
        return "\n".join(lines)
    
    def export_to_obsidian(self, report: Report) -> str:
        """Export report to Obsidian Markdown format"""
        lines = [
            "---",
            f"date: {report.date}",
            f"type: {report.period}-report",
            f"total_ideas: {report.stats.total_ideas}",
            f"new_ideas: {report.stats.new_ideas_today}",
            "---",
            "",
            f"# {report.period.title()} Report - {report.date}",
            "",
            "## Statistics",
            "",
            f"- **New Ideas**: {report.stats.new_ideas_today}",
            f"- **Text Inputs**: {report.stats.text_inputs}",
            f"- **Voice Inputs**: {report.stats.voice_inputs}",
            f"- **Screenshot Inputs**: {report.stats.screenshot_inputs}",
            "",
        ]
        
        if report.stats.top_tags:
            lines.append("### Top Tags")
            lines.append("")
            for tag, count in report.stats.top_tags:
                lines.append(f"- #{tag}: {count}")
            lines.append("")
            
        if report.suggestions:
            lines.append("## Content Suggestions")
            lines.append("")
            for sug in report.suggestions:
                lines.append(f"### {sug.title}")
                lines.append(f"- Confidence: {sug.confidence*100:.0f}%")
                lines.append(f"- Description: {sug.description}")
                if sug.suggested_tags:
                    lines.append(f"- Tags: {', '.join(sug.suggested_tags)}")
                lines.append("")
                
        return "\n".join(lines)
    
    def generate_weekly_report(self, ideas: List[Dict], suggestions: List[Suggestion] = None, week_start: Optional[str] = None) -> Report:
        """Generate weekly summary report"""
        if week_start is None:
            # Get start of current week (Monday)
            today = datetime.now()
            week_start = (today - timedelta(days=today.weekday())).strftime('%Y-%m-%d')
        if suggestions is None:
            suggestions = []
            
        week_end = (datetime.strptime(week_start, '%Y-%m-%d') + timedelta(days=6)).strftime('%Y-%m-%d')
        
        # Filter ideas for the week
        week_ideas = []
        for idea in ideas:
            created = idea.get('created_at', '')
            if week_start <= created <= week_end:
                week_ideas.append(idea)
        
        # Calculate weekly stats
        text_count = sum(1 for i in week_ideas if i.get('input_type') == 'text')
        voice_count = sum(1 for i in week_ideas if i.get('input_type') == 'voice')
        screenshot_count = sum(1 for i in week_ideas if i.get('input_type') == 'screenshot')
        
        # Top tags for the week
        all_tags = []
        for idea in week_ideas:
            all_tags.extend(idea.get('tags', []))
        top_tags = Counter(all_tags).most_common(10)
        
        stats = ReportStats(
            total_ideas=len(ideas),
            new_ideas_today=len(week_ideas),
            text_inputs=text_count,
            voice_inputs=voice_count,
            screenshot_inputs=screenshot_count,
            top_tags=top_tags,
            trend_vs_yesterday=0.0
        )
        
        return Report(
            date=week_start,
            period='weekly',
            stats=stats,
            suggestions=suggestions,
            highlights=[]
        )
