#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Join frozen source-unit census sites to Generation-10 campaign owners.

This is an atlas join, not a name promoter. It re-maps every verified ``__FILE__``
plate site from the frozen source-unit census onto exact Generation-10 function
body fragments or residual intervals, and publishes priors for all 8,124 Gen10
functions. It does not mutate Gen10 ledgers, invent translation-unit names for
unowned functions, or authorize Ghidra mutation.

Authority split:
  - Specimen ``__FILE__`` plate geometry: frozen source-unit census READY
  - Owner intervals: Generation-10 campaign-functions / campaign-residuals
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
from bisect import bisect_right
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA = "bea.re.source-unit-atlas-join.v1"
STATUS = "MEASURED"
SPECIMEN_SHA256 = "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
IMAGE_BASE = 0x00400000
EXPECTED_GEN10_FUNCTIONS = 8124
EXPECTED_GEN10_RESIDUALS = 6117
EXPECTED_CENSUS_SITES = 1870
EXPECTED_CENSUS_UNITS = 151

SITE_OUT_COLUMNS = (
    "siteKey",
    "siteVa",
    "pathKind",
    "canonicalRelativePath",
    "plateClass",
    "lineValue",
    "firstDirectCallTargetVa",
    "censusPathOwnerKind",
    "censusPathOwnerEntityKey",
    "censusCallOwnerKind",
    "censusCallOwnerEntityKey",
    "censusOwnerBoundaryCrossing",
    "gen10PathOwnerKind",
    "gen10PathOwnerEntityKey",
    "gen10PathOwnerEntryVa",
    "gen10PathOwnerName",
    "gen10PathOwnerCampaignState",
    "gen10CallOwnerKind",
    "gen10CallOwnerEntityKey",
    "gen10CallOwnerEntryVa",
    "gen10CallOwnerName",
    "gen10SamePathAndCallOwner",
    "gen10OwnerBoundaryCrossing",
    "pathOwnerAgreement",
    "callOwnerAgreement",
    "evidenceGrade",
)

PRIOR_OUT_COLUMNS = (
    "functionEntityKey",
    "entryVa",
    "currentName",
    "bodyRangeSetSha256",
    "campaignState",
    "semanticGrade",
    "siteCount",
    "cppSiteCount",
    "headerSiteCount",
    "primaryPlateSiteCount",
    "unwindFreeSiteCount",
    "lineSiteCount",
    "distinctUnitCount",
    "directCppUnitKeys",
    "directCppSiteCount",
    "directHeaderPathKeys",
    "directHeaderSiteCount",
    "firstSiteVa",
    "lastSiteVa",
    "priorDisposition",
    "pathOwnerAgreementCount",
    "pathOwnerDisagreementCount",
    "evidenceGrade",
)

UNIT_OUT_COLUMNS = (
    "unitKey",
    "canonicalRelativePath",
    "basename",
    "censusPrimarySiteCount",
    "gen10MappedSiteCount",
    "gen10FunctionCount",
    "gen10ResidualSiteCount",
    "gen10DirectFunctionEntryVas",
    "gen10PriorDisposition",
)

RESIDUAL_OUT_COLUMNS = (
    "residualEntityKey",
    "startVa",
    "endVa",
    "campaignState",
    "observationState",
    "siteCount",
    "cppSiteCount",
    "headerSiteCount",
    "canonicalRelativePaths",
    "evidenceGrade",
)


def _sha_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _require(cond: bool, msg: str) -> None:
    if not cond:
        raise SystemExit(msg)


def _parse_va(value: str, label: str) -> int:
    _require(bool(re.fullmatch(r"0x[0-9A-Fa-f]{1,8}", value or "")), f"{label} bad VA: {value!r}")
    return int(value, 16)


def _read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8") as handle:
        rows = [line for line in handle if line and not line.startswith("#")]
    return list(csv.DictReader(rows, delimiter="\t"))


