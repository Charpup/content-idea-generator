#!/usr/bin/env python3
"""
Content Idea Generator Skill - Main Entry Point

Usage:
    python main.py [command] [args]
    
Commands:
    capture <text>     Capture a text idea
    voice <file>       Capture from voice file
    screenshot <file>  Capture from image
    search <query>     Search ideas
    report             Generate daily report
    help               Show help
"""

import sys
import argparse
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from chat import ChatHandler
from database import Database


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Content Idea Generator - Capture and analyze content ideas"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Capture command
    capture_parser = subparsers.add_parser("capture", help="Capture a text idea")
    capture_parser.add_argument("text", nargs="+", help="Idea text to capture")
    
    # Voice command
    voice_parser = subparsers.add_parser("voice", help="Capture from voice file")
    voice_parser.add_argument("file", help="Path to audio file")
    
    # Screenshot command
    screenshot_parser = subparsers.add_parser("screenshot", help="Capture from image")
    screenshot_parser.add_argument("file", help="Path to image file")
    
    # Search command
    search_parser = subparsers.add_parser("search", help="Search ideas")
    search_parser.add_argument("query", help="Search query")
    
    # Report command
    subparsers.add_parser("report", help="Generate daily report")
    
    # Help command
    subparsers.add_parser("help", help="Show help")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Initialize database
    db = Database()
    db.init_database()
    
    # Build command string for chat handler
    if args.command == "capture" and args.text:
        message = f"/capture {' '.join(args.text)}"
    elif args.command == "voice" and args.file:
        message = f"/voice {args.file}"
    elif args.command == "screenshot" and args.file:
        message = f"/screenshot {args.file}"
    elif args.command == "search" and args.query:
        message = f"/search {args.query}"
    elif args.command == "report":
        message = "/report"
    elif args.command == "help":
        message = "/help"
    else:
        message = f"/{args.command}"
    
    # Handle command
    response = ChatHandler.handle(message)
    print(response)


if __name__ == "__main__":
    main()
