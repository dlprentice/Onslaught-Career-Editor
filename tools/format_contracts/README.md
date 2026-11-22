# Format Contract Tables

Status: active — pinned format layout reference tables read by Toolkit tests
Last updated: 2026-11-21 (relocated from the retired frozen reverse-engineering copy when the repository was repurposed into the Modding & Content Toolkit)
Summary: machine-readable format layout tables kept locally for Toolkit decoder regression tests; their live documentation home is `onslaught-preservation`.

| File | Live home in `onslaught-preservation` | Consumer |
| --- | --- | --- |
| `battle-engine-config-layout.tsv` | [`formats/battle-engine-config-layout.tsv`](https://github.com/dlprentice/onslaught-preservation/blob/main/formats/battle-engine-config-layout.tsv) | [`tools/battle_engine_config_decode_tests.py`](../battle_engine_config_decode_tests.py) |

This table is a byte-identical copy of its counterpart in [onslaught-preservation](https://github.com/dlprentice/onslaught-preservation). It contains field offsets and layout metadata only—never retail game payloads.
