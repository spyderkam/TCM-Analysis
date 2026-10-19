#!/usr/bin/env python3

__author__ = "@spyderkam"
__date__   = "October 13, 2026"

from pathlib import Path


# 1️⃣ Create a Path object (the constructor accepts a normal string).
file_path = Path("path/to/my_file.md")

# 2️⃣ Check whether the file exists.
if file_path.is_file():
    print("File is present!")
else:
    exit("File not found.")
    
# 3️⃣ Read the file in one line.
text = file_path.read_text(encoding="utf-8")
