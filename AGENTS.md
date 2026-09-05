# Onslaught Toolkit: agent guide

Status: active — the single instruction file for this repository; `CLAUDE.md` only points here
Last updated: 2026-09-05
Summary: what the project is, the rules that protect the evidence and the user's files, where things live on this
Linux laptop, which commands work here, and the gotchas that have already cost data.

Read this before changing anything. Read `~/AGENTS.md`, `~/Projects/AGENTS.md` and
`~/Projects/game-dev/AGENTS.md` explicitly when automatic discovery stops at this Git root;
this repository guide is more specific and wins here.

## What this is

A preservation project for *Battle Engine Aquila* (2003) with three coequal outcomes: reverse the retail game so it
can be understood, patched and modded; rebuild it in Godot at 1:1 behavioral parity; and ship the WinUI 3 toolkit
for careers, saves, safe copies, patches and media. RE feeds the rebuild, the rebuild exposes the next retail
questions, and both make safe app features possible. [`GOAL.md`](GOAL.md) states the standing outcomes,
[`PROGRAM.md`](PROGRAM.md) is the work queue, [`CURRENT_CAPABILITIES.md`](CURRENT_CAPABILITIES.md) says what is
proven today, and `~/Projects/game-dev/PLAN.md` section 6 is where David wants the repository to go (three repos).

The host is this Linux laptop. It owns Git, documentation, the Python tooling, reverse engineering, Ghidra and the
Core/Client/headless rebuild lanes. WinUI 3, the full AppCore suite, the Windows-targeted CLI, the portable ZIP
and the controlled Godot launch/smoke/capture routes need Windows; the evaluation VM for them is staged under
`local-data/windows-vm/` (read its `README.md`) and is not activated, so there is no native Windows route today.
Do not report Linux static checks as Windows or Godot evidence.

A storage-consolidation hold has been in force since 2026-08-31 (`developer_state.json` →
`_STORAGE_CONSOLIDATION_HOLD_20260831`): no new RE campaign, rebuild feature, WinUI/CLI feature or semantic
Ghidra mutation until David lifts it. Routing repair, read-only audit, checksum validation and repository
organization are fine.

## Ground rules

- Nothing irreversible happens to a user's files without an explicit informed choice and a verified backup made
  first; `BinaryPatchEngine.AuthorizeInstalledGameWrite` in AppCore is the model. Never manufacture an
  "original" from an already modified file, and never destroy career data as a side effect.
- The pristine specimen (`BEA.exe`, SHA-256 `74154bfa…`) is the byte-measurement baseline: read it, never write
  it. Every byte or address finding names the specimen it was read from, with its hash. The maintainer's
  installed `BEA.exe` is deliberately patched and is not evidence.
- Do not synthesize `.bes` saves. Start from a real baseline and preserve length, reserved fields and unknown
  bytes. `tests_shared/fixtures/gold_career_save.bin` is the one tracked save.
- Never track retail binaries or assets, converted retail material, arbitrary saves, raw debugger logs, bulky
  captures, Ghidra backups or alternate projects, credentials or `.env*`; `npm run test:safety` enforces the
  boundary. A small registered set of the app's own screenshots is the one allowance
  (`reverse-engineering/project-meta/attribution.md`, checked by `tools/check_registered_screenshots.py`).
- Every behavior claim cites a capture, byte comparison, focused test, or pinned source file and line. Decompiler
  output, a plausible name or a model's opinion proves nothing. Static evidence establishes identities and
  structures; only controlled runtime evidence establishes causality and values. Write unknowns as open questions
  with the cheapest falsifier, never as guessed names.
- `developer_state.json` → `current_re_authority` owns the campaign generation, READY/reducer pins and the verify
  command. Do not copy those values into prose (`tools/doc_current_authority_check.py` rejects it) and run
  complete-RE verification only through `current_re_authority.verify`.
- Ghidra has exactly two homes on this laptop plus one cold copy: the tracked checkpoint
  `reverse-engineering/ghidra/` (`db.18634`, never opened for writing), the working project
  `local-lab/ghidra-projects/BEA/BEA.gpr` (Ghidra 12.1.3, `db.18635`, the only writable one), and
  `/srv/archive-a/onslaught-ghidra-cold/` (a dated rsync of both plus Codex's consolidated package; restore a
  copy, never open it in place). A semantic mutation needs the promotion gate in
  `reverse-engineering/ghidra/README.md` and David's explicit go; an open Ghidra MCP connection is access, not
  permission.
- `local-lab/` and `local-data/` are real directories inside this checkout, ignored by Git, never symlinks, bind
  mounts, twins or read-only views; `~/ProjectData` is gone and stays gone. Nothing in them is deleted, moved or
  deduplicated without David's explicit go through `~/Work/storage-migration-2026-08-29/DELETE-QUEUE.md`. A
  2026-08-06 cleanup deleted frozen campaign inputs whose identities were pinned in tooling, so before calling
  anything stale, grep the tooling and tests, not only the docs.
