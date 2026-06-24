# MCP Limitations (Ghidra / GhydraMCP)

Status: private maintainer/workstation note
Release posture: excluded from public/community release profiles
Last updated: 2026-05-01

This file records local Ghidra/GhydraMCP capability gaps and workarounds for private maintainer RE work. Public-safe binary-analysis guidance lives under `reverse-engineering/binary-analysis/`; this root note remains release-excluded because it can include workstation-specific runtime details.

This is a living list of MCP feature gaps and reliability constraints we have hit while mapping `BEA.exe` in Ghidra via GhydraMCP.

If you just hit a chat context reset/compaction or recovered from a Ghidra deadlock/restart, run `AGENTS.md` section `Context Reset / Compaction Resume Checklist` before acting on items below.

## Confirmed Limitations / Gaps

### 1) Cannot Rename Arbitrary Code Labels (`LAB_...`)

GhydraMCP exposes:
- Function rename (`functions_rename`)
- Data rename (`data_rename`)

It does **not** expose a direct “rename code label” operation for non-function labels like `LAB_0041b6a0`.

**Workaround:**
- Add a plate/pre comment at the label address describing the target (and optionally record the intended label name in `reverse-engineering/binary-analysis/MCP-MUTATION-BACKLOG.md`).

### 2) `functions_create` Fails on Some Valid Code Blocks

We have multiple “orphan” code blocks that clearly behave like functions (they have prologue/epilogue and are jumped/called), but `functions_create` can fail with errors like:
- `Function body must contain the entrypoint`
- Follow-on “clear and disassemble” retries also failing

Concrete examples observed in this repo:
- Options context helpers around `0x0051f7e0` (MCP `functions_create` can fail; manual CodeBrowser create (`F`) recovers a function object, after which MCP decompile/rename/signature read-back works)
- Some init-table targets that are referenced as code labels (e.g., `LAB_0041b6a0` referenced by `g_InitFuncTable`)
- FE language-test vtable slot `0x0051bfa0` initially failed via MCP create-path but was successfully recovered via manual CodeBrowser create (`F`) and then mapped with MCP read-back (`CFEPLanguageTest` ownership correction applied).

Upstream context (source-sidequest, 2026-02-11):
- `starsong-consulting/GhydraMCP` commit `f38d51f` changed function creation to use `CreateFunctionCmd`.
- Workstation runtime was upgraded to `v2.2.0-rc.2` on 2026-02-11; previously logged `rc.1` fallback behavior should be revalidated under the new bundle before keeping old assumptions.

**Workaround:**
- Leave as a label and add a high-quality plate comment.
- Optionally create a dedicated RE doc page for the address so the meaning is captured even without a function object.

### 3) Analysis Endpoints Are Partially Available

On the current `BEA.exe` Ghidra instances (`:8192/:8193`), analysis endpoints are a mix of working and missing:
- `analysis_status` works (`GET /analysis/status`)
- `analysis_get_callgraph` works (`GET /analysis/callgraph?...`)
- `analysis_get_dataflow` can still return `HTTP 404 Not Found` (`GET /analysis/dataflow?...`) depending on the plugin build/instance
- `analysis_run` may return `Endpoint not found` even when advertised by the bridge/tool list
- Current validation (2026-02-11, instance `:8193`): `analysis_run` returned `Endpoint not found`, while `analysis_run_background` returned success (`Done`).

**Workaround:**
- Rely on Ghidra UI analysis configuration and built-in graphing when needed.
- Prefer `analysis_run_background` when `analysis_run` is unavailable.
- Treat MCP analysis endpoints as “best effort”; verify any results via xrefs/decompile.

### 4) Data Renames Require Defined Data

`data_rename` only works if there is **defined data** at that address (string, dword, pointer, struct, etc.). For raw/undefined bytes you must define data first.

**Workaround:**
- Use `data_create` (e.g., create a `dword`/`pointer`/`string`) before `data_rename`.
- If the region is truly code-adjacent or ambiguous, prefer a comment over forcing a data type.

### 5) Mutating Calls Are Fragile (Transactions / Timeouts)

