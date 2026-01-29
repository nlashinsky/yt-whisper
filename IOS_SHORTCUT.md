# iOS Shortcut for YouTube Transcripts

## Quick Setup

Create an iOS Shortcut with these steps:

### Step 1: Receive Input
- **Action:** "Receive input from Share Sheet"
- **Input Type:** URLs, Text

### Step 2: Extract Video ID
- **Action:** "Match Text"
- **Pattern:** `(?:youtube\.com\/watch\?v=|youtu\.be\/)([a-zA-Z0-9_-]{11})`
- **Input:** Shortcut Input

### Step 3: Get Transcript
- **Action:** "Get Contents of URL"
- **URL:** `https://tubetext.vercel.app/youtube/transcript?video_id=[Match Group 1]`
- **Method:** GET

### Step 4: Copy to Clipboard
- **Action:** "Copy to Clipboard"
- **Input:** Contents of URL

### Step 5: Show Result
- **Action:** "Show Result"
- **Input:** Contents of URL

---

## Alternative: Using the GitHub Actions Workflow

If the API doesn't work, use the GitHub Actions method:

1. Open GitHub app on iOS (or Safari)
2. Go to: `https://github.com/nlashinsky/yt-whisper/actions`
3. Tap "Fetch YouTube Transcript" workflow
4. Tap "Run workflow"
5. Paste your YouTube URL
6. Wait for completion
7. View transcript in the logs or download the artifact

---

## Command Line (Mac/Linux)

```bash
# One-liner to get transcript and copy to clipboard
python3 -c "
from youtube_transcript_api import YouTubeTranscriptApi
ytt = YouTubeTranscriptApi()
for e in ytt.fetch('VIDEO_ID'): print(e.text)
" | pbcopy
```

Replace `VIDEO_ID` with the 11-character video ID (e.g., `2BJpYTbNQvw`).
