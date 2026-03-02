"""
Content Idea Generator - Report Module

Generate daily, weekly, and monthly inspiration reports
with chat-optimized formatting for Discord/Telegram.
"""

from .daily import DailyReportGenerator, ReportPeriod
from .formatter import ChatFormatter, MarkdownFormatter
from .templates import ReportTemplates

__all__ = [
    "DailyReportGenerator",
    "ReportPeriod", 
    "ChatFormatter",
    "MarkdownFormatter",
    "ReportTemplates"
]

__version__ = "1.0.0"
