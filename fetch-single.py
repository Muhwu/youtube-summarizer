#!/usr/bin/env python3
# pip install youtube_transcript_api
import sys, re
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled

def video_id(url: str) -> str:
    m = re.search(r'(?:v=|\/)([0-9A-Za-z_-]{11})(?=[?&\/]|$)', url)
    if not m:
        raise ValueError("Invalid YouTube URL")
    return m.group(1)

def main():
    if len(sys.argv) != 2:
        sys.exit(f"Usage: {sys.argv[0]} <youtube_url>")
    vid = video_id(sys.argv[1])
    try:
        captions = YouTubeTranscriptApi.get_transcript(vid, languages=['en'])
    except TranscriptsDisabled:
        sys.exit("Captions are disabled for this video.")
    for line in captions:
        print(line['text'])

if __name__ == "__main__":
    main()
