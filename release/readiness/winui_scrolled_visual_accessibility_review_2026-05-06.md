# WinUI Scrolled Visual And Accessibility Review - 2026-05-06

Status: public-safe review note

## Scope

This note corrects the evidence standard for WinUI visual claims after reviewing the current ignored screenshot set and the desktop UI automation smokes. First-viewport screenshots prove only what is visible at launch size. Long WinUI pages also need either scrolled visual proof or accessibility-driven interaction proof before workflow claims should be treated as strong.

Screenshots and contact sheets stay local and ignored under `subagents/`. This note lists filenames only and does not embed screenshots, private paths, save contents, copied executables, generated game assets, data URLs, or base64.

## Review Method

- Reviewed the current first-viewport screenshot set from `winui-visual-qa`.
- Reviewed focused interaction screenshots from Save Analyzer, Save Editor, Patch Bench, Media playback, and real texture preview smokes.
- Reviewed the FlaUI interaction tests for automation IDs, direct text-box value setting, `ScrollItem.ScrollIntoView()`, and `InvokePattern` usage.
- Built a local ignored contact sheet named `contact-sheet.png` for inspection only.

## Evidence Standard

- Functional automation can drive offscreen controls through the accessibility tree when controls have stable automation IDs and support invocation patterns.
- Visual quality still needs screenshot evidence where the relevant region is visible.
- A first-viewport screenshot is not evidence that the lower action/output area of a long page is polished.
- Scrolled workflow screenshots are now treated as separate evidence from first-viewport page screenshots.

## Screen Classification

| Screen or workflow | Evidence filename | Evidence type | Status | Top visible issue | Current interpretation |
| --- | --- | --- | --- | --- | --- |
| Home | `01-home.png` | First viewport | PASS | Dense cards still leave room for visual refinement, but the screen routes by task and does not require scrolling for its primary choice. | First screen is product-facing and stable enough for current WinUI lane work. |
| Save Lab start | `02-save-lab.png` | First viewport | PASS | None blocking; this is an onboarding state, not proof of the full editor workflow. | First-run Save Lab state is acceptable. |
| Save Analyzer result | `01-save-analysis.png` | Real-save interaction screenshot | PASS | Metrics are visible without scrolling for the tested save. | One representative real-save analyzer path is visually and functionally proven. |
| Save Editor copied patch | `01-save-editor-patched.png` | Scrolled workflow screenshot plus UIA interaction | PASS after fix | Earlier private screenshot review found a full local output path in the primary patch log; this pass redacted the visible log to selected-output wording and regenerated the screenshot. | Copied-save patch workflow can be driven through automation, and the scrolled action/output area is now public-safe in visible wording. |
| Media audio | `03-media-audio.png`; `01-audio-playing.png` | First viewport plus interaction screenshot | PASS | Library remains compact and technical source details stay collapsed. | Audio browsing and one inline playback path are visually/functionally proven. |
| Media video | `04-media-video.png`; `02-video-playing.png` | First viewport plus interaction screenshot | PASS | Broader video row coverage remains unproven. | One selected video playback path is visually/functionally proven with a larger in-app player. |
| Asset Library texture | `05-asset-library-texture.png`; `asset-library-real-texture.png` | First viewport plus real-catalog screenshot | PASS | Some private extracted textures may still be dark, transparent, or visually subtle depending on source art. | Texture preview is proven for synthetic and one representative real extracted row; broader row richness remains polish/coverage work. |
| Asset Library model | `06-asset-library-model.png` | First viewport | PASS/YELLOW | Bounded wireframe preview is visible; full 3D/material/animation rendering remains unproven. | Lightweight model inspection is real; do not claim full native 3D rendering. |
| Lore | `07-lore.png` | First viewport | PASS/YELLOW | The reader is comfortable in the captured state, but long-document scrolled sections, tables, and code blocks are not separately captured here. | Reader start state is acceptable; deeper article-scroll visual QA remains useful. |
| Patch Bench | `08-patch-bench.png`; `01-patch-bench-applied.png` | First viewport plus scrolled workflow screenshot and UIA interaction | PASS | The local source executable used for proof was already in the selected stable patched state, so first-time clean-retail-to-patched transition is not proven. | Copied-executable create/verify/apply/restore workflow is visually and functionally proven against an app-owned copy. |
| Settings | `09-settings.png` | First viewport | PASS | None blocking. | Configured install is presented as read-only source material with details collapsed. |
| About | `10-about.png` | First viewport | PASS | None blocking. | Product-lane copy is current and clear. |

## Accessibility And Automation Findings

- Save Analyzer, Save Editor, Patch Bench, Media, and Asset Library now expose stable automation IDs for the controls used by the desktop smokes.
- Long workflow smokes use UI Automation discovery and `ScrollItem.ScrollIntoView()` before invoking or capturing offscreen controls where practical.
- The Save Editor smoke sets `TextBox.Text` directly instead of relying on keyboard text entry, avoiding focus-dependent path splitting after the user accidentally clicked away during an earlier run.
- The Patch Bench smoke drives create, verify, apply, restore, confirmation dialogs, and the output log through UI Automation against an app-owned executable copy.

## Corrective Fix In This Pass

- Save Editor visible patch-result wording now redacts full input/output paths from the primary result banner and output log.
- The underlying copied output file is still written and verified by the smoke.
- The regenerated private screenshot shows the selected-output wording instead of an absolute local path.

## What Is Still Not Proven

- A complete keyboard-only and screen-reader audit.
- Full tab-order review across every page.
- Scrolled visual review for every possible Lore document section.
- Every media, texture, model, and save row variant.
- Full native 3D/material/animation model rendering.
- Signed installer/MSIX install-launch-uninstall behavior.

## Result

WinUI visual evidence is stronger after this review, but the standard is now more precise: first-viewport screenshots, scrolled workflow screenshots, and accessibility-driven automation proof are separate categories. Save Editor and Patch Bench are the strongest long-page workflow proofs because they include scrolled action/output screenshots plus automation that invokes offscreen controls safely. Lore remains acceptable for the captured reader start state but still deserves deeper long-document scrolled review in a future polish pass.
