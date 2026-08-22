# Video evidence protocol — rebuild-vs-retail parity clips

Status: active
Last updated: 2026-08-22
Summary: How a parity claim attaches a screen recording: claim, on-camera script, clip, sidecar manifest, hash. Clips live in local-lab; the repo stores this protocol and the hashes.
Evidence: SOURCE — this protocol is defined by rebuild/tools/Capture-Session.ps1 (gdigrab window-region recorder) and the integration owner's verified gdigrab-to-mp4-to-multimodal-review pipeline; the worked example entry E-0001 cites its own clip manifest and hash.

## Why video

A screenshot pair proves one settled frame. Several frontend parity questions are
about TRANSITIONS: click-to-start reaching the main menu, a hover highlight
appearing, the animated underlay moving, a page change completing without a
stray intermediate state. A clip answers those in one artifact where frame
bursts cannot prove ordering. This lane exists so a parity claim can cite a
recording whose method is reproducible — the same reason Capture-Retail.ps1
exists — and so the recording, not a memory of it, is what gets reviewed.

## The pipeline

1. `rebuild/tools/Capture-Session.ps1` records ONE window (matched by visible
   title substring) as a fixed screen rectangle at 15 fps to `.mp4`, via
   `ffmpeg -f gdigrab`. No audio. The mouse cursor is drawn, so physical or
   window-coordinate cursor motion is visible. A posted background message has
   no physical click indicator; when one is used, the entry cites its
   instrument receipt and states that bounded ambiguity.
2. The script writes a sidecar `<clip>.manifest.json` next to the clip: clip
   SHA-256, byte count, resolved window title and hwnd, captured rectangle,
   frame rate, duration, UTC start/finish, and the exact ffmpeg arguments.
   The manifest is the chain from "a clip file" to "these pixels, that window,
   that moment".
3. Review is multimodal: the clip is watched (frame-by-frame where needed) and
   the reviewer records what specific frames show, with timestamps, into the
   evidence entry. A clip nobody described proves nothing by existing.

A smoke recording from the integration owner's pipeline verification lives at
`%LOCALAPPDATA%/hermes/cache/smoke-rec.mp4` (outside the repo; not evidence,
just proof the pipe runs).

## Rules of the lane

- ONE serialized game at a time, machine-wide. Before launching the rebuild
  (or any BEA target) for a recording, check for a running BEA.exe; if another
  lane holds the slot, wait and note the hold on the card. Never touch the
  installed Steam BEA or `G:`; rebuild recordings launch the tracked rebuild
  only.
- Recordings live in gitignored `local-lab/` (default
  `local-lab/video-evidence/`). The repo stores ONLY this protocol plus, per
  entry, the clip hash and manifest facts. A hash whose clip is gone is an
  honest tombstone, not evidence.
- The capture is a FIXED SCREEN RECTANGLE sampled when recording starts. If
  the window moves, resizes, is occluded, or closes mid-recording, the clip
  keeps showing whatever now occupies that rectangle. There is no post-hoc
  "the window moved" excuse: if the subject moved, the clip is spoiled —
  re-record it. Keep the window still for the whole duration.
- No synthetic input from the capture script. Any clicks/keys shown on camera
  are performed per AGENTS.md's input rules (background window messages where
  supported; armed global input only when the machine is known unattended).
  The recording documents whatever input method was used in its entry.
- 15 fps and CRF 23 are deliberate: enough to order transitions and read
  highlights, small enough that a 60 s clip is a few MB. Do not raise them
  without a stated need; evidence clips are not showreels.

## Anatomy of an evidence entry

Entries live under "Evidence log" below. Each entry is one claim. Required
fields — an entry missing any of these is not evidence:

```
### E-NNNN — <short claim label>
- Date: YYYY-MM-DD
- Claim: the parity behavior asserted, one sentence
- Subject: rebuild | retail | rebuild-vs-retail (and which build/commit)
- Script: exact steps performed on camera (launch command, inputs, waits)
- Clip: local-lab path of the .mp4
- SHA-256: from the clip's manifest
- Frames prove: which timestamps show what, and why that is the claim
- Reviewer: who watched it and what they observed (tool or person)
```

The claim-to-clip chain is: Claim states a falsifiable behavior; Script states
the on-camera procedure that exercises it; Frames prove names the timestamps
that show the outcome. A reviewer must be able to re-derive the conclusion
from the clip alone using the Script and Frames prove fields.

## Evidence log

### E-0001 — rebuild click-to-start reaches the main menu

- Date: 2026-08-22
- Claim: the Godot rebuild's click-to-start interaction advances the frontend
  from the click-to-start page to the main menu in one interaction, as retail
  does.
- Subject: rebuild — tracked launch via `npm run run:rebuild-godot`
  (Run-FirstFlight.ps1, mono engine, window title "Onslaught Rebuild - Battle
  Engine Aquila (DEBUG)").
- Script: verified no other BEA.exe held the serialized-game slot; launched
  the tracked rebuild (one launch); an untracked watcher classified the
  frontend bands (dark cinematic <50 mean luma; white-flood logo card >15000
  bright pixels; beach click-to-start page 800..2000), waited for a fresh page
  birth, spawned Capture-Session.ps1 at page age 4.3 s, then posted one
  background WM_MOUSEMOVE / WM_LBUTTONDOWN / WM_LBUTTONUP sequence to the
  rebuild window centre 1.2 s after recorder-process spawn. ffmpeg startup
  means those wall-clock offsets are not clip PTS. The recording ran its full
  15 s with the menu stable; the rebuild process was closed after review.
- Clip: local-lab/video-evidence/e0001-final.mp4
- SHA-256: 1cf9aa6f8ac762e094c9cfd69017cf98d3619de7589ec01954f7ccbad3308ccf
  (1,285,081 bytes; sidecar `e0001-final.mp4.manifest.json`: hwnd 2296416,
  source rect x=320 y=161 1296x759, encoded 1296x758 by even scaling, 15 fps,
  15.00 s, draw_mouse, no audio, start 2026-08-22T20:00:19Z; hash recomputed
  independently at entry filing and matches the manifest).
- Frames prove: t=0.10 s shows the literal `Click to start` prompt inside the
  capture rect with no covering window; t=0.80 s shows the selectable main
  menu (`New Game` highlighted; `Continue Game` / `Load Game` /
  `Multiplayer` / `Goodies` / `Options` / `Quit`), no item occluded; the
  menu stays stable through the end of the clip. The clip proves the visible
  prompt-to-menu traversal. The watcher receipt identifies the sole input as
  the posted click between those observed states; the clip has no physical
  click indicator, so it does not independently identify the input method.
- Reviewer: PASS — independent steward multimodal review of the actual clip:
  frame extraction with pixel inspection at t=0.10 s and t=0.80 s, plus a
  20-tile 10 fps contact sheet of the first 2 s (prompt in tiles 1–4, menu
  from tile 8 onward). History: TAKE 1 (predecessor card) proved
  cold-boot→click-to-start; TAKE 3 was withdrawn after frame-level review
  showed its click landed before the prompt; TAKE 5 false-arm spoiled;
  TAKE 6 (this entry) is the filed traversal evidence.

## Reviewing a clip

Watch the clip against the entry's Script. Confirm, at named timestamps: the
window title/rect in the manifest matches the subject; physical input lands
(cursor visible), or a posted-message receipt is cited with its bounded
ambiguity; the claimed transition completes; no unexplained occlusion or
window move spoils the rectangle. Record the review verdict and timestamps in
the entry's Reviewer field. A clip that fails any of these is spoiled: mark
the entry superseded and re-record; never edit the claim to fit the footage.
