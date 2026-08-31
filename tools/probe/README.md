# `tools/probe` — the discovery loop

Status: integrated — the three stages below were built in separate lanes and
merged here; on 2026-08-02 the original nine-launch integration was followed by
six replicated Mission-logger launches and seven Mission VM-trace/control
launches, all unattended.
Last updated: 2026-08-30.
Summary: author a probe that makes specific engine behaviour fire, run it
unattended and record it, then put the result through a stage that tries to kill
it. Authoring, running and refuting are three separate programs with three
separate test suites; this file is the one door to all of them.
Evidence: MEASURED for the parts marked so in each section — the container
experiment, console proof, four-arm integration run under `local-lab/probe-runs`,
the replicated logger aggregate at
`local-lab/logger-oracle-pilot-2026-08-02/logger-oracle.ready.json`, and the
replicated stock-script VM trace at
`local-lab/vm-trace-pilot-2026-08-02/vm-trace.ready.json`. INFERRED for
everything each section's own `unproven` list names. Nothing here is SOURCE.
Specimen: every byte claim below is read from
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, sha256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`. The
installed Steam `BEA.exe` is deliberately patched and is never read for evidence.
Verdict: the loop closes for authoring, running and refuting same-length edits
and the bounded length-changing replacement of an existing script record. The
Mission logger can now gate exact ordered text/value content, and the bounded
`set-script-trace` intent exposes executed instruction index, post-instruction
stack size, and flags for one selected script; appending a new script-table
record remains static-only. What still needs a human is named in
"[What still needs a human](#what-still-needs-a-human)".

On the current Omarchy workstation, the private lab root is the real,
Git-ignored canonical-checkout directory
`~/Projects/game-dev/Onslaught-Career-Editor/local-lab/`. The old ProjectData
path is absent; no twin, symlink, bind mount, or read-only substitute exists.
A fresh clone or child worktree does not receive ignored content, so worktrees
must use the canonical absolute path or `BEA_LOCAL_LAB`.

| stage | program | tests |
|---|---|---|
| author | `probe_author.py` (+ `bea_lab.py`) | `test_probe_author.py` |
| run | `probe_harness.py` | `probe_harness_tests.py` (`--prove-can-fail`) |
| refute | `refute.py` (+ `adversary.py`, `finding_schema.json`) | `refute_tests.py` |

## What still needs a human

TTD recording still needs one elevated PowerShell window left open; console-only
and archive-only probes need neither elevation nor a human. Choosing what to
probe next, and reading a receipt whose oracle was satisfied for the wrong
reason, are both still judgement.

---

# Stage 1 — authoring

Turn an intent into a spliced level archive that makes the engine do a specific
thing, plus a manifest saying exactly what changed, plus control arms that
predict their own outcome.

This is the *authoring* half of the discovery loop. It does not run the engine.

Authority for every field it writes:
`~/Projects/game-dev/Onslaught-Career-Editor/local-lab/SCRIPT-FORMAT-SPEC-2026-08-02.md`,
read from the pristine specimen `BEA.exe.original.backup`
(`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`). Section
references in the source read `spec S3.4` and so on.

### Setup

The ignored private lab is not part of Git, so a fresh clone has neither the
retail archives nor the proven readers. The tool **imports** the container codec
and the bytecode grammar from there rather than vendoring a copy, so there is
exactly one definition of each and no chance of a silently divergent second
parser:

| imported | from | why it is trusted |
|---|---|---|
| `read_aya` / `write_aya` | `local-lab/aya_roundtrip.py` | round trip proven by the container experiment |
| `parse_world` and the grammar | `local-lab/msl/script_parse.py` | written to the VM's own readers; `mutation_test.py` shows it capable of failing (10 mutations × 7 levels, 0 survivors) |
| chunk walker | `local-lab/msl/bea_aya.py` | independent second implementation |
| 144-slot native table | `local-lab/msl/natives.json` | lifted from the registry initializer at `0x0052ff30` |

From the canonical checkout, the loader discovers `local-lab/` without an
override. From a child worktree, bind the one physical owner explicitly:

```sh
export BEA_LOCAL_LAB="$HOME/Projects/game-dev/Onslaught-Career-Editor/local-lab"  # or pass --lab
```

Do not create a worktree-local lab copy or link.

### Commands

```
probe_author.py list    <aya>                       scripts, sizes, sentinel counts
probe_author.py show    <aya> <Script> [--world T]   disassembly with writable offsets
probe_author.py natives [--profile --corpus DIR]     the descriptor table, optionally profiled
probe_author.py author  <aya> --out-dir D [...]      author a probe and its control arms
probe_author.py verify  <manifest.json>              re-check an authored archive from disk
```

Exit codes: `0` success, `1` verification failed, `2` refused (any `ProbeError`),
`3` `local-lab` not found.

#### Authoring

```sh
python probe_author.py author 905_res_PC.aya \
    --out-dir /scratch/probes --name laptimer_heartbeat \
    --set-constant  "LapTimer:data31536=2.0"          \
    --retarget-call "LapTimer:13=AddHelpMessage"      \
    --poison opcode --poison null                     \
    --corpus /path/to/data/Resources
