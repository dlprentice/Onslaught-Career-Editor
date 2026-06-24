## Summary
- Delivery status authority is split across roadmap docs: index/hub in `roadmap/ROADMAP-INDEX.md:27-46`, live execution status in `roadmap/status-current.md:1-113`, and phase gates in `roadmap/app-delivery-phases.md:1-50`.
- Debt authority lives primarily in `roadmap/technical-debt.md:1-83`, with parity-specific debt notes in `roadmap/csharp-python-parity.md:117-212` and archival RE debt in `roadmap/re-investigation.md:1-260`.
- Workflow policy authority is mostly `AGENTS.md` (program focus, canonical index rules, state-file policy) at `AGENTS.md:15-23`, `AGENTS.md:360-362`, `AGENTS.md:492-547`, plus execution checklists in `roadmap/app-validation-checklist.md:7-111`.
- Active status files are `developer_agent_state.json`, `documentation_agent_state.json`, `re_orchestrator_state.json`, and `reverse-engineering/binary-analysis/function_mutation_tracking_state.json` (`...tracking_state.json:1-24`).

## Roadmap Map
| Area | Primary Files | What Lives There | Notes |
|---|---|---|---|
| Roadmap hub / navigation | `roadmap/ROADMAP-INDEX.md:27-52` | Canonical roadmap doc map + cross-links to RE/lore/AGENTS | Declares app-first mode (`:4`) and links execution docs.
| Current delivery status | `roadmap/status-current.md:1-113` | Active implementation posture, working features, pending investigations, parity table | This is the clearest app-facing “now” view.
| Delivery phase gates | `roadmap/app-delivery-phases.md:1-50` | Phase A/B/C progression + mandatory gate commands | Defines closure criteria for delivery phases.
| Technical debt | `roadmap/technical-debt.md:18-80` | Open debt by quality/testing/edge-case/refactor/documentation buckets | Core debt tracker for app work.
| C#/Python parity ledger | `roadmap/csharp-python-parity.md:1-212` | Feature-by-feature parity and shelved tab posture | Includes explicit shelf state for Goodie/Asset tabs (`:133-149`).
| Validation execution checklist | `roadmap/app-validation-checklist.md:7-111` | Build/test/CLI parity smoke + regression capture + state-file update reminder | Operational QA checklist.
| RE historical backlog (non-authoritative queue) | `roadmap/re-investigation.md:1-5` + `:79-260` | Archival RE investigations and deferred ideas | Explicitly marked non-canonical active queue.
| RE static gate status | `reverse-engineering/binary-analysis/deep-validation-status.md:1-54` | Static RE completion snapshot and gate decision | Declares `CLOSED` gate (`:49-54`).
| RE mutation pending/completed queue | `reverse-engineering/binary-analysis/MCP-MUTATION-BACKLOG.md:6-21` | Pending mutation backlog + completed mutation history | Tracks unresolved mutation targets.

## Process Docs
| Process Domain | Source | Policy Anchor |
|---|---|---|
| Program execution mode | `AGENTS.md:15-23` | App-first delivery; RE as supporting lane; Goodie/Asset viewer shelved unless requested.
| Canonical doc indexing | `AGENTS.md:360-362` | Canonical indexes are `RE-INDEX`, `LORE-INDEX`, `ROADMAP-INDEX`; subfolders use `_index.md`.
| Agent/state persistence | `AGENTS.md:492-547` | Three repo state files are mandatory and must be updated in the same work window.
| Mirror policy | `AGENTS.md:660-664` | Keep canonical and lore-book mirrors in lockstep (except intentional link-depth differences).
| App validation workflow | `roadmap/app-validation-checklist.md:7-111` | Concrete preflight/build/test/parity steps + failure capture template.
| Delivery phase workflow | `roadmap/app-delivery-phases.md:23-50` | Phase progression and minimum phase-close gate commands.
| Agent session workflow patterns | `roadmap/agent-workflow.md:5-67` | RE-oriented session structure, cross-referencing habits, common pitfalls.
| RE mutation workflow | `reverse-engineering/binary-analysis/ghydra-mcp-runbook.md:15-132` | Transport arbitration, serialized write/readback policy, mandatory mutation logs/state sync.

Active status files inventory:
- `developer_agent_state.json:2-5`: implementation state (`phase`, `focus`, `current_focus`) with long `work_completed` trail.
- `documentation_agent_state.json:2-6`: doc-sync state plus documentation-focused work history.
- `re_orchestrator_state.json:2-10`: RE orchestration status for current tranche (including whether Ghidra was exercised).
- `reverse-engineering/binary-analysis/function_mutation_tracking_state.json:9-24`: RE mutation policy/counters/pending addresses (machine-readable queue state).

## Contradiction Risk Zones
1. RE “closed gate” vs pending mutation queue
- Evidence: `deep-validation-status.md:49-54` says static gate `CLOSED`; `function_mutation_tracking_state.json:18-23` shows `pending: 1` (`0x004ac6b0`), and `MCP-MUTATION-BACKLOG.md:6-11` still lists a pending change.
- Risk: readers may interpret “closed” as “no pending mutation work anywhere.”

2. Archival RE doc contains active-looking TODOs
- Evidence: `roadmap/re-investigation.md:3-5` says non-canonical archival file, but also contains large deferred/TODO queues (`:61-159`, `:163-251`).
- Risk: contributors may execute from archival lists instead of current active trackers.

3. Validation gate drift across two “authoritative” execution docs
- Evidence: `app-delivery-phases.md:45-48` defines a 4-command closure gate; `app-validation-checklist.md:17-21` adds extra regression/smoke commands.
- Risk: phase closure can be declared with a narrower gate than checklist expectations.

4. State-file historical arrays can conflict with current truth if parsed naively
- Evidence: `re_orchestrator_state.json:74` still records “Python GUI ... deferred Binary Patches parity” in historical work entries, while `csharp-python-parity.md:17` marks Binary Patches complete in both stacks.
- Risk: automation that scans `work_completed` text (instead of `phase/current_focus` + canonical docs) can emit stale status.

5. Canonical/mirror duplication drift risk
- Evidence: mirror requirement in `AGENTS.md:660-664`; repo contains mirrored roadmap/RE material under `lore-book/`.
- Risk: high-volume doc edits can drift between canonical and mirror copies unless sync is enforced every change window.
