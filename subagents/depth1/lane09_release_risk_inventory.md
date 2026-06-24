# Release Risk Inventory (Lane 09)

## Summary
Current `wip/sandbox` content shows substantial private-only release risk concentrated in game assets, media artifacts, and RE scratch outputs. Observed tracked counts in this repo snapshot:

- `game/**`: 5,507 tracked files
- `reverse-engineering/binary-analysis/scratch/**`: 12,317 tracked files
- `media/**`: 19 tracked files
- `references/**`: 2 tracked entries (gitlinks/submodules)

Repo policy in `AGENTS.md` explicitly states private branch includes `game/`, `media/`, `tools/` for RE workflows and public branch should exclude those assets due to size/licensing.

## High-Risk Paths
| Path | Why high risk for public release | Evidence seen | Suggested public posture |
|---|---|---|---|
| `game/**` | Full retail game install content (executables, manuals, mission data, audio/video/textures) is likely proprietary redistribution. | Tracked files include `game/BEA.exe`, manuals, `data/resources`, `data/video`, `data/sounds`. | Exclude entirely from public branch/release artifacts. |
| `media/**` | Contains likely copyrighted third-party or game-origin media (packaging scans, wallpapers, SWF, publication PDF, presentations). | Examples: `media/publications/GDM_April_2003.pdf`, `media/packaging/PC_Disc.jpg`, `media/flash/battle_engine_aquila.swf`. | Treat as deny-by-default; publish only items with explicit redistribution permission. |
| `reverse-engineering/binary-analysis/scratch/**` | Large operational/archive corpus with transient outputs (rename maps, decompile exports, wave artifacts) that can leak internal workflow and derivative binary analysis output. | 12,317 tracked files; many `archive/*`, `decompile/*`, wave prep/output artifacts. | Exclude from public by default; only curate minimal intentional artifacts if explicitly needed. |
| `references/Onslaught` and `references/AYAResourceExtractor` | Submodule pointers are safer than vendoring, but URL targets and licensing provenance must be public-safe and stable. | `.gitmodules` points to `https://github.com/dlprentice/...`; tracked as 2 gitlinks. | Keep only if target repos are public + license-compatible; otherwise retarget/remove for public release. |
| `tools/**` | Policy-marked as private-branch asset area; may contain mixed provenance helpers and RE operational scripts. | `AGENTS.md` private/public policy explicitly includes `tools/` in private-only asset set. | Public allowlist only (selected authored scripts), not blanket publish. |

## Candidate Public Paths
| Path | Candidate status | Notes/conditions |
|---|---|---|
| C# app source (`Program.cs`, `BesFilePatcher.cs`, `Views/**`, project files) | Good candidate | Core authored code; primary deliverable path. |
| Python app/CLI source (`patcher.py`, `onslaught/**`, `onslaught_explorer.py`) | Good candidate | Core authored parity implementation. |
| Tests (`OnslaughtCareerEditor.UiTests/**`, `tests_pyqt/**`) | Good candidate | Keep for quality signal; ensure no private test fixtures embedded. |
| Docs (`README.MD`, `roadmap/**`, curated `reverse-engineering/**` excluding `scratch/**`) | Candidate with curation | Remove or redact content that embeds proprietary binaries/assets/long decompile dumps. |
| `references/**` gitlinks only | Conditional candidate | Accept only if submodule URLs point to publicly accessible, license-compatible upstream/forks. |
| Select `tools/*.py` or utility scripts authored in-repo | Conditional candidate | Ship via explicit allowlist; avoid bundling private workflow artifacts or proprietary binaries. |

## Open Questions
1. Are `dlprentice/Onslaught` and `dlprentice/AYAResourceExtractor` publicly accessible and licensed for public dependency pinning, or should `.gitmodules` be retargeted to `stuart73/*` upstream repos?
2. Which files under `media/**` have explicit redistribution rights, and where is that permission documented?
3. Should `game/**` be completely absent from any public branch history, or only excluded from future commits/releases?
4. Is any subset of `reverse-engineering/binary-analysis/scratch/**` intended for publication, or should it be treated as strictly private operational residue?
5. Should `tools/**` be split into `tools/public` (allowlisted) vs `tools/private` to enforce release hygiene mechanically?
6. Do `save-attempts/**` artifacts include user-identifiable or redistribution-sensitive data that also needs public-branch exclusion?
