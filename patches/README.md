# BEA.exe patch catalog

The two JSON catalogs in this directory are the only active executable-patch
sources:

- [patch rows](catalog/patches.v2.json)
- [safe-copy profiles](catalog/safe-copy-profiles.v1.json)

WinUI and AppCore own verification, planning, apply, backup, restore, and
copied-target enforcement. Retired standalone Python patchers are available in
Git history; keeping a second mutation implementation made the safety contract
harder to reason about.

## What is automated

Focused AppCore tests verify the supported clean Steam specimen identity,
expected original bytes, dependencies and conflicts, safe-copy boundaries,
atomic apply, backup integrity, and full-file restore. A catalog row whose
original bytes do not match is refused.

These checks prove byte and filesystem behavior. They do not by themselves
prove that a patch produces the advertised visible or gameplay effect.

## Retail evidence boundary

Some rows have bounded copied-runtime observations documented under
[reverse-engineering/binary-analysis](../reverse-engineering/binary-analysis/).
Those observations are useful evidence, but their private captures are not
reproducible from a clean public checkout. User-facing copy must therefore keep
the distinction clear:

- **bytes checked**: exact supported-specimen mutation is known;
- **observed**: the cited bounded copied-runtime effect was seen;
- **unproven**: broader compatibility, gameplay safety, control feel, and
  parity remain open.

The default safe-copy profile is the narrow compatibility pair. Experimental
rows stay opt-in and must not be promoted by changing catalog prose alone.

## Safety

Never patch an installed game directory or its original `BEA.exe`. Create an
app-owned safe copy through Windowed & Mods, verify the selected rows, and use
the generated full-file backup for restore. The installed game remains
read-only.

Schema, dependency, evidence-reference, and mutation rules are in
[CATALOG_CONTRACT.md](CATALOG_CONTRACT.md).
