#!/usr/bin/env python3
import re
from pathlib import Path

ROOT = Path("src/docai")
patterns = [
    (re.compile(r"\bdocai\.models\b"), "docai.shared.models"),
    (re.compile(r"\bdocai\.utils\b"), "docai.shared.utils"),
]

for fn in ROOT.rglob("*.py"):
    text = fn.read_text(encoding="utf-8")
    new_text = text
    for pattern, repl in patterns:
        new_text = pattern.sub(repl, new_text)
    if new_text != text:
        fn.write_text(new_text, encoding="utf-8")
        print(f"Updated imports in {fn}")
