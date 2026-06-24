# WinUI Music Audible-Output Live Bundle Executor

Status: private executor/checker infrastructure only
Date: 2026-06-24
Scope: `winui-safe-copy-music-audible-output-live-bundle-executor`

This slice adds the private live-bundle executor that can run one bounded music
audible-output raw-bundle attempt when explicitly armed. It composes the
existing producers rather than accepting a hand-authored proof summary.

Added:

| Item | Evidence |
| --- | --- |
| Executor | `tools/run_winui_safe_copy_music_audible_output_live_bundle.py` |
| Tests | `tools/run_winui_safe_copy_music_audible_output_live_bundle_test.py` |
| Package script | `test:winui-safe-copy-music-audible-output-live-bundle-executor` |
| Contract marker | `liveBundleExecutor=true` in `roadmap/music-audible-proof-contract.v1.json` |

Executor responsibilities:

- runs ambient no-BEA process census with a concurrent ambient loopback capture;
- runs clean and staged level-100 copied-game launches with exact-PID CDB
  observer, concurrent loopback capture, trusted-tail CDB observation ledger,
  timestamped CDB log producer, and timeline sidecar;
- runs the mute-control copied-game launch with `--launch-nomusic` and
  concurrent loopback capture;
- builds clean/mute source-music safety sidecars and clean/staged
  capture-source correlation;
- promotes only through
  `tools/winui_safe_copy_music_audible_output_materializer.py` and immediately
  revalidates with
  `tools/winui_safe_copy_music_audible_output_two_run_harness_check.py`.

Safety controls:

- exact arm phrase required: `RUN PRIVATE MUSIC AUDIBLE LIVE BUNDLE`;
- source root must exist and must not overlap the private proof root;
- private proof root must be empty for a new attempt;
- refuses to start while `BEA.exe` or `cdb.exe` is already running;
- child processes run with a stripped Windows/tooling environment instead of
  inheriting the full parent shell;
- stripped child environments preserve Windows loader variables
  case-insensitively, including `SYSTEMROOT`/`COMSPEC`, so native tools such as
  `tasklist.exe` can load their system modules;
- executor subprocesses use outer timeouts and task-tree cleanup on timeout;
- failed bundle attempts now run a proof-root-bounded cleanup pass before the
  final process census. The cleanup only targets copied `BEA.exe` processes
  under a generated stage `live\GameProfiles` folder with a copied-profile
  manifest, or `cdb.exe` processes whose command line points at the exact stage
  CDB log path. Each PID is re-read before `taskkill` to reduce PID-reuse risk;
- loopback capture helper disposes its WAV writer before hashing the raw WAV;
- ambient process census allows for loopback-helper startup/build overhead
  before requiring the ambient audio JSON sidecar;
- copied-game live stages wait for the loopback-helper startup margin before
  launching BEA, so CDB decode rows are not allowed to race ahead of capture;
- CDB-backed music stages can request early exact-PID attach immediately after
  copied-process launch, before main-window/post-window waits, so one-shot
  startup music breakpoints have a chance to arm before the level music path;
- clean/staged CDB-backed live-smoke stages are rejected before timestamping
  or materialization unless the stage binds CDB target PID to the launched
  safe-copy `BEA.exe` PID, reports an attached positive CDB PID, reports a
  matching cleanup PID, and cleanup status is `stopped` or `already-exited`;
- direct live-smoke success also requires a positive CDB PID and accepted CDB
  cleanup status when the CDB observer is enabled;
- the executor reruns the no-`BEA.exe`/no-`cdb.exe` process census after each
  accepted CDB-backed stage before timestamp/timeline generation, and again
  before accepting or recording a failed final receipt;
- live-smoke stages use app-owned copied profiles and the existing
  `ALLOW EXTERNAL LIVE SMOKE ARTIFACT ROOT`, `LAUNCH SAFE COPY BEA`, and
  `ATTACH CDB TO SAFE COPY BEA` arm phrases;
- default proof root is under private external storage:
  `<private-proof-root>\music-audible-live-*`.

Claim boundary:

