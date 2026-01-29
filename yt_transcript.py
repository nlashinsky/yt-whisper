#!/usr/bin/env python3
"""
YouTube Transcript Extractor
Extracts transcripts from YouTube videos and prints them to the terminal.
Uses yt-dlp to fetch subtitles/captions.
"""

import sys
import re
import argparse
import tempfile
import os
import json

try:
    import yt_dlp
except ImportError:
    print("Installing yt-dlp...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "yt-dlp", "-q"])
    import yt_dlp


def extract_video_id(url):
    """Extract video ID from various YouTube URL formats."""
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/|youtube\.com\/v\/)([a-zA-Z0-9_-]{11})',
        r'^([a-zA-Z0-9_-]{11})$'  # Direct video ID
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)

    return None


def parse_vtt(vtt_content):
    """Parse VTT subtitle content and extract text."""
    lines = vtt_content.split('\n')
    transcript_lines = []
    timestamps = []

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # Check for timestamp line (e.g., "00:00:00.000 --> 00:00:05.000")
        if '-->' in line:
            # Extract start timestamp
            start_time = line.split('-->')[0].strip()
            timestamps.append(start_time)

            # Get the text lines after the timestamp
            i += 1
            text_parts = []
            while i < len(lines) and lines[i].strip() and '-->' not in lines[i]:
                text = lines[i].strip()
                # Remove HTML tags
                text = re.sub(r'<[^>]+>', '', text)
                if text:
                    text_parts.append(text)
                i += 1

            if text_parts:
                transcript_lines.append({
                    'timestamp': start_time,
                    'text': ' '.join(text_parts)
                })
        else:
            i += 1

    return transcript_lines


def format_timestamp(vtt_timestamp):
    """Convert VTT timestamp to simple MM:SS format."""
    # Handle formats like "00:00:05.000" or "0:05.000"
    parts = vtt_timestamp.replace(',', '.').split(':')
    if len(parts) == 3:
        hours, minutes, seconds = parts
        total_seconds = int(hours) * 3600 + int(minutes) * 60 + float(seconds.split('.')[0])
    elif len(parts) == 2:
        minutes, seconds = parts
        total_seconds = int(minutes) * 60 + float(seconds.split('.')[0])
    else:
        total_seconds = 0

    mins = int(total_seconds // 60)
    secs = int(total_seconds % 60)
    return f"[{mins:02d}:{secs:02d}]"


def get_transcript(url, language='en'):
    """Fetch transcript for a YouTube video using yt-dlp."""
    with tempfile.TemporaryDirectory() as temp_dir:
        output_template = os.path.join(temp_dir, '%(id)s.%(ext)s')

        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'skip_download': True,
            'writesubtitles': True,
            'writeautomaticsub': True,
            'subtitleslangs': [language, 'en'],
            'subtitlesformat': 'vtt',
            'outtmpl': output_template,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                video_id = info.get('id')
                title = info.get('title', 'Unknown')

                # Look for subtitle files
                subtitle_file = None
                for lang in [language, 'en']:
                    for ext in ['vtt', f'{lang}.vtt']:
                        potential_file = os.path.join(temp_dir, f'{video_id}.{lang}.vtt')
                        if os.path.exists(potential_file):
                            subtitle_file = potential_file
                            break
                    if subtitle_file:
                        break

                # Try to find any subtitle file
                if not subtitle_file:
                    for f in os.listdir(temp_dir):
                        if f.endswith('.vtt'):
                            subtitle_file = os.path.join(temp_dir, f)
                            break

                if not subtitle_file:
                    raise Exception("No subtitles/captions available for this video")

                with open(subtitle_file, 'r', encoding='utf-8') as f:
                    vtt_content = f.read()

                return parse_vtt(vtt_content), title

        except yt_dlp.utils.DownloadError as e:
            raise Exception(f"Failed to fetch video info: {e}")


def format_transcript(transcript_data, include_timestamps=False):
    """Format transcript data into readable text."""
    lines = []
    seen_texts = set()

    for entry in transcript_data:
        text = entry['text'].strip()
        # Skip duplicate lines (common in auto-generated captions)
        if text and text not in seen_texts:
            seen_texts.add(text)
            if include_timestamps:
                ts = format_timestamp(entry['timestamp'])
                lines.append(f"{ts} {text}")
            else:
                lines.append(text)

    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(
        description='Extract transcripts from YouTube videos'
    )
    parser.add_argument('url', help='YouTube video URL or video ID')
    parser.add_argument('-t', '--timestamps', action='store_true',
                        help='Include timestamps in output')
    parser.add_argument('-l', '--language', default='en',
                        help='Preferred language code (default: en)')
    parser.add_argument('-p', '--paragraph', action='store_true',
                        help='Output as a single paragraph (no line breaks)')

    args = parser.parse_args()

    # Convert video ID to full URL if needed
    url = args.url
    video_id = extract_video_id(url)
    if video_id and not url.startswith('http'):
        url = f'https://www.youtube.com/watch?v={video_id}'

    try:
        transcript_data, title = get_transcript(url, args.language)
        output = format_transcript(transcript_data, args.timestamps)

        if args.paragraph:
            # Join all lines into a single paragraph
            output = ' '.join(line.strip() for line in output.split('\n') if line.strip())

        # Print title as header
        print(f"# {title}\n")
        print(output)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
