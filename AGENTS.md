# Onslaught Toolkit

Status: active — authoritative contributor contract for this repository.
Last updated: 2026-08-06 (standing eight-way critic pin: Grok + DS Flash max +
Opus medium + GPT 5.6 Luna Max via Codex; Pro max and Opus max retired for
standing RE; direct DeepSeek session carve-out added — native subagents N+A
when the maintainer works directly with DeepSeek in an interactive OpenCode
session).
Summary: the mission, evidence boundaries, safety rules, and smallest set of
routes every contributor needs before working on Battle Engine Aquila.

## Mission

This is a full-scope *Battle Engine Aquila* preservation and engineering project
with three coequal, mutually reinforcing outcomes:

1. Fully reverse the retail game—functions, contracts, data, systems, patch
   points, and dormant capabilities—so it can be understood, preserved, patched,
   and modded.
2. Rebuild it in Godot at 1:1 behavioral and experiential parity so the released
   experience runs faithfully and feels like the original game.
3. Ship a polished WinUI 3 preservation toolkit for careers, saves, safe copies,
   patching, media, and the other user-facing capabilities the project proves.

Retail RE feeds reconstruction, and reconstruction exposes the next retail
questions; RE and shared tooling also make safe app features possible. None of
the three outcomes is a side lane or a lower priority. The current user goal
selects where limited attention goes now; it does not redefine the repository's
standing priorities.

Discovering a name or one observed call is not the finish line: recover what
enters, what leaves, what changes, and under which conditions. Carry relevant
contracts into `rebuild/` with focused parity evidence, while retaining findings
that matter independently for patching, modding, and the WinUI app. Honest
unknowns and exact falsifiers are progress; invented semantics are not.
[`GOAL.md`](GOAL.md) defines the standing acceptance targets.

The repository lanes are:

- `reverse-engineering/` — promoted, specimen-bound evidence; start at
  [`reverse-engineering/RE-INDEX.md`](reverse-engineering/RE-INDEX.md).
- `local-lab/` — ignored working evidence, retail-derived material, scratch
  binaries, captures, and campaign artifacts; read `local-lab/INDEX.md` when it
  exists.
- `tools/` — RE, validation, asset, and controlled-lab instruments.
- `rebuild/` — the GPL-licensed, RE-informed Godot reconstruction. Read
  [`rebuild/PROVENANCE.md`](rebuild/PROVENANCE.md) and
  [`rebuild/README.md`](rebuild/README.md) before changing it.
- `OnslaughtCareerEditor.WinUI/` — the primary user-facing preservation and
  save/career tool.
- `OnslaughtCareerEditor.AppCore/` — shared save, options, patch-planning,
  media, catalog, and safe-copy correctness.
- `OnslaughtCareerEditor.Cli/` — an unshipped maintainer adapter over AppCore;
  [`CLI.md`](CLI.md) is its headless front door, not a second product lane.

Retired Electron, WPF, and Python app implementations live only in Git history.

## Start from current truth

- Read [`README.MD`](README.MD), this file, and the directly relevant owners.
  Read widely enough to be right: narrow reading has repeatedly produced
  locally correct changes that were wrong against the game.
- [`PROJECT-INDEX.md`](PROJECT-INDEX.md) maps source ownership, application flow,
  and dependency direction. Use it to find the implementation owner; use the
  lane's evidence documents to decide what the implementation must do.
- [`GOAL.md`](GOAL.md) states what is wanted. `developer_state.json` carries
  resumable state and evidence pointers, not unquestionable truth. Current user
  intent, code, runtime behavior, and primary evidence outrank stale prose.
- When `local-lab/` exists, its index is essential: a fresh clone cannot see the
  workstation-local evidence corpus. Promote only the smallest reviewed fact a
  source or rebuild path needs; raw and retail-derived material stays local.

## Hard boundaries

Three principles govern writes to a user's files:

1. Nothing irreversible without an explicit informed choice and a verified
   backup made before the write. Make that backup a precondition the caller
   cannot skip—`BinaryPatchEngine.AuthorizeInstalledGameWrite` is the model.
   Never manufacture an "original" from an already modified file.
2. The user's saves are theirs. Never destroy career data as a side effect;
   detect it, name it, and offer to preserve it.
3. The pristine specimen is absolute: `74154bfa…` is the byte-measurement
   baseline. Read it, never write to it.

Also:

- The maintainer's installed `BEA.exe` is deliberately patched for personal
  testing; that is not drift. Read every byte finding from a named pristine
  specimen and include its hash.
- Do not synthesize `.bes` saves. Start from a real baseline and preserve
  length, reserved fields, and unknown bytes.
- Do not track or redistribute retail binaries or assets, converted retail
  material, arbitrary saves, raw debugger logs, bulky captures, Ghidra backups
  or alternate projects, credentials, or `.env*`. The narrow tracked save
  fixture is `tests_shared/fixtures/gold_career_save.bin`.
- Screenshots are captures, not extracted assets. A small deliberate set may be
  tracked for this project's own surfaces only when registered—and only while
  the set stays too small to substitute for owning the game—in
  [`reverse-engineering/project-meta/attribution.md`](reverse-engineering/project-meta/attribution.md);
  bulk frames and asset-viewer substitutes stay local.
- The canonical distributable Ghidra snapshot lives only under
  `reverse-engineering/ghidra/`; live projects and verified backups stay in
  their machine-local owners.
- The GPL rebuild may adapt the pinned GPL source and consume locally
  materialized retail data. Keep retail executables, decompiler output, and
  separately licensed material out of it; preserve file-level provenance and
  terms.
- Keep `OnslaughtRebuild.Core` deterministic and independent of presentation,
  filesystem, clock, process, network, and GPU APIs. Clients and renderers adapt
  Core state; they do not own simulation truth.
- Do not add hosted CI, release automation, or workflow scaffolding. Validation
  and release gates are local.

## Evidence and reconstruction

- Use the cheapest sufficient authority: pinned GPL source for architecture and
  intent where it exists; retail `data/` for authored content; pristine bytes
  and controlled copied-runtime observations for released behavior. Override
  available source only when retail evidence proves a divergence, and record it.
- Anything the developers shipped may be evidence: RTTI, strings, `FILE` paths,
  registries, assertions, dormant loggers, resource names, traces, data tables,
  and source. Grade and reproduce it; a plausible label is not proof.
- Every behavior claim cites a capture, byte comparison, focused test, or pinned
  source file and line. Decompiler output alone and a model's opinion prove
  nothing. Static evidence establishes only the identities and structures it
  demonstrates; controlled runtime evidence establishes only the causality and
  values it observes.
- Function work should preserve specimen identity, exact body/range identity,
  callers and callees, class ownership, signature, globals and structure fields,
  inputs, outputs, state changes, ordering, failure behavior, confidence,
  unresolved questions, and the cheapest falsifier. Map sufficiently proven
  retail entities to reconstruction owners and tests.
- Account honestly for code, data, padding, library code, ambiguity, and dark
  ranges. "100%" means every item has a defensible terminal state or an explicit
  open question and next instrument—not that every byte executed or received a
  guessed name.
- Prefer a discrete, countable proof gate. `UNSCORED` is not success. Run a
  consequential loop at least twice; when results hit the instrument's noise
  floor, change instruments rather than fit harder.
- Mine existing static evidence, source, level-start traces, and combat traces
  before recording more. Natural traces are broad discovery evidence; authored
  safe-copy scenarios are sparse causal probes for preregistered questions.
- Keep released-behavior evidence, source-informed architecture,
  reconstruction decisions, and remaining hypotheses visibly separate.
- Promote Ghidra changes only after exact program identity, recoverable backup,
  isolated scratch validation, dry-run/apply/readback receipts, and independent
  refutation. Never promote aliased, mismatched, partially applied,
  `UNSCORED`, or refuter-pending claims. The owning procedure is
  [`reverse-engineering/ghidra/README.md`](reverse-engineering/ghidra/README.md).