- `runtimeAudibleOutputProof=false` remains current truth until a private live
  raw bundle passes the materializer and final checker;
- no audible-output proof is added by the executor self-test;
- no public release claim changes;
- no installed-game mutation;
- no original executable mutation;
- no online proof;
- no gameplay parity proof;
- no rebuild proof;
- no no-noticeable-difference parity proof.

Validation:

```powershell
py -3 tools\capture_audio_loopback_test.py
py -3 tools\run_winui_safe_copy_music_audible_output_live_bundle_test.py
py -3 tools\run_winui_safe_copy_music_audible_output_live_bundle.py --self-test
npm run test:audio-loopback-capture-helper
npm run test:winui-safe-copy-music-audible-output-live-bundle-executor
npm run test:winui-safe-copy-live-runtime-smoke-helper
```

Private preflight note: one synthetic calibration-tone loopback capture under
the private external proof root observed non-silent output on the default render
endpoint. A first live-bundle invocation failed before any BEA launch because
the stripped child environment omitted `SYSTEMROOT` for `tasklist.exe`; the
case-insensitive environment preservation above fixes that pre-launch blocker.
The next private live-bundle invocation captured ambient silence but failed
before any BEA launch because the ambient census ended before the audio helper
wrote its JSON sidecar; the startup-margin synchronization above fixes that
pre-launch blocker.
A subsequent clean-commit retry confirmed the race fix: the ambient audio JSON
existed and the census replay accepted the same process samples, but the live
bundle still stopped before BEA launch because the ambient census producer only
accepted literal `Z` UTC timestamps while the loopback helper emitted UTC
`+00:00` timestamps. The census producer now accepts both strict UTC forms and
still normalizes its sidecar output to `Z`.
A later retry progressed into the clean baseline copied-BEA stage and attached
CDB to the exact copied PID. It caught lower-level music/decode rows
(`CMusic__PlaySelection`, async stream kick, Ogg open, update status, and
positive decoded PCM), but the strict materializer contract still rejected the
bundle because the one-shot `CGame__PlayMusicForCurrentLevel level=100` row was
missing. Normal and adversarial consults agreed not to weaken that contract
yet. The live-smoke helper now supports `--cdb-attach-phase after-launch`, and
the private live-bundle executor uses it for clean/staged CDB music stages.
A 2026-06-24 public-primary retry (`music-audible-live-20260624-160116`)
timed out in the clean-baseline live stage after early exact-PID CDB attach and
left copied BEA/CDB processes that required manual cleanup. This slice fixes
that parent-executor cleanup gap. A later retry
(`music-audible-live-20260624-161657`) failed later in the timestamped CDB
producer because the required `CGame__PlayMusicForCurrentLevel level=100` row
was still absent. It recorded `failureProcessCleanup.matchedProcessCount=0`,
and the post-run process census found no `BEA.exe` or `cdb.exe`.
`runtimeAudibleOutputProof=false` remains current truth.
A follow-up caller diagnostic
(`winui_music_cgame_caller_diagnostic_2026-06-24.md`) accepted one bounded
level-100 copied-runtime observation with classification
`restart-loop-direct-level100-music-selection-observed`: the wrapper-entry row
was still absent, but `CMusic__PlaySelection` was reached from return address
`0x0046e0bf`, the direct restart-loop music-selection call site inside
`CGame__RestartLoopRunLevel`. This narrows the prior failure to materializer
contract/attach-timing provenance, not proof that level-100 music selection did
not occur. It still leaves `runtimeAudibleOutputProof=false`.

The materializer/timeline/final-checker contract now carries explicit
`musicSelectionProvenance` values and accepts only `cgame-wrapper` or
`cgame-restart-loop-direct` when the timestamped CDB log and timeline sidecar
agree. This lets a future complete raw bundle represent the observed
restart-loop direct selector path without pretending the wrapper-entry row was
seen. Accept an audible-output claim only if the materializer and final checker
pass against a generated private raw bundle with audio, source-safety,
capture-correlation, process-cleanup, and provenance evidence intact.
