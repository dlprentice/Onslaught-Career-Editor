#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Plate: COVERED FUN_* structural PE templates (campaign name-align only).

Parent tip: Gen37 by default (accepts Gen36–37). Classifies remaining COVERED
FUN without native names by exact pristine PE body templates:

  ZERO_DWORDS3 / STORE_DWORDS3 — three mov [abs],imm ; ret (31B)
  RET / RET_N / XOR_EAX_RET / MOV_AL|EAX_1_RET — tiny stubs
  JMP_THUNK — mov ecx,imm; jmp rel32 (10B)
  DYNINIT22 / DYNINIT29 — CRT/dynamic register thunks
  INIT_IDENTITY_MAT — 195B sub esp,0x30 … add esp,0x30;ret float identity stores

Names are structural identity, not game semantics. No Ghidra. No REBUILD_READY.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import struct
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA = "bea.re.fun-trivial-template-name-align.v1"
PACK_SCHEMA = "bea.re.fun-trivial-template-name-align-formal-pack.v1"
ADVANCE_KIND = "FUNCTION_TRIVIAL_TEMPLATE_NAME_ALIGN.v1"
SPECIMEN_SHA256 = (
    "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
)
IMAGE_BASE = 0x400000
# INIT_IDENTITY_MAT bodies are 195B; keep a modest ceiling for other templates.
MAX_TEMPLATE_BODY_BYTES = 256

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PARENT = Path(
    "local-lab/function-residual-template-name-align-generation39-20260805-v1/"
    "generation-39-function-residual-template-name-align"
)
DEFAULT_SPECIMEN = Path("local-lab/safe-copy-bea-pristine/BEA.exe.original.backup")
DEFAULT_OUT = Path("local-lab/fun-micro-template-name-align-20260805-v1")

DEFAULT_FALSIFIER = (
    "PE body no longer matches template; name collision; REBUILD_READY claim; "
    "Ghidra mutation"
)


def _sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _read_tsv(path: Path) -> list[dict[str, str]]:
    rows = [
        line
        for line in path.read_text(encoding="utf-8").splitlines()
        if line and not line.startswith("#")
    ]
    return list(csv.DictReader(rows, delimiter="\t"))


