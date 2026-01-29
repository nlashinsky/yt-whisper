#!/usr/bin/env python3
"""
Lightweight YouTube Transcript Extractor
Uses youtube-transcript-api for fast transcript retrieval.
"""

import sys
import re

try:
    from youtube_transcript_api import YouTubeTranscriptApi
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "youtube-transcript-api", "-q"])
    from youtube_transcript_api import YouTubeTranscriptApi


def extract_video_id(url):
    """Extract video ID from YouTube URL."""
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([a-zA-Z0-9_-]{11})',
        r'^([a-zA-Z0-9_-]{11})$'
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


def get_transcript(video_id):
    """Fetch transcript using youtube-transcript-api."""
    ytt = YouTubeTranscriptApi()
    try:
        return ytt.fetch(video_id, languages=['en'])
    except:
        # Try any available language
        transcript_list = ytt.list(video_id)
        langs = [t.language_code for t in transcript_list]
        return ytt.fetch(video_id, languages=langs)


def main():
    if len(sys.argv) < 2:
        print("Usage: python transcript.py <youtube_url>")
        print("       python transcript.py <youtube_url> | pbcopy  # Copy to clipboard on macOS")
        sys.exit(1)

    url = sys.argv[1]
    video_id = extract_video_id(url)

    if not video_id:
        print(f"Error: Could not extract video ID from: {url}", file=sys.stderr)
        sys.exit(1)

    try:
        transcript = get_transcript(video_id)
        for entry in transcript:
            print(entry.text)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
