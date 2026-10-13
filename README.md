# Command-line Python, Java, and Ada environment

This workspace contains environment configuration and dependencies only.
There is no application source, default Run command, or workflow.

## Replit configuration

`.replit` uses the current `modules` and `[nix]` configuration:

- `python-base-3.13` supplies the Replit-managed Python interpreter.
- `stable-25_05` is the newest stable Nix channel available in this workspace.
- Nix packages provide OpenJDK 24, GNAT 15, GPRbuild, Alire, Maven, uv, and
  the scientific/native libraries and command-line tools from the reference.
- Java uses `jdk24`, not the older GraalVM module. The available GraalVM
  module bundles Java 19; it is not the newest stable Java in this channel.
- `gcc15` and `gnat15` replace the reference's older default GCC/GNAT.

No `replit.nix` is used. Replit restores the declared toolchains from `.replit`.
Commit `.replit`, `.python-version`, `pyproject.toml`, and `uv.lock`.
Do not commit the generated Python environment.

## Verified toolchain versions

| Tool | Installed version |
| --- | --- |
| Python | 3.13.11 |
| uv | 0.7.20 |
| Java runtime / compiler | OpenJDK 24.0.1, build 24.0.1+9 |
| GNAT Ada compiler / GNATMAKE | 15.1.0 |
| GCC | 15.1.0 |
| Alire | 2.1.0 |
| Maven | 3.9.9 |
| GPRbuild | Nix package 25.0.0; executable reports `GPRBUILD Pro 18.0w (19940713)` |

These are the latest stable Python module and relevant versioned Nix packages
available in the workspace's supported catalogue, not necessarily the newest
upstream releases. Python 3.14 is available through Nix only as `3.14.0b4`
(a prerelease), so it is excluded. Java 25/26 packages are unavailable in this
catalogue. uv is limited to 0.7.20 by this channel. No prereleases are selected.

## Restore and use Python dependencies

From the Replit Shell:

```sh
uv sync --locked
uv run --locked python
uv run --locked python your_script.py
```

`.python-version` selects Python 3.13.11. The project supports only Python
3.13 (`>=3.13,<3.14`), matching the verified toolchain. uv interpreter downloads
are disabled: the project uses Replit's native-library-configured interpreter.
The project is an environment, not an installable application package.

Replit sets `UV_PROJECT_ENVIRONMENT` to `.pythonlibs`; uv used that directory
here. Where that variable is absent, uv uses `.venv`. Both are ignored in Git.

`uv.lock` was freshly resolved with `uv lock --upgrade`; it records exact
versions and artifact hashes. Normal restoration uses `--locked`, not
`--upgrade`. To intentionally update dependencies:

```sh
uv add package-name
uv lock --upgrade
uv sync --locked
```

### Installed Python distributions

| Distribution | Exact version |
| --- | --- |
| astropy | 8.0.1 |
| astropy-iers-data | 0.2026.10.12.1.3.27 |
| contourpy | 1.4.0 |
| cycler | 0.12.1 |
| fonttools | 4.66.1 |
| kiwisolver | 1.5.1 |
| matplotlib | 3.11.2 |
| mpmath | 1.3.0 |
| numpy | 2.5.4 |
| packaging | 26.3 |
| pandas | 3.0.6 |
| pillow | 12.3.0 |
| pyerfa | 2.0.1.5 |
| pyparsing | 3.3.3 |
| python-dateutil | 2.9.0.post0 |
| pyyaml | 6.0.3 |
| scipy | 1.18.1 |
| six | 1.17.0 |
| sympy | 1.14.0 |
| uncertainties | 3.2.3 |

The lockfile additionally contains `tzdata==2026.5` for Windows; it is not
installed on this Linux workspace.

## Java

```sh
javac YourProgram.java
java YourProgram
```

Maven's Nix wrapper defaults to its bundled Java **21.0.7+6**, independently
of the Shell's Java 24. To run Maven with the installed Java 24:

```sh
JAVA_HOME="$(dirname "$(dirname "$(readlink -f "$(command -v javac)")")")" mvn -version
JAVA_HOME="$(dirname "$(dirname "$(readlink -f "$(command -v javac)")")")" mvn package
```

## Ada

```sh
gnatmake your_program.adb
./your_program
alr --version
```

GNAT successfully compiled and ran a temporary Ada program using
`Ada.Numerics.Long_Elementary_Functions`. Java compilation and execution also
passed. Test source and outputs were placed under `/tmp`, not in this project.

### GPRbuild compatibility limit

GPRbuild is installed, but project builds did **not** pass verification:
automatic compiler/runtime discovery stalled while scanning `/nix/store`.
Both normal discovery and explicit compiler-path discovery timed out.
Its version banner also differs from the Nix package version as noted above.
Use the verified `gnatmake` command for single-file Ada builds; do not treat
GPRbuild or Alire project builds as verified by this setup.

## Verification commands

```sh
python --version
uv --version
java -version
javac -version
gnatmake --version
gprbuild --version
alr --version
uv lock --check
uv run --locked python -c "import numpy, pandas, scipy, sympy, matplotlib, astropy, uncertainties; print('All scientific imports passed')"
```

All seven direct Python dependencies imported successfully. A native SciPy
linear-system solve and Matplotlib headless PNG rendering also passed.
Interactive GTK/Tk windows are not verified in this command-line environment;
use a headless Matplotlib backend (`Agg`) for file output.
