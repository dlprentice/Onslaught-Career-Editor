#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Verify the portable five-function fragment scratch package.

This verifier is read-only except for its new JSON receipt.  It never opens or
mutates a Ghidra project and never authorizes a live or tracked project write.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
from typing import Any


class AuthorityError(ValueError):
    pass


def require(value: bool, message: str) -> None:
    if not value:
        raise AuthorityError(message)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def stamp(root: Path, relative: str) -> dict[str, Any]:
    path = root / relative
    require(path.is_file(), f"missing artifact: {relative}")
    return {
        "path": relative.replace("\\", "/"),
        "bytes": path.stat().st_size,
        "sha256": sha256_file(path),
    }


def require_stamp(
    root: Path, relative: str, *, size: int | None = None, sha256: str | None = None
) -> dict[str, Any]:
    actual = stamp(root, relative)
    if size is not None:
        require(actual["bytes"] == size, f"byte drift: {relative}")
    if sha256 is not None:
        require(actual["sha256"] == sha256, f"hash drift: {relative}")
    return actual


def read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as stream:
        return json.load(stream)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


def read_metrics(path: Path) -> dict[str, str]:
    rows = read_tsv(path)
    result: dict[str, str] = {}
    for row in rows:
        require(row["metric"] not in result, f"duplicate metric: {row['metric']}")
        result[row["metric"]] = row["value"]
    return result


def normalized_receipt(value: dict[str, Any]) -> dict[str, Any]:
    result = dict(value)
    result.pop("completedAtUtc", None)
    return result


RETAIL_SHA256 = "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
RETAIL_MD5 = "3b456964020070efe696d2cc09464a55"
MANIFEST_SHA256 = "c44e3671f1b5a28f7e214c572be2efd21046275cf4d97d7bdbac207ba15a87f0"
MUTATOR_SHA256 = "fe845a9df094eff4a1d9b36c9d4a6b141f049356499016a20a673071d492ec4c"
STATIC_TOOL_SHA256 = "a9e5f02e8dddfa64f50aca7821e3afed483de6c349e6ad0ada06ba77e59020ed"
BASE_FUNCTIONS_SHA256 = "c3942b9e340cef71b731290b845843697af5c53204449c51949b779e896272d6"
BASE_PROGRAM_SHA256 = "3e51ce1d5e926c632869b2058c9d89e91f48345a329a724ea9520570bd91212d"
POST_FUNCTIONS_SHA256 = "d2ff1e8e7bd91454fff9822fb7ecc8e624525fa5c6cbc9dcfe06f4e0212b750d"
POST_PROGRAM_SHA256 = "b389487a65d6271329703c9e3ec9186b7261aa871a154c31179322780e1c132e"

TARGETS = {
    "0x00462640": {
        "name": "CFEPMain__Process",
        "changed": {"bodyBytes", "bodyMax", "bodyDigest", "instrCount"},
        "bodyBytes": "1316",
        "bodyRanges": "1",
        "bodyMax": "0x00462b63",
        "bodyDigest": "77418be8ef8eafba7b38b2ee86be8fe7c7e5619f30bebbfcf58903f377b40b1f",
        "instrCount": "356",
    },
    "0x0046ff10": {
        "name": "CGame__HandleEvent",
        "changed": {"bodyBytes", "bodyRanges", "bodyDigest", "instrCount"},
        "bodyBytes": "467",
        "bodyRanges": "2",
        "bodyMax": "0x004700f5",
        "bodyDigest": "6fbdedf7f4cd6e2fc354881e94f045c07e4359ddbcb43dbbdb039d90b90db8a5",
        "instrCount": "142",
    },
    "0x00482590": {
        "name": "CHud__RenderTargetIndicatorOverlay",
        "changed": {"bodyBytes", "bodyRanges", "bodyDigest", "instrCount"},
        "bodyBytes": "3957",
        "bodyRanges": "1",
        "bodyMax": "0x00483504",
        "bodyDigest": "2d66025c2f9cc693ac8f68dc6883d205a773fb4f22dfa26c0700b90a8b5b624e",
        "instrCount": "951",
    },
    "0x004be420": {
        "name": "CExplosionInitThing__SelectNextPathStepDirection",
        "changed": {"bodyBytes", "bodyRanges", "bodyDigest", "instrCount"},
        "bodyBytes": "1324",
        "bodyRanges": "1",
        "bodyMax": "0x004be94b",
        "bodyDigest": "b8c46940dab13abaf529bac99617ebf972a856091711ab8b07c709102a3a4807",
        "instrCount": "345",
    },
    "0x00559410": {
        "name": "CDXTexture__CreateMipmaps",
        "changed": {"bodyBytes", "bodyRanges", "bodyDigest", "instrCount"},
        "bodyBytes": "1882",
        "bodyRanges": "1",
        "bodyMax": "0x00559b69",
        "bodyDigest": "fa0e7f1112396e55ecc7d15d2b92e2a6bf606998eb59589e691caac24cf7e82c",
        "instrCount": "565",
    },
}


