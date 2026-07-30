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

## Virtual address ↔ file offset

**Restored 2026-07-29.** Commit `a777a4ea` (2026-07-17, "Refocus toolkit on active
product and rebuild") removed 213 of this file's 247 lines. Most of that was
product-scope prose and is deliberately not resurrected here. But it also carried
the only statement in the tree of how a catalog row's `file_offset` relates to a
virtual address, and three tracked documents plus the catalog's own
`evidence_refs` still cite this file for exactly that. This section restores the
relation, and nothing else.

For this image the mapping is uniform across every section:

```
VA = file_offset + 0x400000
```

`patches/catalog/patches.v2.json` stores `file_offset` only, so a row cannot be
checked against a disassembly or against `reverse-engineering/` addresses without
this line. That gap has already cost real work: the force-windowed offset was
written down as `0x12A6C4` on 2026-07-28 and corrected to `0x12A644` only after an
adversarial pass caught it — the correct pairing had been in the table deleted
here eleven days earlier.

**Every row was re-verified on 2026-07-29** against the pristine specimen
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, sha256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`, which is also
the hash each row already carries in `target_binary_hashes`, and whose size
(2,506,752 bytes) matches every row's `target_binary_size`:

**29 rows checked, 29 `expected_original_bytes` matched, 0 mismatched.**

Reproduce it by reading `file_offset` from each row and comparing that many bytes
of the specimen against `expected_original_bytes`. Do **not** read these bytes
from the installed Steam `BEA.exe` — it is deliberately patched and is not a
specimen.

The catalog remains the single source of truth for offsets, bytes and eligibility.
This section states the address relation and the verification result; it does not
duplicate the rows.

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

The default Enhanced Copy profile is the verified compatibility base: the
complete 28-region widescreen correction, windowed startup, `-res 1600 900`,
retail 16:9 screen shape, and mouse sensitivity `0.1`. Copied Level 100 runtime
proof is limited to the supported Steam specimen and tested machine.
Experimental rows stay opt-in and must not be promoted by catalog prose alone.

## Safety

Never patch an installed game directory or its original `BEA.exe`. Create an
app-owned safe copy through Windowed & Mods, verify the selected rows, and use
the generated full-file backup for restore. The installed game remains
read-only.

Schema, dependency, evidence-reference, and mutation rules are in
[CATALOG_CONTRACT.md](CATALOG_CONTRACT.md).
