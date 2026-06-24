import argparse
import csv
import json
import re
from pathlib import Path


DEFAULT_ROOT = Path("subagents/ghidra-static-reaudit/cylinder-damage-wave346/current")
OUTPUT_NAME = "cylinder-damage-signature-tranche.json"

EXPECTED_SIGNATURES = {
    "0043fde0": "void __thiscall CCylinder__ctor(void * this, void * sourceCylinder)",
    "0043fe20": "int __thiscall CCylinder__ResolveCollisionVFunc02(void * this, void * movingStateA, void * movingStateB, void * radiusContext, void * contactOut)",
    "00440b90": "void __fastcall CDamage__Init(void * damage)",
    "00440c00": "void __fastcall CDamage__FreeOwnedDamageObjects(void * damage)",
    "00440c40": "void __fastcall CDamage__ResetDamageTables(void * damage)",
    "00440c70": "void __thiscall CDamage__LoadDamageTexture(void * this, char * tgaPath)",
    "00440eb0": "int __thiscall CDamage__InsertCellEntry(void * this, int cellIndex, int coordX, int coordY, int stampValue)",
    "00440f80": "void __thiscall CDamage__RemoveCellEntryByCoords(void * this, int cellIndex, int coordX, int coordY)",
    "00441000": "void __thiscall CDamage__CreateTextureBuffer(void * this, void * chunkReader)",
}

EXPECTED_NAMES = {
    "0043fde0": "CCylinder__ctor",
    "0043fe20": "CCylinder__ResolveCollisionVFunc02",
    "00440b90": "CDamage__Init",
    "00440c00": "CDamage__FreeOwnedDamageObjects",
    "00440c40": "CDamage__ResetDamageTables",
    "00440c70": "CDamage__LoadDamageTexture",
    "00440eb0": "CDamage__InsertCellEntry",
    "00440f80": "CDamage__RemoveCellEntryByCoords",
    "00441000": "CDamage__CreateTextureBuffer",
}

COMMENT_TOKENS = {
    "0043fde0": ["CCylinder constructor", "radius"],
    "0043fe20": ["CCylinder collision", "contact normal"],
    "00440b90": ["damage0.tga", "damage table"],
    "00440c00": ["owned damage texture"],
    "00440c40": ["damage lookup", "flags"],
    "00440c70": ["texture-info", "mipmap"],
    "00440eb0": ["per-cell", "ret 0x10"],
    "00440f80": ["per-cell", "ret 0xc"],
    "00441000": ["CChunkReader", "texture-info"],
}

COMMON_TAGS = {"static-reaudit", "cylinder-damage-wave346", "retail-binary-evidence"}


def split_tags(value):
    return {tag.strip() for tag in re.split(r"[;,]", value or "") if tag.strip()}


def normalize_address(value):
    value = (value or "").strip().lower()
    if value.startswith("0x"):
        value = value[2:]
    return value.zfill(8)


def read_tsv(path):
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def load_rows(root):
    return {
        "metadata": {normalize_address(row.get("address")): row for row in read_tsv(root / "metadata_final.tsv")},
        "tags": {normalize_address(row.get("address")): row for row in read_tsv(root / "tags_final.tsv")},
        "xrefs": read_tsv(root / "xrefs_final.tsv"),
        "instructions": read_tsv(root / "instructions_final.tsv"),
    }


def build_summary(root=DEFAULT_ROOT):
    rows = load_rows(Path(root))
    failures = []
    metadata_hits = 0
    tag_hits = 0
    xref_hits = 0
    stale_signature_hits = 0
    comment_hits = 0

    for address, expected_name in EXPECTED_NAMES.items():
        metadata = rows["metadata"].get(address)
        if not metadata:
            failures.append(f"missing metadata for {address}")
            continue
        metadata_hits += 1
        actual_name = metadata.get("name", "")
        if actual_name != expected_name:
            failures.append(f"{address} name mismatch: {actual_name} != {expected_name}")
        actual_signature = metadata.get("signature", "")
        if actual_signature != EXPECTED_SIGNATURES[address]:
            failures.append(f"{address} signature mismatch: {actual_signature}")
        if actual_signature.startswith("undefined ") or "param_" in actual_signature or "ctor_like" in actual_name or "VFunc_02_0043fe20" in actual_name:
            stale_signature_hits += 1
            failures.append(f"{address} stale signature/name debt remains: {actual_name} / {actual_signature}")
        comment = metadata.get("comment", "")
        for token in COMMENT_TOKENS[address]:
            if token not in comment:
                failures.append(f"{address} comment missing token: {token}")
        if comment:
            comment_hits += 1

        tag_row = rows["tags"].get(address)
        if not tag_row:
            failures.append(f"missing tag row for {address}")
        else:
            tags = split_tags(tag_row.get("tags", ""))
            if not COMMON_TAGS.issubset(tags):
                failures.append(f"{address} missing common tags: {sorted(COMMON_TAGS - tags)}")
            else:
                tag_hits += 1

    xref_targets = {normalize_address(row.get("target_addr")) for row in rows["xrefs"]}
    for address in EXPECTED_NAMES:
        if address in xref_targets:
            xref_hits += 1
        else:
            failures.append(f"missing xref row for {address}")

    ret_10 = any(
        normalize_address(row.get("function_entry")) == "00440eb0"
        and row.get("mnemonic") == "RET"
        and row.get("operands") == "0x10"
        for row in rows["instructions"]
    )
    ret_0c = any(
        normalize_address(row.get("function_entry")) == "00440f80"
        and row.get("mnemonic") == "RET"
        and row.get("operands") == "0xc"
        for row in rows["instructions"]
    )
    if not ret_10:
        failures.append("missing CDamage__InsertCellEntry ret 0x10 evidence")
    if not ret_0c:
        failures.append("missing CDamage__RemoveCellEntryByCoords ret 0xc evidence")

    return {
        "status": "PASS" if not failures else "FAIL",
        "failures": failures,
        "summary": {
            "targets": len(EXPECTED_NAMES),
            "metadataRows": metadata_hits,
            "tagRows": tag_hits,
            "xrefTargets": xref_hits,
            "instructionRows": len(rows["instructions"]),
            "commentRows": comment_hits,
            "staleSignatureHits": stale_signature_hits,
            "ret10Observed": ret_10,
            "ret0cObserved": ret_0c,
        },
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    summary = build_summary(args.root)
    args.root.mkdir(parents=True, exist_ok=True)
    (args.root / OUTPUT_NAME).write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    if args.check and summary["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