def verify_static(root: Path) -> dict[str, Any]:
    expected = {
        "fragment-manifest.tsv": (2878, MANIFEST_SHA256),
        "static-proof.tsv": (
            None,
            "da277134010ee1f31d5fcbb63c31377d44fd1665c02873673b8d38cb7158edea",
        ),
        "runtime-coverage.tsv": (
            None,
            "82d946021da498217e5133ee3eb529a1b942e2428cb749914e58ae8ffff12d71",
        ),
        "result.ready.json": (
            None,
            "330ffc113f451985f5aa24422efdc7c2227e179585ee2000bce56b5f8e8cc7bc",
        ),
    }
    artifacts: list[dict[str, Any]] = []
    for name, (size, digest) in expected.items():
        left = require_stamp(root, f"static/final-a/{name}", size=size, sha256=digest)
        right = require_stamp(root, f"static/final-b/{name}", size=size, sha256=digest)
        require(left["sha256"] == right["sha256"], f"static replicas differ: {name}")
        artifacts.extend((left, right))

    manifest = read_tsv(root / "static/final-a/fragment-manifest.tsv")
    require(len(manifest) == 5, "manifest target count")
    require({row["entry"] for row in manifest} == set(TARGETS), "manifest target set")
    require(sum(int(row["repair_bytes"]) for row in manifest) == 1258, "repair byte total")
    require(sum(int(row["repair_instruction_count"]) for row in manifest) == 325,
            "repair instruction total")
    fep = manifest[0]
    require(fep["repair_ranges"] == "0x0046282b-0x00462b64", "FEP code boundary")
    require(fep["repair_bytes"] == "825", "FEP code byte count")

    ready = read_json(root / "static/final-a/result.ready.json")
    require(ready["status"] == "READY_FOR_SCRATCH_ONLY", "static status")
    require(ready["policy"] == "LIVE_FORBIDDEN", "static policy")
    require(ready["currentGhidra"] == {
        "db": "db.18613.gbf", "functions": 8280, "ownedBytes": 1794212, "ranges": 8400
    }, "static current Ghidra state")
    require(ready["repair"]["addedBodyBytes"] == 1258, "static repair gain")
    require(ready["repair"]["postOwnedBytes"] == 1795470, "static post ownership")
    require(ready["repair"]["postBodyRangeCount"] == 8396, "static post range count")
    require(ready["repair"]["postFunctionCount"] == 8280, "static post function count")
    require(ready["demo"] == {
        "normalizedEqual": 5, "uniqueWithinMappedOwnerBracket": 5
    }, "demo twin proof")
    return {"artifacts": artifacts, "manifestRows": len(manifest)}


def rows_by_address(path: Path) -> tuple[list[str], dict[str, dict[str, str]]]:
    with path.open("r", encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream, delimiter="\t")
        require(reader.fieldnames is not None, f"missing TSV header: {path.name}")
        rows = list(reader)
    result = {row["address"]: row for row in rows}
    require(len(result) == len(rows), f"duplicate address: {path.name}")
    return list(reader.fieldnames), result


