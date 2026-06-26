# Pull Request

Use this template with [CONTRIBUTING.md](../CONTRIBUTING.md) and
[COLLABORATION.md](../COLLABORATION.md). Keep the description concise and
public-safe; do not paste private game payloads, raw proof logs, screenshots,
secrets, or local-only evidence.

## Lane / Scope

Choose one primary lane:

- [ ] WinUI
- [ ] AppCore / CLI
- [ ] Patch / mod safety
- [ ] Docs / release safety
- [ ] Payload/secret-safe reverse-engineering docs

## Summary

Describe the change in plain language.

## Changed Paths

List the main files or folders touched.

## Local Validation

List exact commands run and results.

## Validation Intentionally Skipped

List any relevant gate not run and why.

## Private / Public Boundary Check

Say whether this PR adds or changes hard-payload boundaries, release manifest
entries, copied-game proof summaries, local evidence references, or other
public/private boundary material.

## State Baton Update

Name any updated state files, or explain why no state update was made.

## Installed Game / Original BEA.exe Mutation

Confirm `none` for installed game folder and original `BEA.exe` mutation.
If maintainer-authorized proof used only copied or app-owned targets, note that
separately under the boundary check or remaining risks.

## Safety Confirmations

- [ ] No GitHub Actions, CI/CD, hosted validation, workflow, or release automation was added.
- [ ] No private assets, extracted game content, arbitrary saves/options, screenshots, frame captures, raw CDB logs, copied executables, bulky proof bundles, secrets, or copied runtime outputs were added.
- [ ] Any state batons or `subagents/` text reports added are compact, non-secret, and free of hard payloads or raw local proof output.
- [ ] Meaningful code/docs/runtime/release changes update the relevant state baton, or this PR explains why no state update was made and leaves that handoff to maintainers.
- [ ] The installed game folder and original `BEA.exe` were not mutated.
- [ ] Runtime, online, patch-behavior, rebuild-parity, and static-RE claims are separated and bounded.

## Remaining Risks

Name any follow-up, skipped gate, or review concern.