## Working and delegation

- **Lab evidence is never hard-deleted in one step.** Anything under
  `local-lab/` (and any dated lab output elsewhere) is first **staged** with
  `tools/lab_quarantine.py stage <path> --reason "<why>"`, which moves it to
  `D:\lab-quarantine\<date>\` with a tree SHA-256, byte count, and manifest
  row. True deletion happens later, only under space pressure, via
  `lab_quarantine.py purge <id> --reason "<why>"`; the manifest and purge log
  preserve identity for recovery. `restore <id>` brings a staged item back.
  This rule exists because a 2026-08-06 cleanup deleted a frozen campaign
  carry bundle whose `campaign.ready.json` SHA was hard-pinned in
  `tools/re_campaign.py` — the audit checked *docs* for references, not
  *test code*, and the fixtures were unrecoverable (not in git, not in
  OneDrive, no VSS shadow, recycle bin bypassed by `Remove-Item -Force`).
  Before classifying anything "stale", grep the **tooling and tests** too,
  not only the docs.
- Preserve unrelated and pre-existing work, especially in a dirty tree. Make
  the smallest coherent change that closes the observed contract; do not widen
  into adjacent cleanup or new machinery without evidence that it is needed.
- Delegate bounded reading, searching, measuring, porting, and adversarial
  review when it materially protects context or shortens independent work.
  Keep adjudication, integration, commits, and public claims with one owner.
- A subagent report is data, not authority. Reproduce load-bearing conclusions,
  and verify background reviewers actually reached a working state; a spawn
  receipt alone is not a liveness oracle.
- External CLI reviewers follow the same rule. Keep their lanes read-only unless
  a writing lane is explicitly isolated; preserve prompts and reports under
  `local-lab/`, confirm real work and clean exit, reproduce consequential claims,
  and budget concurrent heavy processes. Never send a hosted reviewer secrets or
  private/raw retail material beyond the user's explicit scope. This repository's
  default reviewer mix is the standing set: **Grok 4.5 High subagents** (normal +
  adversarial), OpenCode **DeepSeek direct Flash-max** (first-party API through
  the OpenCode harness—not InferX mirrors and not OpenCode Zen DeepSeek; normal +
  adversarial), Claude Code headless **Opus 5 medium** (normal + adversarial),
  and **GPT 5.6 Luna Max via Codex** (`codex exec -m gpt-5.6-luna-max`; normal +
  adversarial). Codex remains usable when weekly quota allows; do **not** skip
  Grok, DeepSeek Flash, Opus medium, or GPT 5.6 Luna lanes because a quota
  percentage looks low—use them normally unless the maintainer explicitly parks
  a lane.

  **Historical note (unban):** OpenCode was previously avoided because free /
  Zen / InferX DeepSeek mirrors were unreliable for load-bearing RE. That ban
  is **lifted**. Standing work uses **DeepSeek direct** (maintainer API key via
  OpenCode). Do not revive the ban; do not fall back to Zen/InferX for
  consequential reviews.

  **Standing critic pin (maintainer FRAGO 2026-08-05, extended 2026-08-06):**
  load-bearing plates require **all eight** cells below; incomplete coverage is
  not a finished review. This supersedes the former ten-way pin (DeepSeek
  Pro-max and Opus 5 max are **retired for standing RE**—do not launch them
  unless the maintainer explicitly re-authorizes a one-off).

  **Direct DeepSeek session carve-out (maintainer FRAGO 2026-08-06):** when the
  maintainer is working **directly with DeepSeek in an interactive OpenCode
  session** (the mode this document is currently being edited in), the standing
  external eight-way lanes are **not mandatory**. The reviewer pair in a direct
  session is the **native OpenCode subagent tool** run as normal **and**
  adversarial roles (explore/general), orchestrated by the session lead. The
  external CLIs (Grok, Claude Code headless, Codex, `opencode run` DeepSeek via
  the npm shim) remain **available on request and when available**, but their
  absence does not block or fail a direct-session plate. This carve-out does
  **not** relax the per-generation police or gauntlet-loop bars for campaign
  work launched outside a direct session: any load-bearing plate a session is
  running in the standing campaign/harness machinery still needs its eight-way
  cells unless the maintainer explicitly parks them. It also does not relax the
  DeepSeek authority boundaries: in a direct session DeepSeek is still not the
  integration owner and does not authorize names, signatures, types, memory
  writes, campaign upgrades, rebuild parity, Ghidra mutation, or new captures —
  the maintainer is present and adjudicates. Preserve prompts and reports as
  usual under `local-lab/`.

  **DeepSeek direct pin (standing):**
  - Model: `deepseek/deepseek-v4-flash` only for standing RE
  - Variant: **`max` only** (never `high`, `low`, or unset/default)
  - Official Flash API id serves **DeepSeek-V4-Flash-0731**; do not use InferX
    `inferx/deepseek-v4-flash` (non-0731) or pay InferX for a 0731 mirror when
    direct is funded
  - Do **not** use `opencode/deepseek-*` (Zen) as a fallback
  - **`deepseek/deepseek-v4-pro` is not standing-authorized** (retired for
    routine load-bearing plates; one-off use only with explicit maintainer
    re-authorization)
  - Every consequential review ships **all** of the following when the plate is
    load-bearing (**eight-way**):
    - Grok subagent normal **and** adversarial
    - DeepSeek Flash-max normal **and** adversarial (OpenCode direct)
    - Claude Opus 5 **medium** normal **and** adversarial (headless `claude -p`)
    - GPT 5.6 Luna Max normal **and** adversarial (`codex exec -m gpt-5.6-luna-max`)
    Smaller smokes may run a subset only when explicitly labeled smoke—not as
    generation police. Self-authored `GROK-ADVERSARIAL.json` stubs written by
    the integration owner are **hygiene only** and never satisfy this bar.
  - **Claude Opus 5 pin (standing):** model `claude-opus-5` via Claude Code
    headless (`claude -p --model claude-opus-5`); effort **`medium` only** for
    standing RE. Run **both** normal and adversarial roles at medium. Preserve
    prompt, stdout, model, effort, role, start/finish, exit under `local-lab/`.
    Do not delay Opus medium lanes for “low weekly %” foot-dragging; use
    normally. **Opus effort `max` is not standing-authorized** (same one-off
    rule as DeepSeek Pro).
  - Review **both** campaign/evidence claims **and** the scripts/instruments
    that produced them (compose gates, reducers, verify paths, tests). Grok,
    DeepSeek Flash, and Claude Opus medium are expected to improve code quality
    as well as catch false terminals—not only post-apply attack tables
  - **Per-generation police:** for multi-gen residual/function campaign work,
    each generation is its own review lane (Gen9, Gen10, … GenN separately)—
    not only one mega-sweep. Each load-bearing gen needs the eight-way set
    above. A cross-gen retrospective may supplement but does not replace
    per-gen lanes.
    Scaffold/status: `local-lab/per-gen-review-*/` +
    `tools/re_per_gen_review_scaffold.py` /
    `tools/re_per_gen_review_scaffold_gen26_33.py`
  - **Gauntlet Loop (standing for the complete-RE goal):** ambitious bar
    (specimen + honest 100% terminal/OPEN+falsifier + dual authority + AGENTS
    evidence gates)—not “pretty good.” Lead splits into smallest pieces; each
    piece gets a builder and **separate** critics with fresh context (Grok
    normal+adversarial, DeepSeek Flash-max normal+adversarial, Claude Opus 5
    medium normal+adversarial, GPT 5.6 Luna Max normal+adversarial). Critic
    inspects real artifacts, never the
    builder’s self-summary. No fixed round count; keep looping until the bar
    wins or the maintainer stops. See `local-lab/per-gen-review-*/GAUNTLET.md`
    and https://somethingbig.ai/gauntlet-loop. Grok and Claude fan out in
    parallel; OpenCode DeepSeek runs use **bounded parallel** on this host
    (see below). The goal does **not** authorize skipping critics for throughput.
  - DeepSeek is **read-only** architect/adversarial input—not integration owner
    and not writer
  - Tools are required for real reviews; always `--title`; never `--auto`; use
    single-line CLI messages (multiline positionals truncate); wait long enough
    for tool loops (10–30+ min is fine); on kill/timeout delete the OpenCode
    session and mark the plate failed
  - **OpenCode concurrency (retain across sessions/compactions):** OpenCode
    stores sessions in a shared SQLite DB (`~/.local/share/opencode/opencode.db`).
    Desktop/TUI multi-session is supported; concurrent `opencode run` is also
    **allowed** and was re-measured OK on this host (2026-08-05): 2–4 short
    shared-DB runs and 2 concurrent toolful flash-max runs all exit 0 with no
    lock error. A historical `database is locked` / `SQLITE_BUSY` failure still
    exists under heavy write contention when `busy_timeout=0` (upstream
    issue #21215; also seen once in
    `local-lab/opencode-deepseek-direct-proof/PROOF.md` under parallel
    pro-max-tool). Standing RE path: **bounded parallel** DeepSeek Flash-max
    only (prefer 2 concurrent `opencode run` for the two Flash roles, not large
    fan-out); on lock/fail **retry** that cell; optional isolation via per-job
    `XDG_DATA_HOME` + copied `auth.json` if contention returns. Serial remains
    valid but is not required. Grok subagents fan out freely.
  - `low`/`high` variants may exist on direct Flash (measured) but are **not**
    authorized for standing RE reviews; pin **`max`** only
  - Preserve prompt, stdout/stderr, model id, variant `max`, role
    (normal|adversarial), start/finish, exit code under a distinct `local-lab/`
    review directory
  - DeepSeek may generate hypotheses, designs, and failure modes; it may not
    authorize names, signatures, types, memory writes, campaign upgrades,
    rebuild parity, Ghidra mutation, or new captures. Wrong model, incomplete
    exit, or unauthorized write → stop, preserve failure, discard claims
  - Live pin proof: `local-lab/opencode-deepseek-direct-proof/PROOF.md`
    (historical Flash/Pro measurements remain valid evidence of harness
    capability; standing RE uses Flash-max only)
- Read-only lanes may share the checkout but use distinct output paths. A lane
  that writes uses an isolated worktree, does not commit, and is landed or
  discarded as a unit. Verify its base commit before work begins; the integration
  owner checks the exact staged diff before committing. Let writing lanes reach
  a safe stopping point unless the user redirects them.
- Avoid global synthetic input while the machine may be in use. Prefer
  target-window messages and proxy-owned capture; use global input only when the
  machine is known to be unattended and no bounded alternative exists.

## Validation and authority

Root `package.json` owns commands. Choose the smallest existing check that could
realistically falsify the changed contract; [`VALIDATION.md`](VALIDATION.md) is
the gate-selection table. Documentation changes use `git diff --check` plus the
affected link, JSON, command, mirror, and header checks. Rebuild work uses the
focused Core, client, or native gate named by its owner; broad
`npm run test:rebuild` is for genuinely cross-cutting changes.

Release and public-boundary work follows [`README.RELEASE.md`](README.RELEASE.md)
and `release/readiness/PUBLIC_SIGNOFF_COMMANDS.md`; the first push of a held
backlog requires that clean public-boundary pass.

Commit, push, publication, and release are standing-authorized by the maintainer
(2026-07-30; recorded in `developer_state.json`). That authority is
action-specific: it does not relax the pristine-specimen rule, user-file backup
and choice, save preservation, evidence gates, or public/private boundaries.