def verify_inventory_delta(root: Path) -> dict[str, Any]:
    base_functions = require_stamp(
        root, "inventories/base/functions.tsv", sha256=BASE_FUNCTIONS_SHA256
    )
    base_program = require_stamp(
        root, "inventories/base/program.tsv", sha256=BASE_PROGRAM_SHA256
    )
    post_artifacts: list[dict[str, Any]] = []
    for replica in ("final-replica-a", "final-replica-b"):
        post_artifacts.append(require_stamp(
            root, f"inventories/{replica}/functions.tsv", sha256=POST_FUNCTIONS_SHA256
        ))
        post_artifacts.append(require_stamp(
            root, f"inventories/{replica}/program.tsv", sha256=POST_PROGRAM_SHA256
        ))
    restore_artifacts: list[dict[str, Any]] = []
    for control in ("control-one-restored", "control-all-restored"):
        restore_artifacts.append(require_stamp(
            root, f"inventories/{control}/functions.tsv", sha256=BASE_FUNCTIONS_SHA256
        ))
        restore_artifacts.append(require_stamp(
            root, f"inventories/{control}/program.tsv", sha256=BASE_PROGRAM_SHA256
        ))

    fields, before = rows_by_address(root / "inventories/base/functions.tsv")
    post_fields, after = rows_by_address(
        root / "inventories/final-replica-a/functions.tsv"
    )
    require(fields == post_fields, "function inventory header drift")
    require(len(before) == len(after) == 8280, "function inventory cardinality")
    require(before.keys() == after.keys(), "function entry set drift")
    changed: dict[str, set[str]] = {}
    for address, pre in before.items():
        post = after[address]
        columns = {field for field in fields if pre[field] != post[field]}
        if columns:
            changed[address] = columns
    require(set(changed) == set(TARGETS), f"unexpected changed function rows: {changed}")
    for address, expected in TARGETS.items():
        require(changed[address] == expected["changed"],
                f"changed columns drift at {address}: {changed[address]}")
        require(after[address]["name"] == expected["name"], f"name drift at {address}")
        for field in ("bodyBytes", "bodyRanges", "bodyMax", "bodyDigest", "instrCount"):
            require(after[address][field] == expected[field],
                    f"POST {field} drift at {address}")

    pre_metrics = read_metrics(root / "inventories/base/program.tsv")
    post_metrics = read_metrics(root / "inventories/final-replica-a/program.tsv")
    changed_metrics = {key for key in pre_metrics if pre_metrics[key] != post_metrics[key]}
    require(changed_metrics == {
        "instructions", "instructionLayoutSha256", "undefinedData",
        "symbolsDefaultOther", "references", "referencesSha256"
    }, f"program metric delta drift: {changed_metrics}")
    require(pre_metrics["functions"] == post_metrics["functions"] == "8280", "function count")
    require(pre_metrics["instructions"] == "550991", "PRE instruction count")
    require(post_metrics["instructions"] == "551014", "POST instruction count")
    require(post_metrics["instructionLayoutSha256"] ==
            "2e05b524d6c5d2876517d3f09c8700071c9038a7de1b75b189732d69f4129924",
            "POST instruction layout")
    require(pre_metrics["references"] == "234495", "PRE reference count")
    require(post_metrics["references"] == "234478", "POST reference count")
    require(post_metrics["referencesSha256"] ==
            "ff2c5fb8d4dbc7f5f1e2ca980f8350e39a5d8ca77278b8d1e5d0f93bec27605b",
            "POST references layout")
    return {
        "artifacts": [base_functions, base_program, *post_artifacts, *restore_artifacts],
        "unchangedFunctionRows": 8275,
        "changedFunctionRows": 5,
        "changedProgramMetrics": sorted(changed_metrics),
    }


