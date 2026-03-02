"""
Daily Report Generator for Content Idea Generator

Generates daily, weekly, and monthly inspiration reports
with stats, suggestions, and quick drafts.
"""

from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
import json


class ReportPeriod(Enum):
    """Report period types."""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


@dataclass
class ReportStats:
    """Statistics for the report period."""
    total_ideas: int = 0
    new_ideas: int = 0
    by_source: Dict[str, int] = field(default_factory=dict)
    by_status: Dict[str, int] = field(default_factory=dict)
    by_content_type: Dict[str, int] = field(default_factory=dict)
    avg_confidence: float = 0.0


@dataclass
class TagStat:
    """Tag statistics."""
    tag: str
    count: int
    trend: str = "→"  # ↑ ↓ →


@dataclass
class ContentSuggestion:
    """Content suggestion with confidence."""
    type: str  # cluster, priority, trend, connection
    message: str
    confidence: float  # 0.0 - 1.0
    related_ideas: List[str] = field(default_factory=list)
    action_items: List[str] = field(default_factory=list)


@dataclass
class ConnectionSpotlight:
    """Highlights connections between ideas."""
    theme: str
    ideas: List[str]
    insight: str
    suggested_series: Optional[str] = None


@dataclass
class QuickDraft:
    """Quick content draft for different platforms."""
    platform: str  # twitter, linkedin, blog
    title: str
    content: str
    hashtags: List[str] = field(default_factory=list)
    estimated_engagement: str = "medium"  # low, medium, high


@dataclass
class InspirationReport:
    """Complete inspiration report."""
    period: ReportPeriod
    start_date: datetime
    end_date: datetime
    generated_at: datetime
    stats: ReportStats
    top_tags: List[TagStat]
    top_categories: List[TagStat]
    suggestions: List[ContentSuggestion]
    connections: List[ConnectionSpotlight]
    quick_drafts: List[QuickDraft]
    trends: Dict[str, Any] = field(default_factory=dict)


