# Ghidra Wave976 CRT spawn/path review (2026-05-29)

Status: read-only static review
Date: 2026-05-29
Branch: `main`
Tag: `crt-spawn-path-review-wave976`

## Scope

Wave976 re-reviewed the top remaining Wave911 focused candidate, `CRT__SpawnSearchPathWithFallbackExtensions`, with the adjacent CRT spawn/path helpers that prove its caller/callee context.

| Address | Saved name | Result |
| --- | --- | --- |
| `0x0055e412` | `CRT__SpawnPathVarargsNoEnv_Thunk` | Reviewed; no mutation |
| `0x00564a0b` | `CRT__SpawnSearchPathWithFallbackExtensions` | Reviewed; no mutation |
| `0x00564b54` | `CRT__SpawnResolvedPathWithBuiltCommandEnv` | Reviewed; no mutation |
| `0x0056a7e7` | `CRT__ValidatePathAttributesForOpen` | Reviewed; no mutation |
| `0x0056a936` | `CRT__SpawnVe` | Reviewed; no mutation |
| `0x0056ab1f` | `CRT__BuildSpawnCommandAndEnv` | Reviewed; no mutation |

## Evidence

Private artifacts:

```text
subagents/ghidra-static-reaudit/wave976-crt-spawn-path-review/metadata.tsv
subagents/ghidra-static-reaudit/wave976-crt-spawn-path-review/tags.tsv
subagents/ghidra-static-reaudit/wave976-crt-spawn-path-review/xrefs.tsv
subagents/ghidra-static-reaudit/wave976-crt-spawn-path-review/instructions.tsv
subagents/ghidra-static-reaudit/wave976-crt-spawn-path-review/decompile/
```

Read-back result:

```text
metadata: 6/6 OK
tags: 6/6 OK
xrefs: 8 rows
instructions: 571 rows
decompile: 6/6 OK
```

## Review Result

The saved names/signatures/comments remain appropriate for the current evidence. The primary Wave911 row `0x00564a0b CRT__SpawnSearchPathWithFallbackExtensions` is still a CRT spawn/path helper, not a CDXTexture path loader. Fresh read-back shows the wrapper at `0x0055e412` forwards into it, the body validates direct and fallback-extension candidates through `CRT__ValidatePathAttributesForOpen`, and successful candidates dispatch into `CRT__SpawnResolvedPathWithBuiltCommandEnv`, which builds command/environment blocks and calls `CRT__SpawnVe`.

No Ghidra mutation was performed.

## Backup

Read-only post-wave backup:

```text
G:\GhidraBackups\BEA_20260529-140123_post_wave976_crt_spawn_path_review_verified
files=19
bytes=173804423
MissingCount=0
ExtraCount=0
HashDiffCount=0
```

## Truth Boundary

This review confirms static Ghidra coherence for selected CRT spawn/path helpers. It does not prove exact MSVC CRT version, complete command-line quoting equivalence, environment-block layout/lifetime, runtime `CreateProcessA` behavior, Windows filesystem edge cases, BEA patch behavior, or rebuild parity.

## Next

Continue Wave977 from the next Wave911 focused candidate.