Even when a capability exists, mutating calls can intermittently fail:
- Transaction end failures (e.g., “Failed to end transaction: Rename Function”)
- HTTP 408 timeouts on mutating endpoints (`functions_set_signature`, `functions_set_comment`, `comments_set`, etc.)

This tends to correlate with Ghidra being busy (auto-analysis, large transactions, UI not idle).

**Important root cause (bridge-side):** the stock `bridge_mcp_hydra.py` shipped with GhydraMCP uses a hard-coded HTTP timeout of **10 seconds** for all requests. Some state-changing operations (renames, signature changes, type changes) can legitimately take far longer than 10s on `BEA.exe` (often because Ghidra kicks off follow-on analysis), so the bridge returns a timeout and the client aborts the connection even if Ghidra eventually applies the change.

**Workaround:**
- Do not parallelize mutations.
- Retry a few times after the UI is idle.
- If it still fails, record the intended change in `reverse-engineering/binary-analysis/MCP-MUTATION-BACKLOG.md` and proceed.
 - If timeouts persist, increase the bridge request timeout (e.g., **300s+** for `BEA.exe`) and restart the MCP server process.

Known hotspot (confirmed repeatedly):
- `0x0042b500` (`CConsole__Status`) signature updates via `functions_set_signature` / direct HTTP `PATCH /functions/0x0042b500` can time out even while read endpoints are healthy.
- Reliable fallback is manual CodeBrowser parameter rename (`sectionName` -> `status_line`) plus immediate read-back verification.
- Once read-back is correct, avoid re-running signature patch on this specific address.
- Revalidated on upgraded runtime (2026-02-12, `rc.2`): same-signature reapply still timed out while immediate reads stayed healthy.
- `0x0042b800` (`CConsole__StatusDone`) now shows the same signature-timeout pattern on upgraded runtime (2026-02-12, `rc.2`): MCP `functions_set_signature` timed out while immediate read endpoints stayed healthy, and no signature change landed.
- Reliable fallback for `0x0042b800` is manual CodeBrowser parameter rename (`sectionName` -> `status_line`) plus save and read-back verification; avoid repeated MCP signature retries at this address.
- Fallback outcome: manual rename was applied and read-back verified; current signature is `void CConsole__StatusDone(void * this, char * status_line, char success)`.
- `0x00421350` (`CCareer__Save`) signature updates via MCP can time out and hard-freeze CodeBrowser (observed 2026-02-13).
  - After restart, read-back (`functions_get`) showed the signature present; treat as an MCP-signature hotspot and avoid repeating MCP signature writes here.
  - Reliable fallback (if signature needs to change): set the signature manually in CodeBrowser (`Edit Function...`), save, then verify via read-back (`functions_get(0x00421350)`).

### 6) Decompile Requires a Function Object

`functions_decompile` only works for addresses that are actually defined as functions in Ghidra. For “orphan” blocks with no function object, decompile will fail.

**Workaround:**
- Use `memory_read` / `functions_disassemble` on a nearby known function and reason from control flow.
- Add comments + external documentation until the function can be created in Ghidra UI.

### 7) Local Networking Quirk (WSL)

In this environment, WSL cannot reliably reach Windows services via `127.0.0.1:<port>`. The Ghidra HTTP server is reachable from WSL via the Windows host gateway IP (from `ip route`, usually the default route).

Concrete example (this repo / machine):
- Ghidra instance `:8193` is reachable at `http://172.26.112.1:8193/` (not `http://127.0.0.1:8193/`).

**Workaround:**
- Use `http://<windows_gateway_ip>:8193/...` for direct HTTP probing from WSL.

### 8) `data_list` Filter/Address Quirks (Filters Often Ignored)

`data_list` behaves differently than the function endpoints:
- `addr` filtering expects a plain hex address like `0083d130` (passing `0x0083d130` can return no results).
- Name/type filters (e.g., `name`, `name_contains`, `type`) appear to be ignored by the current `/data` endpoint response ordering, so you generally need to locate data by address, not by name search.

**Workaround:**
- Use `data_list` with `addr="0083d130"` (no `0x` prefix), or use `xrefs_list`/`data_list_strings` to pivot to addresses first.

### 9) Project Management Endpoints Are Useful (But Still “Best Effort”)

