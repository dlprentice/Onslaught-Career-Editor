Onslaught Career Editor - WinUI ZIP Package
===========================================

This ZIP package is the non-cert distribution shape for the WinUI 3 app.
It is not an installer, MSIX package, Microsoft Store package, or signed
installer release.

Quick start
-----------

1. Extract the whole ZIP to a writable folder.
2. Run Launch Onslaught Toolkit.cmd from the extracted top-level folder.
3. If the launcher is blocked by local policy, run
   app\OnslaughtCareerEditor.WinUI.exe directly.
4. Keep the files together; do not move the executable away from the
   app folder and its support files.

Safety notes
------------

- The app is designed to work on copied saves, copied options files, and
  copied game executables for mutating workflows.
- Do not patch an installed Steam/Program Files BEA.exe in place.
- Full game assets, private screenshots, proof JSON, generated media caches,
  and local test outputs are not included in this public-safe ZIP lane.

What this package shape proves
------------------------------

The private maintainer ZIP probe builds disposable WinUI publish output, stages
a friendly portable root with this README, LICENSE, Launch Onslaught
Toolkit.cmd, and app\, creates this ZIP, writes a SHA-256 sidecar, extracts the
ZIP, launches the extracted app from app\, runs native launch smoke, runs
extracted app Home navigation smoke, runs representative Media smoke, and
confirms no WinUI process remains. The probe also rejects raw publish layouts
that expose DLLs or executables at the ZIP root.

What this package shape does not prove
--------------------------------------

- MSIX/AppInstaller packaging.
- Certificate signing or trust.
- Start menu shortcuts, uninstall entries, or installer UX.
- SmartScreen, Microsoft Store, reputation, or malware-scanner posture.
- Legal/compliance approval for public binary redistribution.
- Row-by-row media playback coverage.
