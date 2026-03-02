#!/usr/bin/env python3
"""
Content Idea Generator - Main Entry Point

A comprehensive tool for capturing, organizing, and analyzing content inspiration
to generate actionable content ideas.

Usage:
    python3 main.py init                    # Initialize database
    python3 main.py capture [options]       # Capture new content
    python3 main.py search <query>          # Search content
    python3 main.py list [options]          # List content items
    python3 main.py list-ideas [options]    # List ideas
    python3 main.py analyze [options]       # Run analysis
    python3 main.py export [options]        # Export to Obsidian
    python3 main.py stats                   # Show statistics
    python3 main.py test                    # Run tests
    python3 main.py chat                    # Interactive chat mode
"""

import argparse
import sys
import os
from pathlib import Path

# Add skill directory to path
skill_dir = Path(__file__).parent
sys.path.insert(0, str(skill_dir))

from database import ContentIdeaDatabase, init_database


def cmd_init(args):
    """Initialize database"""
    db_path = args.db or os.path.expanduser("~/.openclaw/content-ideas.db")
    db = init_database(db_path)
    print(f"✅ Database initialized at: {db_path}")
    
    # Show initial stats
    stats = db.get_statistics()
    print(f"\n📊 Initial Statistics:")
    print(f"   Categories: {stats['categories']}")
    print(f"   Tags: {stats['tags']}")
    print(f"   Content Items: {stats['content_items']}")
    print(f"   Ideas: {stats['ideas']}")
    return 0


def cmd_capture(args):
    """Capture new content"""
    db_path = args.db or os.path.expanduser("~/.openclaw/content-ideas.db")
    db = init_database(db_path)
    
    # Get content from file or argument
    content_text = args.content
    if args.file:
        with open(args.file, 'r', encoding='utf-8') as f:
            content_text = f.read()
    
    if not content_text:
        print("❌ Error: No content provided. Use --content or --file")
        return 1
    
    # Handle category
    category_id = None
    if args.category:
        cat = db.get_category_by_name(args.category)
        if cat:
            category_id = cat['id']
        else:
            category_id = db.create_category(args.category)
            print(f"✅ Created category: {args.category}")
    
    # Handle tags
    tag_ids = []
    if args.tags:
        tag_names = [t.strip() for t in args.tags.split(',')]
        for tag_name in tag_names:
            tag = db.get_tag_by_name(tag_name)
            if tag:
                tag_ids.append(tag['id'])
            else:
                tag_id = db.create_tag(tag_name)
                tag_ids.append(tag_id)
                print(f"✅ Created tag: {tag_name}")
    
    # Create content item
    content_id = db.create_content_item(
        type=args.type,
        title=args.title,
        content=content_text,
        source=args.source,
        author=args.author,
        category_id=category_id,
        priority=args.priority or 3,
        status=args.status or 'active',
        tag_ids=tag_ids
    )
    
    print(f"✅ Captured content item: {args.title}")
    print(f"   ID: {content_id}")
    print(f"   Type: {args.type}")
    if args.source:
        print(f"   Source: {args.source}")
    if tag_ids:
        print(f"   Tags: {args.tags}")
    
    return 0


def cmd_search(args):
    """Search content"""
    db_path = args.db or os.path.expanduser("~/.openclaw/content-ideas.db")
    db = init_database(db_path)
    
    query = ' '.join(args.query)
    results = db.search_with_snippet(query, limit=args.limit or 20)
    
    if not results:
        print(f"🔍 No results found for: '{query}'")
        return 0
    
    print(f"🔍 Found {len(results)} results for: '{query}'\n")
    
    for i, result in enumerate(results, 1):
        print(f"{i}. {result['title_highlight'] or result['title']}")
        print(f"   Type: {result['type']} | Status: {result['status']}")
        if result.get('content_preview'):
            preview = result['content_preview'].replace('\n', ' ')
            print(f"   Preview: {preview[:150]}...")
        print()
    
    return 0


def cmd_list(args):
    """List content items"""
    db_path = args.db or os.path.expanduser("~/.openclaw/content-ideas.db")
    db = init_database(db_path)
    
    items = db.list_content_items(
        type=args.type,
        status=args.status,
        limit=args.limit or 50
    )
    
    if not items:
        print("📭 No content items found")
        return 0
    
    print(f"📚 Content Items ({len(items)}):\n")
    
    for item in items:
        tags = item.get('tags') or ''
        tag_str = f" [{tags}]" if tags else ""
        print(f"• [{item['type']}] {item['title']}{tag_str}")
        print(f"  ID: {item['id']} | Priority: {item['priority']}/5 | Status: {item['status']}")
        if item.get('source'):
            print(f"  Source: {item['source'][:60]}...")
        print()
    
    return 0


