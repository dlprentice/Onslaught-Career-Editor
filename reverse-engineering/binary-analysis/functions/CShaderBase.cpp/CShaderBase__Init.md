# PCLTShell__AddDeviceObject

Status: active, bounded static function contract
Last updated: 2026-09-27
Summary: source/caller-grounded shell registration identity; the former shader owner was incorrect.
Source File: pinned `ltshell.h:73,295` and `ltshell.cpp:55` | Binary: pristine `BEA.exe.original.backup`, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Evidence: MEASURED — complete pristine body, ten direct caller bodies and the shell singleton/RTTI constructor chain; SOURCE — commit `5352a81cdb838b145a57f7febc5d9fc4b0129ebb`.

> Address: `0x00512ca0`. The old `CShaderBase__Init` filename is retained for links.

The complete 21-byte body `[0x00512ca0,0x00512cb5)` has SHA-256
`139666059cc555246abb2226fec1de15f03cd2c862a02335434be346571270fa`.
It reads a node pointer from entry `[ESP+4]`, writes the old head at
`0x00889074` to `[node+4]`, then replaces that head with the node. It returns
with `RET 4`; the following padding is outside the body. EAX incidentally
contains the node. Incoming ECX is overwritten without being read.

That unused receiver does not establish a free function or a shader owner.
All ten freshly decoded direct call sites supply `ECX=0x00855bb0` and one
stack node: `0x00488243`, `0x004f7a02`, `0x004fff33`, `0x00501843`,
`0x00544c63`, `0x0054bfd8`, `0x00552111`, `0x00556d48`, `0x0055a399`,
`0x0055b124`. Every inspected caller overwrites EAX before consuming it,
consistent with the source's void return. No newly inferred EAX result is
part of this contract.

Initializer `0x00512010` passes `0x00855bb0` to constructor `0x00512670`.
Its base call to `0x00528f80` and primary table installation `0x005e488c`
bind the object to RTTI `PCLTShell`, with a fixed zero-offset
`CD3DApplication` base. The pinned header's `AddDeviceObject(DeviceObject*)`
performs the same two list writes; `mDeviceObjects` is static. This establishes
the source method identity without trusting the former saved label.

The [shell correction](../../../ghidra/README.md#re-audit-startup-shell-identities--september-27)
changes only the name, comment and tags. Its saved physical interface remains
unchanged; richer class layout is not implied. The
[device-lifecycle contract](../../../source-code/core/platform-system.md#retail-device-lifecycle--september-27-correction)
separately establishes retail's two lists. This insertion affects only one
head and does not prove complete registration, destruction or callback lifetime.

Private exact caller/body pins: `local-data/test-runs/re-audit-20260926/startup-shell/`.
The August note's separate specimen-twin and whole-image immediate-count claims
were not used or reverified here. Unknown indirect callers/linker aliases remain
possible. The cheapest lifetime falsifier is a controlled copied retail run
tracing registration, movement between lists and teardown for one object;
no retail process was launched for this identity correction.

| Address | Name | Verified static scope |
| --- | --- | --- |
| `0x00512ca0` | `PCLTShell__AddDeviceObject` | One node pointer, prepend through node `+4` and head `0x00889074`, callee cleanup four bytes; caller-bound shell method identity |