- Never run `git clean` at the repository root (`-x`/`-X` would erase the lab) and never stage the lab with a broad
  `git add`; add paths explicitly. Preserve unrelated work in a dirty tree and make the smallest change that closes
  the contract.
- The rebuild is GPL: it may adapt the pinned GPL source in `references/Onslaught` and consume locally materialized
  retail data; retail executables, decompiler output and separately licensed material stay out of it
  (`rebuild/PROVENANCE.md`). `OnslaughtRebuild.Core` stays deterministic and free of presentation, filesystem,
  clock, process, network and GPU APIs.
- Reviews by other agents or models are optional and follow `reverse-engineering/REVIEW-PROTOCOL.md`: read-only
  lanes, reports are input to reproduce rather than authority, and hosted reviewers never receive retail material
  or secrets.
- No hosted CI, release automation, duplicate test suites, matrices, status or handoff files. One branch, `main`,
  pushed to `dlprentice/Onslaught-Career-Editor`; commit, push and release are standing-authorized, which relaxes
  none of the rules above.
- Root commands use `python` (3.14) and forward-slash paths; Windows-only scripts fail fast here through
  `tools/require_windows_host.py`. Drive letters in old receipts are history, not routing.

## Layout

| Path | What it is |
| --- | --- |
| `OnslaughtCareerEditor.AppCore/`, `.WinUI/`, `.Cli/` and their `*.Tests/` | The toolkit: shared AppCore (save/options codecs, safe copies, patch planning, media, lore), the WinUI 3 shell, the unshipped maintainer CLI (`CLI.md`). AppCore compiles here; its full suite and the UI run only on Windows. |
| `rebuild/` | The GPL Godot reconstruction: `OnslaughtRebuild.Core` (deterministic 20 Hz simulation), `Client`, `Headless` (tape replay), `Godot` (.NET renderer; launch is Windows-only today), `tools/` (retail materializer, capture scripts). Read `rebuild/README.md`, `PROVENANCE.md`, `DETERMINISM.md` and `PARITY.md` before touching it. |
| `reverse-engineering/` | Promoted, specimen-bound evidence. Start at `RE-INDEX.md`; `ghidra/` is the tracked checkpoint; `REVIEW-PROTOCOL.md` governs external reviews; `EVIDENCE-REGISTER.tsv` is generated from `developer_state.json`. |
| `tools/` | About 550 files: RE and campaign tooling, Ghidra scripts (`*.java`, replayable `cohort-specs/`), documentation and safety gates, asset export, release helpers. `tools/README.md` says what each is for. |
| `references/` | Submodules `Onslaught` (Stuart Gillam's GPL source) and `AYAResourceExtractor`, David's forks pinned at `5352a81` and `53b10b0` (`ONSLAUGHT_PIN` and `EXTRACTOR_PIN` in `tools/aya_extractor_source_audit.py`); `git submodule update --init --recursive` once. Source references, not proof of retail behavior; keep them pinned. |
| `lore/`, `lore-book/`, `patches/`, `roadmap/`, `release/` | Canonical lore library (`lore/_index.md`), its reading guide, the patch catalog, the public roadmap, release readiness. |
| `developer_state.json` | 935 KB of resumable state. `current_re_authority` is the only live selector; the dated `_*` keys are history. Awareness, never truth that primary evidence cannot overturn. |
| Root `*.md` | `README.MD` (product and lanes), `PROJECT-INDEX.md` (code ownership), `VALIDATION.md` (which gate for which change), `DOCUMENTATION.md` (the header standard), `CONTRIBUTING.md`, `SECURITY.md`, `LOCAL_LAB_OVERLAY.md`, `README.RELEASE.md`. A new tracked `.md` needs `Status:`, `Last updated:` (or `Date:`) and `Summary:` (or `Verdict:`) in its header block. |
| `local-lab/` (ignored, 81 GB) | The evidence corpus: retail safe copies, campaign generations, captures, reviewer reports, the working Ghidra project, `rebuild-godot/` staging. Open `local-lab/INDEX.md` first. Absent from fresh clones and worktrees; a worktree uses the canonical absolute path or `BEA_LOCAL_LAB`. |
| `local-data/` (ignored, 9.7 GB) | Machine-local data that is not lab evidence: `host-attestations/` (the gen32 attestor's pinned output), `retail-profiles/`, `media/`, `vm-media/`, `windows-vm/`, `windows-profile-2026-08-28/`, and the `_recovered-*` reconciliation packages described by its own `AGENTS.md`. |
| `.artifacts/` (ignored) | Legacy validation, screenshot and publish output. It can contain unique evidence, so ignored does not mean disposable. Keep existing coupled tool paths; use `local-data/` for new general-purpose outputs and the numbered queue for retirement. |

## Commands

`package.json` scripts are the command authority and [`VALIDATION.md`](VALIDATION.md) maps each kind of change to
the smallest gate. Node 26.7 and npm 11.19 come from mise, `python` is 3.14, `dotnet` is the 10.0 SDK named in
`global.json`; the rebuild also uses the pinned .NET 8 SDK from `~/.local/opt/game-pipeline`.

| Task | Command |
| --- | --- |
| Docs gate: links, headers, function names, authority pointers | `npm run test:docs` (about 2 s) |
| Public payload boundary | `npm run test:safety` (about 20 s) |
| One tools suite | `python tools/<name>_tests.py`; the function-name check alone is `python tools/re_function_doc_names_check.py --strict` |
| Rebuild Core tests | `npm run test:rebuild-core` (materializes first; measured 2026-08-31 at 34 min with three known Linux-host failures in `TapeFileWriteNew_*`); `npm run test:rebuild-ferry-sweep` for the excluded ferry oracle |
| Rebuild Client tests | `npm run test:rebuild-client` |
| Materialize retail inputs | From this repo: `npm run prepare:rebuild-assets -- --game-root "$PWD/local-lab/safe-copy-bea-pristine"` writes into `local-lab/rebuild-godot/`; Linux has no Steam discovery, so a fresh stage needs explicit `--game-root` |
| Headless replay | `npm run run:rebuild-headless -- <args>` |
| Complete-RE verification | the command in `developer_state.json` → `current_re_authority.verify` (`tools/re_campaign_gen32_host_attestation.py` on this host; receipts go to `local-data/host-attestations/`) |
| Ghidra | `ghidraRun` (12.1.3, OpenJDK 21) on `local-lab/ghidra-projects/BEA/BEA.gpr` only; headless scripts are `tools/*.java` |
| Windows lanes: `npm test`, `test:appcore`, `test:ui`, `test:cli`, `run:rebuild-godot`, `release:winui-zip` | Only in the Windows VM once it exists; on Linux they stop at `require:windows-host` by design |

## Definition of done

1. The smallest gate that could falsify the change passed: docs → `git diff --check` and `npm run test:docs`;
   anything that adds files → `npm run test:safety`; a tool → its own `_tests.py`; Core or Client → the matching
   `test:rebuild-*`. Do not run `tools/run_tool_tests.py` whole (about 40 suites, some compile executables and
   spawn PowerShell); run the suite you touched.
2. A new or edited tracked `.md` has the header fields and no volatile generation numbers, and is not added to
   `tools/doc_header_backlog.txt`.
3. Evidence claims name their specimen, capture or test; anything unproven is written as an open question.
4. `git status` shows only your change and nothing from `local-lab/` or `local-data/`. Commit on `main` with a
   plain message and push.

## Gotchas learned the hard way

- `tools/lab_quarantine.py` still targets `H:\graveyard\lab-quarantine`; its stage, restore and purge actions must
  not run on this machine. The 2026-08-06 loss was a `Remove-Item -Force` on inputs whose identities were pinned
  in tooling and tests.
- The gen32 attestor requires the retired `~/ProjectData/Onslaught/local-lab` path to stay absent and pins its
  output owner to `local-data/host-attestations`; do not "fix" either path.
- Opening a Ghidra project without `-readOnly` can roll its `db.NNNNN` version even when a script refused.
  Measure the version, never quote it.
- The retail copy for `--game-root` is `local-lab/safe-copy-bea-pristine/` (complete: `BEA.exe` and the three
  archives). Its `BEA.exe` (`e1436ef7…`) is a safe copy, not the `74154bfa…` specimen. The same copy also lives in
  Archive A at `graveyard/D-backups/Onslaught-Career-Editor-full-copy-20260814-20260814T122949Z/local-lab/`,
  which earlier stages used. The September 5 code/config check found no current hard-wired graveyard
  selection; use the explicit repo-local command above. Archive A's copy is retained history, not permission
  to remove it or the rest of `graveyard` without a numbered batch.
- `BEA.exe` writes `setuphistory.txt` and `cardid.txt` into its working directory, so launch a copy from its own
  folder; both names are ignored in case a launcher forgets.
- `tools/doc_header_backlog.txt` may only shrink. Never add a file to it to silence a header failure.
- `tools/check_installed_game_claims.py` bans standing promises about the installed game (for example that it is
  never modified); the app can patch an installed game after a verified backup, so describe the backup rule
  instead.
- `.claude/worktrees/` and `.worktrees/` are ignored because a broad `git add -A` has twice swept unrelated work
  into a commit.
