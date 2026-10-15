# RTTI and source-path evidence in BEA.exe — a documented ground truth was wrong

Date: 2026-07-25. Method: direct ASCII scan of pristine `BEA.exe.original.backup`
(sha256 `74154bfa…`). Reproducible in seconds with a regex over the file bytes.

## The correction

Project hand-off material has repeatedly asserted:

> The binary has no symbols and never will. Of 9,420 ASCII strings, **zero** match
> `.pdb`, `.map`, RTTI, `assert`, or any source path. There is no symbols file and
> nothing other agents "missed."

**Two of those claims are false.** The binary contains:

| evidence | count |
| --- | ---: |
| RTTI type descriptors (`.?AV…@@` / `.?AU…@@`) | **667** |
| Source-file path strings (`C:\dev\ONSLAUGHT2\*.cpp` / `.h`) | **166** |

The PE *debug directory* is genuinely stripped (`rva=0, size=0`), and there is no
`.pdb`. That part of the claim holds. But "no symbols" was over-generalised from
"no debug directory" into "no name evidence," and the over-generalisation was then
treated as settled fact discouraging further search.

Examples, verbatim from the binary:

```
.?AVCActor@@            .?AVCBitmapFont@@       .?AVCDXBitmapFont@@
.?AVCBattleEngine@@     .?AVCAirUnit@@          .?AVCAsmInstruction@@
C:\dev\ONSLAUGHT2\DXFont.cpp
C:\dev\ONSLAUGHT2\DXFrontEndVideo.cpp
C:\dev\ONSLAUGHT2\DXFMV.CPP
C:\dev\ONSLAUGHT2\CPhysicsScriptStatements.cpp
```

RTTI descriptors carry **real class names as the original developers wrote them**.
Source paths carry **real translation-unit names**. Both are primary naming
evidence of a quality nothing else in this project can match — better than
decompiler inference, and better than Stuart's source, because these came out of
the shipped Steam build itself.

## Size of the opportunity

Measured against the current 6,411-function inventory:

| measure | count |
| --- | ---: |
| RTTI class names in the binary | 667 |
| Distinct class prefixes used in current Ghidra names | 608 |
| RTTI names **already** used as a prefix | **351 (53%)** |
| RTTI names **not used anywhere** | **316** |
| Ghidra prefixes with **no** RTTI backing (invented) | **257 (42%)** |

So roughly half the available real class names are in use, **316 real names are
unused**, and **257 current prefixes are inventions** — some of which are probably
the same classes under a made-up name.

This independently explains the sampled findings audit, which measured ~37% of
class prefixes as having no binary-string support. That was not an unavoidable
consequence of a stripped binary. It was a naming layer built partly by invention
while real names sat unread in the same file.

Unused real class names include: `CBitmapFont`, `CAtmospherics`, `C3DSoundMethod`,
`CBaseWaveFileRead`, `CBattleEngineInitThing`, `CComponentLife`,
`CComponentExplosion`, `CComponentDetach`, `CComponentGuide`,
`CBoatUnitBehaviourType`, `CApplyMenuItem`, `CBOOLMenuItem`, and ~300 more.

## Why this is more powerful than a string list

An RTTI type descriptor is not a loose string. It is one node of a structure that
also contains a **Complete Object Locator**, which is referenced immediately before
the class's **vtable**. Following that chain gives:

```
RTTI descriptor -> complete object locator -> vtable -> every virtual method of that class
```

That converts a class name into correct names for *all* of its virtual functions,
with the class relationship proven by the binary's own layout rather than inferred
from call patterns. It is the single highest-yield naming mechanism available here.

## Probable root cause

Ghidra ships an RTTI analyzer and a Microsoft demangler. If the database had been
built with RTTI analysis enabled and applied, `CBitmapFont` and the other 315
unused names would already appear. They do not. The most likely explanation is
that RTTI analysis was never run, or was run without applying the results — after
which "the binary has no symbols" hardened into project doctrine and stopped anyone
looking again.

**This is unverified.** Confirming it requires inspecting the live database's
analysis options, which is a separate read-only step.

## Consequences for the plan

1. **The name oracle should be the binary's own RTTI first**, and Stuart's source
   second. The earlier plan had this backwards.
2. **Do not grade 6,411 names until RTTI + vtable resolution has run.** Grading
   first means grading names that are about to be replaced by better-evidenced ones.
3. This reinforces the existing ordering decision: recover missing functions and
   apply real names *before* the naming-quality pass.
4. **Treat inherited "settled facts" as claims.** This one was stated confidently,
   repeated across hand-offs, and was wrong in a way that cost real naming quality.
   It was disproved by a regex.

## What is NOT claimed

- Not every RTTI name maps cleanly to a function; abstract classes and
  compiler-generated types exist among the 667.
- The 257 unbacked prefixes are **not** all wrong. Some name real classes that
  genuinely have no RTTI (non-polymorphic types emit none). They are unproven, not
  disproven.
- No naming change has been applied to the live database on the strength of this
  document.
