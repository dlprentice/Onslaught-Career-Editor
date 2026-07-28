# The cockpit's per-part world matrix — stack-frame trace of `0x004b5ad0`

> **Headline.** The identity-world contradiction is **resolved in structure but not
> in value.** A *second*, per-mesh-part `D3DTS_WORLDMATRIX(0)` upload exists at
> **`0x004b697b`**, downstream of the cockpit draw and downstream of the identity
> reset at `0x0053ebb6`. It is reached on the cockpit path and it overwrites that
> reset. Its content is `compose(EBX.transform, localTransform)`, where the
> cockpit's `localTransform` is provably the **identity/zero** class defaults at
> `0x0083ccd8` / `0x0083cd08`, so the entire cockpit placement rides on **`EBX`**.
> `EBX` at `0x004b5b09` is **`0x004b6260`'s argument 3**, which on the cockpit path
> is **`[renderable + 8]`**, where `renderable` is `CCockpit`'s `[this + 0x8c]`.
> **What `[renderable + 8]` points at could not be established statically** — see
> §6 for the precise negative and the one observation that settles it.

Specimen: `local-lab/safe-copy-bea-pristine/BEA.exe`, SHA-256
`e1436ef7e0ad9ccbddd43aaaca952f6e84d4b1a282835cead745efcfc32fadf4`,
2,506,752 bytes — the **capture target**: pristine plus the `force_windowed`
patch and nothing else.
*(Corrected 2026-07-28. This line previously read "`BEA.exe`, local pristine safe
copy `local-lab/safe-copy-bea-pristine/BEA.exe`", and carried no hash at all.
`e1436ef7` is **not** pristine — the pristine specimen is
`BEA.exe.original.backup`, SHA-256 `74154bfa…`, in the same directory; see
[`retail-specimen-baseline.md`](retail-specimen-baseline.md), which records that
the two file names in that directory are inverted. Re-measured 2026-07-28: the
two builds differ at exactly **four** bytes, file offsets `0x12a644`–`0x12a647`
= VA `0x0052a644`–`0x0052a647`. No address cited anywhere in this note falls in
that range — the nearest are `0x00527960` below and `0x0053bb50` above — so
**every byte claim below stands unchanged.**)*
Image base `0x00400000`. All
disassembly is `capstone` linear decode of that file through
`tools/disasm_va.py`; all reference counts are whole-file scans through
`tools/operand_scan.py` / `tools/call_xref_scan.py`; all data reads through
`tools/pe_read_va.py`. No Ghidra database was opened. `BEA.exe` was not launched.
Nothing was written to any installed game directory.

---

## 1. `CMeshPart__RenderAnimatedRecursive` @ `0x004b5ad0` — frame and convention

Prologue bytes (`--bytes` output, verbatim):

```
004b5ad0  81 ec 98 00 00 00     sub  esp, 0x98
004b5ad6  8b 84 24 ec 00 00 00  mov  eax, [esp + 0xec]
004b5add  53                    push ebx
004b5ade  55                    push ebp
004b5adf  8b 9c 24 e8 00 00 00  mov  ebx, [esp + 0xe8]
004b5ae6  56                    push esi
004b5ae7  8b b4 24 e8 00 00 00  mov  esi, [esp + 0xe8]
004b5aee  89 44 24 1c           mov  [esp + 0x1c], eax
004b5af2  57                    push edi
```

Let `E` = value of `esp` at entry (`[E]` = return address, arguments at `E+4`…).

| instruction | `esp` before | effective address | argument slot |
| --- | --- | --- | --- |
| `mov eax,[esp+0xec]` | `E-0x98` | `E+0x54` | `+0x54` |
| `mov ebx,[esp+0xe8]` | `E-0xa0` | `E+0x48` | **`+0x48`** |
| `mov esi,[esp+0xe8]` | `E-0xa4` | `E+0x44` | `+0x44` |

