#!/usr/bin/env python3
# pip install google-api-python-client requests
import os, sys, re, requests
from googleapiclient.discovery import build

API_KEY = os.getenv("YT_API_KEY")            # export YT_API_KEY=your-key
FEED_ID_PATTERNS = (
    r'"channelId":"(UC[\w-]{22})"',
    r'rel="canonical"[^>]+/channel/(UC[\w-]{22})',
    r'/channel/(UC[\w-]{22})'
)
UA = {"User-Agent": "Mozilla/5.0"}

def get_html(url: str) -> str:
    return requests.get(url, headers=UA, timeout=10).text

def chan_id(arg: str) -> str:
    if re.fullmatch(r"UC[\w-]{22}", arg):
        return arg
    for pat in FEED_ID_PATTERNS:
        m = re.search(pat, get_html(arg))
        if m:
            return m.group(1)
    sys.exit("Could not resolve channel ID")

def list_videos(cid: str):
    yt = build("youtube", "v3", developerKey=API_KEY)
    page = None
    while True:
        res = yt.search().list(
            channelId=cid,
            part="id,snippet",
            maxResults=50,
            order="date",
            pageToken=page,
            type="video"
        ).execute()
        for it in res["items"]:
            vid = it["id"]["videoId"]
            print(f'{it["snippet"]["title"]} :: https://youtu.be/{vid}')
        page = res.get("nextPageToken")
        if not page:
            break

def main():
    if len(sys.argv) != 2 or not API_KEY:
        sys.exit(f"Usage: YT_API_KEY=key {sys.argv[0]} <channel_id|url>")
    list_videos(chan_id(sys.argv[1]))

if __name__ == "__main__":
    main()
