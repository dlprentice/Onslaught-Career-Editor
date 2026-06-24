# GhydraMCP Runbook (BEA.exe)

> Practical operating guide for this repo's Ghidra + MCP workflow.
> Last updated: 2026-06-22

## Active Environment (Authoritative)

- Ghidra install (active): `D:\ghidra_12.0.3_PUBLIC_20260210\ghidra_12.0.3_PUBLIC`
- Ghidra projects root (active): `C:\Users\david\Ghidra`
- Active GhydraMCP bundle: `D:\GhydraMCP-Complete-v2.2.0-rc.2-20260211-083952`
- Repo-local `tools/GhydraMCP/` has been removed from this repo to avoid runtime-bundle confusion.
- Canonical workstation setup, mutation discipline, backup-root posture, and static closeout truth live in `AGENTS.md` sections `Ghidra / Headless Rules` and `Current Known Gaps`.
- After any chat context reset/compaction or Ghidra restart/deadlock, reread `AGENTS.md`, this runbook, the three repo state batons, and the relevant wave evidence before attempting mutations.
- Backup root note (2026-06-21): external `G:\` backup storage is not attached. For any new backup-producing Ghidra wave, use `D:\GhidraBackups` or another explicit local backup root until an external drive is available, and record that temporary root in the evidence/state. Historical docs may still cite older verified `G:\GhidraBackups\...` backup IDs.

## Two Access Modes (Same Backend)

There are two client paths to the same GhydraMCP backend:

1. Codex MCP tool transport (`mcp__ghydra__*`)
2. Direct HTTP calls to the GhydraMCP plugin (`http://<host>:8193/...`)

Transport arbitration on this workstation:

1. Use whichever path is currently healthiest (native Codex MCP tools or direct HTTP/curl).
2. Do not keep a fixed preference if reliability changes mid-session.
3. Continue strict serialized mutation/read-back rules regardless of chosen transport.
4. If one path becomes unstable, continue on the healthy path and keep logging outcomes.

If Codex MCP transport fails (for example `Transport closed`) but the plugin is running, direct HTTP still works and is valid for RE operations.

This is not bypassing GhydraMCP; it is bypassing only one client transport path.

## Endpoint Discovery

From WSL, use Windows gateway IP instead of localhost:

```bash
ip route
# Example default gateway observed on this machine:
# 172.26.112.1

curl http://172.26.112.1:8193/
curl http://172.26.112.1:8193/instances
curl http://172.26.112.1:8193/program
curl http://172.26.112.1:8193/analysis/status
```

Use the root `_links` response as the live source of available API routes for the currently running plugin.

## Command Discovery (How We Know What Is Supported)

Use both views:

1. Codex `/mcp` tool inventory (exposes the bridge tools, for example `functions_rename`, `project_info`, `analysis_status`)
2. Live plugin root `_links` (`GET /`) for the currently running GhydraMCP HTTP API

If an operation is not present in either list, treat it as unsupported by the current runtime build.

If `/mcp` shows an unexpected bridge path or `Tools: (none)`:

1. Check active config files for stale paths:
   - `/home/dlprentice/.codex/config.toml`
   - `/mnt/c/Users/david/.codex/config.toml`
   - `/home/dlprentice/.codex/config.wsl.toml`
   - `/mnt/c/Users/david/.codex/config.wsl.toml`
2. Ensure all `ghydra` args point to the pinned bundle bridge:
   - `D:\GhydraMCP-Complete-v2.2.0-rc.2-20260211-083952\bridge_mcp_hydra.py`
3. Kill stale bridge processes using old paths, then reload MCP in the client (`/mcp` disable+enable `ghydra` or restart Codex).

This exact mismatch occurred on 2026-02-11 (`/mcp` still showing `rc.1` while docs/config were on `rc.2`).

Important observed case:
- No reliable explicit "save now" API route is currently exposed in this environment.
- `POST /program/save` and `POST /project/save` return method-not-allowed.

## Save Semantics (Critical)

Ghidra persistence has two distinct concerns:

1. Mutation transaction success (change exists in current open program state)
2. Durable saved project state (`Save BEA.exe`) for clean reopen/restart behavior

Operational rules:

1. Apply mutation.
2. Read back by address immediately.
3. If read-back mismatches intent, record in `reverse-engineering/binary-analysis/MCP-MUTATION-BACKLOG.md`.
4. In throughput mode, perform explicit UI saves at practical checkpoints (risk boundaries, long runs, or before planned restarts).

Notes:

- Recovery snapshots can help after crashes, but they are not a replacement for deliberate save discipline.
- Transaction errors in logs (`Failed to end transaction`, parser errors, HTTP 408) should be treated as "not committed" unless read-back proves otherwise.

## Deadlock / Freeze Avoidance

Avoid automating project-open during active RE sessions:

- `project_open_file` / `/project/open` has triggered Swing deadlock in this project.
- Prefer opening files/programs in the Ghidra UI.
- Use MCP/HTTP primarily for analysis and mutation operations once the program is already open.

## Mutation Safety Pattern

Scope gate: this section applies only when an explicit RE mutation lane is active. It is not the default app-development workflow.

For each edit (rename/signature/comment/type):

1. Execute one mutation at a time (no parallel mutations).
2. Read back via `/functions/<addr>` or `/data?addr=<addr>&limit=1`.
3. If read-back is good, enforce a 5-second inter-command delay (`sleep 5`) before the next mutation command.
4. For owner-correction batches (`<Class>__Unk_*`), filter out non-owner/system caller labels even if singular (`entry`, CRT/stdio wrappers, `_longjmp`, `FatalError`, empty owner, parser artefacts). Promote only class/subsystem owners backed by evidence.
5. Log every touched address in `function_mutation_ledger.jsonl` and `function_mutation_attempt_log.jsonl` (success/failure + transport + operation details).
6. Update `function_mutation_tracking_state.json` in the same work window (counters + last touched + pending set).
7. Mirror status in `MCP-MUTATION-BACKLOG.md` pending/completed sections.
8. Update docs only after read-back confirms change.

Wave sizing rule (this workstation):

1. After restart/compaction, first mutation is a probe-only write (must include immediate read-back).
2. If probe is clean and UI/API remain responsive, switch to uncapped serialized throughput mode.
3. In throughput mode, keep strict per-address lock-step (`write -> read-back -> sleep 5`).
4. There is no wave-size hard cap; wave boundaries are optional checkpointing choices.
5. Save/checkpoint opportunistically (for example after risky operations or long runs), then confirm `saved`.
6. If timeout/deadlock/mismatch occurs, verify survival read-back first, then continue on the healthiest path (HTTP if available) or recover/restart and resume from the first unverified address.

Tracking files (mandatory):

1. `function_mutation_ledger.jsonl`: canonical per-address task ledger (pending/completed mutation intent).
2. `function_mutation_attempt_log.jsonl`: per-attempt execution log (transport + operation + read-back result).
3. `function_mutation_tracking_state.json`: synchronized counters/pending set/next attempt id for fast resume after deadlocks.

Recommended verification snippets:

```bash
curl -sS http://172.26.112.1:8193/functions/00401000
curl -sS 'http://172.26.112.1:8193/data?addr=0083d130&limit=1'
curl -sS 'http://172.26.112.1:8193/functions?name_contains=FUN_&offset=0&limit=1'
```

## Documentation Audit (Read-Only)

This repo includes a read-only “online semantic audit” that cross-checks documented function mappings against the live Ghidra instance via HTTP `GET /functions/<addr>`:

```bash
python3 tools/semantic_audit_online.py --base http://172.26.112.1:8193 --timeout 2
```

Outputs (dated):

- `reverse-engineering/binary-analysis/semantic-audit-online-YYYY-MM-DD.md`
- `reverse-engineering/binary-analysis/semantic-audit-online-pass-YYYY-MM-DD.json`

If the audit reports `missing_function` for a vtable-only target (data xref, no discovered callers), manual UI function creation is often required:

1. `G` -> go to the address (e.g. `004621d0`)
2. Click inside the **Listing** pane (center) so it has focus
3. If bytes are not disassembled: press `D` (Disassemble)
4. Press `F` (Create Function)
5. Save (`File -> Save` / `Save BEA.exe`)

Then rerun the audit and apply renames/signatures as needed (serialized, with read-back).

### Manual-First Batch Rename (Deadlock Mitigation)

When API `PATCH` rename/signature waves are triggering UI deadlocks, use the in-process Ghidra script path instead of HTTP mutation:

1. In Ghidra Script Manager, run `tools/GhidraBatchRename.java` (or use headless wrapper `tools/run_ghidra_batch_rename_headless.sh <map> dry|apply` with GUI closed).
2. Choose a rename map file in this repo (example: `reverse-engineering/binary-analysis/scratch/auto-tail-2026-02-25/auto_tail_manual_rename_2026-02-25.txt`).
3. Run a dry-run first, then run live.
4. Save `BEA.exe`.
5. Have Codex verify via read-only `GET /functions/<addr>` and refresh backlog/state.

This keeps mutation on the CodeBrowser/UI side (same mechanism as manual `L` rename), while still preserving automated verification and documentation sync.

## Current Known Limits

Coverage closure note (2026-03-04): strong semantic naming is at 100% in the canonical tracker. Treat older per-address create-function "gaps" in historical notes as archived unless re-opened with fresh evidence.

- No reliable API route is currently documented/verified for explicit "save program now" from GhydraMCP.
- Use UI save (`Save BEA.exe`) for durability.
- In this runtime, `analysis_run` can be unavailable even when advertised by tool metadata (re-verified 2026-02-11 on `:8193`: `analysis_run` => `Endpoint not found`); use `analysis_run_background` as the fallback.
- `functions_set_signature` on `0x0042b500` (`CConsole__Status`) is a known hotspot: both MCP transport and direct HTTP `PATCH /functions/0x0042b500` can time out while read endpoints remain healthy.
  - Preferred fallback: rename parameter manually in CodeBrowser (`sectionName` -> `status_line`), save, then verify with read-back (`GET /functions/0x0042b500`).
  - Once read-back matches, do not keep re-patching this signature.
  - Revalidation on upgraded runtime (2026-02-12, `rc.2`): same-signature reapply still timed out; `functions_get(0x0042b500)` and `instances_current` remained healthy immediately after.
- `functions_set_signature` on `0x0042b800` (`CConsole__StatusDone`) is also a hotspot on upgraded runtime (`rc.2`):
  - MCP `functions_set_signature(0x0042b800, "...status_line...")` timed out during parameter-name normalization (`sectionName` -> `status_line`).
  - Immediate read endpoints remained healthy and read-back confirmed no signature change landed.
  - Preferred fallback: manual CodeBrowser parameter rename + save + read-back verification, then avoid MCP signature retries on this address.
  - Fallback execution status (2026-02-12): manual rename was applied successfully and read-back now shows `void CConsole__StatusDone(void * this, char * status_line, char success)`.
- `functions_set_signature` on `0x00421350` (`CCareer__Save`) can time out and hard-freeze CodeBrowser (observed 2026-02-13).
  - After restart, read-back showed the signature present; treat as an MCP-signature hotspot and avoid repeating MCP signature writes here.
  - Preferred fallback (if signature needs to change): manual CodeBrowser `Edit Function...`, save, then verify via read-back (`functions_get(0x00421350)`).
- `functions_create` failures with `IllegalArgumentException: Function body must contain the entrypoint` can occur on orphan targets.
  - Current evidence indicates this is not caused by clicking Save in CodeBrowser.
  - `domainFileStatusChanged ... fileIDset=false` is a dirty-state signal (unsaved changes available), not the root cause of create-function rejection.
  - Treat as Ghidra/plugin create-function behavior on those addresses and keep comment-first fallback until manual/UI recovery succeeds.
- Historical recovered-address narratives and prior create-function hotspots are intentionally tracked in mutation logs/backlog, not repeated here to avoid stale runbook drift.
- For other limitations and workarounds, see `MCP_LIMITATIONS.md`.

## Sources / References

- GhydraMCP project: https://github.com/starsong-consulting/GhydraMCP
- Ghidra ProgramManager API (save/close semantics): https://ghidra.re/ghidra_docs/api/ghidra/app/services/ProgramManager.html
- GhidraProject save API: https://ghidra.re/ghidra_docs/api/ghidra/base/project/GhidraProject.html
- Ghidra save dialog docs: https://ghidra.re/ghidra_docs/api/ghidra/framework/main/SaveDataDialog.html
- Ghidra recovery-related APIs:
  - https://ghidra.re/ghidra_docs/api/ghidra/program/database/ProgramContentHandler.html
  - https://ghidra.re/ghidra_docs/api/ghidra/framework/store/local/LocalDataFile.html
