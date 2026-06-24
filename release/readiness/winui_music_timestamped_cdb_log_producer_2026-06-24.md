# WinUI Music Timestamped CDB Log Producer

Status: producer/checker infrastructure only
Date: 2026-06-24
Scope: `winui-safe-copy-music-timestamped-cdb-log-producer`

This slice adds `tools/winui_safe_copy_music_timestamped_cdb_log_producer.py`
and `test:winui-safe-copy-music-timestamped-cdb-log-producer`.

The producer creates a `winui-safe-copy-timestamped-cdb-log.v1` receipt and a
UTC timestamp-prefixed CDB evidence log for the future music audible-output
materializer. It consumes an explicit
`winui-safe-copy-timestamped-cdb-log-observations.v1` trusted-tail wrapper
ledger with `timestampSource=trusted-tail-wrapper-observation-ledger`, binds the
ledger to an untimestamped raw CDB log by raw log SHA-256 and per-line SHA-256,
and validates the produced timestamped log through the existing music CDB
timeline parser before accepting it.

What changed:

| Item | Evidence |
| --- | --- |
| Producer/checker | `tools/winui_safe_copy_music_timestamped_cdb_log_producer.py` |
| Test | `tools/winui_safe_copy_music_timestamped_cdb_log_producer_test.py` |
| Package script | `test:winui-safe-copy-music-timestamped-cdb-log-producer` |
| Contract update | `roadmap/music-audible-proof-contract.v1.json` now records `timestampedCdbLogProducer=true` while preserving `runtimeAudibleOutputProof=false`. |
| Gate update | `tools/winui_safe_copy_music_audible_output_live_bundle_gate.py` now records producer coverage is complete for the next private live attempt after preflight. |

Safety and privacy guards:

- rejects raw CDB logs that are already timestamped
- rejects ledgers not bound to the raw CDB log hash and per-line hashes
- rejects duplicate, out-of-range, or nonmonotonic timestamp observations
- rejects output outside the explicit allowed output root
- rejects overwriting the raw CDB log or observation ledger
- rejects symlink/reparse path components before read/write
- does not include raw file paths in the producer receipt

Claim boundary:

- `runtimeAudibleOutputProof=false`
- producer coverage is complete
- no BEA launch
- no CDB attach
- no audio capture
- no source/game payload read
- no process spawn
- no byte patch
- no installed-game mutation
- no original executable mutation
- no all-cue audio proof
- no gameplay parity proof
- no online proof
- no rebuild parity proof

Representative focused validation:

```powershell
py -3 tools\winui_safe_copy_music_timestamped_cdb_log_producer_test.py
py -3 tools\winui_safe_copy_music_timestamped_cdb_log_producer.py --self-test
npm run test:winui-safe-copy-music-timestamped-cdb-log-producer
npm run test:winui-safe-copy-music-audible-output-live-bundle-gate
```

Remaining future live-bundle raw evidence still required before any audible
claim: actual clean/staged timestamped CDB logs, clean/staged timeline sidecars,
clean/mute source-safety sidecars, ambient census, ambient/clean/staged/mute
audio captures, and capture-correlation sidecars accepted by the materializer
and final checker.
