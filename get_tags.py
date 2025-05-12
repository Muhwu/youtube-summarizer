#!/usr/bin/env python3
from pathlib import Path
import re

root = Path("chapters")
tag_pattern = re.compile(r"#([\w\-]+)")
tags = set()

for md in root.rglob("*.md"):
    with md.open(encoding="utf-8") as f:
        for _ in range(5):                 # scan first 5 lines (or until blank)
            line = f.readline()
            if not line or not line.strip():
                break
            tags.update(tag_pattern.findall(line.lower()))

print(sorted(tags))
