# Coordination Contract

Status: active
Last updated: 2026-06-26

Use this directory for durable, public-safe policy for coordinated multi-thread
campaigns. It is not a campaign log. Active thread IDs, session IDs, raw logs,
temporary ownership locks, process IDs, local proof paths, and worker scratch
material stay in an ignored outside-repo campaign root chosen by the
coordinator.

## Role Model

- Coordinator thread: control plane only. It may inspect, assign, lease, steer,
  monitor, route findings, and report. It does not edit product source, product
  tests, canonical state batons, release front-door docs, reverse-engineering
  material, or runtime proof artifacts.
- Worker parent thread: the sole writer in its assigned branch, worktree, path
  family, and resource scope. It owns implementation judgment, verification,
  report writing, and its bounded commit.
- Worker subagents: specialist or adversarial advisers by default. They are
  read-only unless the worker explicitly isolates a non-overlapping subtask
  with a safe write set.
- Review threads: read-only. They produce findings with owner, evidence,
  severity, correction, and acceptance criteria.
- Integration thread: the only owner of canonical merge, conflict resolution,
  `goal.md`, canonical state batons, shared readiness/front-door docs, and
  cross-slice claim reconciliation after affected leases release.
- Acceptance thread: fresh and read-only. It attacks the integrated result and
  accepts, accepts with explicit blockers, or rejects with a finite correction
  list.

Unknown ownership means read-only. A thread that cannot prove its path or
resource ownership must stop and ask the coordinator or integration owner.

## Durable And Local State

Durable repo policy lives in tracked docs such as this directory, `AGENTS.md`,
`CONTRIBUTING.md`, `LOCAL_LAB_OVERLAY.md`, release readiness notes, roadmaps, and
state batons.

Use these tracked files as the normal source map:

- [AGENTS.md](../AGENTS.md) for agent routing, product lanes, and safety rules
- [CONTRIBUTING.md](../CONTRIBUTING.md) for lane validation and state baton
  expectations
- [LOCAL_LAB_OVERLAY.md](../LOCAL_LAB_OVERLAY.md) for hard-payload and local
  overlay boundaries
- [goal.policy.md](../goal.policy.md) for the long-horizon charter and
  authority boundaries
- [goal.md](../goal.md) for the current active slice, owned by integration
  during coordinated campaigns
- `developer_agent_state.json` and `documentation_agent_state.json` for
  canonical implementation and documentation batons after integration

Volatile campaign-control state stays local and ignored:

- active thread/session IDs
- worker prompts and raw logs
- process IDs and temporary resource locks
- local proof paths and raw runtime evidence
- App Server traffic and tool transcripts
- temporary worktrees and scratch reports that include local-only details

Useful accepted findings should be sanitized and folded into ordinary repo docs,
state batons, readiness notes, or tests by the integration owner. Do not keep
durable truth only in local campaign reports.

## Required Contracts

- [WORKSTREAM_CONTRACT.md](WORKSTREAM_CONTRACT.md) defines write ownership,
  path families, integration boundaries, and stop conditions.
- [RESOURCE_LEASES.md](RESOURCE_LEASES.md) defines exclusive machine-resource
  leases and cleanup expectations.
- [REPORT_CONTRACT.md](REPORT_CONTRACT.md) defines worker, reviewer,
  integration, and acceptance report fields.
- [AUTOMATION_STORAGE_GHIDRA_POSTURE.md](AUTOMATION_STORAGE_GHIDRA_POSTURE.md)
  defines restored high-throughput automation, storage sentinel, Ghidra/headless
  gates, proof-retention, consult, and advancement-vs-hygiene posture.

For contributor setup, payload safety, and normal lane validation, continue to
use [CONTRIBUTING.md](../CONTRIBUTING.md), [SECURITY.md](../SECURITY.md), and
[LOCAL_LAB_OVERLAY.md](../LOCAL_LAB_OVERLAY.md).