def _write_tsv(path: Path, columns: tuple[str, ...], rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        handle.write(f"# {SCHEMA}\n")
        writer = csv.DictWriter(
            handle,
            fieldnames=list(columns),
            delimiter="\t",
            lineterminator="\n",
            extrasaction="ignore",
        )
        writer.writeheader()
        for row in rows:
            writer.writerow({c: row.get(c, "") for c in columns})


def _file_stamp(path: Path) -> dict[str, Any]:
    return {
        "path": str(path.resolve()).replace("\\", "/"),
        "bytes": path.stat().st_size,
        "sha256": _sha_file(path),
    }


def load_gen10_owners(campaign: Path) -> dict[str, Any]:
    functions = _read_tsv(campaign / "campaign-functions.tsv")
    residuals = _read_tsv(campaign / "campaign-residuals.tsv")
    _require(len(functions) == EXPECTED_GEN10_FUNCTIONS, f"gen10 functions {len(functions)}")
    _require(len(residuals) == EXPECTED_GEN10_RESIDUALS, f"gen10 residuals {len(residuals)}")

    intervals: list[dict[str, Any]] = []
    function_by_entry: dict[int, dict[str, str]] = {}
    function_by_key: dict[str, dict[str, str]] = {}

    for row in functions:
        entry = _parse_va(row["entryVa"], "function entry")
        function_by_entry[entry] = row
        function_by_key[row["entityKey"]] = row
        ranges_raw = row.get("bodyRangesRva") or ""
        for item in ranges_raw.split(";"):
            if not item:
                continue
            m = re.fullmatch(r"(0x[0-9A-Fa-f]+)-(0x[0-9A-Fa-f]+)", item)
            _require(m is not None, f"bad body range {item}")
            lo = int(m.group(1), 16) + IMAGE_BASE
            hi = int(m.group(2), 16) + IMAGE_BASE
            _require(lo < hi, f"empty range {item}")
            intervals.append(
                {
                    "lo": lo,
                    "hi": hi,
                    "kind": "FUNCTION",
                    "entityKey": row["entityKey"],
                    "entryVa": row["entryVa"],
                    "name": row.get("currentName") or "",
                    "campaignState": row.get("campaignState") or "",
                }
            )

    residual_by_key: dict[str, dict[str, str]] = {}
    for row in residuals:
        residual_by_key[row["entityKey"]] = row
        lo = _parse_va(row["startVa"], "residual start")
        hi = _parse_va(row["endVa"], "residual end")
        _require(lo < hi, f"bad residual {row['startVa']}")
        intervals.append(
            {
                "lo": lo,
                "hi": hi,
                "kind": "RESIDUAL",
                "entityKey": row["entityKey"],
                "entryVa": row["startVa"],
                "name": "",
                "campaignState": row.get("campaignState") or "",
                "observationState": row.get("observationState") or "",
            }
        )

    intervals.sort(key=lambda x: (x["lo"], x["hi"]))
    # exclusive non-overlap check for integrity
    for i in range(1, len(intervals)):
        prev, cur = intervals[i - 1], intervals[i]
        if cur["lo"] < prev["hi"]:
            raise SystemExit(
                f"overlapping owners {prev['entityKey']}[{prev['lo']:#x},{prev['hi']:#x}) "
                f"vs {cur['entityKey']}[{cur['lo']:#x},{cur['hi']:#x})"
            )

    starts = [iv["lo"] for iv in intervals]
    return {
        "functions": functions,
        "residuals": residuals,
        "intervals": intervals,
        "starts": starts,
        "functionByEntry": function_by_entry,
        "functionByKey": function_by_key,
        "residualByKey": residual_by_key,
    }


def lookup_owner(owners: dict[str, Any], va: int) -> dict[str, Any] | None:
    starts: list[int] = owners["starts"]
    intervals: list[dict[str, Any]] = owners["intervals"]
    i = bisect_right(starts, va) - 1
    if i < 0:
        return None
    iv = intervals[i]
    if iv["lo"] <= va < iv["hi"]:
        return iv
    # rare: sorted by lo only; scan nearby if hole
    for j in range(max(0, i - 2), min(len(intervals), i + 3)):
        cand = intervals[j]
        if cand["lo"] <= va < cand["hi"]:
            return cand
    return None


def classify_agreement(census_key: str, gen10_key: str) -> str:
    if not census_key and not gen10_key:
        return "BOTH_EMPTY"
    if not census_key:
        return "CENSUS_EMPTY"
    if not gen10_key:
        return "GEN10_EMPTY"
    if census_key == gen10_key:
        return "AGREE"
    # same entry VA different range digest still counts as identity drift
    c_va = re.search(r"VA=(0x[0-9a-fA-F]+)", census_key)
    g_va = re.search(r"VA=(0x[0-9a-fA-F]+)", gen10_key)
    if c_va and g_va and c_va.group(1).lower() == g_va.group(1).lower():
        return "AGREE_ENTRY_RANGE_DRIFT"
    return "DISAGREE"


def prior_disposition(site_count: int, cpp_site_count: int) -> str:
    if cpp_site_count > 0:
        return "DIRECT_CPP"
    if site_count > 0:
        return "HEADER_OR_NON_CPP_ONLY"
    return "NO_SITE_EVIDENCE"


def build_join(
    *,
    census_bundle: Path,
    gen10_campaign: Path,
    specimen: Path,
) -> dict[str, Any]:
    ready_path = census_bundle / "source-unit-census.ready.json"
    _require(ready_path.is_file(), f"missing census READY: {ready_path}")
    ready = json.loads(ready_path.read_text(encoding="utf-8"))
    _require(ready.get("schema") == "bea.re.source-unit-census.v1", "census schema drift")
    _require(ready.get("status") == "READY", "census not READY")
    specimen_meta = ready.get("specimen") or {}
    _require(
        (specimen_meta.get("sha256") or "").lower() == SPECIMEN_SHA256,
        "census specimen hash drift",
    )
    _require(
        _sha_file(specimen) == SPECIMEN_SHA256,
        "live specimen hash mismatch",
    )

    sites = _read_tsv(census_bundle / "source-sites.tsv")
    census_units = _read_tsv(census_bundle / "source-units.tsv")
    _require(len(sites) == EXPECTED_CENSUS_SITES, f"census sites {len(sites)}")
    _require(len(census_units) == EXPECTED_CENSUS_UNITS, f"census units {len(census_units)}")

    owners = load_gen10_owners(gen10_campaign)

    atlas_sites: list[dict[str, Any]] = []
    agree = Counter()
    owner_kinds = Counter()
    residual_site_hits: dict[str, list[dict[str, Any]]] = defaultdict(list)
    function_site_hits: dict[str, list[dict[str, Any]]] = defaultdict(list)

    for site in sites:
        site_va = _parse_va(site["siteVa"], "siteVa")
        call_target = site.get("firstDirectCallTargetVa") or ""
        # callOwner is the owner of the CALL INSTRUCTION (firstDirectCallVa),
        # not the callee entry. Census samePathAndCallOwnerSites=1869 depends on this.
        call_site_va_raw = site.get("firstDirectCallVa") or ""
        path_owner = lookup_owner(owners, site_va)
        call_owner = None
        if call_site_va_raw and call_site_va_raw not in {"", "0x0", "0x00000000"}:
            try:
                call_owner = lookup_owner(owners, _parse_va(call_site_va_raw, "call site"))
            except SystemExit:
                call_owner = None

        census_path_key = site.get("pathOwnerEntityKey") or ""
        census_call_key = site.get("callOwnerEntityKey") or ""
        gen10_path_key = (path_owner or {}).get("entityKey") or ""
        gen10_call_key = (call_owner or {}).get("entityKey") or ""

        path_agree = classify_agreement(census_path_key, gen10_path_key)
        call_agree = classify_agreement(census_call_key, gen10_call_key)
        agree[f"path:{path_agree}"] += 1
        agree[f"call:{call_agree}"] += 1

        same_pc = bool(
            gen10_path_key
            and gen10_call_key
            and gen10_path_key == gen10_call_key
        )
        crossing = bool(
            gen10_path_key
            and gen10_call_key
            and gen10_path_key != gen10_call_key
        )
        if path_owner:
            owner_kinds[f"path:{path_owner['kind']}"] += 1
        else:
            owner_kinds["path:NONE"] += 1
        if call_owner:
            owner_kinds[f"call:{call_owner['kind']}"] += 1
        else:
            owner_kinds["call:NONE"] += 1

        row = {
            "siteKey": site.get("siteKey") or "",
            "siteVa": site["siteVa"],
            "pathKind": site.get("pathKind") or "",
            "canonicalRelativePath": site.get("canonicalRelativePath") or "",
            "plateClass": site.get("plateClass") or "",
            "lineValue": site.get("lineValue") or "",
            "firstDirectCallTargetVa": call_target,
            "censusPathOwnerKind": site.get("pathOwnerKind") or "",
            "censusPathOwnerEntityKey": census_path_key,
            "censusCallOwnerKind": site.get("callOwnerKind") or "",
            "censusCallOwnerEntityKey": census_call_key,
            "censusOwnerBoundaryCrossing": site.get("ownerBoundaryCrossing") or "",
            "gen10PathOwnerKind": (path_owner or {}).get("kind") or "NONE",
            "gen10PathOwnerEntityKey": gen10_path_key,
            "gen10PathOwnerEntryVa": (path_owner or {}).get("entryVa") or "",
            "gen10PathOwnerName": (path_owner or {}).get("name") or "",
            "gen10PathOwnerCampaignState": (path_owner or {}).get("campaignState") or "",
            "gen10CallOwnerKind": (call_owner or {}).get("kind") or "NONE",
            "gen10CallOwnerEntityKey": gen10_call_key,
            "gen10CallOwnerEntryVa": (call_owner or {}).get("entryVa") or "",
            "gen10CallOwnerName": (call_owner or {}).get("name") or "",
            "gen10SamePathAndCallOwner": "True" if same_pc else "False",
            "gen10OwnerBoundaryCrossing": "True" if crossing else "False",
            "pathOwnerAgreement": path_agree,
            "callOwnerAgreement": call_agree,
            "evidenceGrade": site.get("evidenceGrade") or "",
        }
        atlas_sites.append(row)

        if path_owner and path_owner["kind"] == "FUNCTION":
            function_site_hits[path_owner["entityKey"]].append(row)
        elif path_owner and path_owner["kind"] == "RESIDUAL":
            residual_site_hits[path_owner["entityKey"]].append(row)

    def _is_primary_plate(plate_class: str) -> bool:
        pc = (plate_class or "").upper()
        return "PRIMARY" in pc

    def _is_unwind_plate(hit: dict[str, Any]) -> bool:
        pc = (hit.get("plateClass") or "").upper()
        if "UNWIND" in pc:
            return True
        return (hit.get("firstDirectCallTargetVa") or "").lower() == "0x00449d40"

    # Function priors for all Gen10 functions.
    # DIRECT_CPP matches census anchor policy: PRIMARY plate + CPP path kind.
    priors: list[dict[str, Any]] = []
    disposition = Counter()
    for fn in owners["functions"]:
        ek = fn["entityKey"]
        hits = function_site_hits.get(ek, [])
        cpp = [h for h in hits if h["pathKind"] == "CPP"]
        hdr = [h for h in hits if h["pathKind"] == "HEADER"]
        primary = [h for h in hits if _is_primary_plate(h.get("plateClass") or "")]
        primary_cpp = [h for h in primary if h["pathKind"] == "CPP"]
        unwind = [h for h in hits if _is_unwind_plate(h)]
        line_sites = [h for h in hits if (h.get("lineValue") or "").strip() not in {"", "0", "NONE"}]
        cpp_unit_keys = sorted({h["canonicalRelativePath"] for h in primary_cpp if h["canonicalRelativePath"]})
        header_keys = sorted({h["canonicalRelativePath"] for h in hdr if h["canonicalRelativePath"]})
        agree_n = sum(1 for h in hits if h["pathOwnerAgreement"] in {"AGREE", "AGREE_ENTRY_RANGE_DRIFT"})
        disagree_n = sum(1 for h in hits if h["pathOwnerAgreement"] == "DISAGREE")
        # Anchor disposition uses primary-CPP only (census DIRECT_CPP = 368 under Gen5).
        if primary_cpp:
            disp = "DIRECT_CPP"
        elif hits:
            disp = "HEADER_OR_NON_CPP_ONLY"
        else:
            disp = "NO_SITE_EVIDENCE"
        disposition[disp] += 1
        site_vas = sorted(h["siteVa"] for h in hits)
        priors.append(
            {
                "functionEntityKey": ek,
                "entryVa": fn["entryVa"],
                "currentName": fn.get("currentName") or "",
                "bodyRangeSetSha256": fn.get("bodyRangeSetSha256") or "",
                "campaignState": fn.get("campaignState") or "",
                "semanticGrade": fn.get("semanticGrade") or "",
                "siteCount": len(hits),
                "cppSiteCount": len(cpp),
                "headerSiteCount": len(hdr),
                "primaryPlateSiteCount": len(primary),
                "unwindFreeSiteCount": len(unwind),
                "lineSiteCount": len(line_sites),
                "distinctUnitCount": len(cpp_unit_keys),
                "directCppUnitKeys": ";".join(cpp_unit_keys),
                "directCppSiteCount": len(primary_cpp),
                "directHeaderPathKeys": ";".join(header_keys),
                "directHeaderSiteCount": len(hdr),
                "firstSiteVa": site_vas[0] if site_vas else "",
                "lastSiteVa": site_vas[-1] if site_vas else "",
                "priorDisposition": disp,
                "pathOwnerAgreementCount": agree_n,
                "pathOwnerDisagreementCount": disagree_n,
                "evidenceGrade": "DIRECT_SITE" if hits else "NONE",
            }
        )

    # Unit coverage (CPP sites only), keyed from frozen census unit table.
    unit_rows: list[dict[str, Any]] = []
    unit_func_entries: dict[str, set[str]] = defaultdict(set)
    unit_primary_func_entries: dict[str, set[str]] = defaultdict(set)
    unit_site_counts: dict[str, int] = Counter()
    unit_residual_sites: dict[str, int] = Counter()
    for site in atlas_sites:
        rel = site["canonicalRelativePath"]
        if not rel or site["pathKind"] != "CPP":
            continue
        unit_site_counts[rel] += 1
        if site["gen10PathOwnerKind"] == "FUNCTION" and site["gen10PathOwnerEntryVa"]:
            unit_func_entries[rel].add(site["gen10PathOwnerEntryVa"])
            if _is_primary_plate(site.get("plateClass") or ""):
                unit_primary_func_entries[rel].add(site["gen10PathOwnerEntryVa"])
        if site["gen10PathOwnerKind"] == "RESIDUAL":
            unit_residual_sites[rel] += 1

    unit_by_rel = {
        (u.get("canonicalRelativePath") or ""): u
        for u in census_units
        if u.get("canonicalRelativePath")
    }
    for rel, u in sorted(unit_by_rel.items()):
        entries = sorted(unit_func_entries.get(rel, set()))
        primary_entries = sorted(unit_primary_func_entries.get(rel, set()))
        unit_rows.append(
            {
                "unitKey": u.get("unitKey") or "",
                "canonicalRelativePath": rel,
                "basename": u.get("basename") or Path(rel).name,
                "censusPrimarySiteCount": u.get("primarySiteCount") or "",
                "gen10MappedSiteCount": unit_site_counts.get(rel, 0),
                "gen10FunctionCount": len(entries),
                "gen10ResidualSiteCount": unit_residual_sites.get(rel, 0),
                "gen10DirectFunctionEntryVas": ";".join(primary_entries if primary_entries else entries),
                "gen10PriorDisposition": (
                    "HAS_GEN10_FUNCTIONS" if entries else (
                        "RESIDUAL_ONLY" if unit_residual_sites.get(rel, 0) else "NO_GEN10_OWNER"
                    )
                ),
            }
        )

    residual_rows: list[dict[str, Any]] = []
    for ek, hits in sorted(residual_site_hits.items()):
        r = owners["residualByKey"].get(ek, {})
        paths = sorted({h["canonicalRelativePath"] for h in hits if h["canonicalRelativePath"]})
        residual_rows.append(
            {
                "residualEntityKey": ek,
                "startVa": r.get("startVa") or (hits[0]["gen10PathOwnerEntryVa"] if hits else ""),
                "endVa": r.get("endVa") or "",
                "campaignState": r.get("campaignState") or "",
                "observationState": r.get("observationState") or "",
                "siteCount": len(hits),
                "cppSiteCount": sum(1 for h in hits if h["pathKind"] == "CPP"),
                "headerSiteCount": sum(1 for h in hits if h["pathKind"] == "HEADER"),
                "canonicalRelativePaths": ";".join(paths),
                "evidenceGrade": "SITE_HIT",
            }
        )

    # Interior / residual site inventory (the 25 path-residual sites etc.)
    residual_path_sites = [s for s in atlas_sites if s["gen10PathOwnerKind"] == "RESIDUAL"]
    none_path_sites = [s for s in atlas_sites if s["gen10PathOwnerKind"] == "NONE"]
    crossings = [s for s in atlas_sites if s["gen10OwnerBoundaryCrossing"] == "True"]
    disagree_path = [s for s in atlas_sites if s["pathOwnerAgreement"] == "DISAGREE"]
    range_drift = [s for s in atlas_sites if s["pathOwnerAgreement"] == "AGREE_ENTRY_RANGE_DRIFT"]

    direct_cpp_functions = sum(1 for p in priors if p["priorDisposition"] == "DIRECT_CPP")

    result = {
        "schema": SCHEMA,
        "status": STATUS,
        "generatedAtUtc": datetime.now(timezone.utc).isoformat(),
        "specimen_sha256": SPECIMEN_SHA256,
        "censusBundle": str(census_bundle).replace("\\", "/"),
        "gen10Campaign": str(gen10_campaign).replace("\\", "/"),
        "counts": {
            "censusSites": len(sites),
            "censusUnits": len(census_units),
            "gen10Functions": len(owners["functions"]),
            "gen10Residuals": len(owners["residuals"]),
            "atlasSites": len(atlas_sites),
            "atlasUnits": len(unit_rows),
            "functionsWithAnySite": sum(1 for p in priors if int(p["siteCount"]) > 0),
            "functionsWithDirectCpp": direct_cpp_functions,
            "functionsWithNoSiteEvidence": sum(1 for p in priors if p["priorDisposition"] == "NO_SITE_EVIDENCE"),
            "residualsWithSites": len(residual_rows),
            "gen10PathResidualSites": len(residual_path_sites),
            "gen10PathNoneSites": len(none_path_sites),
            "gen10PathFunctionSites": sum(1 for s in atlas_sites if s["gen10PathOwnerKind"] == "FUNCTION"),
            "gen10SamePathAndCallOwnerSites": sum(
                1 for s in atlas_sites if s["gen10SamePathAndCallOwner"] == "True"
            ),
            "gen10OwnerBoundaryCrossings": len(crossings),
            "pathOwnerAgree": agree.get("path:AGREE", 0),
            "pathOwnerAgreeEntryRangeDrift": agree.get("path:AGREE_ENTRY_RANGE_DRIFT", 0),
            "pathOwnerDisagree": agree.get("path:DISAGREE", 0),
            "pathOwnerGen10Empty": agree.get("path:GEN10_EMPTY", 0),
            "callOwnerAgree": agree.get("call:AGREE", 0),
            "callOwnerAgreeEntryRangeDrift": agree.get("call:AGREE_ENTRY_RANGE_DRIFT", 0),
            "callOwnerDisagree": agree.get("call:DISAGREE", 0),
            "callOwnerGen10Empty": agree.get("call:GEN10_EMPTY", 0),
            "priorDispositions": dict(disposition),
            "ownerKindHits": dict(owner_kinds),
            "agreementTallies": dict(agree),
        },
        "claimBoundary": [
            "Atlas join remaps plate sites onto Gen10 owners; it does not name unowned functions.",
            "DIRECT_CPP is plate evidence inside a Gen10 function body, not proof the whole function is that TU.",
            "Header paths are context only.",
            "Closed-span / link-order priors from the Gen5 census are not re-promoted as Gen10 names.",
            "No Gen10 ledger mutation; no Ghidra mutation.",
        ],
        "disagreementSamples": [
            {
                "siteVa": s["siteVa"],
                "path": s["canonicalRelativePath"],
                "census": s["censusPathOwnerEntityKey"][:80],
                "gen10": s["gen10PathOwnerEntityKey"][:80],
                "gen10Kind": s["gen10PathOwnerKind"],
            }
            for s in disagree_path[:20]
        ],
        "rangeDriftSamples": [
            {
                "siteVa": s["siteVa"],
                "entryHint": s["gen10PathOwnerEntryVa"],
                "censusKeyTail": s["censusPathOwnerEntityKey"][-40:],
                "gen10KeyTail": s["gen10PathOwnerEntityKey"][-40:],
            }
            for s in range_drift[:10]
        ],
        "crossingSamples": [
            {
                "siteVa": s["siteVa"],
                "pathOwner": s["gen10PathOwnerEntryVa"],
                "callOwner": s["gen10CallOwnerEntryVa"],
                "path": s["canonicalRelativePath"],
            }
            for s in crossings[:10]
        ],
        "atlasSites": atlas_sites,
        "functionPriors": priors,
        "units": unit_rows,
        "residuals": residual_rows,
    }
    return result


def write_plate(result: dict[str, Any], out_dir: Path, *, census_bundle: Path, gen10_campaign: Path, specimen: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    _write_tsv(out_dir / "atlas-sites.tsv", SITE_OUT_COLUMNS, result["atlasSites"])
    _write_tsv(out_dir / "atlas-function-priors.tsv", PRIOR_OUT_COLUMNS, result["functionPriors"])
    _write_tsv(out_dir / "atlas-units.tsv", UNIT_OUT_COLUMNS, result["units"])
    _write_tsv(out_dir / "atlas-residuals.tsv", RESIDUAL_OUT_COLUMNS, result["residuals"])

    summary = {
        "schema": SCHEMA,
        "status": STATUS,
        "plate": str(out_dir).replace("\\", "/"),
        "generatedAtUtc": result["generatedAtUtc"],
        "specimen_sha256": result["specimen_sha256"],
        "censusBundle": result["censusBundle"],
        "gen10Campaign": result["gen10Campaign"],
        "counts": result["counts"],
        "claimBoundary": result["claimBoundary"],
        "disagreementSamples": result["disagreementSamples"],
        "rangeDriftSamples": result["rangeDriftSamples"],
        "crossingSamples": result["crossingSamples"],
        "claims": [
            f"Joined {result['counts']['censusSites']} frozen census plate sites onto Gen10 owners "
            f"({result['counts']['gen10Functions']} functions + {result['counts']['gen10Residuals']} residuals).",
            f"Gen10 path-owner agreement with census entity keys: "
            f"AGREE={result['counts']['pathOwnerAgree']}, "
            f"AGREE_ENTRY_RANGE_DRIFT={result['counts']['pathOwnerAgreeEntryRangeDrift']}, "
            f"DISAGREE={result['counts']['pathOwnerDisagree']}, "
            f"GEN10_EMPTY={result['counts']['pathOwnerGen10Empty']}.",
            f"Functions with DIRECT_CPP plate hits: {result['counts']['functionsWithDirectCpp']}; "
            f"with any site: {result['counts']['functionsWithAnySite']}; "
            f"with no site evidence: {result['counts']['functionsWithNoSiteEvidence']}.",
            f"Residuals hosting plate sites under Gen10 intervals: {result['counts']['residualsWithSites']} "
            f"({result['counts']['gen10PathResidualSites']} sites).",
            f"Gen10 path/call owner boundary crossings: {result['counts']['gen10OwnerBoundaryCrossings']}.",
            "No names, signatures, contracts, or REBUILD_READY promoted from this join.",
        ],
        "non_claims": result["claimBoundary"]
        + [
            "Does not mutate Gen10/Gen11/Gen12 ledgers.",
            "Does not re-derive plate geometry (authority remains frozen census READY).",
            "Stuart source-line calibration against pinned GPL tree is a separate instrument.",
        ],
        "artifacts": [
            "atlas-sites.tsv",
            "atlas-function-priors.tsv",
            "atlas-units.tsv",
            "atlas-residuals.tsv",
            "SUMMARY.json",
            "INTEGRITY.json",
            "README.md",
        ],
    }
    (out_dir / "SUMMARY.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    # Capture Gen10 ledger stamps before any plate write completes; the join
    # never opens campaign paths for write, so these stamps are the mutation gate.
    gen10_fn_stamp = _file_stamp(gen10_campaign / "campaign-functions.tsv")
    gen10_res_stamp = _file_stamp(gen10_campaign / "campaign-residuals.tsv")
    gen10_ready_stamp = _file_stamp(gen10_campaign / "campaign.ready.json")
    gen10_ready = json.loads((gen10_campaign / "campaign.ready.json").read_text(encoding="utf-8"))
    ready_outputs = gen10_ready.get("outputs") or {}
    ready_fn_node = ready_outputs.get("campaign-functions.tsv") if isinstance(ready_outputs, dict) else None
    ready_res_node = ready_outputs.get("campaign-residuals.tsv") if isinstance(ready_outputs, dict) else None
    ready_fn_sha = (
        ((ready_fn_node or {}).get("sha256") or "").lower() or None
        if isinstance(ready_fn_node, dict)
        else None
    )
    ready_res_sha = (
        ((ready_res_node or {}).get("sha256") or "").lower() or None
        if isinstance(ready_res_node, dict)
        else None
    )
    ledger_fn_matches_ready = (
        ready_fn_sha is not None and gen10_fn_stamp["sha256"].lower() == ready_fn_sha
    )
    ledger_res_matches_ready = (
        ready_res_sha is not None and gen10_res_stamp["sha256"].lower() == ready_res_sha
    )
    integrity = {
        "schema": "bea.re.source-unit-atlas-join.integrity.v1",
        "whenUtc": datetime.now(timezone.utc).isoformat(),
        "checks": {
            "census_sites_1870": result["counts"]["censusSites"] == EXPECTED_CENSUS_SITES,
            "census_units_151": result["counts"]["censusUnits"] == EXPECTED_CENSUS_UNITS,
            "gen10_functions_8124": result["counts"]["gen10Functions"] == EXPECTED_GEN10_FUNCTIONS,
            "gen10_residuals_6117": result["counts"]["gen10Residuals"] == EXPECTED_GEN10_RESIDUALS,
            "atlas_sites_1870": result["counts"]["atlasSites"] == EXPECTED_CENSUS_SITES,
            "priors_8124": len(result["functionPriors"]) == EXPECTED_GEN10_FUNCTIONS,
            "specimen_pristine": result["specimen_sha256"] == SPECIMEN_SHA256,
            "path_owner_agree_1870": result["counts"]["pathOwnerAgree"] == EXPECTED_CENSUS_SITES,
            "call_owner_agree_1870": result["counts"]["callOwnerAgree"] == EXPECTED_CENSUS_SITES,
            "direct_cpp_368": result["counts"]["functionsWithDirectCpp"] == 368,
            "boundary_crossings_1": result["counts"]["gen10OwnerBoundaryCrossings"] == 1,
            "gen10_functions_ledger_matches_ready": ledger_fn_matches_ready,
            "gen10_residuals_ledger_matches_ready": ledger_res_matches_ready,
            "no_ledger_mutation": ledger_fn_matches_ready and ledger_res_matches_ready,
        },
        "sources": {
            "censusReady": _file_stamp(census_bundle / "source-unit-census.ready.json"),
            "censusSites": _file_stamp(census_bundle / "source-sites.tsv"),
            "censusUnits": _file_stamp(census_bundle / "source-units.tsv"),
            "gen10Ready": gen10_ready_stamp,
            "gen10Functions": gen10_fn_stamp,
            "gen10Residuals": gen10_res_stamp,
            "specimen": _file_stamp(specimen),
            "atlasSites": _file_stamp(out_dir / "atlas-sites.tsv"),
            "atlasPriors": _file_stamp(out_dir / "atlas-function-priors.tsv"),
            "summary": _file_stamp(out_dir / "SUMMARY.json"),
        },
        "falsifier": [
            "Re-run tools/re_source_unit_atlas_join.py: counts and agreement tallies must match",
            "Any atlas site VA outside all Gen10 function fragments and residuals without GEN10_EMPTY grade",
            "function prior row count != 8124",
            "campaign-functions.tsv or campaign-residuals.tsv sha256 diverges from campaign.ready.json",
            "Ledger mutation of Gen10 campaign files",
        ],
    }
    (out_dir / "INTEGRITY.json").write_text(json.dumps(integrity, indent=2) + "\n", encoding="utf-8")
    # re-bind summary stamp after writing integrity is not required for summary; re-stamp summary in integrity after both exist
    integrity["sources"]["summary"] = _file_stamp(out_dir / "SUMMARY.json")
    integrity["sources"]["integritySelf"] = {
        "note": "self hash omitted; verify by re-run",
    }
    (out_dir / "INTEGRITY.json").write_text(json.dumps(integrity, indent=2) + "\n", encoding="utf-8")

    (out_dir / "README.md").write_text(
        f"""# Source-unit atlas join → Generation 10

Status: **MEASURED**
Schema: `{SCHEMA}`
Date: {result['generatedAtUtc'][:10]}

> **What this settles.** Every frozen census ``__FILE__`` plate site is remapped onto exact Gen10 function body fragments or residual intervals. Publishes priors for all **8124** Gen10 functions. **Does not promote names** or mutate ledgers.

## Headline counts

| Metric | Value |
|--------|------:|
| Census sites joined | {result['counts']['censusSites']} |
| Path owner AGREE | {result['counts']['pathOwnerAgree']} |
| Path owner AGREE_ENTRY_RANGE_DRIFT | {result['counts']['pathOwnerAgreeEntryRangeDrift']} |
| Path owner DISAGREE | {result['counts']['pathOwnerDisagree']} |
| Path owner GEN10_EMPTY | {result['counts']['pathOwnerGen10Empty']} |
| Gen10 functions with DIRECT_CPP | {result['counts']['functionsWithDirectCpp']} |
| Gen10 functions with any site | {result['counts']['functionsWithAnySite']} |
| Gen10 functions with no site evidence | {result['counts']['functionsWithNoSiteEvidence']} |
| Residuals with plate sites | {result['counts']['residualsWithSites']} |
| Gen10 path/call boundary crossings | {result['counts']['gen10OwnerBoundaryCrossings']} |

## Artifacts

- `atlas-sites.tsv` — per-site Gen5 census owner vs Gen10 owner
- `atlas-function-priors.tsv` — all 8124 Gen10 functions
- `atlas-units.tsv` — 151 CPP units under Gen10 ownership
- `atlas-residuals.tsv` — residuals that host plate sites

## Non-claims

- Not a name assignment for the 7k+ functions without plates
- Not REBUILD_READY / not contract promotion
- Not Gen10 mutation
""",
        encoding="utf-8",
    )


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)

    b = sub.add_parser("build", help="build Gen10 source-unit atlas join plate")
    b.add_argument(
        "--census-bundle",
        type=Path,
        default=Path("local-lab/source-unit-census-v1-ready"),
    )
    b.add_argument(
        "--gen10-campaign",
        type=Path,
        default=Path(
            "local-lab/ttd-call-context-level521-impact-generation10-20260804-v1/"
            "generation-10-ttd-call-context-observation-v2"
        ),
    )
    b.add_argument(
        "--specimen",
        type=Path,
        default=Path("local-lab/safe-copy-bea-pristine/BEA.exe.original.backup"),
    )
    b.add_argument(
        "--out",
        type=Path,
        default=Path("local-lab/source-unit-atlas-join-gen10-20260805-v1"),
    )

    v = sub.add_parser("verify", help="re-run join and compare SUMMARY counts")
    v.add_argument("--plate", type=Path, required=True)
    v.add_argument(
        "--census-bundle",
        type=Path,
        default=Path("local-lab/source-unit-census-v1-ready"),
    )
    v.add_argument(
        "--gen10-campaign",
        type=Path,
        default=Path(
            "local-lab/ttd-call-context-level521-impact-generation10-20260804-v1/"
            "generation-10-ttd-call-context-observation-v2"
        ),
    )
    v.add_argument(
        "--specimen",
        type=Path,
        default=Path("local-lab/safe-copy-bea-pristine/BEA.exe.original.backup"),
    )

    args = p.parse_args(argv)
    if args.cmd == "build":
        result = build_join(
            census_bundle=args.census_bundle,
            gen10_campaign=args.gen10_campaign,
            specimen=args.specimen,
        )
        write_plate(
            result,
            args.out,
            census_bundle=args.census_bundle,
            gen10_campaign=args.gen10_campaign,
            specimen=args.specimen,
        )
        print(json.dumps({"status": "OK", "counts": result["counts"]}, indent=2))
        print("SOURCE_UNIT_ATLAS_JOIN_OK")
        return 0

    if args.cmd == "verify":
        summary = json.loads((args.plate / "SUMMARY.json").read_text(encoding="utf-8"))
        result = build_join(
            census_bundle=args.census_bundle,
            gen10_campaign=args.gen10_campaign,
            specimen=args.specimen,
        )
        for key in (
            "censusSites",
            "gen10Functions",
            "functionsWithDirectCpp",
            "pathOwnerAgree",
            "pathOwnerDisagree",
            "residualsWithSites",
        ):
            if summary["counts"].get(key) != result["counts"].get(key):
                raise SystemExit(
                    f"count drift {key}: plate={summary['counts'].get(key)} "
                    f"rederived={result['counts'].get(key)}"
                )
        print(json.dumps({"status": "VERIFIED", "counts": result["counts"]}, indent=2))
        print("SOURCE_UNIT_ATLAS_JOIN_VERIFIED")
        return 0

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
