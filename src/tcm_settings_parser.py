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
    
    def filter_adas(self, section_title: str) -> dict:
        """Extract ADAS settings for all cars in the specified section."""
        
        section_text = self.extract_section_text(section_title)[1]
        
        # Initialize the dictionary.
        self.adas_settings = {}
        
        # Split by ### headings to get individual car sections.
        car_sections = re.split(r'^###\s+', section_text, flags=re.MULTILINE)
        
        # Skip the first element (text before first car).
        for car_section in car_sections[1:]:
            # Extract car name (first line of the section).
            lines    = car_section.split('\n', 1)
            car_name = lines[0].strip()
            
            if len(lines) < 2:
                continue
                
            car_text = lines[1]
            
            # Initialize inner dictionary for this car.
            adas_settings = {
                "ABS"                 : None,
                "Traction Control"    : None,
                "ESP"                 : None,
                "Drift Assist"        : None,
                "Load Cell Dial Knob" : None
            }
            
            # Find all bullet points ("  - Setting: Value").
            bullet_pattern = re.compile(r'^\s*-\s+([^:]+):\s+(.+)$', re.MULTILINE)
            matches        = bullet_pattern.findall(car_text)
            
            for setting_name, setting_value in matches:
                setting_name  = setting_name.strip()
                setting_value = setting_value.strip()
                
                if setting_name == "Load Cell Dial Knob":
                    # Extract integer from TeX format: $80$ -> 80.
                    load_cell_match = re.search(r'\$(\d+)\$', setting_value)
                    if load_cell_match:
                        adas_settings[setting_name] = int(load_cell_match.group(1))
                elif setting_name in adas_settings:
                    # Remove parenthetical notes: "Sport (explanation)" -> "Sport".
                    clean_value = re.split(r'\s*\(', setting_value)[0].strip()
                    adas_settings[setting_name] = clean_value
            
            # Store in main dictionary.
            self.adas_settings[car_name] = adas_settings
        
        return self.adas_settings


if __name__ == "__main__":
    file = TCMFile("../inputs/tcm_adas_settings.md")
    
    #section_text = file.extract_section_text("Cars With Modified Pro Settings")[1]
    #print(section_text)

    adas_setting = file.filter_adas("Cars With Modified Pro Settings")
    print(adas_setting)
