---
name: User configuration preservation
description: Preserve custom bashrc and vimrc in the workspace configuration directory
---

Do not ignore `.config/` wholesale. Preserve and track custom shell/editor
configuration there; exclude only specific generated cache subdirectories.

**Why:** The user keeps custom `bashrc` and `vimrc` files in `.config`.
A blanket ignore added during environment setup excluded them from Git;
the user subsequently reported them missing. The exact removal event was
not established, and no copies were found in the available Git history.

**How to apply:** Distinguish user-authored configuration from generated
library caches before changing ignore rules. An ignore rule does not itself
delete files; do not claim it proves when or how missing files were removed.

The environment also globally ignores `.config/` through `/etc/.gitignore`.
Removing a project-local ignore alone does not make these files trackable.
Keep an explicit project-level unignore for the directory, and verify
effective ignore behavior rather than only reading the local ignore file.

**Why:** Verification of the recreated configuration still reported it ignored
after removing the local blanket rule; the global exclusion was the remaining
cause. Check both sources before attributing missing configuration to one rule.

**How to apply:** Use `git check-ignore -v` to identify the effective rule.
Recreated baseline settings are not recovered originals; preserve that
distinction when describing or changing them.

Keep one project Vim configuration file at `.config/vimrc`; do not add a
redundant `.config/vim/` loader directory.

**Why:** The user explicitly finds the two-file setup redundant and would
rather do without `.config/vim/`.

**How to apply:** If the user adds custom Vim settings, keep them in the
canonical file rather than introducing another Vim file.

Do not add optional Bash or Vim preferences such as history settings, editor
defaults, or Vim editing settings.

**Why:** The user asked to remove the export if unnecessary and to remove all
Vim settings if none are necessary.

**How to apply:** Leave editing and shell preferences at the installed
platform/tool defaults unless the user requests customization.

Keep the Bash VIMINIT export for automatically loading `.config/vimrc`, with
an explicit explanatory comment above it. No other Bash settings are wanted.

**Why:** After clarifying that Bash sources Bash commands and Vim sources Vim
commands, the user requested re-adding the export with an explicit comment.
This supersedes their earlier selection of manual loading.

**How to apply:** Explain `source .config/bashrc` in Bash, followed by ordinary
Vim startup. Keep the sole Vim file at `.config/vimrc`; do not add a loader
directory or populate Vim preferences.
