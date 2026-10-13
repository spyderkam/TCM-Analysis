---
name: Toolchain verification limits
description: Replit Nix toolchain version reporting and Ada discovery caveats
---

Verify executable versions and compilation, not only Nix package metadata.

**Why:** The supported channel's GPRbuild package identified itself differently
in its version banner. GPRbuild and explicit-path GPRconfig discovery both
stalled scanning the shared `/nix/store`, despite GNAT single-file compilation
and long-float numerics working.

**How to apply:** Report both package metadata and executable output when they
disagree. Put a timeout on Ada project discovery and distinguish GNAT compiler
verification from GPRbuild/Alire project-build verification. Do not claim an
installed project build tool works solely because its version command succeeds.