def validate_mutator_receipt(value: dict[str, Any], mode: str) -> None:
    require(value["schema"] == "bea.ghidra.function-fragment-range-repair.v1",
            f"{mode} schema")
    require(value["status"] == "READY_FOR_SCRATCH_ONLY", f"{mode} status")
    require(value["policy"] == "LIVE_FORBIDDEN", f"{mode} policy")
    require(value["mode"] == mode, f"{mode} mode")
    require(value["manifest"] == {
        "name": "fragment-manifest.tsv", "bytes": 2878, "sha256": MANIFEST_SHA256
    }, f"{mode} manifest stamp")
    require(value["tool"] == {
        "name": "GhidraApplyFunctionFragmentRanges.java",
        "bytes": 50339,
        "sha256": MUTATOR_SHA256,
    }, f"{mode} tool stamp")
    require(value["program"] == {
        "name": "BEA.exe", "md5": RETAIL_MD5, "sha256": RETAIL_SHA256
    }, f"{mode} program identity")
    require(value["targets"] == 5 and value["repairBytes"] == 1258,
            f"{mode} repair totals")
    require(value["newFunctionsAuthorized"] is False, f"{mode} function policy")
    require(value["namesSignaturesCommentsTagsDataAuthorized"] is False,
            f"{mode} metadata policy")


def verify_replicas_and_controls(root: Path) -> dict[str, Any]:
    artifacts: list[dict[str, Any]] = []
    receipts: dict[str, list[dict[str, Any]]] = {"apply": [], "readback": []}
    for mode in ("apply", "readback"):
        for replica in ("a", "b"):
            prefix = f"runs/final-replica-{replica}-{mode}"
            result = require_stamp(root, f"{prefix}/result.tsv")
            ready_stamp = require_stamp(root, f"{prefix}/result.ready.json")
            artifacts.extend((result, ready_stamp))
            value = read_json(root / f"{prefix}/result.ready.json")
            validate_mutator_receipt(value, mode)
            require(value["output"]["sha256"] == result["sha256"],
                    f"{prefix} output stamp")
            receipts[mode].append(value)
        require(normalized_receipt(receipts[mode][0]) ==
                normalized_receipt(receipts[mode][1]),
                f"{mode} replica receipts differ beyond timestamp")
    require(artifacts[0]["sha256"] == artifacts[2]["sha256"] ==
            "f62ccc2ceb3b4ed775f19377cf1a514ae1eb4703088902e96ab8399b2347bc25",
            "apply result replica drift")
    require(artifacts[4]["sha256"] == artifacts[6]["sha256"] ==
            "4f765e7b84167abe034625a48b48b02af453406f91751ec1dfb67714c1268a06",
            "readback result replica drift")
    pre_counts = {
        "functions": 8280, "bodyRanges": 8400, "ownedBytes": 1794212,
        "instructions": 550991, "references": 234495,
    }
    post_counts = {
        "functions": 8280, "bodyRanges": 8396, "ownedBytes": 1795470,
        "instructions": 551014, "references": 234478,
    }
    for value in receipts["apply"]:
        require(value["countsBefore"] == pre_counts, "apply PRE counts")
        require(value["countsAfter"] == post_counts, "apply POST counts")
        require(value["postVerified"] is True, "apply POST verification")
    for value in receipts["readback"]:
        require(value["countsBefore"] == value["countsAfter"] == post_counts,
                "readback POST counts")
        require(value["postVerified"] is True, "readback POST verification")

    dry_receipts: list[dict[str, Any]] = []
    for control in ("control-one-restored", "control-all-restored"):
        prefix = f"runs/{control}"
        result = require_stamp(root, f"{prefix}/result.tsv")
        ready = require_stamp(root, f"{prefix}/result.ready.json")
        artifacts.extend((result, ready))
        value = read_json(root / f"{prefix}/result.ready.json")
        validate_mutator_receipt(value, "dry")
        require(value["countsBefore"] == value["countsAfter"] == pre_counts,
                f"{control} PRE counts")
        require(value["output"]["sha256"] == result["sha256"],
                f"{control} output stamp")
        dry_receipts.append(value)
    require(normalized_receipt(dry_receipts[0]) == normalized_receipt(dry_receipts[1]),
            "restored control receipts differ beyond timestamp")

    adverse_one = (root / "controls/adverse-one.log").read_text(
        encoding="utf-8", errors="strict"
    )
    adverse_all = (root / "controls/adverse-all.log").read_text(
        encoding="utf-8", errors="strict"
    )
    require("mode=probe-after-one transient_functions=8280 transient_ranges=8400 "
            "transient_owned=1795037 recovery=RESTORE_VERIFIED_SCRATCH_BASE_REQUIRED"
            in adverse_one, "one-target adverse marker")
    require("forced failure after one function-body repair" in adverse_one,
            "one-target forced failure marker")
    require("mode=probe-after-all transient_functions=8280 transient_ranges=8396 "
            "transient_owned=1795470 recovery=RESTORE_VERIFIED_SCRATCH_BASE_REQUIRED"
            in adverse_all, "all-target adverse marker")
    require("forced failure after all five function-body repairs" in adverse_all,
            "all-target forced failure marker")
    require("Save succeeded for processed file" in adverse_one and
            "Save succeeded for processed file" in adverse_all,
            "adverse save evidence")

    external = (root / "controls/external-output-refusal.log").read_text(
        encoding="utf-8", errors="strict"
    )
    tamper = (root / "controls/tampered-manifest-refusal.log").read_text(
        encoding="utf-8", errors="strict"
    )
    require("output TSV escapes package root" in external, "external output refusal")
    require("manifest sha256 mismatch" in tamper, "tampered manifest refusal")
    tampered_stamp = require_stamp(
        root,
        "controls/tampered-fragment-manifest.tsv",
        sha256="ae99a2068eeb3c036bd38ebc41c254e390f4725e4c74a68d1be3aac8c135d84c",
    )
    artifacts.extend((
        require_stamp(root, "controls/adverse-one.log"),
        require_stamp(root, "controls/adverse-all.log"),
        require_stamp(root, "controls/external-output-refusal.log"),
        require_stamp(root, "controls/tampered-manifest-refusal.log"),
        tampered_stamp,
    ))
    return {
        "artifacts": artifacts,
        "positiveReplicas": 2,
        "savedReadbacks": 2,
        "adverseControls": 2,
        "restoredPreReadbacks": 2,
        "containmentRefusals": 2,
    }


