#!/usr/bin/env python3

__author__ = "@spyderkam"
__date__   = "October 13, 2026 – October 19, 2026"

from pathlib import Path
import re


# 1️⃣ Create a Path object and store the needed section title.
file_path = Path("inputs/tcm_adas_settings.md")
section_title = "Cars With Modified Pro Settings"

# 2️⃣ Check whether the file exists.
if not file_path.is_file():
    exit("File not found.")
    
# 3️⃣ Read the file in one line.
text = file_path.read_text(encoding="utf-8")

# 4️⃣ Extract only the text of <section_title>.
r"""
  - (?P<heading>#{1,3}) : Captures the heading level (#, ##, or ###).
  - [ \t]+              : Requires at least one space/tab after the hashes.
  - [^\n]*?             : Matches a prefix (numbers, &nbsp;, spaces, etc.) on this line only.
  - {title}             : Matches the exact section title literally.
  - [ \t]*(?:\n|\Z)     : Allows trailing whitespace and a heading at end of file.
  - Double quantifier braces in an f-string to preserve literal regex braces.
  - Stop at the next heading of the same or higher level, retaining subsections.
"""
pattern = re.compile(
    rf"^(?P<heading>#{{1,3}})[ \t]+[^\n]*?{re.escape(section_title)}[ \t]*(?:\n|\Z)",
    re.MULTILINE,
)

match = pattern.search(text)
if match is None:
    exit("Section not found.")

next_heading = re.compile(
    rf"^#{{1,{len(match.group('heading'))}}}[ \t]+",
    re.MULTILINE,
).search(text, match.end())
section_end = next_heading.start() if next_heading else len(text)
section_text = text[match.end():section_end].strip()
print(section_text)
