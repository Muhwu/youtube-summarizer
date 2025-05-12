#!/usr/bin/env python3
# pip install google-api-python-client youtube_transcript_api requests
import os, sys, re, xml.etree.ElementTree as ET
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound

INFILE, OUTDIR, LOG = "no_captions.log", "transcripts", "still_no_captions.log"
PAT_VID = r"(?:v=|\/)([0-9A-Za-z_-]{11})(?=[?&\/]|$)"

def video_id(url: str) -> str:
    m = re.search(PAT_VID, url)
    if not m:
        raise ValueError("bad url")
    return m.group(1)

def sanitize(t: str) -> str:
    return re.sub(r"\s+", "_", re.sub(r"[^\w\s-]", "", t).strip().lower())[:100] or "untitled"

def caption(vid: str) -> str:
    try:
        return "\n".join(l["text"] for l in YouTubeTranscriptApi.get_transcript(vid, languages=["en"]))
    except (TranscriptsDisabled, NoTranscriptFound, ET.ParseError):
        return "_no captions_"
    except Exception:
        return "_error_"

def title_api(vid: str, yt):
    res = yt.videos().list(id=vid, part="snippet").execute()
    return res["items"][0]["snippet"]["title"] if res["items"] else vid

def main():
    key = os.getenv("YT_API_KEY") or sys.exit("export YT_API_KEY")
    yt  = build("youtube", "v3", developerKey=key)
    os.makedirs(OUTDIR, exist_ok=True)
    open(LOG, "w").close()                                           # reset log
    with open(INFILE, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            url, *rest = line.split(maxsplit=1)
            vid   = video_id(url)
            title = rest[0] if rest else title_api(vid, yt)
            cap   = caption(vid)

            if cap == "_no captions_":
                with open(LOG, "a", encoding="utf-8") as lf:
                    lf.write(f"{url} {title}\n")
                continue

            path = f"{OUTDIR}/{sanitize(title)}.md-2"
            with open(path, "w", encoding="utf-8") as md:
                md.write(
                    f"# {title}\n\n"
                    f"{cap}\n\n"
                    f"[Source YouTube video]({url})\n"
                )
            print(path)

if __name__ == "__main__":
    main()