class DailyReportGenerator:
    """Generate daily inspiration reports."""
    
    VALID_CONTENT_TYPES = [
        "blog_post", "video_script", "social_post", 
        "tutorial", "note", "research_paper"
    ]
    
    def __init__(self, db_connection=None):
        self.db = db_connection
        
    def generate(
        self, 
        period: ReportPeriod = ReportPeriod.DAILY,
        date: Optional[datetime] = None
    ) -> InspirationReport:
        """
        Generate an inspiration report for the specified period.
        
        Args:
            period: Report period (daily, weekly, monthly)
            date: End date for the report (defaults to now)
            
        Returns:
            InspirationReport with all sections
        """
        end_date = date or datetime.now()
        start_date = self._calculate_start_date(period, end_date)
        
        # Fetch data for the period
        ideas = self._fetch_ideas(start_date, end_date)
        
        # Build report sections
        stats = self._calculate_stats(ideas, start_date, end_date)
        top_tags = self._get_top_tags(ideas, limit=5)
        top_categories = self._get_top_categories(ideas, limit=5)
        suggestions = self._generate_suggestions(ideas, top_tags)
        connections = self._find_connections(ideas)
        quick_drafts = self._generate_quick_drafts(ideas, top_tags)
        trends = self._analyze_trends(ideas)
        
        return InspirationReport(
            period=period,
            start_date=start_date,
            end_date=end_date,
            generated_at=datetime.now(),
            stats=stats,
            top_tags=top_tags,
            top_categories=top_categories,
            suggestions=suggestions,
            connections=connections,
            quick_drafts=quick_drafts,
            trends=trends
        )
    
    def _calculate_start_date(self, period: ReportPeriod, end_date: datetime) -> datetime:
        """Calculate the start date based on period."""
        if period == ReportPeriod.DAILY:
            return end_date - timedelta(days=1)
        elif period == ReportPeriod.WEEKLY:
            return end_date - timedelta(weeks=1)
        elif period == ReportPeriod.MONTHLY:
            # Approximate month as 30 days
            return end_date - timedelta(days=30)
        else:
            return end_date - timedelta(days=1)
    
    def _fetch_ideas(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Fetch ideas from the database for the date range."""
        # This would query the actual database
        # For now, return empty list - implementation depends on db schema
        if self.db is None:
            return []
        
        # Example query structure:
        # return self.db.fetch_all(
        #     "SELECT * FROM ideas WHERE created_at BETWEEN ? AND ?",
        #     (start_date.isoformat(), end_date.isoformat())
        # )
        return []
    
    def _calculate_stats(
        self, 
        ideas: List[Dict[str, Any]], 
        start_date: datetime,
        end_date: datetime
    ) -> ReportStats:
        """Calculate statistics for the report period."""
        if not ideas:
            return ReportStats()
        
        # Count by source
        by_source = {}
        by_status = {}
        by_content_type = {}
        confidences = []
        
        new_ideas = 0
        for idea in ideas:
            # Source stats
            source = idea.get("source", {}).get("type", "unknown")
            by_source[source] = by_source.get(source, 0) + 1
            
            # Status stats
            status = idea.get("status", "unknown")
            by_status[status] = by_status.get(status, 0) + 1
            
            # Content type stats
            content_type = idea.get("content_type", "unknown")
            by_content_type[content_type] = by_content_type.get(content_type, 0) + 1
            
            # Confidence tracking
            confidence = idea.get("source", {}).get("confidence", 0)
            if confidence:
                confidences.append(confidence)
            
            # Count new ideas in period
            created_at = datetime.fromisoformat(idea.get("created_at", "1970-01-01"))
            if start_date <= created_at <= end_date:
                new_ideas += 1
        
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
        
        return ReportStats(
            total_ideas=len(ideas),
            new_ideas=new_ideas,
            by_source=by_source,
            by_status=by_status,
            by_content_type=by_content_type,
            avg_confidence=round(avg_confidence, 2)
        )
    
    def _get_top_tags(self, ideas: List[Dict[str, Any]], limit: int = 5) -> List[TagStat]:
        """Get top tags by usage count."""
        tag_counts = {}
        
        for idea in ideas:
            for tag in idea.get("tags", []):
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        # Sort by count descending
        sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)
        
        return [
            TagStat(tag=tag, count=count, trend="→")
            for tag, count in sorted_tags[:limit]
        ]
    
    def _get_top_categories(self, ideas: List[Dict[str, Any]], limit: int = 5) -> List[TagStat]:
        """Get top categories by usage count."""
        category_counts = {}
        
        for idea in ideas:
            for category in idea.get("categories", []):
                category_counts[category] = category_counts.get(category, 0) + 1
        
        # Sort by count descending
        sorted_categories = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)
        
        return [
            TagStat(tag=cat, count=count, trend="→")
            for cat, count in sorted_categories[:limit]
        ]
    
    def _generate_suggestions(
        self, 
        ideas: List[Dict[str, Any]], 
        top_tags: List[TagStat]
    ) -> List[ContentSuggestion]:
        """Generate content suggestions based on ideas and tags."""
        suggestions = []
        
        if not ideas:
            return suggestions
        
        # Find clusters of related ideas
        tag_to_ideas = {}
        for idea in ideas:
            for tag in idea.get("tags", []):
                if tag not in tag_to_ideas:
                    tag_to_ideas[tag] = []
                tag_to_ideas[tag].append(idea["id"])
        
        # Suggest series for tags with multiple ideas
        for tag, idea_ids in tag_to_ideas.items():
            if len(idea_ids) >= 2:
                suggestions.append(ContentSuggestion(
                    type="cluster",
                    message=f"💡 You have {len(idea_ids)} ideas tagged with '{tag}'. Consider creating a series!",
                    confidence=min(0.7 + (len(idea_ids) * 0.05), 0.95),
                    related_ideas=idea_ids,
                    action_items=[
                        f"Create a content series around '{tag}'",
                        "Outline the connection between these ideas"
                    ]
                ))
        
        # Suggest high priority ideas
        high_priority = [i for i in ideas if i.get("priority") == "high"]
        if high_priority:
            suggestions.append(ContentSuggestion(
                type="priority",
                message=f"⚡ {len(high_priority)} high-priority idea(s) need attention",
                confidence=0.9,
                related_ideas=[i["id"] for i in high_priority],
                action_items=["Review and prioritize these ideas", "Set deadlines for completion"]
            ))
        
        # Suggest content type diversification
        content_types = {}
        for idea in ideas:
            ct = idea.get("content_type", "unknown")
            content_types[ct] = content_types.get(ct, 0) + 1
        
        if len(content_types) == 1:
            only_type = list(content_types.keys())[0]
            suggestions.append(ContentSuggestion(
                type="diversification",
                message=f"🎯 All your ideas are '{only_type}'. Try different formats!",
                confidence=0.75,
                related_ideas=[],
                action_items=[
                    "Consider video scripts for visual topics",
                    "Try social posts for quick tips",
                    "Explore tutorials for how-to content"
                ]
            ))
        
        # Sort by confidence
        suggestions.sort(key=lambda x: x.confidence, reverse=True)
        return suggestions[:5]  # Top 5 suggestions
    
    def _find_connections(self, ideas: List[Dict[str, Any]]) -> List[ConnectionSpotlight]:
        """Find connections between ideas."""
        connections = []
        
        if len(ideas) < 2:
            return connections
        
        # Group ideas by shared tags
        tag_groups = {}
        for idea in ideas:
            for tag in idea.get("tags", []):
                if tag not in tag_groups:
                    tag_groups[tag] = []
                tag_groups[tag].append(idea)
        
        # Find groups with multiple ideas
        for tag, group in tag_groups.items():
            if len(group) >= 2:
                # Check for overlapping tags beyond the main one
                all_tags = set()
                for idea in group:
                    all_tags.update(idea.get("tags", []))
                
                if len(all_tags) > 1:
                    connections.append(ConnectionSpotlight(
                        theme=tag,
                        ideas=[i["id"] for i in group],
                        insight=f"These {len(group)} ideas share the '{tag}' theme and could form a cohesive series",
                        suggested_series=f"{tag.title()} Series: A Deep Dive"
                    ))
        
        return connections[:3]  # Top 3 connections
    
    def _generate_quick_drafts(
        self, 
        ideas: List[Dict[str, Any]], 
        top_tags: List[TagStat]
    ) -> List[QuickDraft]:
        """Generate quick content drafts for different platforms."""
        drafts = []
        
        if not ideas:
            return drafts
        
        # Get the most promising idea for drafting
        candidates = [i for i in ideas if i.get("status") == "active"]
        if not candidates:
            candidates = ideas
        
        # Sort by priority and recency
        priority_order = {"urgent": 0, "high": 1, "medium": 2, "low": 3}
        candidates.sort(
            key=lambda x: (priority_order.get(x.get("priority", "low"), 3), x.get("created_at", "")),
            reverse=False
        )
        
        if not candidates:
            return drafts
        
        top_idea = candidates[0]
        title = top_idea.get("title", "Untitled Idea")
        description = top_idea.get("description", "")
        tags = top_idea.get("tags", [])
        
        # Twitter draft
        drafts.append(self._create_twitter_draft(title, description, tags))
        
        # LinkedIn draft
        drafts.append(self._create_linkedin_draft(title, description, tags))
        
        # Blog draft
        drafts.append(self._create_blog_draft(title, description, tags))
        
        return drafts
    
    def _create_twitter_draft(self, title: str, description: str, tags: List[str]) -> QuickDraft:
        """Create a Twitter-optimized draft."""
        hashtags = [f"#{tag.replace(' ', '')}" for tag in tags[:3]]
        hashtag_str = " ".join(hashtags)
        
        content = f"🚀 {title}\n\n{description[:100]}..." if len(description) > 100 else f"🚀 {title}\n\n{description}"
        content += f"\n\n{hashtag_str}"
        
        return QuickDraft(
            platform="twitter",
            title=title,
            content=content,
            hashtags=hashtags,
            estimated_engagement="high" if len(tags) >= 3 else "medium"
        )
    
    def _create_linkedin_draft(self, title: str, description: str, tags: List[str]) -> QuickDraft:
        """Create a LinkedIn-optimized draft."""
        hashtags = [f"#{tag.replace(' ', '').replace('-', '').title()}" for tag in tags[:5]]
        
        content = f"I'm excited to share some thoughts on {title}.\n\n"
        content += f"{description}\n\n" if description else ""
        content += "What are your thoughts on this? I'd love to hear your perspective in the comments. 👇\n\n"
        content += " ".join(hashtags)
        
        return QuickDraft(
            platform="linkedin",
            title=title,
            content=content,
            hashtags=hashtags,
            estimated_engagement="medium"
        )
    
    def _create_blog_draft(self, title: str, description: str, tags: List[str]) -> QuickDraft:
        """Create a Blog-optimized draft."""
        hashtags = []
        
        content = f"# {title}\n\n"
        content += f"**Tags:** {', '.join(tags)}\n\n" if tags else ""
        content += "## Introduction\n\n"
        content += f"{description}\n\n" if description else "In this article, we'll explore...\n\n"
        content += "## Key Points\n\n"
        content += "- Point 1\n"
        content += "- Point 2\n"
        content += "- Point 3\n\n"
        content += "## Conclusion\n\n"
        content += "[Your conclusion here]\n\n"
        content += "---\n\n"
        content += "*Happy creating!*"
        
        return QuickDraft(
            platform="blog",
            title=title,
            content=content,
            hashtags=hashtags,
            estimated_engagement="medium"
        )
    
    def _analyze_trends(self, ideas: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze trends in the ideas."""
        if not ideas:
            return {}
        
        # Ideas per day (for the period)
        daily_counts = {}
        for idea in ideas:
            created = datetime.fromisoformat(idea.get("created_at", "1970-01-01"))
            day_key = created.strftime("%Y-%m-%d")
            daily_counts[day_key] = daily_counts.get(day_key, 0) + 1
        
        # Most productive day
        most_productive = max(daily_counts.items(), key=lambda x: x[1]) if daily_counts else (None, 0)
        
        # Source distribution percentages
        total = len(ideas)
        source_dist = {}
        for idea in ideas:
            source = idea.get("source", {}).get("type", "unknown")
            source_dist[source] = source_dist.get(source, 0) + 1
        
        source_pct = {k: round(v/total*100, 1) for k, v in source_dist.items()}
        
        return {
            "ideas_per_day": list(daily_counts.values()),
            "most_productive_day": most_productive[0],
            "most_productive_count": most_productive[1],
            "source_distribution_pct": source_pct
        }
    
    def generate_from_data(
        self,
        period: ReportPeriod,
        ideas: List[Dict[str, Any]],
        date: Optional[datetime] = None
    ) -> InspirationReport:
        """
        Generate report from provided data (for testing or external data sources).
        
        Args:
            period: Report period
            ideas: List of idea dictionaries
            date: End date for the report
            
        Returns:
            InspirationReport
        """
        end_date = date or datetime.now()
        start_date = self._calculate_start_date(period, end_date)
        
        stats = self._calculate_stats(ideas, start_date, end_date)
        top_tags = self._get_top_tags(ideas, limit=5)
        top_categories = self._get_top_categories(ideas, limit=5)
        suggestions = self._generate_suggestions(ideas, top_tags)
        connections = self._find_connections(ideas)
        quick_drafts = self._generate_quick_drafts(ideas, top_tags)
        trends = self._analyze_trends(ideas)
        
        return InspirationReport(
            period=period,
            start_date=start_date,
            end_date=end_date,
            generated_at=datetime.now(),
            stats=stats,
            top_tags=top_tags,
            top_categories=top_categories,
            suggestions=suggestions,
            connections=connections,
            quick_drafts=quick_drafts,
            trends=trends
        )
