# Ghidra Wave975 frontend briefing state review (2026-05-28)

Status: saved Ghidra boundary recovery
Date: 2026-05-28
Branch: `main`
Tag: `cfepbriefing-boundary-recovery-wave975`

## Scope

Wave975 recovered the CFEPBriefing vtable state/render/video helper cluster after fresh vtable, xref, instruction, string, and decompile review.

| Address | Saved name | Result |
| --- | --- | --- |
| `0x00451b70` | `CFEPBriefing__Init` | Created function boundary |
| `0x00451b80` | `CFEPBriefing__Process` | Created function boundary |
| `0x00451c20` | `CFEPBriefing__ButtonPressed` | Created function boundary |
| `0x00451c90` | `CFEPBriefing__RenderPreCommon` | Created function boundary |
| `0x00451d50` | `CFEPBriefing__Render` | Created function boundary |
| `0x00452430` | `CFEPBriefing__TransitionNotification` | Renamed and hardened prior timer-reset label |
| `0x00452460` | `CFEPBriefing__ActiveNotification` | Created function boundary |

## Mutation Evidence

Private artifacts:

```text
subagents/ghidra-static-reaudit/wave975-frontend-briefing-state-review/apply-dry.log
subagents/ghidra-static-reaudit/wave975-frontend-briefing-state-review/apply.log
subagents/ghidra-static-reaudit/wave975-frontend-briefing-state-review/apply-final-dry.log
subagents/ghidra-static-reaudit/wave975-frontend-briefing-state-review/post-metadata.tsv
subagents/ghidra-static-reaudit/wave975-frontend-briefing-state-review/post-tags.tsv
subagents/ghidra-static-reaudit/wave975-frontend-briefing-state-review/post-xrefs.tsv
subagents/ghidra-static-reaudit/wave975-frontend-briefing-state-review/post-instructions.tsv
subagents/ghidra-static-reaudit/wave975-frontend-briefing-state-review/post-vtables.tsv
subagents/ghidra-static-reaudit/wave975-frontend-briefing-state-review/post-decompile/
```

Dry/apply/final-dry:

```text
dry:        updated=1 skipped=0 created=0 would_create=6 renamed=0 would_rename=1 signature_updated=1 comment_only_updated=2 missing=0 bad=0
apply:      updated=7 skipped=0 created=6 would_create=0 renamed=1 would_rename=0 signature_updated=7 comment_only_updated=14 missing=0 bad=0
final dry:  updated=0 skipped=7 created=0 would_create=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0
```

Read-back result:

```text
metadata: 7/7 OK
tags: 7/7 OK
xrefs: 7 rows
instructions: 769 rows
decompile: 7/7 OK
vtables: 32 rows
queue: 6217/6217, 0 commentless, 0 undefined signatures, 0 param_N
```

## Review Result

The saved CFEPBriefing vtable slots now resolve through slot 7. Slot 0 initializes briefing state, slot 2 processes timer/button state, slot 3 handles button actions, slot 4 renders the pre-common marker path, slot 5 renders briefing text/UI, slot 6 is the transition notification/timer reset, and slot 7 opens the briefing video variants.

The pass made no executable-byte change and did not launch BEA.

## Backup

Verified post-wave backup:

```text
G:\GhidraBackups\BEA_20260528-225054_post_wave975_frontend_briefing_state_review_verified
files=19
bytes=173804423
MissingCount=0
ExtraCount=0
HashDiffCount=0
```

## Truth Boundary

This review improves saved static Ghidra boundaries, names, signatures, comments, and tags for selected CFEPBriefing helpers. It does not prove exact CFEPBriefing source-body identity, concrete briefing-page/video-state layouts, runtime frontend input/render/video behavior, BEA patch behavior, or rebuild parity.

## Next

Continue from the next Wave911 focused candidate after Wave975 state closeout.