def verify_backup(root: Path) -> dict[str, Any]:
    inspect_stamp = require_stamp(root, "backup/base-inspect.json")
    open_stamp = require_stamp(root, "backup/base-openability.json")
    inspect = read_json(root / "backup/base-inspect.json")
    manifest = inspect["manifest"]
    require(manifest["fileCount"] == 19, "backup file count")
    require(manifest["totalBytes"] == 186960773, "backup byte count")
    require(manifest["structurallyComplete"] is True, "backup structural completeness")
    db = [row for row in manifest["files"] if row["relative_path"].endswith("db.18613.gbf")]
    require(db == [{
        "relative_path": "BEA.rep/idata/00/~00000000.db/db.18613.gbf",
        "sha256": "615497847b0c732077ee7164b0973b9012092523e9ad99b91c21781952420ebe",
        "size": 68337664,
    }], "db.18613 identity")
    opened = read_json(root / "backup/base-openability.json")
    require(opened["sourceStable"] is True, "backup source stability")
    require(opened["copyComparison"]["matches"] is True, "backup copy comparison")
    readonly = opened["readonlyOpen"]
    require(readonly["opened"] is True and readonly["exitCode"] == 0,
            "read-only open")
    require(readonly["contentStable"] is True and
            readonly["postOpenComparison"]["matches"] is True,
            "read-only open stability")
    require(readonly["observedProgramMd5"] == RETAIL_MD5 and
            readonly["observedProgramSha256"] == RETAIL_SHA256,
            "openability program identity")
    return {"artifacts": [inspect_stamp, open_stamp], "readOnlyOpen": "PASS"}


