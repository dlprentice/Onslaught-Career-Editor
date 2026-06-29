# WinUI Music Live Bundle Pre-Arm Readiness

Status: fail-closed prompt/readiness hardening
Date: 2026-06-29
Scope: `winui-safe-copy-music-audible-output-live-bundle-gate`

This slice hardens the public-safe live-bundle gate so producer coverage is not
confused with runtime-proof authority. The gate still records the 13 raw inputs
required by the private materializer path, but now reports:

- `producerCoverageComplete=true`
- `readyToRunLiveAttempt=false`
- `liveArmAllowed=false`
- `runtimeAudibleOutputProof=false`
- `preArmReadiness.status=prearm-readiness-not-proven`

The new `preArmReadiness` block records the pre-arm conditions a future private
operator must prove before running the armed executor:

- explicit runtime-proof authority and exact arm phrase
- exclusive leases for `bea-runtime`, `cdb-debugger`, `audio-loopback`, and
  `proof-root`
- passive no-preexisting-`BEA.exe`/`cdb.exe` process census
- empty isolated private proof root that does not overlap the read-only source
  game root
- copied profile and app-owned artifact roots only
- installed game and original `BEA.exe` read-only
- capture-start/stopwatch alignment, WAV wall-clock duration covering the CDB
  decode window, wall-clock padding metadata, padding byte totals, and canonical
  WAV header/data-frame consistency
- raw proof artifacts remain local/ignored
- readiness failure cannot claim audible output

The armed executor now also requires a private accepted
`winui-safe-copy-music-audible-output-live-bundle-prearm-readiness.v1` JSON
through `--prearm-readiness-json` before it can call the live bundle runner.
That private artifact is not a public proof artifact; it exists only to bind the
operator-side authority, leases, passive process census, proof-root, mutation,
capture-span, and failure-policy checks before live execution.

Claim boundary:

- no BEA launch
- no CDB attach
- no audio capture
- no copied executable mutation
- no installed-game or original `BEA.exe` mutation
- no runtime audible-output proof
- no all-cue, gameplay, online, release, rebuild, or parity proof
