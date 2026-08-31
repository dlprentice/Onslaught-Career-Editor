# Onslaught Toolkit

Status: active — Claude Code bootstrap; rules and routing only.
Last updated: 2026-08-31.
Summary: load the authoritative contributor contract, current state, and the
right evidence owner without duplicating them here.

First read the workspace contract at [`../../AGENTS.md`](../../AGENTS.md), then
read the authoritative repository contract at [`AGENTS.md`](AGENTS.md) in full
before changing files or making evidence claims. Claude Code does not
automatically load either file. This file does not restate or override them.

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
   evidence cannot overturn. For complete-RE replay authority, open
   `current_re_authority`; Generation 73 is a projection oracle, not a parent.
   Ghidra mutation has a separate evidence and authorization gate. There is no
   active mutable Linux project; route the preserved `db.18634` checkpoint and
   recovery copies through
   [`reverse-engineering/ghidra/README.md`](reverse-engineering/ghidra/README.md).
   OpenJDK 21 and Ghidra 12.1.3 are installed, but no mutable Linux project has
   completed activation. On Linux, run complete-RE verification only through
   `current_re_authority.verify`; do not call the frozen bootstrap directly or
   rewrite historical receipt paths.
   Omarchy owns native RE and Core/Client/headless rebuild work. AppCore source
   compiles here, but its full suite, WinUI 3, the Windows-targeted CLI, and the
   currently admitted Godot runtime, smoke, and capture routes remain
   Windows-only; the isolated evaluation VM is prepared but not yet activated.
   Do not claim a current native route or
   substitute Linux static checks. The exact host split is in `AGENTS.md`.
6. `local-lab/INDEX.md`, when present — the real, writable, Git-ignored corpus
   inside the canonical checkout. It is not tracked and remains invisible to a
   fresh clone or child worktree. From a worktree, use the canonical absolute
   path or `BEA_LOCAL_LAB`; never create a twin, symlink, bind mount, or read-only
   substitute.
7. The owning lane: [`reverse-engineering/RE-INDEX.md`](reverse-engineering/RE-INDEX.md)
   (current recovered authority first; Gen10/Gen73 demoted),
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
- Delegate independent measurement and adversarial review when useful, starting
  with this harness's native subagents. External models are situational, not a
  mandatory matrix; follow `reverse-engineering/REVIEW-PROTOCOL.md`. Verify a
  background reviewer actually began, and treat every report as input to
  reproduce rather than authority to publish or promote.
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
