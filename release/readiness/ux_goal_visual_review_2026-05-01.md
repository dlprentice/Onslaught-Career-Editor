# UX Goal Visual Review - 2026-05-01

Status: public-safe review note

Branch: `wip/sandbox`
Reviewed UX goal commit: `9f4842b5e4ffbe2bdedc3b4e534199fd1c184be8`
Review/fix pass commit: `1b57bf4842ea79821bff7de4e6d923d9224501af`
Screenshot source: ignored local files under `subagents/ux-goal/screenshots/`

This note summarizes local screenshot inspection without embedding screenshots, raw game media, raw frame captures, private absolute paths, data URLs, base64 payloads, or private proof JSON. The screenshot files remain ignored/private and are not release artifacts.

## Original Screen Review

The table below preserves the screenshot review findings for `9f4842b5e4ffbe2bdedc3b4e534199fd1c184be8`. Rows marked `YELLOW` are historical pre-fix findings; the current post-fix status is recorded in [Post-Fix Resolution](#post-fix-resolution).

| Screen | Screenshot | Result | Top visible issue | Reference intent fit |
| --- | --- | --- | --- | --- |
| Home | `visible2-home.png` | PASS | Lower readiness cards are partly below the first viewport. | Meets the generated reference intent: clear task routing, calm shell, and product-first language. |
| Save Lab | `visible2-save-lab.png` | PASS | Primary safe-copy action is disabled until a file is selected, so the first action relies on the file picker. | Meets the intent: safe save editing is obvious and the original-file safety model is visible. |
| Media audio | `visible2-media-audio-playing.png` | PASS | The left media filter rail plus app rail consumes horizontal width on small desktop sizes. | Meets the intent: playback is local to the selected item and the active row is obvious. |
| Media video | `visible2-media-video.png` | PASS | The prepared-player area is still visually large before preparation, but it now explains the required action. | Meets the intent: one selected-player panel, clear preparation status, and technical details collapsed. |
| Media texture | `visible2-media-texture.png` | YELLOW | The previewed sample appears mostly black/dark, so the image success state can be hard to distinguish from a blank preview. | Mostly meets the intent: texture cards and preview affordance are clear, but broader texture coverage/placeholder clarity still need polish. |
| Lore | `visible2-lore.png` | PASS | The selected article begins with generated preview copy in browser mode, which is acceptable but less rich than a full desktop document. | Meets the intent: library, article reader, and secondary details are readable without the old status rail squeezing the content. |
| Patch Bench | `visible2-patch-bench.png` | PASS | The apply/review controls sit lower in the scroll, so the first viewport emphasizes setup and patch choice. | Meets the intent: copied-executable workflow, original-file safety, and guided steps are visible. |
| RE Lab | `visible2-re-lab.png` | YELLOW | The screenshot presents Hawk rows like live search results even though they are sample investigation rows. | Reference intent is close visually, but this hard-review pass must make sample/live status explicit before acceptance. |
| Game Harness | `visible2-game-harness.png` | YELLOW | The guided flow looks good, but the reviewed commit had a launch button wired to no job and static objective copy. | Reference intent is close visually, but this hard-review pass must wire launch honestly and clarify objective planning limits. |
| Release | `visible2-release.png` | PASS | Lower evidence-report and gate detail lists continue below the first viewport. | Meets the intent: public-safe readiness, private evidence exclusions, and next proof are understandable. |

## Review Outcome

The screenshots support the overall UX reset as a real product-direction improvement. At the time of the hard review, the acceptance blockers were not broad visual style failures; they were product-trust issues in RE Lab and Game Harness:

- RE Lab needed to clearly label example rows as examples instead of implying live extracted results.
- Game Harness needed to wire the managed launch action to the typed job catalog or name the prerequisites that block it.
- Game Harness needed to state that custom investigation planning is still a future maintainer feature rather than implying open-ended autonomy.

## Post-Fix Resolution

- RE Lab blocker resolved in `1b57bf4842ea79821bff7de4e6d923d9224501af`.
- RE Lab now labels Hawk rows as sample/example investigation rows, not live extracted data.
- Game Harness blocker resolved in `1b57bf4842ea79821bff7de4e6d923d9224501af`.
- Game Harness launch is wired to `game.launchProfile`, stop is wired to `runtime.stopManagedProcess`, and readiness text names prerequisites.
- Remaining visual note: Media texture preview can still look dark/blank for some sample textures, but this is polish, not an acceptance blocker.
- Final visual review status: GREEN with media-texture polish follow-up.

This review note is public-safe and may be included in the curated release readiness manifest.
