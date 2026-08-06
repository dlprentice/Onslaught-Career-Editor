#!/usr/bin/env python3
"""Runtime slot-read contract instrument for CALLBACK_SLOT_INSTALL candidates.

From residual-executed-trace-callback-join terminal candidates:

  1. Static-decode each MOV r/m32, imm32(=candidate) install site to a slot
     expression (abs, [reg+disp], [esp+disp]).
  2. Emit a CDB script that:
       - bu install sites → single-step → dump slot dword → compare to candidate
       - bu residual entry VAs → dump [esp] return address + outside-residual flag
       - bu known control path entries (DecodeJpeg / LoadTexture / Create)
  3. Parse CDB stdout into a hash-bound receipt (no Gen10/Gen11 ledger mutation).

Does not invent names. Pristine backup is never written (runner enforces).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import struct
import sys
from pathlib import Path

PRISTINE_SHA256 = (
    "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
)
REGS = ["eax", "ecx", "edx", "ebx", "esp", "ebp", "esi", "edi"]


def pe_map(data: bytes):
    e_lfanew = struct.unpack_from("<I", data, 0x3C)[0]
    opt = e_lfanew + 24
    image_base = struct.unpack_from("<I", data, opt + 28)[0]
    num = struct.unpack_from("<H", data, e_lfanew + 6)[0]
    size_opt = struct.unpack_from("<H", data, e_lfanew + 20)[0]
    sec = e_lfanew + 24 + size_opt
    sections = []
    for i in range(num):
        o = sec + i * 40
        name = data[o : o + 8].split(b"\0")[0].decode("latin1", "replace")
        vsize, va, rawsize, rawptr = struct.unpack_from("<IIII", data, o + 8)
        sections.append((name, va, vsize, rawptr, rawsize))
    return image_base, sections


def va_to_off(va: int, image_base: int, sections) -> int | None:
    rva = va - image_base
    for _n, sva, vsize, rawptr, rawsize in sections:
        if sva <= rva < sva + max(vsize, rawsize):
            d = rva - sva
            if d >= rawsize:
                return None
            return rawptr + d
    return None


def decode_mov_rm_imm32(data: bytes, image_base: int, sections, va: int) -> dict:
    off = va_to_off(va, image_base, sections)
    if off is None:
        return {"error": "unmapped", "siteVa": f"0x{va:08x}"}
    b = data[off : off + 16]
    if b[0] != 0xC7:
        return {"error": f"not C7 ({b[:6].hex()})", "siteVa": f"0x{va:08x}"}
    modrm = b[1]
    mod = (modrm >> 6) & 3
    reg = (modrm >> 3) & 7
    rm = modrm & 7
    if reg != 0:
        return {"error": "not /0", "siteVa": f"0x{va:08x}"}
    pos = 2
    if mod == 3:
        return {"error": "reg dest", "siteVa": f"0x{va:08x}"}
    if rm == 4:
        sib = b[pos]
        pos += 1
        base = sib & 7
        index = (sib >> 3) & 7
        scale = sib >> 6
        if mod == 0 and base == 5:
            disp = struct.unpack_from("<i", b, pos)[0]
            pos += 4
            imm = struct.unpack_from("<I", b, pos)[0]
            return {
                "siteVa": f"0x{va:08x}",
                "form": "abs_disp32",
                "slotExpr": f"poi(0x{disp & 0xffffffff:08x})",
                "cdbDump": f"dd 0x{disp & 0xffffffff:08x} L1",
                "absVa": disp & 0xFFFFFFFF,
                "imm": imm,
                "insnLen": pos + 4,
                "bytes": b[: pos + 4].hex(),
            }
        if mod == 1:
            disp = struct.unpack_from("<b", b, pos)[0]
            pos += 1
        elif mod == 2:
            disp = struct.unpack_from("<i", b, pos)[0]
            pos += 4
        else:
            disp = 0
        imm = struct.unpack_from("<I", b, pos)[0]
        # index==4 means none
        if index == 4:
            base_name = REGS[base]
            sign = "+" if disp >= 0 else "-"
            adisp = abs(disp)
            expr = f"{base_name}{sign}0x{adisp:x}" if disp else base_name
            return {
                "siteVa": f"0x{va:08x}",
                "form": f"[{base_name}+disp]",
                "baseReg": base_name,
                "disp": disp,
                "slotExpr": f"poi({expr})",
                "cdbDump": f"dd {expr} L1",
                "imm": imm,
                "insnLen": pos + 4,
                "bytes": b[: pos + 4].hex(),
            }
        return {
            "error": "complex SIB index",
            "siteVa": f"0x{va:08x}",
            "bytes": b[:12].hex(),
        }
    # non-SIB
    if mod == 0 and rm == 5:
        disp = struct.unpack_from("<I", b, pos)[0]
        pos += 4
        imm = struct.unpack_from("<I", b, pos)[0]
        return {
            "siteVa": f"0x{va:08x}",
            "form": "abs_disp32",
            "slotExpr": f"poi(0x{disp:08x})",
            "cdbDump": f"dd 0x{disp:08x} L1",
            "absVa": disp,
            "imm": imm,
            "insnLen": pos + 4,
            "bytes": b[: pos + 4].hex(),
        }
    if mod == 1:
        disp = struct.unpack_from("<b", b, pos)[0]
        pos += 1
    elif mod == 2:
        disp = struct.unpack_from("<i", b, pos)[0]
        pos += 4
    else:
        disp = 0
    imm = struct.unpack_from("<I", b, pos)[0]
    base_name = REGS[rm]
    sign = "+" if disp >= 0 else "-"
    adisp = abs(disp)
    expr = f"{base_name}{sign}0x{adisp:x}" if disp else base_name
    return {
        "siteVa": f"0x{va:08x}",
        "form": f"[{base_name}+disp]",
        "baseReg": base_name,
        "disp": disp,
        "slotExpr": f"poi({expr})",
        "cdbDump": f"dd {expr} L1",
        "imm": imm,
        "insnLen": pos + 4,
        "bytes": b[: pos + 4].hex(),
    }


def load_candidates(join_json: Path) -> list[dict]:
    data = json.loads(join_json.read_text(encoding="utf-8"))
    rows = data["rows"] if "rows" in data else data
    return [r for r in rows if r.get("terminalCandidate")]


def build_static_plan(specimen: Path, candidates: list[dict]) -> dict:
    raw = specimen.read_bytes()
    sha = hashlib.sha256(raw).hexdigest()
    if sha != PRISTINE_SHA256:
        raise SystemExit(f"specimen mismatch {sha}")
    image_base, sections = pe_map(raw)
    out_cands = []
    for cand in candidates:
        start = int(cand["startVa"], 16)
        end = int(cand["endVa"], 16)
        installs = []
        detail = cand.get("callregDetail") or {}
        for site in detail.get("sites") or []:
            if site.get("kind") != "MOV_RM32_IMM32_MEM" and site.get("grade") != "CALLBACK_SLOT_INSTALL":
                continue
            if site.get("kind") == "PUSH_IMM32":
                continue
            site_va = int(site["siteVa"], 16)
            dec = decode_mov_rm_imm32(raw, image_base, sections, site_va)
            dec["owner"] = site.get("owner")
            dec["siteGrade"] = site.get("grade")
            if dec.get("imm") is not None:
                dec["immMatchesCandidate"] = dec["imm"] == start
            installs.append(dec)
        consumers = []
        for site in detail.get("sites") or []:
            if site.get("grade") == "SLOT_CONSUMER_NEAR_IMM":
                consumers.append(
                    {
                        "pushSiteVa": site.get("siteVa"),
                        "owner": site.get("owner"),
                        "nearCallMemSites": site.get("nearCallMemSites") or [],
                    }
                )
        out_cands.append(
            {
                "candidateVa": cand["startVa"],
                "endVa": cand["endVa"],
                "bytes": cand.get("bytes"),
                "joinGrade": cand.get("joinGrade"),
                "prevFunc": cand.get("prevFunc"),
                "nextFunc": cand.get("nextFunc"),
                "entityKey": cand.get("entityKey"),
                "installs": installs,
                "consumers": consumers,
                "cheapestFalsifier": cand.get("cheapestFalsifier"),
            }
        )
    return {
        "schema": "bea.re.runtime-slot-read-static-plan.v1",
        "specimen_sha256": sha,
        "n_candidates": len(out_cands),
        "candidates": out_cands,
    }


def emit_cdb_script(plan: dict, path: Path) -> None:
    lines = [
        ".echo PROBE_SCRIPT_START",
        "lm m BEA",
        # controls that previously hit under -skipfmv
        'bu 00557a90 ".echo HIT_CTRL_LoadTextureFromFile_Core; r eip; dds esp L4; gc"',
        'bu 0057af0a ".echo HIT_CTRL_DecodeJpegFromMemory; r eip; dds esp L4; gc"',
        'bu 00529090 ".echo HIT_CTRL_CD3DApplication_Create_near; r eip; dds esp L4; gc"',
    ]
    # better control: CD3DApplication__Create entry if known — use install nearby
    lines.append(
        'bu 00529100 ".echo HIT_CTRL_CD3DApplication_Create_region; r eip; dds esp L4; gc"'
    )

    for c in plan["candidates"]:
        cva = c["candidateVa"].replace("0x", "").lower()
        start = int(c["candidateVa"], 16)
        end = int(c["endVa"], 16)
        token = f"CAND_{cva}"
        # residual entry hit
        lines.append(
            f'bu {cva} ".echo HIT_{token}; r eip; dds esp L8; k L6; '
            f".echo RET_CHECK_{token}; "
            f'gc"'
        )
        for inst in c.get("installs") or []:
            if inst.get("error"):
                continue
            sva = inst["siteVa"].replace("0x", "").lower()
            dump = inst.get("cdbDump", "r")
            insn_len = int(inst.get("insnLen") or 0)
            if insn_len <= 0:
                # fallback: C7 form is typically 7-11 bytes; leave dump at site (pre-write)
                next_va = sva
            else:
                next_va = f"{int(sva, 16) + insn_len:08x}"
            # Do NOT use "p"/"t" inside the bu command body: CDB skips remaining
            # commands after target execution in an event handler. Arm a one-shot
            # bp at the next instruction, then gc so the install runs and the
            # follow-up bp dumps the slot dword.
            lines.append(
                f'bu {sva} ".echo HIT_INSTALL_{token}_AT_{sva}; r; '
                f"bp /1 {next_va} \\\".echo SLOT_DUMP_{token}_AT_{sva}; {dump}; "
                f".echo SLOT_EXPECT_{token}={cva}; gc\\\"; gc\""
            )
        for cons in c.get("consumers") or []:
            for call in cons.get("nearCallMemSites") or []:
                cs = call["siteVa"].replace("0x", "").lower()
                lines.append(
                    f'bu {cs} ".echo HIT_CONSUMER_CALL_{token}_AT_{cs}; r eip; dds esp L8; k L6; gc"'
                )

    lines += [
        "bl",
        'sxe -c ".echo EXIT_PROCESS; q" epr',
        ".echo PROBE_GO",
        "g",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="ascii")


def parse_cdb_log(text: str, plan: dict) -> dict:
    hit_counts: dict[str, int] = {}
    slot_reads: dict[str, list[dict]] = {}
    cand_hits: dict[str, list[dict]] = {}

    def bump(k: str) -> None:
        hit_counts[k] = hit_counts.get(k, 0) + 1

    lines = text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        m = re.match(r"^HIT_(CTRL_\w+|INSTALL_CAND_([0-9a-fA-F]+)_AT_([0-9a-fA-F]+)|CAND_([0-9a-fA-F]+)|CONSUMER_CALL_CAND_([0-9a-fA-F]+)_AT_([0-9a-fA-F]+))\s*$", line)
        if not m:
            # also match simpler tokens
            if line.startswith("HIT_"):
                bump(line)
            i += 1
            continue
        bump(line)
        # INSTALL path: after SLOT_DUMP look for dd line
        if line.startswith("HIT_INSTALL_CAND_"):
            # extract cand
            mm = re.match(r"HIT_INSTALL_CAND_([0-9a-fA-F]+)_AT_([0-9a-fA-F]+)", line)
            cand = mm.group(1).lower() if mm else "?"
            site = mm.group(2).lower() if mm else "?"
            # Find ONLY the exact SLOT_DUMP token for this cand+site.
            # Interleaved one-shot BPs can emit other SLOT_DUMP lines first;
            # a loose "SLOT_DUMP_CAND_" match steals the wrong dword.
            slot_val = None
            expect_tok = f"SLOT_DUMP_CAND_{cand}_AT_{site}"
            for j in range(i + 1, min(i + 40, len(lines))):
                stripped = lines[j].strip()
                if stripped == expect_tok or stripped.upper() == expect_tok.upper():
                    for k in range(j + 1, min(j + 8, len(lines))):
                        dm = re.match(
                            r"^[0-9a-fA-F]{8}\s+([0-9a-fA-F]{8})",
                            lines[k].strip(),
                        )
                        if dm:
                            slot_val = dm.group(1).lower()
                            break
                    break
                # stop at next install hit to avoid unbounded scan noise
                if stripped.startswith("HIT_INSTALL_CAND_") and j > i + 1:
                    # keep scanning; other installs may interleave before our dump
                    pass
            # Also accept imm from the hit disassembly line:
            #   mov dword ptr [...],offset BEA+... (00529070)
            if slot_val is None:
                for j in range(i + 1, min(i + 20, len(lines))):
                    dm = re.search(
                        r"mov\s+dword\s+ptr\s+\[[^\]]+\],.*\(([0-9a-fA-F]{8})\)",
                        lines[j],
                        re.I,
                    )
                    if dm:
                        # static imm seen at install site (pre/during write)
                        slot_reads.setdefault(cand, []).append(
                            {
                                "installSite": f"0x{site}",
                                "slotDword": None,
                                "immFromDisasm": f"0x{dm.group(1).lower()}",
                                "matchesCandidate": dm.group(1).lower() == cand,
                                "evidence": "disasm_imm_at_install",
                            }
                        )
                        break
            ok = slot_val == cand if slot_val else None
            if slot_val is not None:
                slot_reads.setdefault(cand, []).append(
                    {
                        "installSite": f"0x{site}",
                        "slotDword": f"0x{slot_val}",
                        "matchesCandidate": ok,
                        "evidence": "post_install_dd",
                    }
                )
        if line.startswith("HIT_CAND_"):
            mm = re.match(r"HIT_CAND_([0-9a-fA-F]+)", line)
            cand = mm.group(1).lower() if mm else "?"
            eip = None
            ret = None
            for j in range(i + 1, min(i + 25, len(lines))):
                em = re.match(r"^eip=([0-9a-fA-F]+)", lines[j].strip(), re.I)
                if em:
                    eip = em.group(1).lower()
                dm = re.match(
                    r"^[0-9a-fA-F]{8}\s+([0-9a-fA-F]{8})",
                    lines[j].strip(),
                )
                if dm and ret is None and eip is not None:
                    ret = dm.group(1).lower()
                    break
            # outside residual?
            outside = None
            for c in plan["candidates"]:
                if c["candidateVa"].replace("0x", "").lower() == cand:
                    start = int(c["candidateVa"], 16)
                    end = int(c["endVa"], 16)
                    if ret:
                        rva = int(ret, 16)
                        outside = not (start <= rva < end)
                    break
            cand_hits.setdefault(cand, []).append(
                {
                    "eip": f"0x{eip}" if eip else None,
                    "retAddr": f"0x{ret}" if ret else None,
                    "retOutsideResidual": outside,
                }
            )
        i += 1

    # summarize per candidate
    per = []
    for c in plan["candidates"]:
        cand = c["candidateVa"].replace("0x", "").lower()
        installs = slot_reads.get(cand, [])
        hits = cand_hits.get(cand, [])
        any_post = any(
            x.get("matchesCandidate") and x.get("evidence") == "post_install_dd"
            for x in installs
        )
        any_disasm = any(
            x.get("matchesCandidate") and x.get("evidence") == "disasm_imm_at_install"
            for x in installs
        )
        any_slot_ok = any_post or any_disasm
        any_entry = len(hits) > 0
        any_ret_out = any(x.get("retOutsideResidual") for x in hits)
        grade = "RUNTIME_UNREACHED"
        if any_post and any_entry and any_ret_out:
            grade = "RUNTIME_SLOT_INSTALL_AND_ENTRY_EXTERNAL_RET"
        elif any_post and any_entry:
            grade = "RUNTIME_SLOT_INSTALL_AND_ENTRY"
        elif any_post:
            grade = "RUNTIME_SLOT_WRITTEN_NO_ENTRY"
        elif any_disasm and any_entry:
            grade = "RUNTIME_INSTALL_IMM_AND_ENTRY"
        elif any_disasm:
            grade = "RUNTIME_INSTALL_IMM_SEEN_NO_POST_READ"
        elif any_entry and any_ret_out:
            grade = "RUNTIME_ENTRY_EXTERNAL_RET_NO_SLOT_CAPTURE"
        elif any_entry:
            grade = "RUNTIME_ENTRY_ONLY"
        per.append(
            {
                "candidateVa": c["candidateVa"],
                "joinGrade": c.get("joinGrade"),
                "runtimeGrade": grade,
                "installHits": installs,
                "entryHits": hits,
                "nInstallHits": len(installs),
                "nEntryHits": len(hits),
                "anySlotMatchesCandidate": any_slot_ok,
                "anyEntryHit": any_entry,
                "anyRetOutsideResidual": any_ret_out,
            }
        )

    return {
        "schema": "bea.re.runtime-slot-read-parse.v1",
        "hitTokenCounts": hit_counts,
        "perCandidate": per,
        "nCandidates": len(per),
        "nSlotOk": sum(1 for p in per if p["anySlotMatchesCandidate"]),
        "nEntryHit": sum(1 for p in per if p["anyEntryHit"]),
        "nEntryExternalRet": sum(1 for p in per if p["anyRetOutsideResidual"]),
        "probeGo": bool(re.search(r"(?m)^PROBE_GO\s*$", text)),
        "bpInsertFailed": bool(
            re.search(r"Unable to insert breakpoint|bp0 at .* failed", text)
        ),
    }


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)

    b = sub.add_parser("plan", help="static install decode + CDB script")
    b.add_argument("--specimen", type=Path, required=True)
    b.add_argument("--join-json", type=Path, required=True)
    b.add_argument("--out-dir", type=Path, required=True)

    r = sub.add_parser("parse", help="parse cdb log into receipt fragment")
    r.add_argument("--plan-json", type=Path, required=True)
    r.add_argument("--cdb-log", type=Path, required=True)
    r.add_argument("--json-out", type=Path, required=True)

    args = p.parse_args(argv)
    if args.cmd == "plan":
        cands = load_candidates(args.join_json)
        plan = build_static_plan(args.specimen, cands)
        args.out_dir.mkdir(parents=True, exist_ok=True)
        plan_path = args.out_dir / "static-plan.json"
        plan_path.write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8")
        emit_cdb_script(plan, args.out_dir / "cdb-commands.txt")
        print(json.dumps({k: plan[k] for k in plan if k != "candidates"}, indent=2))
        print("n_candidates", plan["n_candidates"])
        for c in plan["candidates"]:
            print(
                c["candidateVa"],
                c["joinGrade"],
                "installs",
                len(c["installs"]),
                "consumers",
                len(c["consumers"]),
            )
            for inst in c["installs"]:
                print(" ", inst.get("siteVa"), inst.get("form"), inst.get("cdbDump"), inst.get("error"))
        print("RUNTIME_SLOT_READ_PLAN_OK")
        return 0
    if args.cmd == "parse":
        plan = json.loads(args.plan_json.read_text(encoding="utf-8"))
        log = args.cdb_log.read_text(encoding="utf-8", errors="replace")
        parsed = parse_cdb_log(log, plan)
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(parsed, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({k: parsed[k] for k in parsed if k != "perCandidate"}, indent=2))
        print("RUNTIME_SLOT_READ_PARSE_OK")
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
