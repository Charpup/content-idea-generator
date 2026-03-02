"""
Formatters for inspiration reports

Supports chat-optimized formatting (Discord/Telegram) and Markdown export.
"""

from datetime import datetime
from typing import Dict, List, Any, Optional
from .daily import InspirationReport, ReportPeriod, ReportStats, ContentSuggestion


class ChatFormatter:
    """
    Format reports for chat platforms (Discord, Telegram).
    
    Uses emojis, short paragraphs, and compact formatting
    optimized for mobile chat consumption.
    """
    
    # Emoji mappings
    EMOJI = {
        "report": "📊",
        "stats": "📈",
        "tags": "🏷️",
        "suggestion": "💡",
        "connection": "🔗",
        "draft": "📝",
        "trend": "📉",
        "idea": "💭",
        "new": "✨",
        "total": "📦",
        "star": "⭐",
        "fire": "🔥",
        "rocket": "🚀",
        "target": "🎯",
        "warning": "⚡",
        "check": "✅",
        "calendar": "📅",
        "twitter": "🐦",
        "linkedin": "💼",
        "blog": "📄",
        "sparkles": "✨"
    }
    
    def __init__(self, max_length: int = 2000):
        """
        Initialize formatter.
        
        Args:
            max_length: Maximum message length (Discord: 2000, Telegram: 4096)
        """
        self.max_length = max_length
    
    def format(self, report: InspirationReport) -> str:
        """
        Format complete report for chat.
        
        Args:
            report: The inspiration report to format
            
        Returns:
            Formatted string ready for chat
        """
        sections = []
        
        # Header
        sections.append(self._format_header(report))
        
        # Quick Stats
        sections.append(self._format_stats(report.stats))
        
        # Top Tags & Categories
        sections.append(self._format_tags(report.top_tags, report.top_categories))
        
        # Suggestions
        if report.suggestions:
            sections.append(self._format_suggestions(report.suggestions))
        
        # Connections
        if report.connections:
            sections.append(self._format_connections(report.connections))
        
        # Quick Drafts
        if report.quick_drafts:
            sections.append(self._format_quick_drafts(report.quick_drafts))
        
        # Footer
        sections.append(self._format_footer(report))
        
        # Join with double newlines for spacing
        result = "\n\n".join(sections)
        
        # Truncate if too long
        if len(result) > self.max_length:
            result = result[:self.max_length - 20] + "\n\n... (truncated)"
        
        return result
    
    def _format_header(self, report: InspirationReport) -> str:
        """Format report header."""
        e = self.EMOJI
        
        period_name = {
            ReportPeriod.DAILY: "Daily",
            ReportPeriod.WEEKLY: "Weekly", 
            ReportPeriod.MONTHLY: "Monthly"
        }.get(report.period, "Daily")
        
        date_str = report.end_date.strftime("%b %d, %Y")
        
        return f"{e['report']} **{period_name} Inspiration Report** {e['sparkles']}\n*{date_str}*"
    
    def _format_stats(self, stats: ReportStats) -> str:
        """Format statistics section."""
        e = self.EMOJI
        
        lines = [f"{e['stats']} **Quick Stats**"]
        lines.append(f"{e['new']} New ideas: {stats.new_ideas}")
        lines.append(f"{e['total']} Total ideas: {stats.total_ideas}")
        
        if stats.by_source:
            source_emoji = {"voice": "🎤", "screenshot": "📸", "manual": "✏️"}
            source_parts = []
            for source, count in sorted(stats.by_source.items(), key=lambda x: -x[1]):
                emoji = source_emoji.get(source, "📌")
                source_parts.append(f"{emoji} {source}: {count}")
            if source_parts:
                lines.append(f"{e['idea']} By source: {' | '.join(source_parts)}")
        
        if stats.avg_confidence > 0:
            confidence_emoji = "🎯" if stats.avg_confidence > 0.8 else "📍"
            lines.append(f"{confidence_emoji} Avg confidence: {stats.avg_confidence:.0%}")
        
        return "\n".join(lines)
    
    def _format_tags(
        self, 
        top_tags: List[Any], 
        top_categories: List[Any]
    ) -> str:
        """Format tags and categories section."""
        e = self.EMOJI
        
        lines = [f"{e['tags']} **Top Tags**"]
        
        if top_tags:
            tag_parts = []
            for tag_stat in top_tags[:5]:
                trend = tag_stat.trend if hasattr(tag_stat, 'trend') else "→"
                tag_parts.append(f"#{tag_stat.tag} ({tag_stat.count}) {trend}")
            lines.append(" ".join(tag_parts))
        else:
            lines.append("No tags yet — start adding some! 🏷️")
        
        if top_categories:
            lines.append(f"\n{e['star']} **Top Categories**")
            cat_parts = []
            for cat in top_categories[:3]:
                cat_parts.append(f"{cat.tag} ({cat.count})")
            lines.append(" • ".join(cat_parts))
        
        return "\n".join(lines)
    
    def _format_suggestions(self, suggestions: List[ContentSuggestion]) -> str:
        """Format suggestions section."""
        e = self.EMOJI
        
        lines = [f"{e['suggestion']} **Content Suggestions**"]
        
        for i, suggestion in enumerate(suggestions[:3], 1):
            # Confidence indicator
            if suggestion.confidence >= 0.8:
                conf_indicator = "🟢"
            elif suggestion.confidence >= 0.6:
                conf_indicator = "🟡"
            else:
                conf_indicator = "🔴"
            
            lines.append(f"\n{i}. {conf_indicator} {suggestion.message}")
            
            # Add action items if available
            if suggestion.action_items:
                for action in suggestion.action_items[:2]:
                    lines.append(f"   → {action}")
        
        return "\n".join(lines)
    
    def _format_connections(self, connections: List[Any]) -> str:
        """Format connection spotlight section."""
        e = self.EMOJI
        
        lines = [f"{e['connection']} **Connection Spotlight**"]
        
        for conn in connections[:2]:
            lines.append(f"\n🔹 **{conn.theme.title()}** ({len(conn.ideas)} ideas)")
            lines.append(f"   {conn.insight}")
            if conn.suggested_series:
                lines.append(f"   💡 Series idea: *{conn.suggested_series}*")
        
        return "\n".join(lines)
    
    def _format_quick_drafts(self, drafts: List[Any]) -> str:
        """Format quick drafts section."""
        e = self.EMOJI
        
        lines = [f"{e['draft']} **Quick Drafts**"]
        lines.append("Ready-to-use content snippets:\n")
        
        platform_emoji = {
            "twitter": e['twitter'],
            "linkedin": e['linkedin'],
            "blog": e['blog']
        }
        
        for draft in drafts[:3]:
            emoji = platform_emoji.get(draft.platform, "📝")
            engagement = "🔥" if draft.estimated_engagement == "high" else "📊"
            
            lines.append(f"{emoji} **{draft.platform.title()}** {engagement}")
            
            # Truncate content for chat
            content = draft.content[:150] + "..." if len(draft.content) > 150 else draft.content
            # Escape markdown
            content = content.replace("*", "\\*").replace("_", "\\_")
            lines.append(f"   \"{content}\"")
        
        return "\n".join(lines)
    
    def _format_footer(self, report: InspirationReport) -> str:
        """Format report footer."""
        e = self.EMOJI
        
        time_str = report.generated_at.strftime("%H:%M")
        return f"{e['calendar']} Generated at {time_str} • Keep creating! {e['rocket']}"
    
    def format_compact(self, report: InspirationReport) -> str:
        """
        Format a compact version for quick overview.
        
        Args:
            report: The inspiration report
            
        Returns:
            Compact formatted string
        """
        e = self.EMOJI
        
        lines = [
            f"{e['report']} **Daily Summary**",
            f"{e['new']} {report.stats.new_ideas} new • {e['total']} {report.stats.total_ideas} total"
        ]
        
        if report.top_tags:
            tags_str = " ".join([f"#{t.tag}" for t in report.top_tags[:3]])
            lines.append(f"{e['tags']} {tags_str}")
        
        if report.suggestions:
            top_suggestion = report.suggestions[0]
            lines.append(f"{e['suggestion']} {top_suggestion.message[:80]}...")
        
        return "\n".join(lines)


