# Rebuild parity contract

Status: active — what "1:1 behavioral and experiential parity" means operationally
Last updated: 2026-08-07
Evidence: SOURCE — authority order and the three known divergences are
recorded in `PROVENANCE.md`; gate capabilities are MEASURED claims of the
tracked harnesses named in the table.
Specimen: `BEA.exe.original.backup`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
(the retail addresses cited in the divergences table are from the pristine
specimen; the installed BEA.exe is deliberately patched).
Summary: the gradeable dimensions of parity, the gate each currently has (or
lacks), and the standing exceptions. This document names the gap; it does not
claim the gap is closed.

## Authority order (from PROVENANCE.md)

> **Port Stuart's shape first. Cite the file and line. Override from bytes
> only where measurement proves divergence.**

The pinned `references/Onslaught` source is the architecture and intent
authority. The pristine retail specimen (`74154bfa…`) is the behavior
authority. Where they disagree, the shipped bytes win — but only after a
measurement proves the divergence, and the divergence is recorded.

## Known divergences (measured)

| Divergence | Stuart source | Shipped bytes | Where recorded |
|---|---|---|---|
| `InJetMode` | 0.3 s | 0.5 s | PROVENANCE.md |
| `CPanCamera` length | Stuart value | 6.0 | PROVENANCE.md (VA 0x004198D0, vtable 0x005D92A8) |
| Weapon resource path | pinned path | differing path | PROVENANCE.md |

These are exceptions to record precisely, not templates for loose porting.

## Parity dimensions and their gates

| Dimension | What it means | Current gate | What the gate does / does not prove |
|---|---|---|---|
| **Deterministic sim state** | Identical tick-by-tick simulation given identical inputs | Core cold-start + full-chain tests, `--expect` trace hashes | Proves determinism and self-consistency. Does NOT prove retail equality — retail has no tape to replay against |
| **Visual frame** | Rendered output matches retail within tolerance | `Capture-Frontend.ps1 -Plan mainmenu` + `score_frontend_capture.py` + `frontend-regions-*.json`, `gameplay-regions-level100.json` | Proves region-level visual regression against captured retail references. The JSON thresholds are **regression ceilings, not parity claims** (rebuild README is explicit) |
| **Audio** | Playback behavior matches retail | None (no automated audio gate) | Not gradeable today |
| **Timing / feel** | Response latency, animation cadence feel equivalent | None dedicated | Not gradeable today; 20 Hz step + floor semantics are the strongest proxy |
| **Content completeness** | All retail content reachable/present | Materializer hash checks (200+ pinned inputs), level-100 slice | Proves the retail inputs consumed are byte-exact. Does NOT prove every level plays |

## The honest reading

The lane runs a scoring harness that is documented as *not* measuring the
thing the lane exists to achieve. Visual parity gates are regression
ceilings; there is no gate today that compares rebuild behavior to retail
behavior directly (retail is not automatable in the same harness). This gap
is named here so it is not mistaken for closure.

## What "done" would require (per dimension)

- Sim: a retail-derived expected-trace source (e.g. a verified capture of
  retail's own sequence) or an accepted contract per system.
- Visual: measured tolerance windows per region against retail frames, not
  just self-regression.
- Audio: a playback contract (tracks, triggers, volume semantics).
- Timing/feel: a documented comparison protocol (the maintainer's ear is a
  legitimate instrument for feel; it is not a substitute for the others).
- Content: per-level playthrough evidence, not only input hashes.

## Standing rule

No claim of parity may be published from this file's existence. Parity is
per-dimension, measured, and gated — or it is not parity.