`project_info` and `project_list_files` work on the current instance and are useful for confirming which program is open.

**Workaround:**
- Use Ghidra UI for project browsing/opening, and use MCP primarily for program-level analysis/editing.

### 10) `/project/open` Can Trigger Swing Deadlock

On this project we observed `POST /project/open` leading to:
- `Timed-out waiting to run a Swing task--potential deadlock!`
- CodeBrowser becoming unresponsive until restart

**Workaround:**
- Avoid automated project-open calls during active analysis sessions.
- Open files/programs from the Ghidra UI when possible.

### 11) Codex MCP Transport Can Fail While Ghidra API Is Healthy

In this environment, Codex-side MCP tool calls can fail with `Transport closed` even while the GhydraMCP HTTP server remains responsive on `:8193`.

**Workaround:**
- Validate health directly with lightweight HTTP checks (`/instances`, `/program`, `/analysis/status`).
- Continue read/write operations via direct HTTP if MCP transport is unhealthy.
- Keep mutation backlog updated for any operation that cannot be confirmed by read-back.

### 12) “Save BEA.exe” Still Matters

A successful mutation request and a durable saved project state are related but not identical concerns:
- Transaction success controls whether a change exists in the current open program state.
- Ghidra's save flow (`Save BEA.exe`) is still important for clean persistence across reopen/restart.
- Recovery snapshots can help after crashes, but should not be treated as the primary persistence mechanism.

**Workaround:**
- Always do address-level read-back after mutations.
- After significant batches, perform explicit UI save when possible.

### 13) MCP Can Keep Running a Stale Bridge Command

Observed failure mode:
- `/mcp` reported old bridge command/path and `Tools: (none)` even after docs were updated.
- Root cause was stale `ghydra` path entries in base Codex config files plus an already-running old bridge process.

**Workaround:**
- Verify all active config files (`config.toml`, `config.wsl.toml`, `config.windows.toml`) point to the pinned bridge path.
- Kill stale bridge processes launched with old paths.
- Reload MCP server in client (`/mcp` disable+enable `ghydra` or restart Codex session).

## Where We Track Pending Fixups

When MCP can’t apply an edit, we track it here for later replay:
- `reverse-engineering/binary-analysis/MCP-MUTATION-BACKLOG.md`

## Feature Wishlist (Would Help RE)

These are capabilities we repeatedly want during BEA.exe reverse engineering that are either missing entirely, or would benefit from a more direct endpoint.

### 1) Rename Any Symbol (Not Just Functions/Data)

What we want:
- Rename labels / code symbols (`LAB_...`) and other non-function, non-data symbols

Why:
- Many init routines and jump targets are labels (not functions) but are semantically important.

### 2) Reliable Function Creation for Orphan Blocks

What we want:
- Create a function at an address by providing a body range, or by running a “recover function” step at an address

Why:
- Some real functions are present as raw code blocks and decompile is blocked until a function object exists.

### 3) Bulk/Batched Mutations (One Transaction)

What we want:
- Apply many renames/signatures/comments in one request/transaction
- Import a rename map (JSON/CSV) and apply it deterministically

Why:
- Mapping thousands of functions is mutation-heavy and single-edit calls increase timeout/transaction failure rate.

### 4) “Wait for Idle” / Analysis Progress Introspection

What we want:
- Query whether auto-analysis is currently running
- A `wait_until_idle` endpoint (or analysis job status) before mutations

Why:
- Many transaction failures/timeouts correlate with the UI being busy or analysis running.

### 5) Stronger Calling-Convention + Prototype Controls

What we want:
- Explicitly set calling convention (`__thiscall`, `__cdecl`, `__stdcall`, `__fastcall`)
- Explicitly control parameter storage (ECX/stack) for recovered prototypes

Why:
- Correct prototypes make decompilation and subsequent inference much faster, especially for `this` methods and small helper thunks.

### 6) First-Class “Apply Type To Memory Range”

What we want:
- Define an array/struct type and apply it to a range in one operation (including pointer tables)

Why:
- A large portion of progress is turning unknown memory into typed tables (vtables, pointer arrays, struct arrays).
