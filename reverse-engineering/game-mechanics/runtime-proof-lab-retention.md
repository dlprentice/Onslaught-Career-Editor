# Runtime proof lab retention (tracked summary)

Status: active  
Last updated: 2026-07-14

## Rule

**Safe-copy while running. Compact evidence after closeout.**

| Phase | Action |
|-------|--------|
| Live run | Operate only on copied targets / app-owned profile roots. Never patch Steam or original `BEA.exe`. |
| After closeout | Delete full `profile-app-config` game trees and private runner `bin`/`obj` junk. |
| Durable science | Keep metrics, raw sample JSON (if small), receipts, digests, and **tracked** public contracts under `reverse-engineering/`. |

Ignored lab roots (`local-proofs/`, `game/`, `local-lab/`) may hold temporary copies. They are not the long-term archive of multi-GB duplicates per attempt.

## Walker scalar precedent

Accepted measurement is published at
[walker-forward-scalar-response-v2.json](walker-forward-scalar-response-v2.json).
Private full-profile pair directories from the 2026-07-14 campaign were pruned after
compact closeout retention; do not re-hoard them.

## Implementation target

Pair / live-runtime runners should automate post-closeout strip of game payloads
while preserving compact evidence (see current `goal.md` slice item 1).
