"""
Chat Interaction Module for Content Idea Generator Skill

Handles commands and responses for chat platforms.
"""

import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum


class CommandType(Enum):
    """Available commands."""
    CAPTURE = "capture"
    VOICE = "voice"
    SCREENSHOT = "screenshot"
    SEARCH = "search"
    REPORT = "report"
    HELP = "help"
    UNKNOWN = "unknown"


@dataclass
class Command:
    """Parsed command from user input."""
    type: CommandType
    args: str
    raw: str


class ChatHandler:
    """Handle chat interactions."""
    
    COMMAND_PREFIXES = ["/", "!", "."]
    
    @classmethod
    def parse_command(cls, message: str) -> Command:
        """Parse command from message."""
        message = message.strip()
        
        # Check if it's a command
        if not any(message.startswith(p) for p in cls.COMMAND_PREFIXES):
            # Natural language fallback
            return cls._parse_natural_language(message)
        
        # Extract command and args
        parts = message[1:].split(maxsplit=1)
        cmd = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""
        
        # Map to command type
        cmd_map = {
            "capture": CommandType.CAPTURE,
            "c": CommandType.CAPTURE,
            "voice": CommandType.VOICE,
            "v": CommandType.VOICE,
            "screenshot": CommandType.SCREENSHOT,
            "ss": CommandType.SCREENSHOT,
            "search": CommandType.SEARCH,
            "s": CommandType.SEARCH,
            "report": CommandType.REPORT,
            "r": CommandType.REPORT,
            "help": CommandType.HELP,
            "h": CommandType.HELP,
        }
        
        return Command(
            type=cmd_map.get(cmd, CommandType.UNKNOWN),
            args=args,
            raw=message
        )
    
    @classmethod
    def _parse_natural_language(cls, message: str) -> Command:
        """Parse natural language as command."""
        # Check for capture patterns
        if any(kw in message.lower() for kw in ["save this", "remember this", "capture"]):
            return Command(CommandType.CAPTURE, message, message)
        
        # Check for search patterns
        if message.lower().startswith(("find", "search for", "look for")):
            return Command(CommandType.SEARCH, message, message)
        
        # Check for report patterns
        if any(kw in message.lower() for kw in ["report", "summary", "what did i save"]):
            return Command(CommandType.REPORT, "", message)
        
        return Command(CommandType.UNKNOWN, message, message)
    
    @classmethod
    def handle(cls, message: str, context: Dict = None) -> str:
        """Handle incoming message and return response."""
        command = cls.parse_command(message)
        
        handlers = {
            CommandType.CAPTURE: cls._handle_capture,
            CommandType.VOICE: cls._handle_voice,
            CommandType.SCREENSHOT: cls._handle_screenshot,
            CommandType.SEARCH: cls._handle_search,
            CommandType.REPORT: cls._handle_report,
            CommandType.HELP: cls._handle_help,
            CommandType.UNKNOWN: cls._handle_unknown,
        }
        
        handler = handlers.get(command.type, cls._handle_unknown)
        return handler(command, context)
    
    @classmethod
    def _handle_capture(cls, cmd: Command, context: Dict) -> str:
        """Handle capture command."""
        if not cmd.args:
            return "📝 What idea would you like to capture?"
        
        # Import here to avoid circular dependency
        from capture import CaptureService
        from database import Database
        
        idea = CaptureService.capture_text(cmd.args)
        
        # Save to database
        db = Database()
        idea_id = db.save_idea(idea)
        
        # Format response
        tags_str = " ".join([f"#{t}" for t in idea.tags]) if idea.tags else ""
        return (
            f"✅ **Idea saved!**\n"
            f"> {idea.content[:100]}{'...' if len(idea.content) > 100 else ''}\n"
            f"Type: {idea.idea_type.value} | Tags: {tags_str or 'none'}\n"
            f"ID: `{idea_id}`"
        )
    
    @classmethod
    def _handle_voice(cls, cmd: Command, context: Dict) -> str:
        """Handle voice command."""
        return (
            "🎙️ **Voice Capture**\n"
            "Send me a voice message and I'll transcribe and save it!\n"
            "Tip: Speak clearly for best results."
        )
    
    @classmethod
    def _handle_screenshot(cls, cmd: Command, context: Dict) -> str:
        """Handle screenshot command."""
        return (
            "📸 **Screenshot Capture**\n"
            "Send me an image and I'll extract ideas from it!\n"
            "I can read text from screenshots, notes, or any image."
        )
    
    @classmethod
    def _handle_search(cls, cmd: Command, context: Dict) -> str:
        """Handle search command."""
        if not cmd.args:
            return "🔍 What would you like to search for?"
        
        from database import Database
        
        db = Database()
        results = db.search_ideas(cmd.args)
        
        if not results:
            return "🔍 No ideas found. Try different keywords?"
        
        response = f"🔍 **Found {len(results)} ideas:**\n\n"
        for i, idea in enumerate(results[:5], 1):
            response += f"{i}. {idea['content'][:80]}{'...' if len(idea['content']) > 80 else ''}\n"
        
        if len(results) > 5:
            response += f"\n...and {len(results) - 5} more"
        
        return response
    
    @classmethod
    def _handle_report(cls, cmd: Command, context: Dict) -> str:
        """Handle report command."""
        from report.daily import DailyReportGenerator
        from report.formatter import ChatFormatter
        
        generator = DailyReportGenerator()
        report = generator.generate()
        
        formatter = ChatFormatter()
        return formatter.format(report)
    
    @classmethod
    def _handle_help(cls, cmd: Command, context: Dict) -> str:
        """Handle help command."""
        return (
            "📚 **Content Idea Generator Commands**\n\n"
            "**Capture Ideas:**\n"
            "• `/capture <text>` - Save text idea\n"
            "• `/voice` - Send voice message\n"
            "• `/screenshot` - Send image\n\n"
            "**Manage:**\n"
            "• `/search <query>` - Find ideas\n"
            "• `/report` - Daily inspiration report\n\n"
            "**Tips:**\n"
            "• Use #tag to add tags\n"
            "• Say 'tutorial', 'blog', 'video' to set type\n"
            "• I analyze daily and suggest content!"
        )
    
    @classmethod
    def _handle_unknown(cls, cmd: Command, context: Dict) -> str:
        """Handle unknown command."""
        return (
            "🤔 I'm not sure what you mean.\n"
            "Try `/capture your idea here` or `/help` for commands."
        )


class ResponseBuilder:
    """Build formatted responses for chat."""
    
    @staticmethod
    def success(message: str) -> str:
        return f"✅ {message}"
    
    @staticmethod
    def error(message: str) -> str:
        return f"❌ {message}"
    
    @staticmethod
    def info(message: str) -> str:
        return f"ℹ️ {message}"
    
    @staticmethod
    def idea_card(idea: Dict) -> str:
        """Format idea as a card."""
        content = idea.get('content', '')[:150]
        if len(idea.get('content', '')) > 150:
            content += "..."
        
        tags = " ".join([f"#{t}" for t in idea.get('tags', [])])
        
        return (
            f"📝 **{idea.get('idea_type', 'idea').replace('_', ' ').title()}**\n"
            f"> {content}\n"
            f"Tags: {tags or 'none'} | "
            f"Status: {idea.get('status', 'new')}"
        )
