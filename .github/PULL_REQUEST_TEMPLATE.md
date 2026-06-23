# Pull Request

## Lane

Choose one primary lane:

- [ ] WinUI
- [ ] AppCore / CLI
- [ ] Patch / mod safety
- [ ] Docs / release safety
- [ ] Public-safe reverse-engineering docs

## Summary

Describe the change in plain language.

## Changed Paths

List the main files or folders touched.

## Local Validation

List exact commands run and results. If a relevant gate was skipped, explain why.

## Safety Confirmations

- [ ] No GitHub Actions, CI/CD, hosted validation, workflow, or release automation was added.
- [ ] No private assets, extracted game content, saves, screenshots, frame captures, copied executables, proof bundles, secrets, state files, or `subagents/` outputs were added.
- [ ] The installed game folder and original `BEA.exe` were not mutated.
- [ ] Runtime, online, patch-behavior, rebuild-parity, and static-RE claims are separated and bounded.

## Remaining Risks

Name any follow-up, skipped gate, or review concern.
