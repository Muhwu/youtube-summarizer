#!/usr/bin/env python3
# pip install google-api-python-client requests youtube_transcript_api
# Example channel id: UCTAfm-YD2M9xzvbYvRc5ttA
import os, sys, re, requests, xml.etree.ElementTree as ET
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound

UA, OUT, LOG = {"User-Agent": "Mozilla/5.0"}, "transcripts", "no_captions.log"
PAT_ID = r"UC[\w-]{22}"

def chan_id(arg: str) -> str:
    if re.fullmatch(PAT_ID, arg):
        return arg
    if m := re.search(r"/channel/(%s)" % PAT_ID, arg):
        return m.group(1)
    html = requests.get(arg, headers=UA, timeout=10).text
    m = re.search(r'"channelId":"(%s)"' % PAT_ID, html)
    return m.group(1) if m else sys.exit("resolve id")

def sanitize(t: str) -> str:
    return re.sub(r"\s+", "_", re.sub(r"[^\w\s-]", "", t).strip().lower())[:100] or "untitled"

def caption(vid: str) -> str:
    try:
        return "\n".join(l["text"] for l in YouTubeTranscriptApi.get_transcript(vid, languages=["en"]))
    except (TranscriptsDisabled, NoTranscriptFound, ET.ParseError):
        return "_no captions_"
    except Exception:
        return "_error_"

def main():
    if len(sys.argv) < 2:
        sys.exit("usage: script <channel_url|id|handle> [n]")
    n  = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    key = os.getenv("YT_API_KEY") or sys.exit("export YT_API_KEY")
    yt  = build("youtube", "v3", developerKey=key)
    cid = chan_id(sys.argv[1])
    upl = yt.channels().list(id=cid, part="contentDetails").execute()["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

    vids, page = [], None
    while len(vids) < n:
        res = yt.playlistItems().list(playlistId=upl, part="snippet", maxResults=50, pageToken=page).execute()
        vids += [(it["snippet"]["title"], it["snippet"]["resourceId"]["videoId"]) for it in res["items"]]
        page = res.get("nextPageToken") or ""
        if not page: break
    os.makedirs(OUT, exist_ok=True)
    for title, vid in vids[:n]:
        cap = caption(vid)
        if cap == "_no captions_":                      # ✨ log videos without captions
            with open(LOG, "a", encoding="utf-8") as log:
                log.write(f"https://www.youtube.com/watch?v={vid} {title}\n")
        path = f"{OUT}/{sanitize(title)}.md"
        with open(path, "w", encoding="utf-8") as f:
            f.write(
                f"# {title}\n\n"
                f"[Source YouTube video](https://www.youtube.com/watch?v={vid})\n\n"
                f"{cap}\n"
                
            )
        print(path)

if __name__ == "__main__":
    main()
