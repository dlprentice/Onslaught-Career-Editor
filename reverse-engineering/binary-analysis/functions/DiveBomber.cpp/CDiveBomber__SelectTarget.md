# CDestructableSegmentsController__GetAimPosition

Status: active — corrected static aim-position contract
Last updated: 2026-09-19
Summary: selects a part of the owning Unit for aiming; the historical dive-bomber/entity-selection interpretation is withdrawn.
Source File: `DestructableSegmentsController.cpp` (retail ownership evidence at `006287b4`; exact method name unknown) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

Address: `0x00445070`; body `[00445070,0044515b)`, 235 bytes.
Specimen: `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Body SHA-256: `6eba7123575d16111736169e32371763e66189e238a524bca70cf585d2ecc072`.

The historical filename stays in place for existing links. Its former title,
`CDiveBomber__SelectTarget`, misidentified both the receiver and the operation.
The prior claims of distance/allegiance filtering, entity acquisition, assertions
and SEH are not supported by this body and are withdrawn. A saved name or an
earlier decompiler interpretation did not establish those behaviors.

## Receiver and native call contract

```c
void __thiscall CDestructableSegmentsController__GetAimPosition(
    void *this, void *out_target_position);
```

ECX holds the controller, with one output pointer at `Stack[4]` and `RET 4`.
Controller `+10` points to its owning Unit. Constructor `00443fc0` stores that
owner; Building and HiveBoss construction install the controller at Unit `+178`
(`00417223/00417246` and `0047fe99/0047feba`). The source string
`DestructableSegmentsController.cpp` at `006287b4` supports the existing owner
classification. The method name is analyst-authored; this is not a recovery of
the controller's exact original C++ declaration or complete layout.

Shared Unit provider `004fd4d0` delegates here when Unit `+178` is nonnull;
otherwise it uses the Unit centre helper `004f3ac0`. Unit and Plane primary
vtables `005df998` and `005e1930` both bind that provider at `+168`.
The weapon prediction helper calls the slot on its already supplied target.
Neither provider acquires a new target entity.

## Ordered part selection

The owner's renderer at Unit `+30` supplies a mesh through virtual slot `+24`.
The body visits mesh parts at mesh `+160` in ascending index order, below the
signed count at mesh `+15c`. For each nonnull part:

1. Use the part's index at `+88` in the controller's segment array at `+4`.
2. Require a nonnull segment, segment virtual `+14` returning zero, and an
   ordered floating-point comparison `segment[+0c] > 0`.
3. Retain the part only when signed `segment[+40]` exceeds the best value,
   initially zero. Equal values retain the earlier part.

For the selected part, call
`004b4de0(renderer, owner ? owner+8 : 0, part, out, local_matrix, 0, 0)`.
With no eligible part, call `004f3ac0(owner, out)` for the centre.
The precise meanings of virtual `+14` and integer `+40` remain open; the
comparison itself does not establish health, priority or distance units.

Keep the void output-buffer signature. Delegate return values in EAX are
incidental: the centre helper's plain-position fallback returns its copied
fourth word, not the output pointer. Renderer-derived paths also do not prove
that every output has a normalized or initialized fourth word.

## Evidence and remaining limits

The correction is based on freshly exported function metadata, all 87 body
instructions compared with pristine bytes, constructor/caller instructions and
virtual-table routing. It is part of the exact four-function
[aim-provider correction](../../../ghidra/README.md#aim-provider-metadata-correction-2026-09-19).
Private before/after exports and recovery receipts live under
`local-lab/ghidra-first-training-20260907-v1/aircraft-audit-20260919/aim-provider-semantics/`.

The [weapon contract](../CComplexThing.cpp.md#target-point-providers-and-weapon-prediction)
separately records execution of the original prediction helper and Actor motion
getter with supplied point/attachment providers. Those experiments do not execute
this segment selector or prove real part poses, selection frequency, destruction
lifecycle or live combat. A controlled original-body experiment with ordered
parts, equal selection values, ineligible segments and the centre fallback is
the next direct falsifier for this provider's static contract.
