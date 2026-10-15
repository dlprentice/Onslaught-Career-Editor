# CFrontEnd__NumControllersPresent

Status: bounded retail behavior rechecked; saved identity and older promotion receipt retained
Last updated: 2026-09-27
Summary: the complete retail helper returns constant 2; it does not count attached controllers.
Specimen: `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.

- Address: 0x00466990
- Historical receipt: Wave467 signature/comment hardened (not rerun here)
- Signature: `int __thiscall CFrontEnd__NumControllersPresent(void * this)`
- Source match: `references/Onslaught/FrontEnd.cpp:464` (`int CFrontEnd::NumControllersPresent()`)

## Purpose

Returns constant DWORD 2 and ignores the receiver. The complete six bytes are
`b8 02 00 00 00 c3`, SHA-256
`7140f35dee6220b79b12aecc27acf5105bf3b77d1588e89fce345de7c16c72b7`.
This establishes neither the number of ports nor attached/available devices.

## Notes

Pinned `FrontEnd.cpp:464–474` counts present controllers, a concrete difference
from these retail instructions. The saved name is an inherited source mapping,
not a new name-audit disposition. The unchanged helper now executes inside
21 isolated [options-callback controls](../display-settings.md#september-27-options-processing-recheck).
In that callback, the constant holds local word 4 at 4; an explicit helper-1
counterfactual advances it to 6. Actual controller discovery and whole frontend
behavior remain outside the experiment.