def cmd_list_ideas(args):
    """List ideas"""
    db_path = args.db or os.path.expanduser("~/.openclaw/content-ideas.db")
    db = init_database(db_path)
    
    ideas = db.list_ideas(
        status=args.status,
        min_priority=args.min_priority
    )
    
    if not ideas:
        print("💡 No ideas found")
        return 0
    
    print(f"💡 Ideas ({len(ideas)}):\n")
    
    for idea in ideas:
        tags = ', '.join(idea.get('tags', [])) if idea.get('tags') else ''
        tag_str = f" [{tags}]" if tags else ""
        print(f"• {idea['concept']}{tag_str}")
        print(f"  ID: {idea['id']} | Priority: {idea['priority']}/5 | Status: {idea['status']}")
        if idea.get('elaboration'):
            elaboration = idea['elaboration'].replace('\n', ' ')
            print(f"  {elaboration[:100]}...")
        print()
    
    return 0


def cmd_analyze(args):
    """Run analysis"""
    db_path = args.db or os.path.expanduser("~/.openclaw/content-ideas.db")
    
    try:
        from analysis import AnalysisEngine
        
        db = init_database(db_path)
        engine = AnalysisEngine(db)
        
        if args.daily:
            print("📊 Running daily analysis...\n")
            report = engine.run_daily_analysis()
            
            print(report['formatted_report'])
            
        elif args.cluster:
            print("🔗 Running clustering analysis...\n")
            clusters = engine.cluster_content()
            print(f"Found {len(clusters)} clusters\n")
            
            for i, cluster in enumerate(clusters[:5], 1):
                print(f"Cluster {i}: {cluster['name']}")
                print(f"  Items: {len(cluster['items'])}")
                print(f"  Coherence: {cluster.get('coherence', 0):.2f}")
                print()
        
        else:
            print("📊 Running full analysis...\n")
            report = engine.run_daily_analysis()
            print(report['formatted_report'])
        
        return 0
        
    except ImportError as e:
        print(f"❌ Analysis module not available: {e}")
        print("   Run: pip3 install -r requirements.txt")
        return 1


def cmd_export(args):
    """Export to Obsidian"""
    db_path = args.db or os.path.expanduser("~/.openclaw/content-ideas.db")
    db = init_database(db_path)
    
    output_dir = args.output or os.path.expanduser("~/Obsidian/Content Ideas")
    
    if args.content_id:
        # Export single item
        md = db.export_content_to_markdown(args.content_id)
        if md:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            content = db.get_content_item(args.content_id)
            filename = f"{content['title'][:50].replace(' ', '_')}.md"
            
            with open(output_path / filename, 'w', encoding='utf-8') as f:
                f.write(md)
            
            print(f"✅ Exported to: {output_path / filename}")
        else:
            print(f"❌ Content item {args.content_id} not found")
            return 1
    else:
        # Export all
        counts = db.export_all_content(output_dir)
        print(f"✅ Exported {counts['content']} content items")
        print(f"✅ Exported {counts['ideas']} ideas")
        print(f"   Output: {output_dir}")
    
    return 0


def cmd_stats(args):
    """Show statistics"""
    db_path = args.db or os.path.expanduser("~/.openclaw/content-ideas.db")
    db = init_database(db_path)
    
    stats = db.get_statistics()
    
    print("📊 Content Library Statistics\n")
    print(f"Categories:        {stats['categories']}")
    print(f"Tags:              {stats['tags']}")
    print(f"Content Items:     {stats['content_items']}")
    print(f"Text Snippets:     {stats['text_snippets']}")
    print(f"Gold Sentences:    {stats['gold_sentences']}")
    print(f"Ideas:             {stats['ideas']}")
    print(f"Idea Relations:    {stats['idea_relations']}")
    
    if stats.get('content_by_type'):
        print("\n📚 Content by Type:")
        for content_type, count in sorted(stats['content_by_type'].items()):
            print(f"   {content_type:12s} {count}")
    
    if stats.get('ideas_by_status'):
        print("\n💡 Ideas by Status:")
        for status, count in sorted(stats['ideas_by_status'].items()):
            print(f"   {status:12s} {count}")
    
    return 0


