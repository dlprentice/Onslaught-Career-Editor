# Contributing

Status: active — the contributor entry point
Last updated: 2026-10-22 (Onslaught CE and onslaught-godot linked; earlier: the retired AppCore patching core removed, inbound = outbound licensing)
Summary: what a focused change looks like here, what must never be added to the
repository, and which checks a change owes.

This public repository holds the Godot toolkit companion (paused until new requirements), documentation of
*Battle Engine Aquila* as prose and specs, our tools and a frozen copy of the Godot
rebuild, which is developed in [onslaught-godot](https://github.com/dlprentice/onslaught-godot). The byte-matching decompilation's public export is
[onslaught-decomp](https://github.com/dlprentice/onslaught-decomp); its native port is published separately as [Onslaught CE](https://github.com/dlprentice/onslaught-ce);
report port problems in [its issues](https://github.com/dlprentice/onslaught-ce/issues). [GOAL.md](GOAL.md) states the
direction and [PROGRAM.md](PROGRAM.md) the work queue. Keep changes focused and use existing records and
validation.

## Start here

1. Read [`AGENTS.md`](AGENTS.md), [`README.MD`](README.MD), and only the owning
   README or evidence files for your change.
2. Confirm the branch, upstream, dirty state, and submodule pins. Initialize
   missing references only when the authorized work needs them.
3. Preserve unrelated work and keep `references/Onslaught` pinned unless a
   separately authorized source-reference update requires otherwise.
4. Make the smallest coherent change that fixes a current product, contract,
   evidence, or contributor problem.
5. Run the smallest check capable of falsifying that change.

No game installation is required to test ordinary documentation changes. On
Omarchy, start with the host-appropriate portable gates:

```bash
npm run test:docs
npm run test:safety
```

`npm test` runs the companion's contract and tooling checks without opening a window;
`npm run dev` launches the companion. No Windows host is provisioned; Linux checks do not
establish Windows behaviour. Native workflow checks are separate from build, static or headless
evidence.

Root [`package.json`](package.json) is the command authority. Do not duplicate
its command list in new documents.

## Licensing of contributions

Inbound = outbound: by opening a pull request you agree that your contribution is
licensed under the same terms as the paths it changes, as [`REUSE.toml`](REUSE.toml) and any
per-file SPDX line state them: code GPL-3.0-only ([`LICENSE`](LICENSE)), documentation and lore
CC BY-SA 4.0 ([`LICENSES/CC-BY-SA-4.0.txt`](LICENSES/CC-BY-SA-4.0.txt)). Contribute only work you
have the right to license this way; credit quoted or third-party material and keep its notice.
New code files start with an `SPDX-License-Identifier: GPL-3.0-only` comment.

## Ownership

- The companion owns its career codec, file safety, game text, lore and every screen.
- The rebuild's simulation, `OnslaughtRebuild.Parity`, is deterministic given its inputs (the tape, the
  retail data and options files it reads as the game does, and the virtual clock) and has no presentation,
  process, network or GPU dependency; `OnslaughtRebuild.Host` owns presentation. The earlier
  `OnslaughtRebuild.Core` is reference material.
- `lore/` is the canonical public lore/history source.
- `reverse-engineering/` documents the game with provenance-bounded prose and specs. Static,
  runtime and source-reference claims must remain distinct.

## Product changes

Keep primary workflows understandable without lab knowledge. Use clear action
labels, explicit target paths, visible success/error state, keyboard focus,
accessible names, and sufficient contrast. Mutating actions must state whether
they write a selected file, a copy, or an app-owned profile.

Do not expose Host/Join as available, represent a generated catalog as bundled
game content, claim reconstruction parity, or turn research controls into a
normal-user promise without corresponding proven behavior.

## Files and retail inputs

Never commit retail binaries, arbitrary saves, copied executables, Ghidra databases or
backups, decompiler output, decomp source, debugger logs, private captures, credentials, or
`.env*` files.
Use the ignored locations described in [`LOCAL_LAB_OVERLAY.md`](LOCAL_LAB_OVERLAY.md)
for retail inputs, extraction, conversions, and experiments. Do not commit or
package retail game assets or derived copies. Contribute the smallest exact
recipe a current product or rebuild path consumes, with credits, provenance,
and third-party terms intact.

Screenshots are treated separately, because a picture of the game running is a
new work rather than one of the game's files. A few chosen ones may be tracked
and shipped for this project's own surfaces; bulk capture directories may not.
[`AGENTS.md`](AGENTS.md) carries the conditions, and anything tracked under that
allowance is listed in
[`reverse-engineering/project-meta/attribution.md`](reverse-engineering/project-meta/attribution.md).

File extensions are not provenance. Small project-authored or specifically
developer-provided assets may be committed in their owning source path when
their origin, license, and attribution are clear. The rebuild materialization
owners are reserved for local retail-derived outputs; large opaque additions
require a reviewed hash exception in the existing public-safety check.

Save edits must start from a real baseline and preserve unknown bytes. An
installed executable may be changed only when its owner explicitly chooses it
and the write path has already made and verified a pre-write backup; otherwise
use a verified copy. The pristine specimen is never a mutation target. The
full three-principle contract is [`AGENTS.md`](AGENTS.md); this is the
contributor-facing summary, not a second owner.
Exporters must require explicit local inputs and a separate local output root.

## Game documentation and the rebuild

Use [`reverse-engineering/RE-INDEX.md`](reverse-engineering/RE-INDEX.md) to find the owning document. New
findings come from the byte-matching decompilation or controlled observation; write them as prose and specs,
cite the function or capture, and never paste decompiler output. Contract grades follow
[`CONTRACTS.md`](CONTRACTS.md). Retain raw or bulky proof locally; commit only the smallest public-safe evidence
a document needs, and state what it does not prove.

`rebuild/` is a frozen copy: rebuild changes belong in [onslaught-godot](https://github.com/dlprentice/onslaught-godot). For the record, read
[`rebuild/PROVENANCE.md`](rebuild/PROVENANCE.md) and [`rebuild/README.md`](rebuild/README.md): GPL-compatible source adaptation and locally materialized
user-supplied retail data are permitted; retail executable or decompiler text and separately licensed
third-party material are not.

## Validation

Use [`VALIDATION.md`](VALIDATION.md) to choose checks. Typical focused commands
are:

```bash
npm run test:docs
npm run test:safety
npm test
```

Do not run a root aggregate merely for ceremony.
