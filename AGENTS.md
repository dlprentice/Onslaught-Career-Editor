# Onslaught Toolkit: agent guide

Status: active — the single instruction file for this repository; `CLAUDE.md` only points here
Last updated: 2026-09-07
Summary: what the project is, the rules that protect the evidence and the user's files, where things live on this
Linux laptop, which commands work here, and the gotchas that have already cost data.

Read this before changing anything. Read `~/AGENTS.md`, `~/Projects/AGENTS.md` and
`~/Projects/game-dev/AGENTS.md` explicitly when automatic discovery stops at this Git root;
this repository guide is more specific and wins here.

## What this is

A preservation project for *Battle Engine Aquila* (2003) with three coequal outcomes: reverse the retail game so it
can be understood, patched and modded; rebuild it in Godot at 1:1 behavioral parity; and ship a Godot toolkit
companion for Linux and Windows for careers, saves, safe copies, patches and media. RE feeds the rebuild,
the rebuild exposes the next retail questions, and both make safe app features possible.
[`GOAL.md`](GOAL.md) states the standing outcomes,
[`PROGRAM.md`](PROGRAM.md) is the work queue, [`CURRENT_CAPABILITIES.md`](CURRENT_CAPABILITIES.md) says what is
proven today. David's September 6 direction keeps this repository and consolidates
implementation responsibilities; older Blazor/Uno and repository-split recommendations
in `~/Projects/game-dev/PLAN.md` are superseded.

David replaced the WinUI 3 development lane with the Godot companion on September 6.
Keep the existing WinUI/AppCore source as migration material. After the completed
baseline report, David authorized the first Godot Save Lab workflow. Existing Windows
release procedures describe the retained implementation, not a queued WinUI release.

Linux owns development and native Godot execution. The rebuild now has Linux build/run/smoke/capture
commands, and the companion has a native Save Lab shell backed by portable AppCore. The complete player
walkthrough and Save Lab UI write/reopen acceptance remain unfinished; read `CURRENT_CAPABILITIES.md`.
The full legacy AppCore suite, WinUI, Windows-targeted CLI and portable ZIP retain Windows dependencies.
The evaluation VM is staged under `local-data/windows-vm/` and remains inactive. Linux evidence does not
establish Windows behavior. While David uses the desktop, continue code/RE and noninteractive checks;
wait for him to announce availability before resuming live input or visible launches.

David resumed scoped development on September 6 after accepting the baseline and
assessment. The active phase covers native Linux Godot launch/input/audio/capture,
the complete player-input Level 100 route, targeted RE, the first Godot Save Lab
workflow, and real World 110 construction/transition. Refactor and consolidate where
these deliverables require it; keep the three standing outcomes. The former storage
hold is retained as history in `developer_state.json`; it does not block this phase.
The Windows VM remains inactive. Ghidra changes still require the preservation workflow
and an exact declared cohort. External archive reconciliation and historical recovery
investigation remain outside this repository's development scope. Use native subagents;
do not use Claude Code during this phase.

## Ground rules

- Game/save writes require an informed user choice and a verified recovery copy before overwriting original
  data; `BinaryPatchEngine.AuthorizeInstalledGameWrite` in AppCore is the model. Never manufacture an
  "original" from an already modified file, and never destroy career data as a side effect.