def cmd_test(args):
    """Run tests"""
    test_file = skill_dir / "test_database.py"
    
    if not test_file.exists():
        print("❌ Test file not found")
        return 1
    
    import subprocess
    result = subprocess.run([sys.executable, str(test_file)])
    return result.returncode


def cmd_chat(args):
    """Interactive chat mode"""
    try:
        from chat import ChatInterface
        
        db_path = args.db or os.path.expanduser("~/.openclaw/content-ideas.db")
        interface = ChatInterface(db_path)
        interface.run()
        return 0
        
    except ImportError as e:
        print(f"❌ Chat module not available: {e}")
        return 1


def main():
    parser = argparse.ArgumentParser(
        description="Content Idea Generator - Capture and organize content inspiration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s init
  %(prog)s capture --type article --title "My Article" --content "..." --tags "tag1,tag2"
  %(prog)s search "machine learning"
  %(prog)s list --type book --limit 10
  %(prog)s analyze --daily
  %(prog)s export --output ~/Obsidian/Vault
  %(prog)s stats
        """
    )
    
    parser.add_argument('--db', help='Database path (default: ~/.openclaw/content-ideas.db)')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # init
    subparsers.add_parser('init', help='Initialize database')
    
    # capture
    capture_parser = subparsers.add_parser('capture', help='Capture new content')
    capture_parser.add_argument('--type', required=True, 
                               choices=['article', 'book', 'video', 'podcast', 'tweet', 'note', 'idea'],
                               help='Content type')
    capture_parser.add_argument('--title', required=True, help='Content title')
    capture_parser.add_argument('--content', help='Content text')
    capture_parser.add_argument('--file', help='Read content from file')
    capture_parser.add_argument('--source', help='Source URL or reference')
    capture_parser.add_argument('--author', help='Content author')
    capture_parser.add_argument('--category', help='Category name')
    capture_parser.add_argument('--tags', help='Comma-separated tags')
    capture_parser.add_argument('--priority', type=int, choices=range(1, 6), help='Priority (1-5)')
    capture_parser.add_argument('--status', choices=['active', 'archived', 'draft'], help='Status')
    
    # search
    search_parser = subparsers.add_parser('search', help='Search content')
    search_parser.add_argument('query', nargs='+', help='Search query')
    search_parser.add_argument('--limit', type=int, help='Maximum results')
    
    # list
    list_parser = subparsers.add_parser('list', help='List content items')
    list_parser.add_argument('--type', choices=['article', 'book', 'video', 'podcast', 'tweet', 'note', 'idea'],
                            help='Filter by type')
    list_parser.add_argument('--status', choices=['active', 'archived', 'draft'],
                            help='Filter by status')
    list_parser.add_argument('--limit', type=int, help='Maximum results')
    
    # list-ideas
    list_ideas_parser = subparsers.add_parser('list-ideas', help='List ideas')
    list_ideas_parser.add_argument('--status', choices=['new', 'developing', 'ready', 'used', 'archived'],
                                  help='Filter by status')
    list_ideas_parser.add_argument('--min-priority', type=int, choices=range(1, 6),
                                  help='Minimum priority')
    
    # analyze
    analyze_parser = subparsers.add_parser('analyze', help='Run analysis')
    analyze_parser.add_argument('--daily', action='store_true', help='Run daily analysis')
    analyze_parser.add_argument('--cluster', action='store_true', help='Run clustering only')
    
    # export
    export_parser = subparsers.add_parser('export', help='Export to Obsidian')
    export_parser.add_argument('--output', help='Output directory')
    export_parser.add_argument('--content-id', type=int, help='Export single content item')
    
    # stats
    subparsers.add_parser('stats', help='Show statistics')
    
    # test
    subparsers.add_parser('test', help='Run tests')
    
    # chat
    subparsers.add_parser('chat', help='Interactive chat mode')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Route to command handler
    commands = {
        'init': cmd_init,
        'capture': cmd_capture,
        'search': cmd_search,
        'list': cmd_list,
        'list-ideas': cmd_list_ideas,
        'analyze': cmd_analyze,
        'export': cmd_export,
        'stats': cmd_stats,
        'test': cmd_test,
        'chat': cmd_chat,
    }
    
    handler = commands.get(args.command)
    if handler:
        return handler(args)
    else:
        parser.print_help()
        return 1


if __name__ == '__main__':
    sys.exit(main())