class MarkdownFormatter:
    """
    Format reports as Markdown for Obsidian and other Markdown tools.
    
    Creates well-structured Markdown with frontmatter, headings,
    and Obsidian-compatible formatting.
    """
    
    def __init__(self, include_frontmatter: bool = True):
        """
        Initialize formatter.
        
        Args:
            include_frontmatter: Whether to include YAML frontmatter
        """
        self.include_frontmatter = include_frontmatter
    
    def format(self, report: InspirationReport) -> str:
        """
        Format complete report as Markdown.
        
        Args:
            report: The inspiration report to format
            
        Returns:
            Markdown formatted string
        """
        sections = []
        
        # Frontmatter
        if self.include_frontmatter:
            sections.append(self._format_frontmatter(report))
        
        # Header
        sections.append(self._format_header(report))
        
        # Table of Contents
        sections.append(self._format_toc())
        
        # Quick Stats
        sections.append(self._format_stats(report.stats))
        
        # Top Tags & Categories
        sections.append(self._format_tags(report.top_tags, report.top_categories))
        
        # Suggestions
        if report.suggestions:
            sections.append(self._format_suggestions(report.suggestions))
        
        # Connections
        if report.connections:
            sections.append(self._format_connections(report.connections))
        
        # Quick Drafts
        if report.quick_drafts:
            sections.append(self._format_quick_drafts(report.quick_drafts))
        
        # Trends
        if report.trends:
            sections.append(self._format_trends(report.trends))
        
        # Footer
        sections.append(self._format_footer(report))
        
        return "\n\n".join(sections)
    
    def _format_frontmatter(self, report: InspirationReport) -> str:
        """Format YAML frontmatter for Obsidian."""
        period_str = report.period.value
        date_str = report.end_date.strftime("%Y-%m-%d")
        
        frontmatter = f"""---
title: "{period_str.title()} Inspiration Report - {date_str}"
date: {report.generated_at.isoformat()}
period: {period_str}
tags:
  - content-ideas
  - report
  - {period_str}
total_ideas: {report.stats.total_ideas}
new_ideas: {report.stats.new_ideas}
---"""
        
        return frontmatter
    
    def _format_header(self, report: InspirationReport) -> str:
        """Format report header."""
        period_name = {
            ReportPeriod.DAILY: "Daily",
            ReportPeriod.WEEKLY: "Weekly", 
            ReportPeriod.MONTHLY: "Monthly"
        }.get(report.period, "Daily")
        
        date_str = report.end_date.strftime("%B %d, %Y")
        period_range = f"{report.start_date.strftime('%b %d')} - {report.end_date.strftime('%b %d, %Y')}"
        
        return f"# {period_name} Inspiration Report\n\n**Period:** {period_range}\n**Generated:** {report.generated_at.strftime('%Y-%m-%d %H:%M')}"
    
    def _format_toc(self) -> str:
        """Format table of contents."""
        return """## Table of Contents

- [[#Quick Stats|Quick Stats]]
- [[#Top Tags & Categories|Top Tags & Categories]]
- [[#Content Suggestions|Content Suggestions]]
- [[#Connection Spotlight|Connection Spotlight]]
- [[#Quick Drafts|Quick Drafts]]
- [[#Trends|Trends]]"""
    
    def _format_stats(self, stats: ReportStats) -> str:
        """Format statistics section."""
        lines = ["## Quick Stats\n"]
        
        # Summary table
        lines.append("| Metric | Value |")
        lines.append("|--------|-------|")
        lines.append(f"| New Ideas | {stats.new_ideas} |")
        lines.append(f"| Total Ideas | {stats.total_ideas} |")
        
        if stats.avg_confidence > 0:
            lines.append(f"| Avg Confidence | {stats.avg_confidence:.0%} |")
        
        lines.append("")
        
        # By source
        if stats.by_source:
            lines.append("### By Source\n")
            for source, count in sorted(stats.by_source.items(), key=lambda x: -x[1]):
                lines.append(f"- **{source.title()}:** {count}")
            lines.append("")
        
        # By status
        if stats.by_status:
            lines.append("### By Status\n")
            for status, count in sorted(stats.by_status.items(), key=lambda x: -x[1]):
                lines.append(f"- **{status.title()}:** {count}")
            lines.append("")
        
        return "\n".join(lines)
    
    def _format_tags(
        self, 
        top_tags: List[Any], 
        top_categories: List[Any]
    ) -> str:
        """Format tags and categories section."""
        lines = ["## Top Tags & Categories\n"]
        
        # Tags
        lines.append("### Top Tags\n")
        if top_tags:
            lines.append("| Tag | Count | Trend |")
            lines.append("|-----|-------|-------|")
            for tag in top_tags:
                trend = tag.trend if hasattr(tag, 'trend') else "→"
                lines.append(f"| #{tag.tag} | {tag.count} | {trend} |")
        else:
            lines.append("*No tags recorded yet*")
        lines.append("")
        
        # Categories
        if top_categories:
            lines.append("### Top Categories\n")
            lines.append("| Category | Count |")
            lines.append("|----------|-------|")
            for cat in top_categories:
                lines.append(f"| {cat.tag} | {cat.count} |")
            lines.append("")
        
        return "\n".join(lines)
    
    def _format_suggestions(self, suggestions: List[ContentSuggestion]) -> str:
        """Format suggestions section."""
        lines = ["## Content Suggestions\n"]
        
        for i, suggestion in enumerate(suggestions, 1):
            # Confidence badge
            if suggestion.confidence >= 0.8:
                badge = "🟢 High"
            elif suggestion.confidence >= 0.6:
                badge = "🟡 Medium"
            else:
                badge = "🔴 Low"
            
            lines.append(f"### {i}. {suggestion.type.title()} ({badge} Confidence)\n")
            lines.append(f"{suggestion.message}\n")
            
            if suggestion.related_ideas:
                lines.append("**Related Ideas:**")
                for idea_id in suggestion.related_ideas:
                    lines.append(f"- `[[{idea_id}]]`")
                lines.append("")
            
            if suggestion.action_items:
                lines.append("**Action Items:**")
                for action in suggestion.action_items:
                    lines.append(f"- [ ] {action}")
                lines.append("")
        
        return "\n".join(lines)
    
    def _format_connections(self, connections: List[Any]) -> str:
        """Format connection spotlight section."""
        lines = ["## Connection Spotlight\n"]
        lines.append("Discover hidden connections between your ideas:\n")
        
        for conn in connections:
            lines.append(f"### {conn.theme.title()}\n")
            lines.append(f"{conn.insight}\n")
            lines.append(f"**Connected Ideas:** {len(conn.ideas)}")
            for idea_id in conn.ideas:
                lines.append(f"- `[[{idea_id}]]`")
            
            if conn.suggested_series:
                lines.append(f"\n💡 **Series Idea:** *{conn.suggested_series}*")
            lines.append("")
        
        return "\n".join(lines)
    
    def _format_quick_drafts(self, drafts: List[Any]) -> str:
        """Format quick drafts section."""
        lines = ["## Quick Drafts\n"]
        lines.append("Ready-to-use content for your favorite platforms:\n")
        
        platform_icons = {
            "twitter": "🐦",
            "linkedin": "💼",
            "blog": "📄"
        }
        
        for draft in drafts:
            icon = platform_icons.get(draft.platform, "📝")
            engagement = draft.estimated_engagement.title()
            
            lines.append(f"### {icon} {draft.platform.title()} ({engagement} Engagement)\n")
            lines.append(f"**Title:** {draft.title}\n")
            
            lines.append("**Content:**")
            lines.append("```")
            lines.append(draft.content)
            lines.append("```\n")
            
            if draft.hashtags:
                lines.append(f"**Hashtags:** {' '.join(draft.hashtags)}\n")
        
        return "\n".join(lines)
    
    def _format_trends(self, trends: Dict[str, Any]) -> str:
        """Format trends section."""
        lines = ["## Trends\n"]
        
        if "ideas_per_day" in trends:
            lines.append("### Ideas Per Day\n")
            lines.append(f"```\n{trends['ideas_per_day']}\n```\n")
        
        if "most_productive_day" in trends and trends["most_productive_day"]:
            lines.append(f"**Most Productive Day:** {trends['most_productive_day']} ({trends.get('most_productive_count', 0)} ideas)\n")
        
        if "source_distribution_pct" in trends:
            lines.append("\n### Source Distribution\n")
            for source, pct in trends["source_distribution_pct"].items():
                lines.append(f"- {source.title()}: {pct}%")
            lines.append("")
        
        return "\n".join(lines)
    
    def _format_footer(self, report: InspirationReport) -> str:
        """Format report footer."""
        return """---

*Generated by Content Idea Generator*  
*Keep creating amazing content! 🚀*"""
    
    def save_to_file(
        self, 
        report: InspirationReport, 
        filepath: str,
        obsidian_vault_path: Optional[str] = None
    ) -> str:
        """
        Save formatted report to a Markdown file.
        
        Args:
            report: The inspiration report
            filepath: Path to save the file
            obsidian_vault_path: Optional Obsidian vault path for wiki links
            
        Returns:
            Absolute path to the saved file
        """
        import os
        
        content = self.format(report)
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return os.path.abspath(filepath)