```

That produces three archives from one source, each with its own manifest and its
own stated prediction:

| arm | file | prediction |
|---|---|---|
| probe | `laptimer_heartbeat.aya` | **RUNS** — `LapTimer`'s `Start Race Timer` loop now calls `AddHelpMessage` every 2 s instead of `PostEvent` every 0.05 s |
| poison | `laptimer_heartbeat.poison-opcode.aya` | **DIES** — `0xC0000005` during level load |
| control | `laptimer_heartbeat.null-control.aya` | **NO DIFFERENCE** from the probe |

Intents can also be given as JSON (`--intent '{...}'`) or a recipe file
(`--recipe r.json` → `{"world": "RLWD", "intents": [...]}`), which is the form to
use when a loop is generating them.

### What it can author

| intent | length | status |
|---|---|---|
| `set-constant` int / float / bool | same | **proven** — this is the container experiment's edit |
| `set-constant` string, same length | same | same-length, same mechanism |
| `retarget-call` | same | same-length; arity guarded against the corpus |
| `poison-opcode` | same | **proven** — the measured `0xC0000005` |
| `poison-datatype` | same | derived from `CreateFromType` |
| `null-control` | same | derived from `LoadScriptEvents` discarding the sentinel |
| `set-script-trace` | same | **runtime-proven twice** on stock Level 100 `Setup`; exact values 0 and 2 are negative controls, 1 emits indices 1..136 |
| `raw` | same | escape hatch, still content-anchored |
| `set-constant` string, different length | changes | **statically verified, never executed** |
| `splice-script` | changes | **statically verified, never executed** |
| `replace-script` | changes | **runtime-proven for a generated Level 100 `Setup`**; preserves name, ordinal, and every non-target record; each new program still needs its own controls |

`retarget-call` is guarded by a corpus profile: all 9,236 shipped `CALL`s give
each of the 108 called natives exactly one `(argc, returns)` pair, so a retarget
that would change arity or return discipline — and unbalance the VM stack — is
refused with the observed profile in the message.

`set-script-trace` resolves the first object-trailer dword by script name rather
than asking a caller for an inflated offset. The constructor reads that dword
into `CScriptObjectCode+0x60`; retail compares it exactly with `1`. Authoring is
same-length and content-anchored, but output also requires the selected script
to execute and the separately enabled logger to have a writable path. The
campaign-grade proof therefore pairs value `1` with value `0`, value `2`, and
logger-disabled controls; traced-run timing is void because the logger opens,
writes, and closes the file once per instruction.

#### What it will not author, deliberately

* **Type tags 5 and 6.** Never exercised by shipped data (spec §9.4); their
  widths come from the factory only. Refused rather than guessed.
* **Inserting a script anywhere but the end of the table.** Whether world
  `things` reference scripts by table index is not established, so no existing
  script is ever renumbered.
* **Compiling `.msl`.** The executable has the VM and no compiler.
  `splice-script` copies a donor object verbatim; `replace-script` emits only
  bounded straight-line `let`/`call` recipes from pinned native signatures.
* **Inventing control flow.** Opcodes `0x06, 0x0e, 0x12, 0x14, 0x15, 0x16, 0x19,
  0x1a` are framing-settled but behaviour-unknown (spec §9.1), so the tool moves
  a `CALL` and changes a constant and does not synthesise branches.

#### On length-changing edits

The `13 × u32` block turned out to be the **event entry table**, not a header
with a size or offset in it, and spec §7.1 establishes that *nothing inside a
script object is an offset*. So that question does **not** block length changes.
What the tool does for them:

1. rewrites the `string32` length prefix (for a resized string),
2. walks the chunk tree and fixes every enclosing size field — `WRES` → `WRLD` →
   `RLWD`, each as its own content-anchored edit,
3. re-blocks the container preserving the shipped rule (every block inflates to
   exactly 1 MiB except the last),
4. re-parses the whole payload and requires the chunk chain to close exactly and
   every sentinel to survive.

Length-changing `replace-script` archives have now loaded and executed under
matched controls. Two narrower residuals remain rather than being papered over:
different-length `set-constant` and appended `splice-script` outputs are still
static-only, and the successful re-blocked runs do not establish whether the
loader *requires* the shipped 1 MiB block rule. Every length-changing operation
remains gated behind `--allow-length-change`.

### Safety properties

* **Every write is content-anchored.** The caller states the bytes it expects to
  displace; `verify_anchor` refuses on mismatch. There is no bare-offset path —
  `Edit` rejects empty expected bytes at construction, and the `raw` escape
  hatch requires `expect`. This is the guard that turns the container spec's
  26-byte-wrong offset into a refusal instead of a desynchronised symbol table.
* **Refuse before writing.** All gates run against the in-memory payload; a
  refused build leaves no output file.
* **The result must break exactly as intended.** After the edit the payload is
  re-parsed. For a probe that means the grammar must still walk and every
  sentinel must survive. For a poison the gate **inverts**: a `poison-datatype`
  that fails to desynchronise is refused, because an arm that should die and
  does not proves nothing. Breaking a sentinel you did not declare is refused
  too.
* **No collateral.** The byte diff between source and output must lie entirely
  inside the declared edits.
* **Round trip before delivery.** The output is re-inflated and compared to the
  patched payload, and the block structure is compared, before the run is
  reported as successful.
* **Control arms derive from the probe archive, not from retail.** "This arm
  differs from the probe only by its control edit" is therefore true by
  construction, which is what lets a dead poison arm mean *the engine consumed
  the bytes we changed here* rather than *something else differed*.
* **Protected trees are unwritable.** Any path under `safe-copy-bea-pristine`,
  `steamapps` or `steamlibrary` is refused, as is any directory holding ten or
  more `*_res_PC.aya` — a shelf of retail archives is a game data directory
  whatever it is called, and dropping an authored archive there is the
  `autoexec.con` contamination failure in a different file.

### Manifest format

One JSON file per authored archive, next to it.

```jsonc
{
  "tool": "tools/probe/probe_author.py", "tool_version": "1.0.0",
  "spec": "local-lab/SCRIPT-FORMAT-SPEC-2026-08-02.md",
  "specimen_sha256": "74154bfa…",
  "generated_utc": "…", "arm": "probe", "label": "laptimer_heartbeat",
  "prediction": "RUNS: the probe's edits take effect; …",

  "source": { "path": …, "sha256": …, "bytes": …,
              "inflated_sha256": …, "inflated_bytes": …, "blocks": [1048576, …] },
  "output": { … same shape … },
  "world":  { "tag": "RLWD", "payload_offset": 2864881, "payload_bytes": 49238,
              "script_count_before": 14, "script_count_after": 14, "level_id": 905 },

  "intents": [ … exactly as supplied … ],

  "edits": [{
    "kind": "retarget-call", "offset": 2886171, "payload_offset": 21290, "length": 8,
    "expect_hex": "18 00 00 00 05 01 00 00",
    "new_hex":    "18 00 00 00 76 01 00 00",
    "description": "LapTimer instruction 13: CALL PostEvent -> CALL AddHelpMessage …",
    "script": "LapTimer", "instruction": 13,
    "old_native": "PostEvent", "new_native": "AddHelpMessage",
    "argc": 1, "returns_value": false,
    "new_native_named_in_symtab": false     // not required by ExecuteCall; recorded
  }],                                       // because all 9,236 shipped calls satisfy it

  "splice": null,                           // or the length-changing edit

  "verification": {
    "source_parsed": true, "source_sentinels": {"RLWD": "14/14", "BSWD": "4/4"},
    "output_parsed": true, "output_sentinels": {"RLWD": "14/14", "BSWD": "4/4"},
    "intended_framing_break": null, "framing_error": null,
    "chunk_chain_closes": true,
    "roundtrip_inflated_identical": true, "block_structure": "preserved",
    "diff_ranges": 2, "edit_ranges": 2, "ranges_within_edits": true, "changed_bytes": 5
  },

  "derived_from": { … present on control arms: the probe's path and sha … },
  "unproven": [ … anything this build cannot claim … ],
  "notes": [ … ]
}
```

`verify` re-reads the manifest, confirms the source is still the archive the
edits were computed against (every `expect_hex` still present at its offset),
and confirms the output on disk is still the file described.

### Tests

```sh
python tools/probe/test_probe_author.py        # exit 0 = pass
```

43 checks and **17 guards proven falsifiable**. Every guarded behaviour is tested
twice: once that it works or refuses, and once that the thing it guards, when
deliberately broken, is *caught*. A sabotage that sails through is reported as
`VACUOUS` and fails the suite — because a guard that cannot fail is worse than no
guard, it is a trusted one.

The suite hashes the specimen and every source archive before and after, and
asserts they are byte-identical.

---

# Stage 2 — running

Status: implemented, and run against the real binary. Its tests still use fakes
only; the original nine live launches of 2026-08-02 are recorded in
[`probes.integration-proof.json`](probes.integration-proof.json), which is the
manifest that was actually executed. The six logger replications and aggregate
READY live under `local-lab/logger-oracle-pilot-2026-08-02/`.
Last updated: 2026-08-02.
Summary: run a list of engine probes end to end, unattended, and get a receipt
per probe. This directory owns launch mechanics so probe authors do not have to.

### Why this exists

On 2026-08-02 three console probes measured nothing and a fourth, differing by
one command-line argument, executed four console commands. The difference
between an answer and a wasted afternoon was launch mechanics, not science.

Everything that has to be right at launch time is here and is enforced, not
remembered:

| Mistake | What it looks like | What the harness does |
|---|---|---|
| no `-level` | game sits in the frontend, `autoexec.con` never read, arm reads as "console is gated" | `-level` is appended from the probe's `level` field and is **refused** in `gameArguments` |
| wrong CWD | dies at sound init, reads as "the payload killed it" | CWD is pinned to the staged root; `diagnose` reads `setuphistory.txt` and names this case explicitly |
| forgotten `autoexec.con` | executes silently on every future level load of that tree | armed stale files are a hard stop before the run; ours is removed after, even on the failure path, even with `--keep-scratch` |
| writing to the shared safe copy | every other instrument in the repo is now measuring a different game | staging always copies out; source `BEA.exe` and `BEA.exe.original.backup` are hashed before **and after** |
| a payload that is not the one the probe was written against | a real result about the wrong bytes | `expectSha256` per staged file, verified before the copy |
| a declared output inherited from the copied source tree | stale bytes satisfy a content oracle before the game writes anything | recursively declared oracle/collection outputs are removed before launch and recorded in `removedInheritedOutputs` |

### Interface

```
python tools/probe/probe_harness.py <manifest.json> [options]

  --dry-run              enforce every interlock, stage nothing, launch nothing
  --out DIR              receipts and artefacts (default local-lab/probe-runs)
  --scratch DIR          parent for staged copies (default %TEMP%/bea-probe-scratch)
  --only NAME            run one probe; repeatable
  --keep-scratch         keep the staged tree for inspection
  --strict-autoexec      treat ANY autoexec.con as fatal, not just armed ones
```

Exit codes: `0` every oracle satisfied (or a clean dry run), `1` a probe ran and
its oracle was not satisfied, `2` something failed closed — a refused interlock,
a bad manifest, a failed teardown. **An error is never excused by `--dry-run`**:
a refused interlock is exactly what a dry run exists to surface, and the first
live dry run of this harness reported one in the receipt and then exited 0.

A probe is a JSON object. `probes.example.json` is a working four-arm manifest.

```jsonc
{
  "name": "console-smoke",      // safe directory name; must be unique
  "level": 100,                 // becomes "-level 100"; NOT optional
  "sourceRoot": "…",            // relative to the manifest file
  "gameArguments": ["-skipfmv", "-forcewindowed"],
  "makeDirs": ["data/Memory"],  // the engine does not create output dirs
  "autoexec": ["Echo HI", "Quit"],   // written CRLF/ASCII with a terminator
  "stage": [{ "source": "…", "dest": "data/Resources/905_res_PC.aya",
              "expectSha256": "…" }],
  "collect": ["data/Memory/probe_ok.txt"],
  "oracle": { … },
  "record": false,              // optional TTD arm, see below
  "recordSeconds": 45,
  "note": "prose, reproduced in the receipt"
}
```

Unknown keys and unknown oracle kinds are **hard failures**. A typo that
silently defaults is how a probe reports PASS without checking anything.

### Oracles

A probe declares what would count as having happened. All signals below are
measured ones.

| kind | satisfied when | use it for |
|---|---|---|
| `processExit` | the process exits on its own; optional `expectExitCode` | a `Quit` in `autoexec.con` — the container experiment's oracle |
| `fileAppears` | `path` exists with `minBytes` | anything a console command writes: `MemStats <n>` → `data\Memory\<n>`, `DumpMem` → `MemoryDumps\dump<n>.mem` |
| `fileTextSequence` | a safe relative file contains each distinct exact line `exactOccurrences` times and positive lines occur in declared order; `0` is an exclusion decided only at the deadline | authored logger sentinels, typed value transport, and stock-content negative controls |
| `fatalFault` | `OnslaughtException.txt` at the game root exists | the **poison control**: an arm that should die |
| `setupHistoryContains` | `setuphistory.txt` contains `text` | `Game::LoadLevel <n>`, render-method negotiation |
| `survives` | still alive at the deadline with no fault log | the accept arm: "the engine took these bytes" |
| `all` / `any` | over `of: [...]` | independent confirmations in one run |

`survives` is the only oracle whose PASS is *reaching* the timeout; the poller
knows this and does not decide it early. Every other oracle is decided the
moment it is true, the moment the process dies, or at the deadline — whichever
comes first — and a dead process always ends the wait, because a dead process
cannot produce new evidence.

### Diagnosis — separate from the oracle, run every time

Whatever the oracle says, every run reads `setuphistory.txt` and records
whether `Game::LoadLevel <n>` was ever logged. This is the check that keeps a
launch failure from being written up as an engine finding:

* fault log present → a fatal fault inside the engine;
* `setuphistory.txt` absent or empty → the game never reached its own logging;
* logging present but no `Game::LoadLevel` → **died before level load; this is
  what a wrong working directory looks like, and it is not evidence about the
  payload**;
* `Game::LoadLevel` present → a negative result here is about the payload.

### Receipts

One directory per probe run under `--out`, containing `receipt.json`,
`receipt.md`, and an `artefacts/` copy of everything collected — always
including `setuphistory.txt` and `OnslaughtException.txt` whether or not the
probe asked for them.

`receipt.md` carries, in this order: verdict and wall time; **Staged** (source
root, scratch root, `BEA.exe` sha256, every staged file with its sha256 and the
sha256 of what it replaced, the `autoexec.con` body and its sha256, and the
source witness hashes re-verified after the run), plus inherited engine logs and
declared outputs removed before launch; **Command** (the exact argv and the
working directory); **Oracle** (kind, outcome, detail, exit code);
**Diagnosis**; **Artefacts**; **Teardown**; and **Failure** if there was one.

### Teardown, and how it is enforced

Teardown is in a `finally` that runs on every path — oracle failure, launcher
exception, interlock refusal after staging. It does three things and then
**verifies rather than assumes**:

1. delete `autoexec.con`, unconditionally;
2. delete the scratch tree, unless `--keep-scratch`;
3. re-check that no `autoexec.con` survives, and re-hash the source witnesses.

Anything left undone is recorded in `teardown.errors`, flips the receipt to
`ERROR`, and fails the run. `--keep-scratch` preserves the staged tree but
never the `autoexec.con`: keeping the landmine for inspection is not worth the
chance it is forgotten.

The pre-run scan classifies rather than blanket-bans. **ARMED** means the file
sits beside a `BEA.exe` — a directory that can be a process CWD, the only place
it has any effect — and is a hard stop. **INERT** means anywhere else (an
archived probe input under `local-lab`, a fixture) and is reported in the
receipt. `--strict-autoexec` makes inert ones fatal too.

### Recording

`record: true` delegates the launch to `tools/ttd_record.ps1` and reimplements
none of it — not its interlocks, not its drive policy, not its elevation
refusal, not its receipt deferral. It needs the maintainer's elevated window.

**The harness does not need it.** Without `record`, a console-only probe runs
today with zero human involvement, which is the whole point of the console
route.

### Tests

```
python tools/probe/probe_harness_tests.py                 # 82 tests
python tools/probe/probe_harness_tests.py --prove-can-fail
```

Nothing here launches the game. A fake launcher writes exactly the artefacts
the engine writes, on a fake clock, so a 90-second timeout is exercised in under
a millisecond.

`--prove-can-fail` is the important one. It breaks each guarded behaviour in
turn — disables the pristine-hash interlock, neuters the stale-`autoexec.con`
scan, makes teardown skip the file, makes every oracle agree, stops re-checking
the source witnesses, lets the parser accept unknown keys, unpins the CWD,
demotes the installed-game refusal, lets a dry run excuse an error — and
requires the guarding test to fail. A mutation that leaves the suite green is
reported as a survivor and exits non-zero, because a test that cannot fail
proves nothing.

Current: **82 tests pass; 16 mutations, 16 detected, 0 survived.**

The last two mutations exist because the first live dry run of this harness
found two real defects that the fake-driven suite had missed — the exit code
excusing an errored dry run, and the installed-game refusal being ordered after
the existence check, so a Program Files path that happened not to exist was
reported as a fixable typo. Both are fixed, both now have tests, and both
mutations confirm those tests bite.

---

# Stage 3 — refuting

Status: exercised on live findings — two records from the 2026-08-02 integration
run were adjudicated, one SURVIVED and one UNSCORED, and all 16 rules were shown
to fire on the surviving record by mutating it one field at a time. Two
adjudications is still far too few for `--audit` to say anything, and it says so:
INSUFFICIENT_DATA, exit 1.
Last updated: 2026-08-02
Summary: a discovery loop that generates findings unattended needs a stage that
tries to kill them unattended. This is that stage — a finding schema, a checker
that enforces admissibility, and an adversary harness — plus the self-test that
holds it to the case that beat us.

### Why

On 2026-07-31 this project derived a skin-weight law, byte-verified it against
the pristine specimen, reproduced it independently over all 3,203 shipped
skinned vertices, stated four predictions in advance and got MATCH on every one.
It was wrong, and an implementation built on it would have deformed a quarter of
every character's vertices toward the wrong bone.

Nothing in that note was false. The byte facts were true under the wrong law and
under the right one, because the thing separating them — one dead register write
in the shader's final combine — was named in the note's own residual list as
unresolved and *"not load-bearing for the law"*.

`local-lab/SKIN-WEIGHT-LAW-2026-07-31.md` (superseded) and
`local-lab/PUZZLE-SKIN-WEIGHTS-2026-07-31.md` (what was true) are the pair. They
are the specification for this directory, and both are transcribed into
`fixtures/` so the stage is tested against the real record rather than a
sanitised one.

### What is here

| file | what it is |
| --- | --- |
| `finding_schema.json` | the record a discovery loop must emit. Single source of truth for fields and enums — `refute.py` loads it rather than restating it |
| `refute.py` | the checker: 16 named admissibility rules, four verdicts, four exit codes |
| `ADVERSARY-PROMPT.md` | the brief handed to a refuting agent. Six attacks, run in order, with a required return shape |
| `adversary.py` | renders the brief, merges the attack report back into the finding, and audits the refuter's own kill rate |
| `fixtures/` | the two real 2026-07-31 records |
| `refute_tests.py` | 43 tests, including 16 mutations and 16 rule-neuterings |

No third-party dependencies; `jsonschema` is not installed on this machine, so
`refute.py` carries a small validator for the schema subset the file uses.

### Using it

```
python tools/probe/refute.py FINDING.json                # adjudicate
python tools/probe/refute.py --template > new.json       # blank record
python tools/probe/refute.py --explain                   # the 16 rules
python tools/probe/adversary.py --brief FINDING.json     # the attack brief
python tools/probe/adversary.py --merge FINDING.json --attack ATTACK.json -o merged.json
python tools/probe/adversary.py --audit --ledger local-lab/probe/refutation-ledger.jsonl
python tools/probe/refute_tests.py                       # self-test
```

The loop shape:

```
    discover  ->  finding.json
                     |
                     v
              refute.py ------------------ exit 2 INADMISSIBLE -> back to the author
                     |                     exit 1 REFUTED      -> kill it, record it
                     |                     exit 3 UNSCORED     -> go and observe
                     v
              adversary --brief  ->  refuting agent  ->  attack.json
                     |
              adversary --merge  ->  finding.json (now carrying a live rival)
                     |
                     v
              refute.py again    ->  exit 0 SURVIVED -> may be promoted
```

A rival merged in with `status: not_observed` turns SURVIVED into UNSCORED. That
is the loop working: the refuter has named an observation nobody made, and the
next probe now has a target.

### Verdicts and exit codes

| verdict | exit | meaning |
| --- | ---: | --- |
| `SURVIVED` | 0 | admissible, every rival eliminated by an observed discriminator. **Only this may be promoted.** |
| `REFUTED` | 1 | a prediction mismatched, or a discriminator landed on a rival's side. A good outcome. |
| `INADMISSIBLE` | 2 | the record cannot be judged. Not a finding yet. |
| `UNSCORED` | 3 | admissible, and a required observation was not made. |

`UNSCORED` follows the precedent set by `tools/score_frontend_capture.py`, whose
docstring is the canonical statement of the rule: *"no evidence" must never
render as "no problem"*. One deliberate divergence — that tool exits 0 on
UNSCORED because a human reads its output; here the caller is an unattended loop
that promotes on exit 0, so UNSCORED exits **non-zero**.

### The two rules that carry the 2026-07-31 lesson

**R05_RIVALS_STATED.** A finding must name at least one live competing
explanation. The record as actually written names none, so nothing in it was
ever asked to choose. This is the only rule that fires on the real record.

**R08_RESIDUAL_TOUCHES_DISCRIMINATOR.** A residual marked `blocksClaim: false`
may not name a mechanism that a rival's discriminator depends on. Give the
2026-07-31 author every benefit of the doubt — write the rival down correctly —
and this fires on the residual that waved the shader combine away.

Mark that residual blocking instead, and the verdict is UNSCORED, because the
shader had not been read. **There is no honest spelling of that claim that
reaches SURVIVED**, and `test_no_honest_spelling_of_the_2026_07_31_claim_
reaches_survived` asserts exactly that over all three spellings.

### The checker is itself checked

Three layers, because a gate that cannot fail is the defect this exists to
prevent:

1. `MutationTests` — one mutation per rule against the record that *does*
   survive. 16 mutations, 0 survivors. `test_every_rule_has_a_mutation` makes a
   new rule without a falsification a red suite.
2. `EveryRuleIsLoadBearing` — each rule is replaced in turn by a stub that can
   never fire, and its own mutation is re-adjudicated. If the verdict does not
   change, the rule is dead weight. All 15 are load-bearing.
3. `adversary.py --audit` — the kill rate over a trailing window. Below the
   floor is a rubber stamp; above the ceiling is a stage that has stopped
   discriminating; a high UNSCORED share is a different disease
   (`LOOP_NOT_OBSERVING`) and gets its own name. `INSUFFICIENT_DATA` is not a
   pass and exits non-zero.

### Known limits

* The mechanism-overlap check in R08 compares **strings**. It cannot see that
  `shader.final_combine` and `palette.translation` are the same question written
  two ways. That gap is what the human/agent refuter in `ADVERSARY-PROMPT.md` is
  for, and it is the most likely way a bad finding still gets through.
* Grades are self-reported. R09 catches a claim graded above its own
  discriminating evidence; it cannot catch evidence graded generously.
* The fixtures are transcriptions. They are faithful to the notes, but they are
  not the notes, and the notes are the evidence.
* The author, runner, mutation proof, refuter, comparison self-check and selector
  self-check are wired into `npm run test:tools` through
  `tools/run_tool_tests.py`.
