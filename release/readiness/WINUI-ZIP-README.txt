Onslaught Career Editor - WinUI ZIP Package
===========================================

This ZIP package is the non-cert distribution shape for the WinUI 3 app.
It is not an installer, MSIX package, Microsoft Store package, or signed
installer release.

Quick start
-----------

1. Extract the whole ZIP to a writable folder.
2. Run OnslaughtCareerEditor.WinUI.exe from the extracted folder.
3. Keep the files together; do not move the executable away from the
   extracted support files.

Safety notes
------------

- The app is designed to work on copied saves, copied options files, and
  copied game executables for mutating workflows.
- Do not patch an installed Steam/Program Files BEA.exe in place.
- Full game assets, private screenshots, proof JSON, generated media caches,
  and local test outputs are not included in this public-safe ZIP lane.

What this package shape proves
------------------------------

The repository ZIP probe builds disposable WinUI publish output, creates this
ZIP, writes a SHA-256 sidecar, extracts the ZIP, launches the extracted app,
runs native launch smoke, runs extracted-exe Home navigation smoke, runs
representative Media smoke, and confirms no WinUI process remains.

What this package shape does not prove
--------------------------------------

- MSIX/AppInstaller packaging.
- Certificate signing or trust.
- Start menu shortcuts, uninstall entries, or installer UX.
- SmartScreen, Microsoft Store, reputation, or malware-scanner posture.
- Legal/compliance approval for public binary redistribution.
- Row-by-row media playback coverage.
