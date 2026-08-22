# Contract factory mechanical gate

Status: active — deterministic schema gate for packet-to-contract drafts
Last updated: 2026-08-22
Summary: defines the contract-only tree accepted by
`tools/contract_factory_validate.py`, its stable diagnostics, and the boundary
between mechanical completeness and semantic verification.
Evidence: MEASURED — 60 focused fixtures exercise every fail-closed class; the
read-only wave-1 dry run and byte-identical repeated output are recorded in the
delivery receipt, not treated as semantic contract evidence.
Specimen: pristine BEA.exe, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`;
identity constant only — this mechanical gate does not infer from retail bytes.

## Integration command

From the repository root, after a factory cohort has been written to its
contract-only tree:

```text
py -3 tools/contract_factory_validate.py reverse-engineering/contracts
```

The factory lane should run that command before a cohort is proposed for
review. The repository tool-test sweep also runs the focused self-tests through
`tools/run_tool_tests.py`; the standalone command is:

```text
py -3 tools/contract_factory_validate_tests.py
```

Do not point the validator at a documentation directory. Every `*.md` below the
argument is treated as a contract candidate, so rule documents such as this
page or the factory's `TEMPLATE.md` are expected to fail as candidates.

## Input contract

Each candidate is UTF-8 Markdown (an optional UTF-8 BOM and either LF or CRLF
are accepted) named exactly. Structural headings, identity claims, and evidence
claims inside Markdown code fences do not count:

```text
<full tracked name>__<normalized VA without 0x>.md
```

The suffix is eight lowercase hexadecimal digits. The H1 is the full tracked
name and the `> Address: \`<va>\`` block must use the canonical
`0x` + eight-lowercase-hex spelling and resolve to the same VA. The tracked
name is never shortened to make the suffix look less repetitive. For example,
if the tracked name is `CBattleEngine__VFunc_7_00405ed0`, the only canonical
filename at VA `0x00405ed0` is:

```text
CBattleEngine__VFunc_7_00405ed0__00405ed0.md
```

The gate rejects anonymous `FUN_*` names at this first boundary. It also
requires one non-empty instance of every factory section:

- Identity
- Calling convention
- Prototype and parameter semantics
- Return value meaning
- Globals read/written (the template's `Globally referenced data` alias is
  accepted)
- Callees relied on / callers
- Behavior summary
- Error / edge behavior
- Runtime corroboration (TTD, bounded)
- Evidence
- Confidence
- Unresolved questions

Unknowns must be stated honestly. Empty or whitespace-only sections fail, as do
placeholder-only `TBD`, `TODO`, `-`, and `N/A` bodies, including bulleted,
multi-line, or fenced variants. Use `unknown`, `not_applicable`, or
`not_determinable` where those statements are accurate. Confidence starts with
`0` through `4`, a dash, and a justification.

Identity must carry an explicitly labeled, lowercase 64-hex SHA-256 body
digest. The `Binary: BEA.exe, SHA-256` header claim must carry the exact
pristine image SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Backticked relative paths in Evidence that claim tracked repository locations
are checked against the repository and may not traverse outside its root.
Absolute packet paths and ignored `local-lab/` evidence are outside this
tracked-file existence check. Registered submodule paths may be absent from the
working tree; other claimed repository paths must exist.

Across the complete input tree, normalized VAs and case-folded tracked names
are unique. This makes the cohort, not an individual file, the unit of the
duplicate check.

## Output and determinism

The validator collects all findings instead of stopping at the first one. Each
diagnostic has this shape:

```text
path: line: [CODE] message
```

Paths are POSIX-style and relative to the input root; lines are absolute
one-based source line numbers. Diagnostics are sorted by path, line, code, and
message before printing, followed by one count summary. The same files and
repository checkout therefore produce byte-identical output on repeated runs,
even when the input tree is checked out at a different absolute location.

Exit codes are:

- `0`: every candidate passed; the summary reports the file count and zero
  violations.
- `1`: one or more schema violations were found.
- `2`: the input root is missing, is not a directory, or contains no Markdown
  candidates.

The stable codes cover decoding, title/address/stem identity, anonymous names,
missing/duplicate/empty/placeholder sections, confidence syntax, image/body
digests, missing evidence paths, and duplicate VA/name claims. Codes are
machine-readable; the accompanying message is for the operator.

## Policy boundary

Passing this gate means only that a draft is mechanically complete and
internally consistent. It does not establish that:

- the prototype, parameter meanings, return meaning, globals, callees, or
  behavior are true;
- a packet body range or digest was derived from the correct pristine bytes;
- a runtime observation establishes causality beyond its bounded capture;
- source analogies prove retail behavior;
- the draft has been independently reviewed; or
- the function qualifies for C1, `C1_CANDIDATE_PARTIAL`, or any promotion.

The factory owner must still compare each claim with its packet/decompile,
reconcile exact body range and pristine digest, audit cited evidence, and pass
the repository's independent promotion procedure. The validator uses no LLM
and never grades semantics or edits a contract.

## Dry-run rule

When `reverse-engineering/contracts/**` is present on `origin/main`, scan that
tracked tree. Until it is merged, the bounded acceptance run is the focused
fixture suite plus a read-only invocation against the factory lane's
`.scratch/wave1/TEMPLATE.md`. The template invocation must be isolated from its
sibling drafts and is expected to return schema violations because the template
is a rule document, not a candidate contract. Never copy sibling scratch into
git to manufacture a live-tree result.
