# CText__GetLanguageName

Status: independently rechecked instructions and bounded original execution
Last updated: 2026-09-20
Summary: active-header language naming, unknown-ID fallback and its distinct English audio-bank policy.
Source File: no retained text.cpp source body | Binary: pristine `BEA.exe.original.backup`.
Evidence: MEASURED — complete original getter, switch table and literals; executed inside 22 bank controls with ordinary logger intercepted.
Specimen: `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Address: `0x004f2190`

ECX supplies the text header. The body reads DWORD `+0x1c`, takes no
stack argument and returns a constant string pointer with plain RET.
The complete body is `[004f2190,004f21d0)`; its five-entry jump table
begins at `004f21d0`.

| Header ID | Returned name | Original pointer |
| --- | --- | --- |
| 0 | english | `00632d74` |
| 1 | french | `00632d7c` |
| 2 | german | `00632d94` |
| 3 | spanish | `00632d84` |
| 4 | italian | `00632d8c` |

The unsigned guard at `004f2193..004f2196` sends every other value to
logger `00441740`, then returns English. The controls cover 5 and
`0xffffffff`; no exit or fatal-handler call occurs in this body.

This is distinct from [Init](CText__Init.md)'s file-selection policy. The
getter does not inspect the American-text selector at `0083d990`; the
controlled American setting still produces the English bank path. It also
reads the selected receiver's header field, not the separate language mirror.
The [bank controls](../../../../VALIDATION.md#original-language-bank-admission-and-retry--september-20)
execute the getter on global active CText `0083d960` and observe the returned
pointer at the path-formatting boundary.

Original printf/log formatting, text loading, bank parsing and audio playback
are outside this getter result. No Ghidra metadata was changed by this note.
