"""
Report Templates

Pre-defined templates for different report styles and use cases.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field


@dataclass
class ReportTemplate:
    """Report template configuration."""
    name: str
    description: str
    sections: List[str]
    style: str  # "chat", "markdown", "minimal"
    max_length: Optional[int] = None
    include_drafts: bool = True
    include_connections: bool = True
    emoji_level: str = "high"  # none, low, high


class ReportTemplates:
    """Collection of report templates."""
    
    # Template definitions
    TEMPLATES: Dict[str, ReportTemplate] = {
        "default": ReportTemplate(
            name="default",
            description="Standard report with all sections",
            sections=["header", "stats", "tags", "suggestions", "connections", "drafts", "footer"],
            style="chat",
            max_length=2000,
            include_drafts=True,
            include_connections=True,
            emoji_level="high"
        ),
        
        "discord": ReportTemplate(
            name="discord",
            description="Optimized for Discord (2000 char limit)",
            sections=["header", "stats", "tags", "suggestions", "drafts", "footer"],
            style="chat",
            max_length=1900,  # Leave buffer for safety
            include_drafts=True,
            include_connections=False,  # Skip to save space
            emoji_level="high"
        ),
        
        "telegram": ReportTemplate(
            name="telegram",
            description="Optimized for Telegram (4096 char limit)",
            sections=["header", "stats", "tags", "suggestions", "connections", "drafts", "footer"],
            style="chat",
            max_length=4000,
            include_drafts=True,
            include_connections=True,
            emoji_level="high"
        ),
        
        "minimal": ReportTemplate(
            name="minimal",
            description="Quick summary only",
            sections=["header", "stats", "tags", "footer"],
            style="chat",
            max_length=500,
            include_drafts=False,
            include_connections=False,
            emoji_level="low"
        ),
        
        "obsidian": ReportTemplate(
            name="obsidian",
            description="Full Markdown for Obsidian vault",
            sections=["frontmatter", "header", "toc", "stats", "tags", "suggestions", "connections", "drafts", "trends", "footer"],
            style="markdown",
            max_length=None,
            include_drafts=True,
            include_connections=True,
            emoji_level="low"
        ),
        
        "weekly_digest": ReportTemplate(
            name="weekly_digest",
            description="Weekly summary with highlights",
            sections=["header", "stats", "tags", "connections", "suggestions", "footer"],
            style="chat",
            max_length=2500,
            include_drafts=False,
            include_connections=True,
            emoji_level="high"
        ),
        
        "executive": ReportTemplate(
            name="executive",
            description="Executive summary (no emojis, professional)",
            sections=["header", "stats", "suggestions", "footer"],
            style="chat",
            max_length=1000,
            include_drafts=False,
            include_connections=False,
            emoji_level="none"
        )
    }
    
    @classmethod
    def get(cls, name: str) -> ReportTemplate:
        """
        Get a template by name.
        
        Args:
            name: Template name
            
        Returns:
            ReportTemplate instance
            
        Raises:
            ValueError: If template not found
        """
        if name not in cls.TEMPLATES:
            available = ", ".join(cls.TEMPLATES.keys())
            raise ValueError(f"Template '{name}' not found. Available: {available}")
        
        return cls.TEMPLATES[name]
    
    @classmethod
    def list_templates(cls) -> List[Dict[str, str]]:
        """
        List all available templates.
        
        Returns:
            List of template info dictionaries
        """
        return [
            {
                "name": t.name,
                "description": t.description,
                "style": t.style,
                "max_length": str(t.max_length) if t.max_length else "unlimited"
            }
            for t in cls.TEMPLATES.values()
        ]
    
    @classmethod
    def create_custom(
        cls,
        name: str,
        description: str,
        sections: List[str],
        style: str = "chat",
        max_length: Optional[int] = None,
        include_drafts: bool = True,
        include_connections: bool = True,
        emoji_level: str = "high"
    ) -> ReportTemplate:
        """
        Create a custom template.
        
        Args:
            name: Template name
            description: Template description
            sections: List of section names to include
            style: Output style (chat, markdown, minimal)
            max_length: Maximum output length
            include_drafts: Whether to include quick drafts
            include_connections: Whether to include connections
            emoji_level: Emoji density (none, low, high)
            
        Returns:
            New ReportTemplate instance
        """
        return ReportTemplate(
            name=name,
            description=description,
            sections=sections,
            style=style,
            max_length=max_length,
            include_drafts=include_drafts,
            include_connections=include_connections,
            emoji_level=emoji_level
        )
    
    # Section templates for quick reference
    SECTION_TEMPLATES = {
        "header": {
            "chat": "📊 **{period} Inspiration Report** ✨\n*{date}*",
            "markdown": "# {period} Inspiration Report\n\n**Date:** {date}"
        },
        
        "stats_compact": {
            "chat": "✨ {new} new • 📦 {total} total",
            "markdown": "| New | Total |\n|-----|-------|\n| {new} | {total} |"
        },
        
        "tag_badge": {
            "chat": "#{tag} ({count})",
            "markdown": "`#{tag}` ({count})"
        },
        
        "suggestion_card": {
            "chat": "{confidence} {message}\n   → {action}",
            "markdown": "### {type} ({confidence})\n\n{message}\n\n**Action:** {action}"
        },
        
        "connection_card": {
            "chat": "🔗 **{theme}** ({count} ideas)\n   {insight}",
            "markdown": "### {theme}\n\n{insight}\n\n**Ideas:** {count}"
        },
        
        "draft_preview": {
            "chat": "📝 **{platform}**\n   \"{preview}...\"",
            "markdown": "### {platform}\n\n```\n{content}\n```"
        }
    }
    
    @classmethod
    def get_section_template(cls, section: str, style: str = "chat") -> str:
        """
        Get a section template string.
        
        Args:
            section: Section name
            style: Output style
            
        Returns:
            Template string
        """
        templates = cls.SECTION_TEMPLATES.get(section, {})
        return templates.get(style, templates.get("chat", ""))
    
    # Emoji sets for different contexts
    EMOJI_SETS = {
        "high": {
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
            "voice": "🎤",
            "screenshot": "📸",
            "manual": "✏️"
        },
        
        "low": {
            "report": "📋",
            "stats": "📊",
            "tags": "#",
            "suggestion": "→",
            "connection": "•",
            "draft": "✎",
            "trend": "~",
            "idea": "•",
            "new": "+",
            "total": "=",
            "star": "*",
            "fire": "!",
            "rocket": "↑",
            "target": "◎",
            "warning": "!",
            "check": "✓",
            "calendar": "📅",
            "twitter": "T",
            "linkedin": "L",
            "blog": "B",
            "voice": "V",
            "screenshot": "S",
            "manual": "M"
        },
        
        "none": {
            "report": "",
            "stats": "",
            "tags": "",
            "suggestion": "",
            "connection": "",
            "draft": "",
            "trend": "",
            "idea": "",
            "new": "",
            "total": "",
            "star": "",
            "fire": "",
            "rocket": "",
            "target": "",
            "warning": "",
            "check": "",
            "calendar": "",
            "twitter": "",
            "linkedin": "",
            "blog": "",
            "voice": "",
            "screenshot": "",
            "manual": ""
        }
    }
    
    @classmethod
    def get_emoji_set(cls, level: str = "high") -> Dict[str, str]:
        """
        Get an emoji set by level.
        
        Args:
            level: Emoji level (high, low, none)
            
        Returns:
            Dictionary of emoji mappings
        """
        return cls.EMOJI_SETS.get(level, cls.EMOJI_SETS["high"])


# Pre-built message templates for common use cases
MESSAGE_TEMPLATES = {
    "daily_summary": """📊 **Daily Inspiration Report** ✨
