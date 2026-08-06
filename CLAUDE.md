# Onslaught Toolkit

Status: active — Claude Code bootstrap; rules and routing only.
Last updated: 2026-08-06.
Summary: load the authoritative contributor contract, current state, and the
right evidence owner without duplicating them here.

[`AGENTS.md`](AGENTS.md) is the authoritative contributor contract. Claude Code
does not automatically load it: open and read it in full before changing files
or making evidence claims. This file does not restate or override it.

## Mission

This is one full-scope project with three coequal outcomes: completely reverse
the retail game so it can be understood, preserved, patched, and modded; rebuild
it in Godot at 1:1 behavioral and experiential parity; and ship the polished
WinUI 3 preservation toolkit. They reinforce one another. None is a side lane or
lower priority; the current goal selects focus, not rank. A function name without
a bounded contract is not completion.

## Start here

1. [`README.MD`](README.MD) — repository and product orientation.
2. [`PROJECT-INDEX.md`](PROJECT-INDEX.md) — source ownership, application flow,
   and dependency direction.
3. [`AGENTS.md`](AGENTS.md) — safety, evidence, delegation, and validation.
4. [`GOAL.md`](GOAL.md) — standing outcomes and acceptance targets.
5. [`developer_state.json`](developer_state.json) — resumable state and exact
   evidence pointers. Treat it as awareness, never as truth that primary
   evidence cannot overturn. For complete-RE tip census and Ghidra-apply
   authorization, open key `complete_re_tip_20260805` (and
   `cumulative_checkpoints` when present). Prefer the path named as
   FINAL-3WAY-DELTA over Gen10 “current handoff” prose in GOAL/DELTA.
6. `local-lab/INDEX.md`, when present — ignored working evidence invisible to a
   fresh clone.
7. The owning lane: [`reverse-engineering/RE-INDEX.md`](reverse-engineering/RE-INDEX.md)
   (live tip first, historical Gen10 demoted),
   [`rebuild/PROVENANCE.md`](rebuild/PROVENANCE.md), or [`CLI.md`](CLI.md).

Current user intent, code, runtime behavior, and primary evidence outrank stale
documentation. Supersede a stale claim in place; do not preserve parallel truth.
Do not paste live C1/OPAQUE numbers into this file.

## Stop signs before any write

- Never mutate the pristine `74154bfa…` specimen.
- Never make an irreversible user-file change without explicit informed choice
  and a verified pre-write backup; never destroy career saves as a side effect.
- Never track retail binaries/assets, converted retail material, arbitrary
  saves, raw debugger logs, bulky captures, Ghidra backups, or secrets.
- Never turn source intent, decompiler output, a document label, or an agent's
  opinion into a retail-behavior claim without the evidence required by
  `AGENTS.md`.

## Operating posture

- Use everything legitimately shipped as potential evidence—RTTI, strings,
  `FILE` paths, registries, asserts, dormant loggers, resources, data, and
  traces—but reproduce and grade every conclusion against the pristine
  specimen or controlled copied runtime.
- Recursively move unknown functions and ranges toward exact identities,
  contracts, patch/mod value, and reconstruction owners/tests. Preserve open
  questions and the cheapest falsifier instead of filling gaps with plausible
  names.
- Delegate independent measurement and adversarial review when useful. Verify a
  background reviewer actually began; a spawn receipt is not liveness. Treat
  every report as input to reproduce, not authority to publish or promote.
- The presence of a Ghidra MCP connection grants access, not permission to
  mutate the maintainer project. Follow the promotion gate in `AGENTS.md` and
  `reverse-engineering/ghidra/README.md`.

## Context hygiene

Keep this file to stable rules and pointers. Current resumable state belongs in
`developer_state.json`; detailed findings and raw evidence belong to their
tracked or ignored owners. A finding should enter always-loaded context only
when it remains valid even if its underlying measurement is later overturned.

Keep `developer_state.json` current as evidence lands, but always include the
path, identity, or test that can recheck it. Measurements win when state and
reality disagree.