- The pristine specimen (`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, SHA-256 `74154bfa…`)
  is the byte-measurement baseline: read it, never write
  it. Every byte or address finding names the specimen it was read from, with its hash. The lab folder's
  `BEA.exe` is patched. The Linux Steam executable matched the pristine hash on September 6; measure the
  exact selected file before making a new claim. Old Windows-install descriptions are not Linux identities.
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
  copy, never open it in place). Necessary semantic work must have an exact mutation plan; its
  declared cohort proceeds through the promotion gate in `reverse-engineering/ghidra/README.md` without
  another permission request for each ordinary gate. An open Ghidra MCP connection is access, not permission
  to invent a different mutation scope.
- `local-lab/` and `local-data/` are real writable directories inside this checkout, ignored by Git, not
  symlinks or separately mounted recovery views. The complete checkout physically resides at
  `/srv/archive-b/Onslaught-Career-Editor`; the familiar Projects path bind-mounts the same files.
  `~/ProjectData` is gone and stays gone. Carry out the approved organization plan under `~/AGENTS.md`:
  exact moves, hash-proven duplicate retirement and routing repairs do not need another batch-number reply.
  Record targets, evidence and outcomes in `~/Work/storage-migration-2026-08-29/DELETE-QUEUE.md`; preserve
  unique work and explicit KEEP holds, and ask about uncertain/last-copy loss or genuinely new scope. A
  2026-08-06 cleanup deleted frozen campaign inputs whose identities were pinned in tooling, so before calling
  anything stale, grep the tooling and tests, not only the docs.
- Never run `git clean` at the repository root (`-x`/`-X` would erase the lab) and never stage the lab with a broad
  `git add`; add paths explicitly. Preserve unrelated work in a dirty tree and make the smallest change that closes
  the contract.
- The rebuild is GPL: it may adapt the pinned GPL source in `references/Onslaught` and consume locally materialized
  retail data; retail executables, decompiler output and separately licensed material stay out of it
  (`rebuild/PROVENANCE.md`). `OnslaughtRebuild.Core` stays deterministic and free of presentation, filesystem,
  clock, process, network and GPU APIs.
  Using Godot for the companion does not merge MIT application code, GPL rebuild code
  and private retail material into one licensing boundary.
- Reviews by other agents or models are optional and follow `reverse-engineering/REVIEW-PROTOCOL.md`: read-only
  lanes, reports are input to reproduce rather than authority, and hosted reviewers never receive retail material
  or secrets.
- Reuse existing tooling and records; avoid duplicate test frameworks, broad routine matrices and new status
  or handoff files. Add a focused test when a real behavioral gap needs one. Hosted CI and release automation
  are outside this phase. Use a branch or repo-local `.worktrees/` when useful;
  David retired the blanket main-only restriction on 2026-09-06. Worktrees use the canonical lab explicitly
  and never receive a copied corpus. Keep scoped work pushed to `dlprentice/Onslaught-Career-Editor`;
  normal commits and pushes are authorized. Release claims require the selected platform's validation.
- Root commands use `python` (3.14) and forward-slash paths; Windows-only scripts fail fast here through
  `tools/require_windows_host.py`. Drive letters in old receipts are history, not routing.

## Layout

| Path | What it is |
| --- | --- |
| `companion/OnslaughtToolkit.Godot/` | MIT Godot companion, currently the first Save Lab workflow. References AppCore only; no rebuild or retail dependency. |
| `OnslaughtCareerEditor.AppCore/`, `.WinUI/`, `.Cli/` and their `*.Tests/` | Shared correctness code targets .NET 8 and 10; Save Lab has a Linux create-new-copy transaction. WinUI and the Windows-targeted maintainer CLI remain migration material (`CLI.md`). The full legacy suite retains Windows dependencies. |
| `rebuild/` | GPL reconstruction: deterministic 20 Hz `Core`, `Client`, `Headless` tape replay, native Godot renderer, and retail materializer. Read `rebuild/README.md`, `PROVENANCE.md`, `DETERMINISM.md` and `PARITY.md` before touching it. |
| `reverse-engineering/` | Promoted, specimen-bound evidence. Start at `RE-INDEX.md`; `ghidra/` is the tracked checkpoint; `REVIEW-PROTOCOL.md` governs external reviews; `EVIDENCE-REGISTER.tsv` is generated from `developer_state.json`. |
| `tools/` | About 550 files: RE and campaign tooling, Ghidra scripts (`*.java`, replayable `cohort-specs/`), documentation and safety gates, asset export, release helpers. `tools/README.md` says what each is for. |
| `references/` | Submodules `Onslaught` (Stuart Gillam's GPL source) and `AYAResourceExtractor`, David's forks pinned at `5352a81` and `53b10b0` (`ONSLAUGHT_PIN` and `EXTRACTOR_PIN` in `tools/aya_extractor_source_audit.py`); `git submodule update --init --recursive` once. Source references, not proof of retail behavior; keep them pinned. |
| `lore/`, `lore-book/`, `patches/`, `roadmap/`, `release/` | Canonical lore library (`lore/_index.md`), its reading guide, the patch catalog, the public roadmap, release readiness. |
| `developer_state.json` | Current owner pointers and required compatibility data. `current_re_authority` is the only live selector; `_history` recovers retired execution diaries from an exact Git object. Retained dated fields are provenance, not a task queue or authorization. |
| Root `*.md` | `README.MD` (product and lanes), `PROJECT-INDEX.md` (code ownership), `VALIDATION.md` (which gate for which change), `DOCUMENTATION.md` (the header standard), `CONTRIBUTING.md`, `SECURITY.md`, `LOCAL_LAB_OVERLAY.md`, `README.RELEASE.md`. A new tracked `.md` needs `Status:`, `Last updated:` (or `Date:`) and `Summary:` (or `Verdict:`) in its header block. |
| `local-lab/` (ignored) | The evidence corpus: retail safe copies, campaign generations, captures, reviewer reports, the working Ghidra project, `rebuild-godot/` staging. Open `local-lab/INDEX.md` first. Absent from fresh clones and worktrees; a worktree uses the canonical absolute path or `BEA_LOCAL_LAB`. |
| `local-data/` (ignored) | Machine-local data that is not lab evidence: `host-attestations/`, current retail/media inputs, staged VM data, operational outputs and grouped `recovered/` packages. `_recovered-worktrees/` and `windows-profile-2026-08-28/` retain protected historical Ghidra material in place. Its own `AGENTS.md` owns the exact map. |
| `.artifacts/` (ignored) | Legacy validation, screenshot and publish output. It can contain unique evidence, so ignored does not mean disposable. Keep existing coupled tool paths; use `local-data/` for new general-purpose outputs and the numbered queue for retirement. |

## Commands

`package.json` scripts are the command authority and [`VALIDATION.md`](VALIDATION.md) maps each kind of change to
the smallest gate. Node 26.7 and npm 11.19 come from mise, `python` is 3.14, `dotnet` is the 10.0 SDK named in
`global.json`; the rebuild also uses the pinned .NET 8 SDK from `~/.local/opt/game-pipeline`.

| Task | Command |
| --- | --- |
| Docs gate: links, headers, function names, authority pointers | `npm run test:docs` (about 2 s) |
| Public payload boundary | `npm run test:safety` (about 20 s) |
| Default Linux companion gate | `npm test` (Save Lab and launcher tests; no visible app) |
| Native companion build/run | `npm run build:companion-godot`; `npm run run:companion-godot` (also `npm run build` / `npm run dev`) |
| Native rebuild build/run/smoke/capture | `npm run build:rebuild-godot`; `npm run run:rebuild-godot`; `npm run test:rebuild-godot-smoke`; `npm run capture:rebuild-godot`. Runtime commands need the desktop. |
| One tools suite | `python tools/<name>_tests.py`; the function-name check alone is `python tools/re_function_doc_names_check.py --strict` |
| Rebuild Core tests | `npm run test:rebuild-core` (materializes first; the August 31 broad run took 34 min; its three Linux assertion failures were corrected and the affected class passed 22/22 on September 6 — see `VALIDATION.md`); `npm run test:rebuild-ferry-sweep` for the excluded ferry oracle |
| Rebuild Client tests | `npm run test:rebuild-client` |
| Materialize retail inputs | `npm run prepare:rebuild-assets` discovers Linux Steam libraries and writes canonical `local-lab/rebuild-godot/`; `-- --game-root "/absolute/game/root"` selects another supported installation |
| Headless replay | `npm run run:rebuild-headless -- <args>` |
| Complete-RE verification | the command in `developer_state.json` → `current_re_authority.verify` (`tools/re_campaign_gen32_host_attestation.py` on this host; receipts go to `local-data/host-attestations/`) |
| Ghidra | `ghidraRun` (12.1.3, OpenJDK 21) on `local-lab/ghidra-projects/BEA/BEA.gpr` only; headless scripts are `tools/*.java` |
| Retained Windows lanes: `test:winui`, `test:appcore`, `test:ui`, `test:cli`, `release:winui-zip` | Windows-only; the VM remains inactive. Historical rebuild PowerShell launchers have explicit `:windows` aliases and need toolchain revalidation. |

## Definition of done

1. The smallest gate that could falsify the change passed: docs → `git diff --check` and `npm run test:docs`;
   anything that adds files → `npm run test:safety`; a tool → its own `_tests.py`; Core or Client → the matching
   `test:rebuild-*`. Start with the suite you touched; the full `tools/run_tool_tests.py` is expensive and is
   appropriate only when the affected scope requires it. Documentation-only edits do not require engine builds.
2. A new or edited tracked `.md` has the header fields and no volatile generation numbers, and is not added to
   `tools/doc_header_backlog.txt`.
3. Evidence claims name their specimen, capture or test; anything unproven is written as an open question.
4. Review `git status`, preserve unrelated changes, and stage only the scoped tracked paths, never
   `local-lab/` or `local-data/`. Commit with a plain message and push the working branch, then continue
   the remaining authorized work rather than stopping after a substep.

## Gotchas learned the hard way

- `tools/lab_quarantine.py` still targets `H:\graveyard\lab-quarantine`; its stage, restore and purge actions must
  not run on this machine. The 2026-08-06 loss was a `Remove-Item -Force` on inputs whose identities were pinned
  in tooling and tests.
- The gen32 attestor requires the retired `~/ProjectData/Onslaught/local-lab` path to stay absent and pins its
  output owner to `local-data/host-attestations`; do not "fix" either path.
- Opening a Ghidra project without `-readOnly` can roll its `db.NNNNN` version even when a script refused.
  Measure the version, never quote it.
- The retained lab game is `local-lab/safe-copy-bea-pristine/`; its `BEA.exe` (`e1436ef7…`) is patched.
  Linux Steam is under `~/.local/share/Steam/steamapps/common/Battle Engine Aquila/` on this host.
  Launch an experimental copy from its own directory. The storage owner's September 6 receipts retire
  the proven Archive A safe-copy twin and both B-side mirrors; they do not establish a whole-lab backup
  or resolve historical ignored-data recovery. Current retention details belong to `local-lab/INDEX.md`
  and the migration deletion queue, not assumptions about folder names.
- `BEA.exe` writes `setuphistory.txt` and `cardid.txt` into its working directory, so launch a copy from its own
  folder; both names are ignored in case a launcher forgets.
- `tools/doc_header_backlog.txt` may only shrink. Never add a file to it to silence a header failure.
- `tools/check_installed_game_claims.py` bans standing promises about the installed game (for example that it is
  never modified); the app can patch an installed game after a verified backup, so describe the backup rule
  instead.
- `.claude/worktrees/` and `.worktrees/` are ignored because a broad `git add -A` has twice swept unrelated work
  into a commit.
