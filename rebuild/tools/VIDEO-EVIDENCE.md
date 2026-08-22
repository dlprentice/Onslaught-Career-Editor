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
   `ffmpeg -f gdigrab`. No audio. The mouse cursor is drawn, so scripted input
   is on camera.
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
  Engine Aquila").
- Script: verified no other BEA.exe held the serialized-game slot; launched
  the rebuild (one tracked launch); recorded the rebuild window with
  Capture-Session.ps1 for the traversal; performed click-to-start on camera;
  stopped recording after the main menu settled; closed the rebuild.
- Clip: local-lab/video-evidence/rebuild-click-to-start-mainmenu.mp4
- SHA-256: recorded in the clip manifest at capture time; see
  `<clip>.manifest.json` in local-lab (hash re-verified at entry filing).
- Frames prove: pending first recording — the serialized-game slot was held by
  another lane at protocol-writing time (BEA.exe PID 28856,
  GameProfiles\ps2-baseline). This entry is completed with frame timestamps
  by the first recorded traversal; until then it is a registered claim, not
  evidence.
- Reviewer: pending.

## Reviewing a clip

Watch the clip against the entry's Script. Confirm, at named timestamps: the
window title/rect in the manifest matches the subject; the scripted input
lands (cursor visible); the claimed transition completes; no unexplained
occlusion or window move spoils the rectangle. Record the review verdict and
timestamps in the entry's Reviewer field. A clip that fails any of these is
spoiled: mark the entry superseded and re-record; never edit the claim to fit
the footage.