def _write_tsv(path: Path, columns: list[str], rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        handle.write(f"# {SCHEMA}\n")
        w = csv.DictWriter(
            handle,
            fieldnames=columns,
            delimiter="\t",
            lineterminator="\n",
            extrasaction="ignore",
        )
        w.writeheader()
        for row in rows:
            w.writerow({c: row.get(c, "") for c in columns})


def is_real_native_name(raw: str | None) -> bool:
    native = (raw or "").strip()
    if not native:
        return False
    return native.lower() not in {"none", "null", "nil", "n/a", "-"}


def is_fun_identity(row: dict[str, str]) -> bool:
    name = str(row.get("currentName") or "")
    return row.get("nameClass") == "FUN" or name.startswith("FUN_")


def va_suffix(entry_va: str) -> str:
    return entry_va.lower().replace("0x", "").zfill(8)


def classify_body(entry_va: int, body: bytes) -> dict[str, Any] | None:
    if not body:
        return None
    # RET
    if body == b"\xc3":
        return {
            "lane": "RET",
            "newName": f"SharedRet_{va_suffix(hex(entry_va))}",
            "nameClass": "SHARED_STUB",
            "note": "ret",
        }
    if len(body) == 3 and body[0] == 0xC2:
        imm = struct.unpack_from("<H", body, 1)[0]
        if imm in (4, 8, 0x0C, 0x10):
            return {
                "lane": f"RET_{imm}",
                "newName": f"SharedRet{imm}_{va_suffix(hex(entry_va))}",
                "nameClass": "SHARED_STUB",
                "note": f"ret {imm}",
            }
    if body in (b"\x33\xc0\xc3", b"\x31\xc0\xc3"):
        return {
            "lane": "XOR_EAX_RET",
            "newName": f"SharedXorEaxRet_{va_suffix(hex(entry_va))}",
            "nameClass": "SHARED_STUB",
            "note": "xor eax,eax; ret",
        }
    if body == b"\xb0\x01\xc3":
        return {
            "lane": "MOV_AL_1_RET",
            "newName": f"SharedMovAl1Ret_{va_suffix(hex(entry_va))}",
            "nameClass": "SHARED_STUB",
            "note": "mov al,1; ret",
        }
    if body == b"\xb8\x01\x00\x00\x00\xc3":
        return {
            "lane": "MOV_EAX_1_RET",
            "newName": f"SharedMovEax1Ret_{va_suffix(hex(entry_va))}",
            "nameClass": "SHARED_STUB",
            "note": "mov eax,1; ret",
        }

    # STORE_DWORDS3: three mov dword [abs], imm32 ; ret  (31 bytes)
    # ZERO_DWORDS3 when all imm==0 (Gen37); non-zero often float constants.
    if len(body) == 31 and body[-1] == 0xC3:
        addrs: list[int] = []
        imms: list[int] = []
        pos = 0
        ok = True
        for _ in range(3):
            if pos + 10 > len(body):
                ok = False
                break
            if body[pos : pos + 2] != b"\xc7\x05":
                ok = False
                break
            addr = struct.unpack_from("<I", body, pos + 2)[0]
            imm = struct.unpack_from("<I", body, pos + 6)[0]
            addrs.append(addr)
            imms.append(imm)
            pos += 10
        if ok and pos == 30 and body[30] == 0xC3:
            if addrs[1] == addrs[0] + 4 and addrs[2] == addrs[0] + 8:
                base = addrs[0]
                if imms == [0, 0, 0]:
                    return {
                        "lane": "ZERO_DWORDS3",
                        "newName": f"ZeroDwords3_{va_suffix(hex(base))}",
                        "nameClass": "SHARED_STUB",
                        "note": f"zero 3 dwords at 0x{base:08x}",
                        "dataVa": f"0x{base:08x}",
                    }
                return {
                    "lane": "STORE_DWORDS3",
                    "newName": f"StoreDwords3_{va_suffix(hex(base))}",
                    "nameClass": "SHARED_STUB",
                    "note": (
                        f"store 3 dwords at 0x{base:08x} "
                        f"imm={imms[0]:08x}/{imms[1]:08x}/{imms[2]:08x}"
                    ),
                    "dataVa": f"0x{base:08x}",
                }

    # JMP_THUNK: mov ecx, imm32; jmp rel32
    if len(body) == 10 and body[0] == 0xB9 and body[5] == 0xE9:
        ecx = struct.unpack_from("<I", body, 1)[0]
        rel = struct.unpack_from("<i", body, 6)[0]
        target = entry_va + 10 + rel
        return {
            "lane": "JMP_THUNK",
            "newName": f"JmpThunk_{va_suffix(hex(target))}",
            "nameClass": "SHARED_STUB",
            "note": f"mov ecx,0x{ecx:08x}; jmp 0x{target:08x}",
            "thunkTarget": f"0x{target:08x}",
            "ecxImm": f"0x{ecx:08x}",
        }

    # DYNINIT22: mov ecx,X; call; push Y; call; pop ecx; ret
    if (
        len(body) == 22
        and body[0] == 0xB9
        and body[5] == 0xE8
        and body[10] == 0x68
        and body[15] == 0xE8
        and body[20] == 0x59
        and body[21] == 0xC3
    ):
        pushed = struct.unpack_from("<I", body, 11)[0]
        return {
            "lane": "DYNINIT22",
            "newName": f"DynInit22_{va_suffix(hex(pushed))}",
            "nameClass": "SHARED_STUB",
            "note": f"dynamic init/register push 0x{pushed:08x}",
            "thunkTarget": f"0x{pushed:08x}",
        }

    # DYNINIT29: push imm8; push str; mov ecx; call; push func; call; pop ecx; ret
    # Retail uses push 0 (Gen37/38) and nonzero imm8 (remaining COVERED FUN after Gen38).
    if (
        len(body) == 29
        and body[0] == 0x6A
        and body[2] == 0x68
        and body[7] == 0xB9
        and body[12] == 0xE8
        and body[17] == 0x68
        and body[22] == 0xE8
        and body[27] == 0x59
        and body[28] == 0xC3
    ):
        push_imm = body[1]
        pushed = struct.unpack_from("<I", body, 18)[0]
        return {
            "lane": "DYNINIT29",
            "newName": f"DynInit29_{va_suffix(hex(pushed))}",
            "nameClass": "SHARED_STUB",
            "note": f"dynamic init push{push_imm}+str; reg 0x{pushed:08x}",
            "thunkTarget": f"0x{pushed:08x}",
        }

    # STORE_DWORD1: mov dword [abs], imm32 ; ret  (11B)
    if len(body) == 11 and body[0:2] == b"\xc7\x05" and body[10] == 0xC3:
        addr = struct.unpack_from("<I", body, 2)[0]
        imm = struct.unpack_from("<I", body, 6)[0]
        return {
            "lane": "STORE_DWORD1",
            "newName": f"StoreDword1_{va_suffix(hex(addr))}",
            "nameClass": "SHARED_STUB",
            "note": f"store dword [0x{addr:08x}]=0x{imm:08x}",
            "dataVa": f"0x{addr:08x}",
        }

    # STORE_DWORDS2: two mov dword [abs], imm32 ; ret  (21B)
    if len(body) == 21 and body[-1] == 0xC3:
        if body[0:2] == b"\xc7\x05" and body[10:12] == b"\xc7\x05":
            a0 = struct.unpack_from("<I", body, 2)[0]
            i0 = struct.unpack_from("<I", body, 6)[0]
            a1 = struct.unpack_from("<I", body, 12)[0]
            i1 = struct.unpack_from("<I", body, 16)[0]
            if a1 == a0 + 4:
                return {
                    "lane": "STORE_DWORDS2",
                    "newName": f"StoreDwords2_{va_suffix(hex(a0))}",
                    "nameClass": "SHARED_STUB",
                    "note": f"store 2 dwords at 0x{a0:08x} imm={i0:08x}/{i1:08x}",
                    "dataVa": f"0x{a0:08x}",
                }

    # STORE_BYTE1: mov byte [abs], imm8 ; ret (8B)
    if len(body) == 8 and body[0:2] == b"\xc6\x05" and body[7] == 0xC3:
        addr = struct.unpack_from("<I", body, 2)[0]
        imm = body[6]
        return {
            "lane": "STORE_BYTE1",
            "newName": f"StoreByte1_{va_suffix(hex(addr))}",
            "nameClass": "SHARED_STUB",
            "note": f"store byte [0x{addr:08x}]=0x{imm:02x}",
            "dataVa": f"0x{addr:08x}",
        }

    # PUSH_CALL_POP_RET: push imm; call; pop ecx; ret (12B)
    if (
        len(body) == 12
        and body[0] == 0x68
        and body[5] == 0xE8
        and body[10] == 0x59
        and body[11] == 0xC3
    ):
        pushed = struct.unpack_from("<I", body, 1)[0]
        return {
            "lane": "PUSH_CALL_POP_RET",
            "newName": f"PushCallPopRet_{va_suffix(hex(pushed))}",
            "nameClass": "SHARED_STUB",
            "note": f"push 0x{pushed:08x}; call; pop; ret",
            "thunkTarget": f"0x{pushed:08x}",
        }

    # ZERO_A3_CHAIN: xor eax,eax; (mov [abs],eax)+; ret
    if len(body) >= 8 and body[0:2] == b"\x33\xc0" and body[-1] == 0xC3:
        bases: list[int] = []
        pos = 2
        while pos + 5 <= len(body) - 1 and body[pos] == 0xA3:
            bases.append(struct.unpack_from("<I", body, pos + 1)[0])
            pos += 5
        if bases and pos == len(body) - 1:
            base = bases[0]
            return {
                "lane": f"ZERO_A3x{len(bases)}",
                "newName": f"ZeroA3x{len(bases)}_{va_suffix(hex(base))}",
                "nameClass": "SHARED_STUB",
                "note": f"xor eax,eax; {len(bases)}x mov [abs],eax; ret base 0x{base:08x}",
                "dataVa": f"0x{base:08x}",
            }

    # ZERO_OBJ_16: mov eax,ecx; xor ecx,ecx; 4x mov [eax+off],ecx; ret
    if body == bytes.fromhex("8bc133c9890889480489480889480cc3"):
        return {
            "lane": "ZERO_OBJ_16",
            "newName": f"ZeroObj16_{va_suffix(hex(entry_va))}",
            "nameClass": "SHARED_STUB",
            "note": "zero 4 dwords at *ecx via xor",
        }

    # ZERO_OBJ_16_IMM: mov eax,ecx; mov dword [eax],0; mov [eax+4],0; ret
    if (
        len(body) == 16
        and body[0:2] == b"\x8b\xc1"
        and body[2:4] == b"\xc7\x00"
        and body[-1] == 0xC3
    ):
        return {
            "lane": "ZERO_OBJ_16_IMM",
            "newName": f"ZeroObj16Imm_{va_suffix(hex(entry_va))}",
            "nameClass": "SHARED_STUB",
            "note": "zero two dwords at *ecx via imm stores",
        }

    # INIT_FLOAT_BLOCK_226: sub esp, imm8; …; add esp,imm8; ret (float matrix-ish)
    if (
        len(body) == 226
        and body[0:2] == b"\x83\xec"
        and body[-4] == 0x83
        and body[-3] == 0xC4
        and body[-1] == 0xC3
        and body[-2] == body[2]
    ):
        # first absolute store via 89 0d or a3
        base = None
        for i in range(0, len(body) - 5):
            if body[i] == 0xA3:
                base = struct.unpack_from("<I", body, i + 1)[0]
                break
            if body[i : i + 2] in (b"\x89\x0d", b"\x89\x15", b"\xc7\x05"):
                base = struct.unpack_from("<I", body, i + 2)[0]
                break
        if base is not None:
            return {
                "lane": "INIT_FLOAT_BLOCK_226",
                "newName": f"InitFloatBlock226_{va_suffix(hex(base))}",
                "nameClass": "SHARED_STUB",
                "note": f"226B float/matrix init block base 0x{base:08x}",
                "dataVa": f"0x{base:08x}",
            }

    # INIT_IDENTITY_MAT 195B (retail BEA): sub esp,0x30; stack setup with 1.0f;
    # stores via a3 / 89 0d / 89 15 to contiguous globals; add esp,0x30; ret.
    # Not c7 05 — prior probe wrongly required that form and matched zero bodies.
    if (
        len(body) == 195
        and body[0:3] == b"\x83\xec\x30"
        and body[3:11] == b"\xc7\x44\x24\x00\x00\x00\x80\x3f"
        and body[-4:] == b"\x83\xc4\x30\xc3"
    ):
        base = None
        for i in range(0, len(body) - 5):
            if body[i] == 0xA3:
                base = struct.unpack_from("<I", body, i + 1)[0]
                break
            if body[i : i + 2] in (b"\x89\x0d", b"\x89\x15", b"\xc7\x05"):
                base = struct.unpack_from("<I", body, i + 2)[0]
                break
        if base is not None:
            return {
                "lane": "INIT_IDENTITY_MAT",
                "newName": f"InitIdentityMat_{va_suffix(hex(base))}",
                "nameClass": "SHARED_STUB",
                "note": f"195B identity-matrix store template base 0x{base:08x}",
                "dataVa": f"0x{base:08x}",
            }
    return None


def select_proofs(
    functions: list[dict[str, str]], pe: bytes
) -> tuple[list[dict], list[dict]]:
    proofs: list[dict[str, Any]] = []
    still: list[dict[str, Any]] = []
    used_names: set[str] = set()
    for row in functions:
        if not is_fun_identity(row):
            continue
        if row.get("executionState") != "COVERED":
            continue
        if is_real_native_name(row.get("nativeShippedName")):
            continue
        try:
            entry = int(row["entryVa"], 16)
            nb = int(row.get("bodyBytes") or 0)
        except (KeyError, ValueError):
            continue
        if nb <= 0 or nb > MAX_TEMPLATE_BODY_BYTES:
            still.append(
                {
                    "entryVa": row.get("entryVa"),
                    "lane": "BODY_OUT_OF_RANGE",
                    "bodyBytes": row.get("bodyBytes"),
                }
            )
            continue
        off = entry - IMAGE_BASE
        if off < 0 or off + nb > len(pe):
            still.append({"entryVa": row.get("entryVa"), "lane": "UNMAPPED"})
            continue
        body = pe[off : off + nb]
        rec = classify_body(entry, body)
        if rec is None:
            still.append(
                {
                    "entryVa": row.get("entryVa"),
                    "lane": "NO_TEMPLATE",
                    "bodyBytes": str(nb),
                }
            )
            continue
        new_name = rec["newName"]
        # disambiguate collisions (same data base rare; thunk targets may collide)
        if new_name in used_names:
            new_name = f"{new_name}_{va_suffix(row['entryVa'])}"
        used_names.add(new_name)
        if new_name == (row.get("currentName") or ""):
            still.append({"entryVa": row.get("entryVa"), "lane": "ALREADY_ALIGNED"})
            continue
        proofs.append(
            {
                "entityKey": row.get("entityKey"),
                "entryVa": row.get("entryVa"),
                "oldName": row.get("currentName"),
                "newName": new_name,
                "nameClass": rec["nameClass"],
                "recoveryLane": rec["lane"],
                "bodyBytes": row.get("bodyBytes"),
                "peBodySha256": hashlib.sha256(body).hexdigest(),
                "note": rec.get("note") or "",
                "dataVa": rec.get("dataVa") or "",
                "thunkTarget": rec.get("thunkTarget") or "",
                "proposed": {
                    "currentName": new_name,
                    "nameClass": rec["nameClass"],
                    "evidenceAppend": "CAMPAIGN_TRIVIAL_TEMPLATE_NAME_ALIGNED",
                    "rebuildState": "NOT_READY",
                    "cheapestFalsifier": DEFAULT_FALSIFIER,
                    "nonClaims": [
                        "Structural template name only",
                        "Not game-logic recovery",
                        "Not REBUILD_READY",
                        "Not Ghidra mutation",
                    ],
                },
            }
        )
    return proofs, still


def build(*, campaign: Path, specimen: Path, out_dir: Path) -> dict[str, Any]:
    ready = json.loads((campaign / "campaign.ready.json").read_text(encoding="utf-8"))
    # Accept Gen36–39 parents (successive structural-template waves).
    gen = int(ready.get("generation") or 0)
    if gen not in {36, 37, 38, 39}:
        raise SystemExit(f"expected Gen36–39 parent, got {ready.get('generation')}")
    pe = specimen.read_bytes()
    if hashlib.sha256(pe).hexdigest() != SPECIMEN_SHA256:
        raise SystemExit("specimen mismatch")
    functions = _read_tsv(campaign / "campaign-functions.tsv")
    if len(functions) != 8124:
        raise SystemExit(f"functions {len(functions)}")
    proofs, still = select_proofs(functions, pe)
    hard: list[str] = []
    seen_va: set[str] = set()
    for p in proofs:
        va = (p.get("entryVa") or "").lower()
        if va in seen_va:
            hard.append(f"dup {va}")
        seen_va.add(va)
        if p["oldName"] == p["newName"]:
            hard.append(f"noop {va}")
        if not p.get("entityKey"):
            hard.append(f"no ek {va}")
        # recheck pe
        entry = int(p["entryVa"], 16)
        nb = int(p["bodyBytes"])
        body = pe[entry - IMAGE_BASE : entry - IMAGE_BASE + nb]
        if hashlib.sha256(body).hexdigest() != p["peBodySha256"]:
            hard.append(f"sha {va}")
        again = classify_body(entry, body)
        if again is None or again["lane"] != p["recoveryLane"]:
            hard.append(f"reclass {va}")

    status = (
        "READY_FOR_GENERATION"
        if proofs and not hard
        else "EMPTY"
        if not proofs and not hard
        else "BLOCKED"
    )
    pack = {
        "schema": PACK_SCHEMA,
        "status": status,
        "advance_kind_proposed": ADVANCE_KIND,
        "specimen_sha256": SPECIMEN_SHA256,
        "campaign": str(campaign).replace("\\", "/"),
        "campaignGeneration": gen,
        "n_functions_input": len(functions),
        "n_proofs": len(proofs),
        "n_still_held": len(still),
        "n_hard_mismatches": len(hard),
        "hardMismatches": hard[:50],
        "recoveryLaneCounts": dict(Counter(p["recoveryLane"] for p in proofs)),
        "hold_generation_apply": True,
        "claims": [
            f"Selected {len(proofs)} COVERED FUN_* with exact PE structural templates.",
            "Names encode template identity "
            "(StoreDwords3/DynInit/InitIdentityMat/…), not game design.",
            "No Ghidra; no REBUILD_READY; residuals untouched.",
        ],
        "non_claims": [
            "Does not recover full function contracts",
            "Does not invent non-template names",
            "Does not re-close police residual OPEN_DARK",
        ],
        "proofs": proofs,
        "stillHeldSample": still[:30],
        "stillHeldCounts": dict(Counter(s.get("lane") for s in still)),
    }
    summary = {
        "schema": SCHEMA,
        "status": "MEASURED",
        "plate": str(out_dir).replace("\\", "/"),
        "generatedAtUtc": datetime.now(timezone.utc).isoformat(),
        "specimen_sha256": SPECIMEN_SHA256,
        "campaignGeneration": gen,
        "formalPackStatus": status,
        "counts": {
            "n_proofs": len(proofs),
            "n_still_held": len(still),
            "lanes": pack["recoveryLaneCounts"],
            "stillHeldCounts": pack["stillHeldCounts"],
        },
        "claims": pack["claims"],
        "non_claims": pack["non_claims"],
        "proofEntryVas": [p["entryVa"] for p in proofs[:20]],
        "parentFunctionsSha256": _sha(campaign / "campaign-functions.tsv"),
        "cheapestNext": [
            "Dual-role Grok+DeepSeek review then Gen38 apply",
            "Remaining COVERED FUN need deeper identity (source/TTD)",
            "Police OPEN_DARK needs non-envelope instrument",
        ],
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "FORMAL-PACK.json").write_text(
        json.dumps(pack, indent=2) + "\n", encoding="utf-8"
    )
    (out_dir / "SUMMARY.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    _write_tsv(
        out_dir / "proofs.tsv",
        [
            "entryVa",
            "entityKey",
            "oldName",
            "newName",
            "nameClass",
            "recoveryLane",
            "bodyBytes",
            "note",
            "dataVa",
            "thunkTarget",
            "peBodySha256",
        ],
        proofs,
    )
    (out_dir / "README.md").write_text(
        f"# Trivial template FUN name align\n\n**{status}** proofs **{len(proofs)}**\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2))
    print("FUN_TRIVIAL_TEMPLATE_NAME_ALIGN_MEASURED")
    print(f"formal_pack_status={status} n_proofs={len(proofs)}")
    return summary


def verify(*, plate: Path) -> dict[str, Any]:
    pack = json.loads((plate / "FORMAL-PACK.json").read_text(encoding="utf-8"))
    if pack.get("n_hard_mismatches", 1) != 0:
        raise SystemExit(f"hard {pack.get('hardMismatches')}")
    if pack.get("status") not in {"READY_FOR_GENERATION", "EMPTY"}:
        raise SystemExit(f"status {pack.get('status')}")
    out = {
        "status": "VERIFIED",
        "formalPackStatus": pack.get("status"),
        "n_proofs": pack.get("n_proofs"),
        "lanes": pack.get("recoveryLaneCounts"),
    }
    print(json.dumps(out, indent=2))
    print("FUN_TRIVIAL_TEMPLATE_NAME_ALIGN_VERIFIED")
    return out


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build")
    b.add_argument("--campaign", type=Path, default=DEFAULT_PARENT)
    b.add_argument("--specimen", type=Path, default=DEFAULT_SPECIMEN)
    b.add_argument("--out", type=Path, default=DEFAULT_OUT)
    v = sub.add_parser("verify")
    v.add_argument("--plate", type=Path, default=DEFAULT_OUT)
    args = p.parse_args(argv)
    if args.cmd == "build":
        build(campaign=args.campaign, specimen=args.specimen, out_dir=args.out)
        return 0
    verify(plate=args.plate)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