def verify_tools(root: Path) -> list[dict[str, Any]]:
    return [
        require_stamp(
            root, "tools/GhidraApplyFunctionFragmentRanges.java",
            size=50339, sha256=MUTATOR_SHA256,
        ),
        require_stamp(
            root, "tools/re_pc_function_body_fragments.py",
            size=28787, sha256=STATIC_TOOL_SHA256,
        ),
        require_stamp(
            root, "tools/ExportFullFunctionInventory.java",
            size=23963,
            sha256="04519cd813f2fc25ddea8a6660f87c010f8aa4e053560993e4b35cafcc0b5197",
        ),
        require_stamp(root, "tools/ghidra_project_backup.py"),
        require_stamp(root, "tools/ghidra_function_fragment_range_scratch_authority.py"),
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package-root", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    root = args.package_root.resolve(strict=True)
    require(root.is_dir(), "package root is not a directory")
    packaged_tool = (
        root / "tools/ghidra_function_fragment_range_scratch_authority.py"
    ).resolve(strict=True)
    require(Path(__file__).resolve(strict=True) == packaged_tool,
            "authority must execute from the sealed package tools directory")
    output = args.output.resolve(strict=False)
    require(output.is_relative_to(root), "authority output escapes package root")
    require(not output.exists(), "refusing to overwrite authority output")
    require(output.parent.is_dir(), "authority output parent is missing")

    static = verify_static(root)
    inventory = verify_inventory_delta(root)
    replicas = verify_replicas_and_controls(root)
    backup = verify_backup(root)
    tools = verify_tools(root)
    artifacts = sorted(
        [*static["artifacts"], *inventory["artifacts"],
         *replicas["artifacts"], *backup["artifacts"], *tools],
        key=lambda row: row["path"],
    )
    require(len({row["path"] for row in artifacts}) == len(artifacts),
            "duplicate authority artifact path")

    receipt = {
        "schema": "bea.ghidra.function-fragment-scratch-authority.v1",
        "status": "READY",
        "verdict": "STRICT_GO_FOR_LATER_TRACKED_PREPARATION",
        "policy": "LIVE_FORBIDDEN",
        "program": {"name": "BEA.exe", "md5": RETAIL_MD5, "sha256": RETAIL_SHA256},
        "base": {
            "functions": 8280,
            "bodyRanges": 8400,
            "ownedBytes": 1794212,
            "instructions": 550991,
            "references": 234495,
            "db": "db.18613.gbf",
            "dbSha256": "615497847b0c732077ee7164b0973b9012092523e9ad99b91c21781952420ebe",
        },
        "repair": {
            "existingFunctionsOnly": 5,
            "newFunctions": 0,
            "addedBodyBytes": 1258,
            "postFunctions": 8280,
            "postBodyRanges": 8396,
            "postOwnedBytes": 1795470,
            "postInstructions": 551014,
            "postReferences": 234478,
            "bridgedPriorRangeComponents": 4,
            "extendedSinglePriorComponent": 1,
        },
        "proof": {
            "exhaustiveMechanicalCandidates": static["manifestRows"],
            "positiveReplicas": replicas["positiveReplicas"],
            "savedReadbacks": replicas["savedReadbacks"],
            "adverseControls": replicas["adverseControls"],
            "restoredPreReadbacks": replicas["restoredPreReadbacks"],
            "containmentRefusals": replicas["containmentRefusals"],
            "unchangedFunctionRowsExact": inventory["unchangedFunctionRows"],
            "changedFunctionRowsExact": inventory["changedFunctionRows"],
            "readOnlyOpen": backup["readOnlyOpen"],
        },
        "limitations": [
            "0x00462B64..0x00462B70 is twelve-byte NOP alignment and is excluded from CFEPMain__Process.",
            "No retained runtime range intersects the CGame tail or CDXTexture fragment; their ownership rests on static CFG and unique normalized demo twins.",
            "Ghidra nested script rollback does not undo the enclosing headless save; both adverse copies were therefore discarded and restored from the independently verified exact base.",
            "This authority permits only later tracked preparation and never a live, shared, or canonical Ghidra mutation.",
        ],
        "artifacts": artifacts,
    }
    output.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        "FUNCTION_FRAGMENT_SCRATCH_AUTHORITY_READY "
        "functions=8280 ranges=8396 gain=1258 replicas=2 controls=2 "
        "verdict=STRICT_GO_FOR_LATER_TRACKED_PREPARATION policy=LIVE_FORBIDDEN"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
