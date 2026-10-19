#!/usr/bin/env python3

__author__ = "@spyderkam"
__date__   = "October 13, 2026 – October 19, 2026"

from pathlib import Path
import os
import re


class TCMFile:
    """Class of TCM input file."""

    def __init__(self, file_path: str) -> None:
        path = Path(file_path)
        
        self.file_path = path
        self.file_name = path.name
        self.file_type = path.suffix.lstrip('.')

        if not path.is_file():
            exit("File not found.")

        self.full_text = path.read_text(encoding="utf-8")

    def extract_section_text(self, section_title: str) -> tuple[str, str]:
        """Method to extract the text of a specific section."""
        
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
        
        match = pattern.search(self.full_text)
        if match is None:
            exit("Section not found.")
        
        next_heading = re.compile(
            rf"^#{{1,{len(match.group('heading'))}}}[ \t]+",
            re.MULTILINE,
        ).search(self.full_text, match.end())
        section_end  = next_heading.start() if next_heading else len(self.full_text)
        section_text = self.full_text[match.end():section_end].strip()

        return f"# {section_title}", section_text


if __name__ == "__main__":
    file = TCMFile("../inputs/tcm_adas_settings.md")
    section_text = file.extract_section_text("Cars With Modified Pro Settings")[1]
    print(section_text)
