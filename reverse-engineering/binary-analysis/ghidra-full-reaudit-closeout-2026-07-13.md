# Ghidra correction authority

Status: current static-metadata authority
Evidence date: 2026-07-13

Two trusted exports agreed on a 6,411-address function inventory and exposed a
459-address metadata delta: 343 comment-only changes, 114 rename-and-comment
changes, and 2 rename-only changes. A fresh semantic review then examined 92
unique correction targets. Ninety-one were confirmed and applied; the proposed
`0x004dac90` ABI correction was rejected because the observed epilogue is
`RET 0x4`, not `RET 0x8`.

The canonical machine-readable record is
[`ghidra-reviewed-correction-plan-2026-07-13.json`](ghidra-reviewed-correction-plan-2026-07-13.json).
It contains the per-address classification, exact before/after name, signature,
comment and prototype keys, fresh-evidence summary, and review rationale. Its
confirmed apply plan SHA-256 is
`a2a5f4210f060d1ce1ecc8f7d11ef041954b7c6951860b3026a32dd857bf2148`.

The confirmed apply changed 26 names, 88 comments, and 9 rendered signatures.
Eight signature edits changed only owner/name or parameter rendering. The one
structured prototype correction was `0x0050b9c0 CWorld__LoadWorld`, whose three
stack arguments are supported by `RET 0x0c`. No function body or boundary and no
game executable byte changed. After save and reopen, all 91 confirmed rows
matched and the final read-only snapshot SHA-256 was
`0fc34624a5683732fcc999e7b9df931b91d2f7f55f096a5dfde207a1ff73d059`.

## How to use this evidence

- Treat the correction plan as provenance and review evidence, not as standing
  authorization to mutate a Ghidra project.
- Prefer current per-function notes under [`functions/`](functions/_index.md)
  for implementation questions; use the plan when a corrected row or exact
  before/after value matters.
- Re-check the local executable specimen and live database before any future
  metadata change. Historical hashes do not prove the state of another local
  project.
- The 6,411-address inventory is accounting evidence, not proof that every
  name, type, layout, or semantic interpretation is correct.

## Claim boundary

This is static metadata, instruction, decompile, xref, and bounded source-shape
evidence. It does not establish runtime gameplay, patch safety, exact source
identity, visual or online behavior, or rebuild parity. Ghidra databases,
backups, executables, raw exports, and proprietary payloads remain local and
untracked.
