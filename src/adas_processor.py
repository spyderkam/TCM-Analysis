#!/usr/bin/env python3

""" 
This script parses a *The Crew Motorfest (TCM)* ADAS markdown file, extracts each car’s Advanced
Driver Assistance System (ADAS) settings, and stores them in a searchable structure. It builds a
dictionary (self.adas_settings) mapping car names to their raw ADAS values, then provides
filter_adas which:

  1. Normalizes user‑supplied filter values (case‑insensitive, with “off” automatically mapped to
     “completely off”).
  2. Validates filters against allowed option sets.
  3. Scans the stored ADAS hash and returns a tuple containing:
       - A set containing a single ADASConfig that reflects the universal filter criteria you
         supplied (or None for any criterion you omitted, e.g., load_cell).
       - A set of car names that satisfy those criteria.

The script can be run as a standalone tool: it reads the markdown file, builds the ADAS hash for the
“Cars With Modified Pro Settings” section, and demonstrates filtering for a typical “Sport”
configuration. It is designed for easy extension (e.g., adding more filters or processing additional
sections).
"""

__author__ = "@spyderkam"
__date__   = "October 13, 2026 – October 20, 2026"

from pathlib import Path
from typing  import Tuple, Set, NamedTuple
import re


class ADASConfig(NamedTuple):
    """Immutable representation of a single car's ADAS settings."""
    abs_             : str
    traction_control : str
    esp_             : str
    drift_assist     : str
    load_cell        : int


class TCMFile:
    """Class of TCM input file."""

    # Canonical alias map and normaliser shared by filter_adas().
    _CANONICAL = {
        "on"            : "on",
        "off"           : "completely off",   # alias → canonical
        "completely off": "completely off",
        "comfort"       : "comfort",
        "sport"         : "sport",
    }

    @staticmethod
    def _norm_synonym(val: str | None, allowed: set[str]) -> str | None:
        """
        Lower‑case, validate against `allowed`, then resolve known synonyms.
        Returns the canonical representation or None.
        """
        if val is None:
            return None
        low = val.strip().lower()
        if low not in allowed:
            raise ValueError(f"Invalid value {val!r}; allowed: {allowed}")
        # Resolve alias (e.g. "off" → "completely off").
        return TCMFile._CANONICAL.get(low, low)

    def __init__(self, file_path: str) -> None:
        path = Path(file_path)

        self.file_path = path
        self.file_name = path.name
        self.file_type = path.suffix.lstrip('.')

        if not path.is_file():
            exit("File not found.")

        self.full_text = path.read_text(encoding="utf-8")

    def adas_hash(self, section_title: str) -> dict:
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
                "ABS":                 None,
                "Traction Control":    None,
                "ESP":                 None,
                "Drift Assist":        None,
                "Load Cell Dial Knob": None,
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
                    clean_value                 = re.split(r'\s*\(', setting_value)[0].strip()
                    adas_settings[setting_name] = clean_value

            # Store in main dictionary.
            self.adas_settings[car_name] = adas_settings

        # Having both a self variable and returning it allows for flexibility
        # This could be handy with ADAS settings under multiple sections.
        return self.adas_settings

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

    def filter_adas(
        self,
        abs_setting      : str | None = None,
        traction_control : str | None = None,
        esp_setting      : str | None = None,
        drift_assist     : str | None = None,
        load_cell        : int | None = None,
    ) -> Tuple[Set[ADASConfig], Set[str]]:
        """
        Returns
        _______
        Tuple
            1. A single‑element set containing an ADASConfig that reflects the
               universal filter criteria you supplied (None for any omitted 
               criterion).
            2. A set of car names that satisfy those criteria.

        Parameters
        ----------
        abs_setting, traction_control, esp_setting, drift_assist : str, optional
            Expected values are case‑insensitive and must belong to the
            respective allowed sets (e.g., {"on", "completely off"}).
        load_cell : int, optional
            Exact load cell value to match (no dollar signs).

        Raises
        ------
        AttributeError
            If self.adas_settings has not been created yet.
        ValueError
            If a supplied option is not in the permitted set.
        """

        # Ensure the hash exists.
        if not hasattr(self, 'adas_settings'):
            raise AttributeError("ADAS dictionary not generated; call adas_hash first")

        # Allowed value sets (include the alias “off”).
        abs_ok   = {"on",               "off", "completely off"}
        tc_ok    = {"comfort", "sport", "off", "completely off"}
        esp_ok   = {"comfort", "sport", "off", "completely off"}
        drift_ok = {"comfort", "sport", "off", "completely off"}

        # Normalise all filters using the shared helper.
        abs_setting      = TCMFile._norm_synonym(abs_setting,      abs_ok)
        traction_control = TCMFile._norm_synonym(traction_control,  tc_ok)
        esp_setting      = TCMFile._norm_synonym(esp_setting,      esp_ok)
        drift_assist     = TCMFile._norm_synonym(drift_assist,   drift_ok)

        # Build the universal ADASConfig set (single element).
        universal_cfg = ADASConfig(
            abs_             = abs_setting,
            traction_control = traction_control,
            esp_             = esp_setting,
            drift_assist     = drift_assist,
            load_cell        = load_cell,
        )
        universal_set: Set[ADASConfig] = {universal_cfg}

        # Find car names that match the supplied criteria.
        matched_cars: Set[str] = set()

        for car_name, cfg in self.adas_settings.items():
            if abs_setting and cfg["ABS"].lower() != abs_setting:
                continue
            if traction_control and cfg["Traction Control"].lower() != traction_control:
                continue
            if esp_setting and cfg["ESP"].lower() != esp_setting:
                continue
            if drift_assist and cfg["Drift Assist"].lower() != drift_assist:
                continue
            if load_cell is not None and cfg["Load Cell Dial Knob"] != load_cell:
                continue
            matched_cars.add(car_name)

        return universal_set, matched_cars


if __name__ == "__main__":
    """Example usage."""

    tcm_file = TCMFile("../inputs/tcm_adas_settings.md")
    tcm_file.adas_hash("Cars With Modified Pro Settings")

    general_adas_hash = {
        "ABS"                 : "On",
        "Traction Control"    : "Sport",
        "ESP"                 : "Off",
        "Drift Assist"        : "Sport",
        "Load Cell Dial Knob" : None
    }

    universal_set, matching_cars = tcm_file.filter_adas(
        abs_setting      = general_adas_hash["ABS"],
        traction_control = general_adas_hash["Traction Control"],
        esp_setting      = general_adas_hash["ESP"],
        drift_assist     = general_adas_hash["Drift Assist"],
        load_cell        = general_adas_hash["Load Cell Dial Knob"],
    )

    print("Universal ADAS configurations:")
    for feature, setting in general_adas_hash.items():
        if setting is not None and setting.lower() == "off":
            print(f"  {feature}: Completely OFF")
        else:
            print(f"  {feature}: {setting}")
    
    print("\nCars that satisfy those criteria:")
    for car in matching_cars:
        print(f"  {car}")
