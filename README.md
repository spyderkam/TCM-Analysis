# Motorfest ADAS Analysis

Parse and filter vehicle assistance settings for **The Crew Motorfest**.
The project reads a Markdown reference file and finds cars whose recorded
Advanced Driver Assistance Systems (ADAS) settings match your chosen criteria.

**Author:** @spyderkam

## What it does

- Extracts a named Markdown section while retaining its nested car entries.
- Builds a dictionary of each car's ABS, traction control, ESP, drift assist,
  and load-cell dial settings.
- Filters cars by any combination of those five settings.
- Accepts case-insensitive text filters and treats `off` as an alias for
  `completely off`.
- Prints a demonstration query and its matching cars in alphabetical order.

This is an early-stage, offline analysis tool for the supplied settings—not
a connection to the game. It does not change in-game settings, simulate
vehicle physics, or generate tuning recommendations.

## Requirements

- **Python 3.13**, as specified by the project's Python version constraint.
- **uv** for restoring the locked Python environment and running examples.

The current ADAS processor uses only Python's standard library. The repository
also declares a broader scientific environment, but those packages are not
required by the parser itself. Java and Ada are development toolchains, not
runtime requirements for this script.

For the environment setup, recorded toolchain versions, and compatibility
notes, see [DEVELOPMENT.md](DEVELOPMENT.md).

## Quick start

From the repository root:

```sh
uv sync --locked
(cd src && uv run --locked python adas_processor.py)
```

The included demonstration reads `inputs/tcm_adas_settings.md` and selects
cars with:

| Setting | Filter |
| --- | --- |
| ABS | On |
| Traction Control | Sport |
| ESP | Completely Off |
| Drift Assist | Sport |
| Load Cell Dial Knob | Unrestricted |

It prints the selected criteria followed by the matching car names.

**Working directory matters:** the script currently uses
`../inputs/tcm_adas_settings.md`, relative to the process's working directory.
Use the command above; running `uv run --locked python src/adas_processor.py`
directly from the root will report `File not found.`

There are no command-line filter flags yet. Change the demonstration's
`general_adas_hash` dictionary or use the Python interface below for your
own query.

## Filter from Python

Start Python from the repository root:

```sh
uv run --locked python
```

Then:

```python
from src.adas_processor import TCMFile

tcm = TCMFile("inputs/tcm_adas_settings.md")
settings_by_car = tcm.adas_hash("Cars With Modified Pro Settings")

criteria, matching_cars = tcm.filter_adas(
    abs_setting="on",
    traction_control="sport",
    esp_setting="off",
    drift_assist="sport",
    load_cell=None,
)

print(f"Parsed {len(settings_by_car)} cars")
for car in sorted(matching_cars):
    print(car)
```

Call `adas_hash()` before `filter_adas()`. Each call to `adas_hash()` replaces
the stored dictionary with settings from the requested section.

### Available filters

| Argument | Accepted values |
| --- | --- |
| `abs_setting` | `on`, `off`, `completely off` |
| `traction_control` | `comfort`, `sport`, `off`, `completely off` |
| `esp_setting` | `comfort`, `sport`, `off`, `completely off` |
| `drift_assist` | `comfort`, `sport`, `off`, `completely off` |
| `load_cell` | An integer for an exact match |

All arguments default to `None`, which leaves that setting unrestricted.
Supplied criteria must all match. Omitting every argument returns all parsed
cars.

Text filters ignore case and surrounding whitespace. Invalid text options
raise `ValueError`. The load-cell reference uses values from 0 to 100; the
current code does not validate that range or apply a tolerance.

`filter_adas()` returns a tuple containing:

1. A single-element set containing an `ADASConfig` with the normalized query
   criteria, using `None` for omitted criteria.
2. A set of matching car names. Use `sorted()` when displaying it for
   consistent ordering.

## Input format

The included reference is `inputs/tcm_adas_settings.md`. The parser expects
level-three headings for cars and named bullet points for their settings,
inside the selected section:

```markdown
## Cars With Modified Pro Settings

### Example Car

  - ABS: ON
  - Traction Control: Sport
  - ESP: Completely OFF
  - Drift Assist: Sport
  - Load Cell Dial Knob: $80$
```

Use the setting names shown above. Load-cell values are extracted from
dollar-delimited integers such as `$80$`. Parenthetical notes following text
settings are removed during parsing.

The selected section ends at the next heading of the same or a higher level,
so subsequent sections are not treated as car entries.

## Current limitations

- Input must follow the expected Markdown structure and contain complete
  settings for the fields being filtered; this is not a general Markdown
  parser or a comprehensive data validator.
- Missing files or sections terminate processing with `File not found.` or
  `Section not found.`
- Filtering before calling `adas_hash()` raises `AttributeError`.
- Results reflect the reference file's recorded settings, not live game data
  or independent verification of those recommendations.

## Project layout

```text
inputs/tcm_adas_settings.md  Vehicle settings reference
src/adas_processor.py       Section extraction, ADAS parsing, and filtering
README.md                   Project overview and usage
DEVELOPMENT.md              Environment and toolchain documentation
pyproject.toml              Python version constraint and dependencies
uv.lock                     Reproducible Python dependency lockfile
```
