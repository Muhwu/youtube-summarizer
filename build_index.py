#!/usr/bin/env python3
# Build readme.md with tag index for files in ./chapters
from pathlib import Path
import re
from collections import defaultdict

root = Path("chapters")
tag_re = re.compile(r"#([\w\-]+)")
tags = defaultdict(list)

for md in root.rglob("*.md"):
    if md.name.lower() == "readme.md":
        continue
    with md.open(encoding="utf-8") as f:
        for _ in range(5):
            line = f.readline()
            if not line:
                break
            tags_in_line = tag_re.findall(line)
            if tags_in_line:
                for t in tags_in_line:
                    tags[t.lower()].append(md)
            if not line.strip():
                break

out = []
for tag in sorted(tags):
    out.append(f"#{tag}")
    for fp in sorted(set(tags[tag])):
        path = fp.as_posix()          # e.g. chapters/file.md
        out.append(f"* [{fp.name}]({path})")
    out.append("")                    # blank line between tags

Path("readme.md").write_text("\n".join(out), encoding="utf-8")
print("readme.md generated.")
