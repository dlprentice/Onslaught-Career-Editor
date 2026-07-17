# PhysicsScript copied-corpus parser evidence

Status: aggregate copied-corpus framing evidence; not runtime proof
Last updated: 2026-07-16

A shallow parser was applied to an ignored, user-supplied copy of
`data/default physics.dat`. Raw bytes, strings, absolute paths, and specimen
hashes remain local; this page retains only the aggregate result needed to
evaluate the static load contract.

| Metric | Result |
| --- | ---: |
| Parsed files | 1 |
| Parsed bytes | 175,603 |
| Stream header | `0x12` |
| Top-level statements | 777 |
| Type counts `1..9` | `160 / 139 / 145 / 91 / 38 / 118 / 39 / 43 / 4` |
| Unknown top-level ids | 0 |
| Value-list nodes | 6,803 |
| Unique statement/value-id pairs | 185 |
| Raw value payload bytes preserved by the parser | 73,796 |
| Continuation / terminator markers | 6,026 / 777 |
| Stop condition | terminating `-1` at EOF |

The parser follows the saved `CPhysicsScript__Load` framing: a two-byte `0x12`
header, repeated top-level type and declared-size rows, known ids routed through
the `1..9` factory range, name spans, shallow value-list records, and raw payload
skip/preservation. For known statements it follows the observed value-chain
terminator rather than treating declared size as a proven complete body layout.

Unknown value IDs and layouts remain unknown. Generated proof-plan crosswalks
and rollups are not retained as separate authorities.

This evidence supports framing and aggregate census claims only. It does not
prove runtime execution, serialized-format completeness, complete value
semantics, exact layouts, source identity, gameplay behavior, patch safety, or
rebuild parity.