*{date}*

📈 **Quick Stats**
✨ New ideas: {new_ideas}
📦 Total ideas: {total_ideas}

🏷️ **Top Tags**
{top_tags}

💡 **Top Suggestion**
{suggestion}

🚀 Keep creating!""",

    "weekly_digest": """📊 **Weekly Inspiration Digest** ✨
*{week_range}*

📈 **This Week**
✨ New ideas: {new_ideas}
📦 Total ideas: {total_ideas}
🎯 Conversion rate: {conversion_rate}%

🏷️ **Trending Tags**
{top_tags}

🔗 **Connection Spotlight**
{connection}

Keep up the momentum! 🚀""",

    "milestone_celebration": """🎉 **Milestone Reached!** 🎉

You've captured **{milestone}** content ideas!

🏷️ Top themes: {top_tags}
📈 Most productive day: {best_day}

Here's to the next {milestone}! 🥂""",

    "streak_reminder": """🔥 **Idea Streak: {streak} days!**

Don't break the chain! Capture an idea today to keep your streak alive.

💡 Quick prompt: {prompt}

You've got this! 💪"""
}


def get_message_template(name: str) -> str:
    """
    Get a pre-built message template.
    
    Args:
        name: Template name
        
    Returns:
        Template string
    """
    return MESSAGE_TEMPLATES.get(name, "")


def format_template(template: str, **kwargs) -> str:
    """
    Format a template with provided values.
    
    Args:
        template: Template string
        **kwargs: Values to substitute
        
    Returns:
        Formatted string
    """
    try:
        return template.format(**kwargs)
    except KeyError as e:
        # Return template with missing keys marked
        return template + f"\n\n[Missing: {e}]"
