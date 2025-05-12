#!/usr/bin/env python3
# pip install google-generativeai

import os, re, glob, sys
from google import genai
from google.genai import types

# folders
SRC = "transcripts"
DST = "chapters"
os.makedirs(DST, exist_ok=True)

# Gemini client
client = genai.Client(vertexai=True, project="muhwu-com", location="us-central1")
model_id = "gemini-2.5-pro-preview-05-06"

cfg = types.GenerateContentConfig(
    temperature=1,
    top_p=0.95,
    max_output_tokens=8192,
    response_modalities=["TEXT"],
    safety_settings=[
        types.SafetySetting(category=c, threshold="OFF")
        for c in (
            "HARM_CATEGORY_HATE_SPEECH",
            "HARM_CATEGORY_DANGEROUS_CONTENT",
            "HARM_CATEGORY_SEXUALLY_EXPLICIT",
            "HARM_CATEGORY_HARASSMENT",
        )
    ],
)

template = """You will receive a raw YouTube-video transcript that **begins with a Markdown H1 line (`# …`) containing the video title**.

---

**TASK**

1. You are writing a chapter to a game development e-book and your task is to extract useful actionable information for it.
2. Generate **3 – 6 lowercase tags** prefixed with `#`, each relevant to game-development domains (e.g. `#game_design`, `#audio_design`, `#programming`, `#level_design`, `#visual_effects`).  
3. Write a concise (≤ 3-sentence) professional summary of the transcript’s main topic.
4. Write out the key learnings from this transcript as a concise, to-the-point, bulleted list
5. Break the remainder of the content into logical sub-chapters, each with a Markdown H2 heading (`## …`) followed by its content.  
6. Remove filler words/greetings; keep useful information only. 
7. For instructions or actionable step type material, arrange it clearly into specific bullet pointed or numbered lists when applicable.

---

**OUTPUT – use *exactly* this Markdown skeleton**

# <<TITLE>>
#tag-1 #tag-2 #tag-3 …

## Summary
<<BRIEF SUMMARY>>

### Key Learnings
<<KEY LEARNINGS>>

## <<sub-chapter title 1>>
<<sub-chapter content>>

## <<sub-chapter title 2>>
<<sub-chapter content>>

*Do not add anything outside this structure.*

---

**TRANSCRIPT**
"""

def sanitize(name: str) -> str:
    return re.sub(r"\s+", "_", re.sub(r"[^\w\s-]", "", name).strip().lower())[:100] or "untitled"

for fp in glob.glob(f"{SRC}/*.md"):
    transcript = open(fp, "r", encoding="utf-8").read()
    title = transcript.splitlines()[0].lstrip("# ").strip() or "untitled"
    prompt  = f"{template}\n{transcript}\n"

    contents = [types.Content(role="user", parts=[types.Part(text=prompt)])]
    resp = client.models.generate_content(model=model_id, contents=contents, config=cfg)
    out_md = resp.candidates[0].content.parts[0].text

    out_path = f"{DST}/{sanitize(title)}.md"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(out_md)
    print(f"Saved → {out_path}")