So the frame base after the four pushes is `S = E-0xa8`, and **`EBX` at
`0x004b5b09` is exactly the argument at callee slot `+0x48`** — the register the
task names. Cross-check: `[esp+0xac] = E+4`, and `0x004b5b15`/`0x004b5b1f`/
`0x004b5b29` load `[esp+0xb4]`/`[esp+0xb0]`/`[esp+0xac]` = `E+0xc`/`E+8`/`E+4`,
three consecutive floats — the argument-0 vector. Consistent.

**Calling convention: `__cdecl`, caller-cleaned, 0x54 bytes of arguments.** Proof:
the only callers are `0x004b5e4b` (self-recursion) and `0x004b6324`, and both
clean with `add esp, 0x54` (`0x004b5e57`, `0x004b6329`). No `ret n`; `ecx` is not
a `this` pointer (it is loaded from `ebx` before each virtual call).

Argument map (derived below from the caller's push sequence):

| slot | contents |
| --- | --- |
| `+0x04 .. +0x13` | 4 floats — the incoming **position** (x,y,z,w), overwritten in place |
| `+0x14 .. +0x43` | 12 floats — the incoming **3x4 rotation**, overwritten in place |
| `+0x44` | the `CMeshPart` node (`esi`; `[esi+0x90]` child count, `[esi+0x94]` child array) |
| `+0x48` | **`EBX`** — the transform/state object under investigation |
| `+0x4c` | the renderable (`0x004b6260`'s arg 4) |
| `+0x50` | `0x004b6260`'s arg 5 |
| `+0x54` | `0x004b6260`'s arg 7 — the render flag word |

### What the function does with `EBX`

```
004b5b09  8b 13        mov  edx, [ebx]          ; vptr
004b5b0b  8d 44 24 48  lea  eax, [esp + 0x48]   ; out buffer
004b5b0f  50           push eax
004b5b10  8b cb        mov  ecx, ebx
004b5b12  ff 52 04     call [edx + 4]           ; -> eax = 3x4 matrix
...
004b5b88  50           push eax                 ; second out buffer [esp+0x38]
004b5b8f  ff 12        call [edx]               ; -> eax = 3-float position
```

* **vtable slot `+4`** — `Matrix3x4* f(Matrix3x4* out)`, `__thiscall`. Its result
  is consumed as three rows at `+0x00`, `+0x10`, `+0x20` (stride `0x10`), i.e. a
  4-row-of-4 layout with only the first three columns used.
* **vtable slot `+0`** — `Vector3* f(Vector3* out)`, `__thiscall`. Its result is
  read at `[eax]`, `[eax+4]`, `[eax+8]` and **added** to the rotated position
  (`0x004b5b95`, `0x004b5b9f`, `0x004b5bae`).

The composition performed, in place on the argument slots, is:

```
pos' = EBX.slot4() * pos + EBX.slot0()        (written back to E+4 .. E+0x13)
rot' = EBX.slot4() * rot                      (written back to E+0x14 .. E+0x43,
                                               via rep movsd at 0x004b5d70)
```

`0x004b5b01 test ebx,ebx / 0x004b5b03 je 0x004b5d79` **skips the whole
composition when `EBX` is null**, leaving `pos`/`rot` exactly as supplied.

`EBX` is then forwarded unchanged to `0x004b5330` (`0x004b5d94 push ebx`), to
`0x004b6350` (`0x004b5db6 push ebx`), and to **every recursive call**
(`0x004b5e07 push ebx`, landing again at callee `+0x48`). It is never reassigned
inside the function.

Further `EBX` virtual slots observed: `+0x1c` and `+0x70` (`0x004b5350`,
`0x004b536d`, inside `0x004b5330`); `+0x68` (`0x004b699d`, called with
`[mesh+0x88]`, one argument, result `> 0` stored to `0x00704e64` and OR-ing flag
`0x20`); `+0x60` (`0x004dce40`, on the type-1 renderer's copy of the same field).
So `EBX`'s vtable is at least `0x74` bytes and **slot 0 is not a destructor** —
it is a getter. This is an interface-style base, not an MSVC single-inheritance
class laid out dtor-first.

---

## 2. Which of `0x004b6260`'s arguments lands at `+0x48`

`0x004b6260` prologue: `push ebx; push ebp; mov ebp,[esp+0x14]; push esi; push edi;
mov ebx,[esp+0x24]`. With `C` = entry `esp`: `ebp = [C+0xc]` = **arg 2**,
`ebx = [C+0x14]` = **arg 4**. It branches on `ebx` and `[ebx+0xc]`
(`0x004b6282`, `0x004b6286`); the `[ebx+0xc] == 0` branch is the one that calls
`0x004b5ad0`.

That branch's push sequence (`esp = C-0x10` on entry to it):

```
004b62e8  push edx   ; edx = [esp+0x30] = C+0x20 = arg 7      -> C-0x14
004b62f3  push eax   ; eax = [esp+0x28] = C+0x18 = arg 5      -> C-0x18
004b62f4  push ebx   ;                              arg 4      -> C-0x1c
004b62f7  push ecx   ; ecx = [esp+0x20] = C+0x10 = arg 3      -> C-0x20
004b62f8  push eax   ; eax = *[ebp+0x160]  (the mesh part)     -> C-0x24
004b62fe  sub  esp,0x30 ; rep movsd 12 dwords from arg 1 (matrix)
004b6303  sub  esp,0x10 ; 4 dwords copied from *arg 0 (position)
004b6324  call 0x4b5ad0
004b6329  add  esp,0x54
```

`esp` at the `call` is `C-0x64`, so the callee's `E = C-0x68` and
`E+0x48 = C-0x20`.

> **Answer to question 2: callee slot `+0x48` is `0x004b6260`'s argument 3**
> (the dword at `C+0x10`, the fourth argument).

At every one of the eight call sites of `0x004b6260`, argument 3 has the same
shape:

| call site | arg 3 | arg 4 |
| --- | --- | --- |
| `0x004db9bc` | `[eax+8]` | `eax` (this) |
| `0x004dbf4c` | `[ebx+8]` | `ebx` (this) — **the cockpit** |
| `0x004dce20` | `[ebx+8]` | `ebx` (this) |
| `0x0045f2c7`, `0x00482f68`, `0x004ddf60` | `0` | `0` |

So **`EBX` = `[renderable + 8]`**, and it is legitimately optional — three call
sites pass null, which is exactly why `0x004b5b01` guards it.

---

## 3. The cockpit path, established end to end

```
0053ec6a  call 0x0053bb50                  ; CCockpit::Render (sole caller)
0053bbe1  mov  ecx, [esi + 0x8c]           ; the renderable
0053bbe7  push edi                         ; 0 or 0x40
0053bbea  call [edx + 8]                   ; vtable slot +8
```

The class whose vtable slot `+8` is a `ret 4` render entry calling `0x004b6260`
is the one with **vptr `0x005dea38`**:

```
0x005dea38: +0x00 0x004dbc30  (scalar deleting dtor)
            +0x04 0x004dbd80  (load / build mesh table)
            +0x08 0x004dbec0  <- Render, ret 4
            ...
            +0x24 0x004dbf80  (GetCurrentMesh: [this+0x14][ [this+0x24] ])
```

`operand_scan` for `0x005dea38` returns exactly two writers, both `mov [reg],
0x5dea38` at `0x004dbb67` (constructor) and `0x004dbc6e` (destructor). The
constructor is reached only from `0x00516651`, which is entry 4 of the jump table
at `0x005166a0` dispatched by `0x005165a3 jmp [eax*4 + 0x5166a0]` inside
`CreateRenderable @ 0x00516580`. `CreateRenderable` has 17 callers; exactly one
stores the result to `+0x8c`:

```
0042459b  call 0x516580
004245a5  mov  [ebp + 0x8c], eax
```

and the same function also initialises `[ebp+0x110]` (`0x00424677`) and
`[ebp+0x12c]` (`0x004245c0`) — the two other fields `CCockpit::Render` reads at
`0x0053bb56` and `0x0053bb97`. That is a three-field match; I treat the identity
of the cockpit's renderable class as established, with the caveat that the type
selector at `0x0042459a` (`push [esp+0x5c]`) is data-driven, so a different level
configuration could instantiate a sibling class.

### The cockpit's incoming local transform is identity / zero

`0x004dbec0` builds `0x004b6260`'s arg 0 and arg 1 from two globals:

```
004dbef4  mov ecx,[0x0083cd08] ; ...0x0083cd0c, 0x0083cd10, 0x0083cd14  -> 4-dword position
004dbf13  mov esi, 0x0083ccd8  ; rep movsd 12 dwords                    -> 3x4 rotation
```

Both are `.bss`. `operand_scan` over all 2,506,752 bytes returns, for
`0x0083ccd8`, three hits: two are the *reads* above (`mov esi, 0x83ccd8`), and one
is the sole writer at `0x004dc1e7`; for `0x0083cd08`, two hits: the read at
`0x004dbef4` and the sole writer at `0x004dc190`. Those writers are:

```
004dc190  mov [0x83cd08], 0 ; mov [0x83cd0c], 0 ; mov [0x83cd10], 0      -> zero
004dc1b0  builds 1.0/0/0 , 0/1.0/0 , 0/0/1.0 on the stack and stores to
          0x83ccd8 .. 0x83cd04                                          -> identity
```

**So the transform handed into the recursive walker for the cockpit is the
identity rotation and the zero position.** Everything the cockpit's placement can
possibly come from is `EBX = [renderable+8]`.

The same pattern exists per class: `0x004db960`'s class uses `0x0083cc98` /
`0x0083ccc8` (identity/zero, writers `0x004dbac7` / `0x004dba70`).

---

## 4. Yes — a per-part world matrix is composed and uploaded

`0x004b5ad0` calls `0x004b6350` at `0x004b5dc8` with argument 0 = `&E+4`
(the composed position) and argument 1 = `&E+0x14` (the composed 3x4). Inside
`0x004b6350`:

```
004b6946  mov  esi, [esp+0x88]        ; arg 1 = the 3x4 rotation
004b694d  sub  esp, 0x30
004b6957  rep movsd (12 dwords)       ; push the matrix by value
004b6959  sub  esp, 0x10
004b695c  mov  ecx, ebx               ; ebx = [esp+0x84] = arg 0 = position
004b6960..004b6973  copy 4 dwords     ; push the position by value
004b6976  mov  ecx, 0x009c65c0        ; CDXEngine
004b697b  call 0x00550ca0             ; CDXEngine::SetWorldMatrix
```

`0x00550ca0` is `__thiscall`, `ret 0x40` (16 dwords of by-value arguments,
`A0..A15` at `[esp+0x44]`…`[esp+0x80]`). It assembles a D3D row-major 4x4 at
`[this+0x354]` (= `0x009c6914`) and sets the dirty byte `[this+0xe28] = 1`:

| destination dword | source |
| --- | --- |
| `D0,D4,D8` | `A4,A5,A6` (source matrix row 0) |
| `D1,D5,D9` | `A8,A9,A10` (row 1) |
| `D2,D6,D10` | `A12,A13,A14` (row 2) |
| `D3,D7,D11` | `0` |
| `D12,D13,D14` | `A0,A1,A2` (the position) |
| `D15` | `0x3f800000` |

i.e. the source 3x4 is **transposed** into the upper 3x3 and the position becomes
row 3. `A3`, `A7`, `A11`, `A15` are discarded.

`[engine+0x354]` is the world slot, proven by the flush at:

```
00551034  lea  edx, [ebp + 0x354]
0055103a  push edx
0055103b  push 0x100                  ; D3DTS_WORLDMATRIX(0)
00551043  call [ecx + 0xb0]           ; IDirect3DDevice9::SetTransform
```

(the same function uploads `[ebp+0x394]` with state `2` = `D3DTS_VIEW` at
`0x00551068` and `[ebp+0x3d4]` with state `3` at `0x005110bd`).

**This is a second, later, per-mesh-part upload than the one at `0x0053ebb6`.**
Ordering in the frame function: `0x0053ebb6` (identity reset) → … →
`0x0053ec6a call CCockpit::Render` → `0x004dbf4c` → `0x004b6324` → `0x004b5dc8` →
`0x004b697b`. So the previously-catalogued identity upload at `0x0053ebb6` is
**not** the matrix in effect when cockpit geometry is drawn. **That part of the
live contradiction is dead: the world-matrix reset is not the cockpit's world
matrix.**

Reachability of `0x004b697b` on the cockpit path: `0x004b6350` tests
`[mesh+0x8c]` against `5` at `0x004b63ee`; the `!= 5` path jumps to `0x004b69bc`,
which reloads the position pointer and jumps to `0x004b691e`, falling straight
through to `0x004b697b`. The `test byte ptr [esp+0x9c], 4 / je 0x004b6b93` guard
at `0x004b6909` sits only on the `[mesh+0x8c] == 5` branch, so the flag word
`0x004dbec0` passes as `0` (`0x004dbf1e push 0`) does not suppress the upload for
ordinary meshes.

> **Answer to question 4: yes.** The uploaded world matrix is
> `transpose3x3(EBX.slot4() * localRot)` with translation
> `EBX.slot4() * localPos + EBX.slot0()`, and for the cockpit `localRot` is the
> identity at `0x0083ccd8` and `localPos` is the zero at `0x0083cd08`. Therefore
> **the cockpit's world matrix is exactly `EBX`'s transform**, whatever that is.

---

## 5. The recursion applies `EBX` once per hierarchy level

`0x004b5e4b` re-enters `0x004b5ad0` with the *composed* position/rotation and the
**same** `EBX` (`0x004b5e07 push ebx`, landing again at `+0x48`; verified by the
push ordering: `push eax(+0x54); push ecx(+0x50); push edx(+0x4c); push ebx(+0x48);
push ecx(child)(+0x44)`). Sibling parts are iterated in `0x004b6260`
(`0x004b6334 mov ebp,[ebp+8]`), each with a **fresh copy** of the caller's
arg 0 / arg 1.

Consequence, stated plainly because it constrains any interpretation of `EBX`:
for a flat part list `EBX`'s transform is applied exactly once, but for a part
with children it is applied once **per level of depth**. A fixed
owner-entity transform would be applied twice for a depth-2 part, which would be
wrong. That is evidence — not proof — that `EBX`'s slots `0`/`4` return
*per-node* state that something advances between levels. `0x004b5330`, which is
called with `EBX` as argument 0 immediately before `0x004b6350`, does invoke
`EBX`'s vtable slots `+0x70` (`0x004b5350`) and `+0x1c` (`0x004b536d`) with the
part in scope, which is where such an advance would live. **I did not verify
that either of those slots mutates `EBX`.**

---

## 6. The precise negative: `[renderable + 8]` is not identified

What is proven about the field:

* It is dereferenced as a vtable pointer at `0x004b5b09` and null-checked at
  `0x004b5b01`, so it is a polymorphic object pointer, deterministically either
  null or valid.
* For the cockpit's class (vptr `0x005dea38`, allocation size `0x28` at
  `0x0051665a`), **no instruction in the class writes `[this+8]`**. Verified by
  reading every function reachable from the vtable
  (`0x004dbb60` ctor, `0x004dbc30`/`0x004dbc50` dtors, `0x004dbd80`,
  `0x004dbe50`, `0x004dbe90`, `0x004dbec0`, `0x004dbf70`, `0x004dbf80`,
  `0x004dbfb0`, `0x004dbfc0`, `0x004dbb80`, `0x004dbbe0`): the constructor writes
  only `[+0x10]`, `[+0]`, `[+0x18]`; `0x004dbd80` writes `[+0x14]`, `[+0x18]`,
  `[+0x1c]`; `0x004dbe39`/`0x004dbe40`/`0x004dbe44` write `[+4] = 1.0f`,
  `[+0x20] = 0`, `[+0x24] = -1`. The destructor frees `[+0x14]`, `[+0x1c][i]`,
  `[+0x1c]`, releases `[+0x10]`, and **does not touch `[+8]` or `[+0xc]`**.
* The shared base class (vtable `0x005deaac`, dtor `0x004dbd50`/`0x004dbd20`)
  manages only `[+0x10]`.
* The allocator behind it (`0x005490e0` → `0x004a1810`) is a free-list pool with
  no `memset` on any return path (`0x004a1875`, `0x004a1c0f`, `0x004a1c11`), so
  recycled blocks are **not** zeroed.

What I could not establish, and tried to:

* A whole-`.text` capstone scan (621,736 instructions, resuming past invalid
  bytes) for `mov dword ptr [reg+8], reg` preceded within 25 instructions by a
  load of `reg` from any struct field returned 697 candidates; filtering for the
  offsets renderables are actually stored at (`+0x30`, `+0x8c`, `+0x4c`, `+0x58`,
  `+0x5ec`) left four, all of which are 16-byte vector copies
  (`0x0044acbf`, `0x0044acde`, `0x004d7d31`, `0x004f3b5d`) — false positives.
* The same scan restricted to stores following a `call` within four instructions
  returned 278 candidates, none of which resolves to a renderable.
* The single image-wide occurrence of the canonical setter shape
  `mov eax,[esp+4]; mov [ecx+8],eax; ret 4` is `0x00527960`, whose only two
  callers (`0x0051be91`, `0x0051be9d`) are unrelated.

So the honest state is: **`EBX` is `[renderable+8]`, an object exposing
`GetPosition(out)` at vtable `+0`, `GetOrientation3x4(out)` at vtable `+4`, plus
slots `+0x1c`, `+0x60`, `+0x68`, `+0x70`; and no writer of that field was found
in the image.** Two possibilities remain open and I can distinguish neither from
bytes alone:

1. an external writer exists that my scans missed (they are pattern-based, not a
   sound dataflow analysis, and would miss e.g. a store through a pointer held in
   a local, or a `rep movsd` that covers offset 8); or
2. the field is genuinely always null for this class, in which case the cockpit's
   uploaded world matrix at `0x004b697b` is literally the identity/zero from
   `0x0083ccd8`/`0x0083cd08` and **the original contradiction survives in a
   sharper form** — a real VIEW matrix with a literal identity WORLD, which is
   the "cockpit at the world origin" that retail cannot be displaying, unless the
   VIEW in force at `0x0053ec6a` is itself not the camera view.

I am explicitly **not** guessing which. Do not treat either as established.

### The single observation that settles it

Read `[renderable + 8]` — equivalently, the `EBX` register at `0x004b5ad0+0x39`
(`0x004b5b09`) — once, during a Level 100 gameplay frame, on a **copied** runtime.
A hardware/data breakpoint at `0x004b5b09` reached from `0x0053ec6a`, reporting
`EBX` and, if non-null, `*(void**)EBX` (its vptr, which maps straight back to a
`.rdata` address in this note's terms), decides between (1) and (2) outright.

The strictly-better version of the same observation, which also ends the whole
question rather than just this branch: capture the 16 dwords at **`0x009c6914`**
(the engine's world slot, written by `0x00550ca0` at `0x00550d3b`) immediately
after `0x004b697b` on a cockpit part. That is the actual matrix D3D receives, and
it needs no interpretation.

---

## 7. Corrections this note implies for other documents (not applied here)

`reverse-engineering/binary-analysis/cockpit-lighting-law-2026-07-26.md` §7 says
"the real per-part world matrix is set inside the virtual mesh render reached
through `[this+0x8c]->vtable[+8]` at `0x0053bbea`, which this note did not
resolve." That is correct and this note resolves the *location*: it is
`0x004b697b`. The §7 statement that the `0x0053ebb6` upload "is a reset, not the
cockpit's transform" is confirmed by call ordering, not merely by the absence of
writers to `0x0089d640`.

`local-lab/HANDOFF-2026-07-26.md` §3.1's phrasing "both traceable world-matrix
uploads are identity with zero translation" should be narrowed: a **third**
upload site exists (`0x004b697b`), it is the one the cockpit actually uses, and
its value is not statically constant.

## CONFIRMED INDEPENDENTLY, same day, by runtime capture

This trace was performed blind to a concurrent controlled copied-runtime
observation, and the two agree. See
[`cockpit-lighting-law-2026-07-26.md`](cockpit-lighting-law-2026-07-26.md) §7 and
`local-lab/COCKPIT-WORLD-MATRIX-RUNTIME-2026-07-26.md`.

The runtime capture of `SetTransform(D3DTS_WORLDMATRIX(0))` at the cockpit draw
records **seven** non-identity uploads per cockpit render — matching this note's
finding that the real upload is a per-part site downstream of the identity reset,
not the reset itself. Measured batch 0 has `det = +1.000000`, translation equal to
the camera world position, and `R_world · R_view` equal to the axis map
`x→x, y→z, z→−y` to within 2.8774°.

That **settles §6's remaining gap in the affirmative**: `[renderable+8]` is not
null, and the identity-WORLD-against-real-VIEW contradiction does not survive.
The single settling observation proposed above — dumping the 16 dwords at
`0x009c6914` after `0x004b697b` — was effectively made by breaking at
`0x00551043` instead, inside a breakpoint window armed at `0x0053bb50` and
disarmed at `0x0053ec6f`. The writer of `[renderable+8]` is still unidentified
statically; that is now a naming question, not a behavioural one.

One residual the runtime data adds and this trace could not see: **two of the
seven batches carry a negative-determinant (mirrored) world matrix.**

## Reproduction

```
py -3 tools/disasm_va.py local-lab/safe-copy-bea-pristine/BEA.exe 0x004b5ad0 --count 90  --bytes
py -3 tools/disasm_va.py local-lab/safe-copy-bea-pristine/BEA.exe 0x004b5c28 --count 130
py -3 tools/disasm_va.py local-lab/safe-copy-bea-pristine/BEA.exe 0x004b6260 --count 80  --bytes
py -3 tools/disasm_va.py local-lab/safe-copy-bea-pristine/BEA.exe 0x004b68c0 --count 70  --bytes
py -3 tools/disasm_va.py local-lab/safe-copy-bea-pristine/BEA.exe 0x00550ca0 --count 45
py -3 tools/disasm_va.py local-lab/safe-copy-bea-pristine/BEA.exe 0x0053bb50 --count 45  --bytes
py -3 tools/disasm_va.py local-lab/safe-copy-bea-pristine/BEA.exe 0x004dbeeb --count 30  --bytes
py -3 tools/disasm_va.py local-lab/safe-copy-bea-pristine/BEA.exe 0x004dc190 --count 40  --bytes
py -3 tools/disasm_va.py local-lab/safe-copy-bea-pristine/BEA.exe 0x00516590 --count 20  --bytes
py -3 tools/call_xref_scan.py local-lab/safe-copy-bea-pristine/BEA.exe 0x004b6260 0x004b5ad0 0x004b5e80 0x00516580 0x00550ca0
py -3 tools/operand_scan.py   local-lab/safe-copy-bea-pristine/BEA.exe 0x005dea38 0x005deaac 0x0083ccd8 0x0083cd08 0x0083cc98 0x0083ccc8
py -3 tools/pe_read_va.py     local-lab/safe-copy-bea-pristine/BEA.exe 0x005dea38 --count 64 --as hex
```
