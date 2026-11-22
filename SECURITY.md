# Security And Private Data Reporting

Status: active disclosure guidance
Last updated: 2026-11-21 (updated for the repurposed Onslaught Modding & Content Toolkit; retired Companion GUI references removed)
Summary: how to report a defect that touches local paths, generated outputs, mod staging or private data boundaries, and the safety contracts a report is judged against.

The Onslaught Modding & Content Toolkit reads local game installations and produces private local catalogues, inventories, format reports and staged mod folders. Reports should expose only what is needed to reproduce the defect.

## Consequential safety contracts

- Every Toolkit reader and inspector treats the selected game installation as read-only and never modifies or patches game files or executables.
- Writing tools publish through `tools/safe_generated_output.py` (descriptor-relative no-follow directory traversal, atomic rename, refusal of symlinks, hard links, existing destinations or output roots overlapping a protected game installation).
- Generated catalogues and inventories use bundle-relative paths, carry the generated-retail-derived JSON marker (refused from Git by `npm run test:safety`) and stay inside ignored `local-data/`.
- Save-related logic never synthesizes `.bes` saves from scratch and preserves unknown bytes.

These contracts protect data and filesystem integrity. They do not establish format completeness, gameplay compatibility or runtime parity.

## Report privately

Use GitHub's private vulnerability reporting (the repository's Security tab, "Report a vulnerability": https://github.com/dlprentice/Onslaught-Career-Editor/security/advisories/new) for:

- leaked secrets, credentials, private paths or machine identifiers;
- any tool writing into a game installation, following symlinks or escaping its selected output root;
- tracked retail payloads, raw debugger/runtime captures, Ghidra projects or unreviewed bulk game data that should not be posted publicly.

In the first report, include the affected path and commit, the command or action, high-level reproduction steps and the smallest redacted evidence. Do not paste secrets, executable/save bytes, machine-local paths or raw captures.

## Other repositories

Each public repository has its own `SECURITY.md` and private vulnerability reporting form:
[Onslaught CE](https://github.com/dlprentice/onslaught-ce/security/policy),
[onslaught-decomp](https://github.com/dlprentice/onslaught-decomp/security/policy),
[onslaught-godot](https://github.com/dlprentice/onslaught-godot/security/policy) and
[onslaught-preservation](https://github.com/dlprentice/onslaught-preservation/security/policy).
Report a problem in the repository that owns the affected files ([Where to contribute](CONTRIBUTING.md#where-to-contribute)).

## Public reports

Source-code bugs, documentation defects, redacted validation failures and feature requests are normally safe to discuss publicly. Do not attach local retail payloads or generated retail catalogues.

## License and asset boundary

Project code and schemas are GPL-3.0-only under [`LICENSE`](LICENSE); documentation, format-contract tables and lore are CC BY-SA 4.0, as [`REUSE.toml`](REUSE.toml) maps them. `references/Onslaught` and `references/AYAResourceExtractor` keep their own licences.

Retail game files and converted copies remain user-supplied local inputs and must not be committed, attached to reports or packaged. Repository licenses grant no rights in the retail executable, game assets, trademarks or third-party components. The pinned reference submodules and [`tests_shared/fixtures/gold_career_save.bin`](tests_shared/fixtures/README.md) are explicit repository exceptions with separate provenance and terms; no Ghidra project is tracked.
