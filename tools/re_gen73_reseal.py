#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Derive the post-loss Gen73 claim closure from exact local evidence.

This module treats the historical Generation 73 tree as a projection oracle,
never as a campaign parent or reducer authority.  It starts from canonical 10R,
admits only field-level claims backed by the allowlisted current proof packs,
preserves the police-open frontier, and emits a mechanically complete delta
disposition.  `re_campaign.py` owns campaign publication and frozen replay.
"""

from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import json
import os
import re
import shutil
import tempfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


SCHEMA = "bea.re.candidate-chain-post-loss-closure.v1"
SPECIMEN_SHA256 = (
    "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
)
SCRIPT = Path(__file__).resolve()
REPO_ROOT = Path(
    os.environ.get("BEA_REPO_ROOT", os.fspath(SCRIPT.parent.parent))
).resolve()

PARENT_RELATIVE = Path(
    "local-lab/re-campaign-incident-recovery-20260808-v1/"
    "generation-10-ttd-call-context-recovered-v2"
)
PARENT_READY_SHA256 = (
    "12cb61f9d8cad06cd0c58ca5262a9c497a62d7268fc108d546ed988b9a757561"
)
PARENT_REDUCER_ID = (
    "88d61c227970ead0807e110ff14712ca74fcf23ce51b4bc88434b98bc0e956d4"
)

HISTORICAL_BASELINE_RELATIVE = Path(
    "local-lab/ttd-call-context-level521-impact-generation10-20260804-v1/"
    "generation-10-ttd-call-context-observation-v2"
)
HISTORICAL_BASELINE_READY_SHA256 = (
    "b349f0b2895849ba320b0b0b783c60a98794d01f375d57d9a04bbe4a5aebabb2"
)

CANDIDATE_RELATIVE = Path(
    "local-lab/function-c1-opaque-squad-spawn-helpers-batch-generation73-"
    "20260806-v1/generation-73-function-c1-opaque-squad-spawn-helpers-batch"
)
CANDIDATE_READY_SHA256 = (
    "c0305111ead911cdb8e5bb1d5c8d56819b50c3b0a2ed788d8ea95a01aa593ce8"
)

POLICE_RELATIVE = Path(
    "local-lab/residual-terminal-generation25-police-reopen-20260805-v1/"
    "generation-25-residual-terminal-police-reopen"
)
POLICE_READY_SHA256 = (
    "ee319930c2a8693c592bc4a4c12b179e247a2e9e16f1b846b771d3bd3e3f343c"
)

SPECIMEN_RELATIVE = Path("local-lab/safe-copy-bea-pristine/BEA.exe.original.backup")
WEAK_NATIVE_TABLE_RELATIVE = Path(
    "local-lab/ghidra-from-trace-2026-07-28/script-native-table-144.tsv"
)
WEAK_NATIVE_TABLE_SHA256 = (
    "42027af22e1d4a0611bf7286fd1ea0df17adf01f7bf54ad5a2196f8484f40d86"
)
RTTI_TABLE_RELATIVE = Path(
    "local-lab/rtti-strict-census-2026-08-03/strict-census-v1-ready/vtables.tsv"
)
RTTI_TABLE_SHA256 = (
    "2f1602d4c7ffffa9c2b5116c60a23d23b2f8bf923495feded54ebb67aff1f178"
)
APPLY_DAMAGE_RUNTIME_RELATIVE = Path(
    "local-lab/damage-chain-pilot-2026-08-02/runtime-contract.json"
)
APPLY_DAMAGE_RUNTIME_SHA256 = (
    "a1d7f7a99fb7dea47195c4c83559b20a0c557ed9a41b8250ea8ac804ef455728"
)

OUTPUT_NAMES = (
    "campaign-functions.tsv",
    "campaign-residuals.tsv",
    "campaign-questions.tsv",
    "campaign-scenarios.tsv",
    "campaign-levers.tsv",
    "campaign-contracts.tsv",
    "campaign-adjudications.tsv",
    "campaign-supersessions.tsv",
)
LEDGER_KEYS = {
    "functions": "entityKey",
    "residuals": "entityKey",
    "questions": "questionId",
    "scenarios": "scenarioId",
    "levers": "regionKey",
    "contracts": "contractId",
    "adjudications": "adjudicationId",
    "supersessions": "supersessionId",
}

PARENT_STAMPS = {
    "campaign.ready.json": (32794, PARENT_READY_SHA256),
    "campaign-functions.tsv": (5098270, "6b18eda4b537fa17aba9e41a519cc47fb3c41836f9ff9877cf735ebe7a8933f1"),
    "campaign-residuals.tsv": (2930767, "aa62128b8b472311ebd2c3279a59a354495855e8640e4dbaa1147d507efd25f2"),
    "campaign-questions.tsv": (8428469, "dc918c4c3fa507dba4e943cd842c8d0ada71961d14e7ed95f3d3238b067915ec"),
    "campaign-scenarios.tsv": (31860, "35a84fad46065d1317e48b41c66889a1dd12327077766423693b8839be857542"),
    "campaign-levers.tsv": (329226, "fa337d96cfe7b6eca266b44aa39deded516e3a8cc02979a31671b449c66e3cdc"),
    "campaign-contracts.tsv": (8854868, "05f73d3dfdfcdbd454fad97f90d9f5c02094b26047e6b5d4648509f1eecfdf5a"),
    "campaign-adjudications.tsv": (6056, "8693f81f9cf8531961460d09087b018c73b981246bdc839c88b438947e41ff0c"),
    "campaign-supersessions.tsv": (446447, "7569852a3fe9aea25a4fcc4f6d17b6d9d81ff658f644b007bda1f50ae55559cb"),
}

CANDIDATE_STAMPS = {
    "campaign.ready.json": (2148, CANDIDATE_READY_SHA256),
    "campaign-functions.tsv": (
        5138662,
        "1a2f3a03b726d2671854681974d3328c7d5f72f72ba18ff5d2bbcd670fb3df25",
    ),
    "campaign-residuals.tsv": (
        2756482,
        "92cd0f5c179399f4c4612810dd5af8d72729027b841139bb4b2a342ec580afc0",
    ),
    "campaign-questions.tsv": (
        8470365,
        "8912c398db4f2cff2a92964dbed6e4a8e26dee65ea0a69005e66c15ed37794e9",
    ),
    "campaign-scenarios.tsv": (
        31860,
        "35a84fad46065d1317e48b41c66889a1dd12327077766423693b8839be857542",
    ),
    "campaign-levers.tsv": (
        329226,
        "fa337d96cfe7b6eca266b44aa39deded516e3a8cc02979a31671b449c66e3cdc",
    ),
    "campaign-contracts.tsv": (
        12304835,
        "6a27d99a6f1d0b06f7ef609819f1cd825caa5480a075e5323885ba23ba43182f",
    ),
    "campaign-adjudications.tsv": (
        3534170,
        "e8a1cc40e7b0ad0edaa4df208f688a59c6de9918ab11ae2d424b3d44cf2fabe1",
    ),
    "campaign-supersessions.tsv": (
        3319491,
        "aedac23ea6e3f3b596544b3603183a78cc74f123fdda1a76b940edc3075567a9",
    ),
}

HISTORICAL_BASELINE_STAMPS = {
    "campaign.ready.json": (29921, HISTORICAL_BASELINE_READY_SHA256),
    "campaign-functions.tsv": (
        5098270,
        "6b18eda4b537fa17aba9e41a519cc47fb3c41836f9ff9877cf735ebe7a8933f1",
    ),
    "campaign-residuals.tsv": (
        2930767,
        "aa62128b8b472311ebd2c3279a59a354495855e8640e4dbaa1147d507efd25f2",
    ),
    "campaign-questions.tsv": (
        8428469,
        "dc918c4c3fa507dba4e943cd842c8d0ada71961d14e7ed95f3d3238b067915ec",
    ),
    "campaign-scenarios.tsv": (
        31860,
        "35a84fad46065d1317e48b41c66889a1dd12327077766423693b8839be857542",
    ),
    "campaign-levers.tsv": (
        329226,
        "fa337d96cfe7b6eca266b44aa39deded516e3a8cc02979a31671b449c66e3cdc",
    ),
    "campaign-contracts.tsv": (
        8854607,
        "89014479c3013c71848204a28fafc9e81c93daff6f1ac9351916405cabcadced",
    ),
    "campaign-adjudications.tsv": (
        6047,
        "40a471f1630ea2109108d7171be030df95bec5ff95e851a3fa0eb4e495aafdad",
    ),
    "campaign-supersessions.tsv": (
        445925,
        "7ac03203257370124b9b21bb16cd5de522c7abb6a6ce7170e93d00eafc647c9a",
    ),
}

# Paths are policy.  The prepared closure receipt binds their exact bytes,
# hashes, schemas, statuses, proof selection, and auxiliary authorities.
RESIDUAL_PACKS = (
    "residual-terminal-formal-pack-padding-xrefclean-20260805-v1",
    "residual-mixed-shape-formal-pack-20260805-v1",
    "open-dark-pad-data-formal-pack-20260805-v1",
    "code-envelope-adjudication-20260805-v1",
    "open-dark-remaining-frontier-gen14-20260805-v1",
    "open-dark-code-like-mass-gen15-20260805-v1",
    "open-dark-still-open-inbound-gen16-20260805-v1",
    "open-residual-gen17-table-align-20260805-v1",
    "open-residual-gen18-code-envelope-20260805-v1",
    "open-residual-gen19-multi-unit-20260805-v1",
    "open-residual-gen20-code-pad-20260805-v1",
    "open-residual-gen21-data-shape-20260805-v1",
    "open-residual-gen22-partial-data-20260805-v1",
    "open-residual-gen23-small-table-20260805-v1",
    "open-residual-gen26-unit-split-20260805-v1",
    "open-residual-gen26-tiny-fragment-20260805-v1",
    "open-residual-gen27-open-dark-unit-split-20260805-v1",
    "open-residual-gen28-pad-peel-sandwich-20260805-v1",
    "open-residual-gen29-msvc-table-mix-20260805-v1",
    "open-residual-gen30-seh-segment-resolve-20260805-v1",
    "open-residual-gen31-deep-segment-resolve-20260805-v1",
    "open-residual-gen32-large-island-resolve-20260805-v1",
)

NAME_PACKS = (
    "fun-native-name-align-20260805-v1",
    "fun-rtti-vfunc-name-align-20260805-v1",
    "fun-trivial-template-name-align-20260805-v1",
    "fun-extended-template-name-align-20260805-v2",
    "fun-residual-template-name-align-20260805-v1",
    "fun-micro-template-name-align-20260805-v1",
    "fun-residual-microstruct-name-align-20260805-v1",
    "fun-rtti-residual-name-align-20260805-v1",
    "fun-callback-install-name-align-20260805-v1",
    "fun-console-cohort-name-align-20260805-v1",
    "fun-dyninit-atexit-name-align-20260805-v1",
    "fun-firstcall-name-align-20260805-v1",
    "fun-firstnamedcall-name-align-20260805-v1",
    "fun-string-ref-name-align-20260805-v1",
    "fun-weak-native-name-align-20260805-v1",
)

C1_PACKS = (
    "c1-pe-field-enrichment-20260805-v1",
    "c1-pe-field-enrichment-remaining-20260805-v1",
    "c1-applydamage-runtime-measured-20260805-v1",
    "c1-opaque-hiveboss-forward-applydamage-20260805-v1",
    "c1-opaque-applydamage-script-batch-20260805-v1",
    "c1-getmapheight-identity-extras-20260805-v1",
    "c1-opaque-hit-initbuiltins-batch-20260805-v1",
    "c1-opaque-damage-hit-helpers-batch-20260805-v1",
    "c1-opaque-weapon-destroyable-batch-20260805-v1",
    "c1-opaque-weapon-load-create-batch-20260805-v1",
    "c1-opaque-apply-segment-ai-batch-20260805-v1",
    "c1-opaque-unit-health-apply-batch-20260805-v1",
    "c1-opaque-combat-lock-segment-batch-20260805-v1",
    "c1-opaque-deploy-lock-support-batch-20260805-v1",
    "c1-opaque-weapon-unit-tuning-batch-20260806-v1",
    "c1-opaque-collision-battle-ground-batch-20260806-v1",
    "c1-opaque-mapwho-ground-walker-batch-20260806-v1",
    "c1-opaque-mapwho-occupancy-batch-20260806-v1",
    "c1-opaque-battleengine-mode-helpers-batch-20260806-v1",
    "c1-opaque-unit-targeting-batch-20260806-v1",
    "c1-opaque-unit-thing-helpers-batch-20260806-v1",
    "c1-opaque-unit-combat-helpers-batch-20260806-v1",
    "c1-opaque-squad-spawn-helpers-batch-20260806-v1",
)

DISPOSITION_PACKS = (
    "c2-applydamage-primary-20260805-v1",
    "c1-to-c2-damage-path-refuter-20260805-v1",
    "c1-to-c2-perva-measured-io-20260805-v1",
)

# These are new, explicitly reviewed post-loss evidence identities.  Historical
# Gen73 citations are never used to select a file, and a same-schema or
# same-status replacement is not accepted.  Some source packs carry historical
# hold flags because they were already consumed by their original campaign;
# this recovery owner admits only the narrower, profile-specific fields below
# after revalidating every named PE span against the pristine specimen.
EXPECTED_PACK_STAMPS = {
    "residual-terminal-formal-pack-padding-xrefclean-20260805-v1": (3832706, "a5a95e006745fb1ee3004b6f1fb63a718840d9a69b67514f993f54f4040b5358"),
    "residual-mixed-shape-formal-pack-20260805-v1": (430401, "cdaec3a4be98b847667cab284a4ed44d48038e0ee93b48a40ad4e1867462e7d7"),
    "open-dark-pad-data-formal-pack-20260805-v1": (16614, "64274c1826213f97bd837d3997b55dc84f3387fab0294247c9fec01aebf1d7a2"),
    "code-envelope-adjudication-20260805-v1": (364318, "27b58d5f5585e396f2671985400c9c64ab811739fdd9042e73af1eca17930b60"),
    "open-dark-remaining-frontier-gen14-20260805-v1": (69131, "85a691197e7d9c0c83ec8696b4250aba0a9f63d5279c59cdac6987f5882529fd"),
    "open-dark-code-like-mass-gen15-20260805-v1": (72918, "9770b87a655c164a7bb8a907ffcc32af158dbdb12ed7188d80bfe56f7af24aed"),
    "open-dark-still-open-inbound-gen16-20260805-v1": (62074, "41a231d7d394e623a3cb45eb5f4fd8d02d8bd888d7226348aeadb4688e4d9042"),
    "open-residual-gen17-table-align-20260805-v1": (57843, "868ae536f3ac9fd8d2f0928cfb72a3dd6cf4c38ec188c93c597267bf252b5350"),
    "open-residual-gen18-code-envelope-20260805-v1": (170668, "cdc8456dcacee3206910a2dd64f14af1663bdc0c820a143019840c3841e2ffcb"),
    "open-residual-gen19-multi-unit-20260805-v1": (104407, "1b7338bd2e60c28c8a3cae0fc8ae51172ff2e9529ff3614e8e433d778fb8e716"),
    "open-residual-gen20-code-pad-20260805-v1": (10685, "aa5310d504d1c2aaa60a095223079845b150a2ce61f2076edc7e04cd1adcbe10"),
    "open-residual-gen21-data-shape-20260805-v1": (49888, "76c5efa79236118c8ff27a7580bffcf8f8d87135f8cf0922e94f18d6794f1ff6"),
    "open-residual-gen22-partial-data-20260805-v1": (18075, "60bd7b16197ef8f27d94e47ecf85684bfd0c3f2b59987966fc1f86bd2f015ad6"),
    "open-residual-gen23-small-table-20260805-v1": (76419, "b3c1b12deb722b0a10e67cdd2cd64c5727aa85691419b224a79affd2e6f8f872"),
    "open-residual-gen26-unit-split-20260805-v1": (11048, "9aee28f0bd8d50f281eacb41edc73e714ad051487d644b9d90f3676ec76056a1"),
    "open-residual-gen26-tiny-fragment-20260805-v1": (26296, "fad2108dae0349fe6ec3c1a4cd7af1bc8d9f71cdb8ced6bd38d859f480f65fe8"),
    "open-residual-gen27-open-dark-unit-split-20260805-v1": (39209, "6575c0abaa1ec75a40789c0a9181c40040e1b78cc41c66a70188fd4265d66808"),
    "open-residual-gen28-pad-peel-sandwich-20260805-v1": (32471, "96fff2aa69b64ba5bfcda1e5e34d47c7483a6f47856601ef3f6b1d0d6f52d2dd"),
    "open-residual-gen29-msvc-table-mix-20260805-v1": (23886, "ab3e939102fb0f88c8263913ada914b39c63a3bfd89ab6d7325553709140058f"),
    "open-residual-gen30-seh-segment-resolve-20260805-v1": (11739, "e567ae0280c39568e2699d446f70893cece8433bcc1d10183b7125f77d91c7b2"),
    "open-residual-gen31-deep-segment-resolve-20260805-v1": (5281, "e862ac33f7f1f4ded42cf354d279a5f07ed506ffbd4bdb3f3d0090dc72eb4c44"),
    "open-residual-gen32-large-island-resolve-20260805-v1": (7535, "039a2f59a065b1529a61644dec6139566a13af4c1dca9b818e5ed659ee274e7c"),
    "fun-native-name-align-20260805-v1": (71096, "0891b541cdfce746b432e0537498a99ee4e4be27d568a394f2630cd7504aa310"),
    "fun-rtti-vfunc-name-align-20260805-v1": (45411, "ee4ebe5663e80decedc8721c992ea4f4f73647ba78a5b240001e3a7e743b6a4a"),
    "fun-trivial-template-name-align-20260805-v1": (417164, "f923f7ae0a452e87dc521b6a3136c7cc51e03ba9b1a8698de92db5a8c159bfec"),
    "fun-extended-template-name-align-20260805-v2": (368247, "c7ca2bd8fe558bd1ddf02cb68fc1e6c898dab08bb29dcb324eb54b80442bdfe0"),
    "fun-residual-template-name-align-20260805-v1": (39593, "38bd7c3909a7993961e9439203efa89f7bf3b2d84a93c4b91ac091b29dab8a39"),
    "fun-micro-template-name-align-20260805-v1": (13533, "7d32d0ec9e3ecee05c3f1eedbf7575211cc981aceef6048a3e82e1a469aac8b2"),
    "fun-residual-microstruct-name-align-20260805-v1": (14812, "90bc4cfaf28311cb84e557977211a142f8e9fa51ecb62194f2e357065953348e"),
    "fun-rtti-residual-name-align-20260805-v1": (19418, "8ffad6e246e39562a783f2b02a7a03037f51739200952f02933aea711fbc7e9b"),
    "fun-callback-install-name-align-20260805-v1": (53008, "2206be018f0d1f9ff263c29c48b558e7899c3da7409f6825786f94e77e2a793e"),
    "fun-console-cohort-name-align-20260805-v1": (7902, "dfd586b0aaa7d93c6a8fa22353ecc36fef9b8f89caee5cf6303195f2bb9b7525"),
    "fun-dyninit-atexit-name-align-20260805-v1": (9246, "2ac4d0445bdae864ca465173ac0973775ea1de8cc6894d2aed601e4efa71f373"),
    "fun-firstcall-name-align-20260805-v1": (29387, "6dfdc71a0665fb51ad2dd4076c0748b1994d0b9b731b6f09f0a9d5b5b744a04f"),
    "fun-firstnamedcall-name-align-20260805-v1": (5635, "b95154a8f1d8f5d92ea7d488f449cf42ce9a87acd5ffbd6989c90da45eb0cf92"),
    "fun-string-ref-name-align-20260805-v1": (18707, "491cd7b32cddd80701d37a2bc2e4872de9ea3e1a0c633ff179e35f87694b8f04"),
    "fun-weak-native-name-align-20260805-v1": (19929, "696b9fd5f6e7c7e61e2c52c7e3181bcd10a377925eeaaea3e42918f68cce7815"),
    "c1-pe-field-enrichment-20260805-v1": (13474, "77e0f70eb8332c318844ecc4bca1b9edfd113fd98211d9d44d9daba407c180db"),
    "c1-pe-field-enrichment-remaining-20260805-v1": (10195, "93c4408de24a40dbad8384fe9ff9c383f4f932150150db99ac76e1591ae39d34"),
    "c1-applydamage-runtime-measured-20260805-v1": (4399, "fb36f6a47a96189182be33caf7679edf615ee8c738f35655b7ea8a8489886656"),
    "c1-opaque-hiveboss-forward-applydamage-20260805-v1": (2965, "f84fcc051d639af0887ce03dd8f5629d51df740888a93cd6e9797f0229bf60eb"),
    "c1-opaque-applydamage-script-batch-20260805-v1": (11464, "427589f2420374fedba56cd01ffa2f049a584f8f3a0a63a2dcd605fae0c68571"),
    "c1-getmapheight-identity-extras-20260805-v1": (9576, "183a941ee427af383e66dde43498097c5bbfb76fb2419b2f5ba1092928bdfbab"),
    "c1-opaque-hit-initbuiltins-batch-20260805-v1": (10075, "0ef8d10618c41890be9c51b3640554514d863e6a6a64529ea4f2be4968c52623"),
    "c1-opaque-damage-hit-helpers-batch-20260805-v1": (18930, "5024dcaf05f7221f3bf9ed0599128ed58047474ca073e335732fb67911a6f902"),
    "c1-opaque-weapon-destroyable-batch-20260805-v1": (23870, "412624df49bff9afc348241e7d0f71c02eda09642679bf5bf7a5e5c59142363b"),
    "c1-opaque-weapon-load-create-batch-20260805-v1": (18272, "296d93c4bfa29ffce7191a898283634575df135606b2d5ba3f8a958ec5a8867f"),
    "c1-opaque-apply-segment-ai-batch-20260805-v1": (23416, "57bff53e6b02b608f63e4b7083373086a328d19156d9687de35f0616854d016d"),
    "c1-opaque-unit-health-apply-batch-20260805-v1": (20701, "6ff38853cf6cf2f38fbf39e4038aa8e4840e4dab8cdbf3998a66373ac335dafd"),
    "c1-opaque-combat-lock-segment-batch-20260805-v1": (25267, "9b8e1e0641049f01170e3ebfa0282f1e9b78b1f049effe2e6b58d1b57a21513c"),
    "c1-opaque-deploy-lock-support-batch-20260805-v1": (21577, "913e0c58a8c454032330d59064be10f6e678e27d9a11d80603658dd4381745d0"),
    "c1-opaque-weapon-unit-tuning-batch-20260806-v1": (24457, "6fea0a8970049369f38e9b554a0b1881ba6928813bb030dd630ed64d27be5d66"),
    "c1-opaque-collision-battle-ground-batch-20260806-v1": (28859, "388a55a4d9a0c7b589623884387f0f95be66e30667eb0f52ba0b06411599e89d"),
    "c1-opaque-mapwho-ground-walker-batch-20260806-v1": (24687, "b2d302676b9229d8e446d98535081d814fd8a04d0e1881099da482438f22a015"),
    "c1-opaque-mapwho-occupancy-batch-20260806-v1": (25536, "1b01fda2a2f6248f4d0b09c5b0065fbd3ce135684175c61ae4a90dd3358d67b0"),
    "c1-opaque-battleengine-mode-helpers-batch-20260806-v1": (24145, "b1d1eaa2ff541364327c143291b65f9c8a2a0ef911e0712c3b18176d67de7156"),
    "c1-opaque-unit-targeting-batch-20260806-v1": (27363, "018ea645da1547597a207ba7bc66d6cf092e94133a3b412f64a13dc8fdb0e3a4"),
    "c1-opaque-unit-thing-helpers-batch-20260806-v1": (31061, "5050454fbed7c0dabbcff4b68fe5090d57ac69d2a3b2d1e2aa8ad18b45986b0a"),
    "c1-opaque-unit-combat-helpers-batch-20260806-v1": (34937, "3f85677449a903b6c48a56a1af00d77aa1f860740d81b613ed8b5f18fdadf58e"),
    "c1-opaque-squad-spawn-helpers-batch-20260806-v1": (32612, "96c0ce0fcbe05eef2f98f2f2221107a07310d2ccffb50e3a6bbbc85da72678b7"),
    "c2-applydamage-primary-20260805-v1": (4130, "61295806d62f68e6dd557e8bd08917dcb9144fba91dd6d4fa1590333cbc3b30b"),
    "c1-to-c2-damage-path-refuter-20260805-v1": (7549, "2864961f3fecac8c2767b42dcd3e43774273036d5fad63017b1d1a12ff4446c4"),
    "c1-to-c2-perva-measured-io-20260805-v1": (13368, "d6cfd7b01d2217a7e8ba5ea3f541fb676797f8155dcb76f05a8bef5250b9650c"),
}

APPLY_DAMAGE_ENTITY = (
    "CODE:" + SPECIMEN_SHA256
    + ":VA=0x004f9a90:RANGES="
    + "3c07541ed870843444b66909c62014e975fc8f43c349891da0e9129654016c97"
)

EXPECTED_COUNTS = {
    "functions": 8124,
    "residuals": 6117,
    "questions": 15241,
    "scenarios": 72,
    "levers": 915,
    "contracts": 14241,
    "adjudications": 6088,
    "supersessions": 584,
}
EXPECTED_MODIFIED = {
    "functions": 1133,
    "residuals": 6082,
    "questions": 6082,
    "scenarios": 0,
    "levers": 0,
    "contracts": 7215,
    "adjudicationsAdded": 6082,
    "supersessions": 0,
}
EXPECTED_HISTORICAL_CANDIDATE_ROW_DELTAS = {
    "functions": 1134,
    "residuals": 6102,
    "questions": 6318,
    "scenarios": 0,
    "levers": 0,
    "contracts": 7236,
    "adjudications": 7294,
    "supersessions": 7099,
}
EXPECTED_PARENT_CANDIDATE_ROW_DELTAS = {
    "functions": 1134,
    "residuals": 6102,
    "questions": 6318,
    "scenarios": 0,
    "levers": 0,
    "contracts": 7251,
    "adjudications": 7302,
    "supersessions": 7128,
}
EXPECTED_PARENT_CANDIDATE_FIELD_DELTAS = {
    "functions": 4786,
    "residuals": 48079,
    "questions": 24620,
    "scenarios": 0,
    "levers": 0,
    "contracts": 54029,
    "adjudications": 7302,
    "supersessions": 7157,
}


class ResealError(ValueError):
    """A candidate input or claim does not meet the recovery policy."""


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def require_plain_single_link_file(path: Path, label: str) -> Path:
    """Reject aliases before reading an evidence-bearing file."""
    raw = Path(os.path.abspath(path))
    if not raw.is_file():
        raise ResealError(f"{label} is missing: {raw}")
    if os.path.normcase(os.path.realpath(raw)) != os.path.normcase(os.fspath(raw)):
        raise ResealError(f"{label} is reached through a symlink/reparse alias: {raw}")
    try:
        relative = raw.relative_to(Path(os.path.abspath(REPO_ROOT)))
    except ValueError:
        relative = None
    if relative is not None:
        cursor = Path(os.path.abspath(REPO_ROOT))
        for part in relative.parts:
            cursor /= part
            info = cursor.lstat()
            if cursor.is_symlink() or getattr(info, "st_file_attributes", 0) & 0x400:
                raise ResealError(f"{label} has a reparse ancestor: {cursor}")
    info = raw.lstat()
    if getattr(info, "st_nlink", 1) != 1:
        raise ResealError(f"{label} is hard-linked: {raw}")
    return raw


def stamp(path: Path, *, relative_to: Path | None = None) -> dict[str, object]:
    resolved = require_plain_single_link_file(path, "required file")
    display = (
        resolved.relative_to(relative_to.resolve()).as_posix()
        if relative_to is not None and resolved.is_relative_to(relative_to.resolve())
        else os.fspath(resolved)
    )
    return {"path": display, "bytes": resolved.stat().st_size, "sha256": sha256(resolved)}


def require_stamp(path: Path, expected: tuple[int, str], label: str) -> None:
    path = require_plain_single_link_file(path, label)
    actual = (path.stat().st_size, sha256(path))
    if actual != expected:
        raise ResealError(f"{label} identity differs: {actual} != {expected}")


def read_json(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ResealError(f"cannot read JSON {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ResealError(f"JSON root is not an object: {path}")
    return value


def read_tsv(path: Path) -> list[dict[str, str]]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise ResealError(f"cannot read TSV {path}: {exc}") from exc
    if not lines or not lines[0].startswith("# bea.re.campaign"):
        raise ResealError(f"campaign TSV header is missing: {path}")
    return list(csv.DictReader(lines[1:], delimiter="\t"))


def campaign_rows(root: Path) -> dict[str, list[dict[str, str]]]:
    return {
        name: read_tsv(root / f"campaign-{name}.tsv")
        for name in LEDGER_KEYS
    }


def keyed(rows: Iterable[dict[str, str]], field: str, label: str) -> dict[str, dict[str, str]]:
    result: dict[str, dict[str, str]] = {}
    for row in rows:
        key = row.get(field, "")
        if not key or key in result:
            raise ResealError(f"{label} contains a missing/duplicate {field}: {key!r}")
        result[key] = row
    return result


def union_tokens(*values: object) -> str:
    result: list[str] = []
    for value in values:
        for token in str(value or "").split(";"):
            if token and token not in result:
                result.append(token)
    return ";".join(result)


def canonical_row(row: dict[str, str]) -> str:
    return json.dumps(row, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _pe_sections(image: bytes) -> tuple[int, list[tuple[int, int, int, int]]]:
    if len(image) < 0x100 or image[:2] != b"MZ":
        raise ResealError("pristine specimen is not a PE image")
    pe = int.from_bytes(image[0x3C:0x40], "little")
    if image[pe:pe + 4] != b"PE\0\0":
        raise ResealError("pristine specimen lacks a PE signature")
    section_count = int.from_bytes(image[pe + 6:pe + 8], "little")
    optional_size = int.from_bytes(image[pe + 20:pe + 22], "little")
    optional = pe + 24
    image_base = int.from_bytes(image[optional + 28:optional + 32], "little")
    table = optional + optional_size
    sections: list[tuple[int, int, int, int]] = []
    for index in range(section_count):
        row = table + index * 40
        virtual_size = int.from_bytes(image[row + 8:row + 12], "little")
        virtual_address = int.from_bytes(image[row + 12:row + 16], "little")
        raw_size = int.from_bytes(image[row + 16:row + 20], "little")
        raw_offset = int.from_bytes(image[row + 20:row + 24], "little")
        sections.append((virtual_address, max(virtual_size, raw_size), raw_offset, raw_size))
    return image_base, sections


def pe_bytes(
    image: bytes,
    pe_layout: tuple[int, list[tuple[int, int, int, int]]],
    start_va: str | int,
    size: int,
) -> bytes:
    start = int(start_va, 16) if isinstance(start_va, str) else start_va
    image_base, sections = pe_layout
    rva = start - image_base
    for section_rva, span, raw_offset, raw_size in sections:
        if section_rva <= rva and rva + size <= section_rva + span:
            delta = rva - section_rva
            if delta + size > raw_size:
                raise ResealError(f"PE span exceeds raw section at 0x{start:08x}")
            return image[raw_offset + delta:raw_offset + delta + size]
    raise ResealError(f"PE span does not map to a section: 0x{start:08x}+{size}")


def pack_path(name: str) -> Path:
    return REPO_ROOT / "local-lab" / name / "FORMAL-PACK.json"


def _status_allowed(profile: str, status: object) -> bool:
    text = str(status or "")
    if profile in {"residual", "name"}:
        return text == "READY_FOR_GENERATION"
    if profile == "c1":
        return text.startswith("APPLIED_GEN")
    if profile == "disposition":
        return text in {
            "APPLIED_GEN53",
            "READY_FOR_GENERATION",
            "REFUTED_DO_NOT_APPLY",
        }
    return False


def load_pack(name: str, profile: str) -> tuple[Path, dict, dict[str, object]]:
    path = pack_path(name)
    expected = EXPECTED_PACK_STAMPS.get(name)
    if expected is None:
        raise ResealError(f"proof pack is not identity-allowlisted: {name}")
    require_stamp(path, expected, f"{profile} proof pack {name}")
    value = read_json(path)
    if not _status_allowed(profile, value.get("status")):
        raise ResealError(f"{profile} pack has a disallowed status: {name}: {value.get('status')}")
    specimen = value.get("specimen_sha256")
    if specimen not in {None, SPECIMEN_SHA256}:
        raise ResealError(f"pack specimen differs: {name}: {specimen}")
    proofs = value.get("proofs")
    if not isinstance(proofs, list):
        raise ResealError(f"pack proofs are missing: {name}")
    return path, value, {
        **stamp(path, relative_to=REPO_ROOT),
        "schema": value.get("schema"),
        "status": value.get("status"),
        "profile": profile,
        "proofCount": len(proofs),
        "historicalHoldGenerationApply": (
            value["hold_generation_apply"]
            if "hold_generation_apply" in value
            else "ABSENT"
        ),
        "specimenSha256": value.get("specimen_sha256", "ABSENT"),
    }


def validate_fixed_inputs() -> dict[str, object]:
    parent = REPO_ROOT / PARENT_RELATIVE
    candidate = REPO_ROOT / CANDIDATE_RELATIVE
    historical = REPO_ROOT / HISTORICAL_BASELINE_RELATIVE
    police = REPO_ROOT / POLICE_RELATIVE
    for name, expected in PARENT_STAMPS.items():
        require_stamp(parent / name, expected, f"canonical 10R parent {name}")
    parent_ready = read_json(parent / "campaign.ready.json")
    if parent_ready.get("generation") != 10 or parent_ready.get("reducer", {}).get("id") != PARENT_REDUCER_ID:
        raise ResealError("10R READY generation/reducer differs")
    for name, expected in CANDIDATE_STAMPS.items():
        require_stamp(candidate / name, expected, f"Gen73 projection oracle {name}")
    for name, expected in HISTORICAL_BASELINE_STAMPS.items():
        require_stamp(historical / name, expected, f"historical Gen10 oracle {name}")
    require_stamp(police / "campaign.ready.json", (13008, POLICE_READY_SHA256), "Gen25 police READY")
    specimen = REPO_ROOT / SPECIMEN_RELATIVE
    require_stamp(specimen, (2506752, SPECIMEN_SHA256), "pristine specimen")
    weak_table = REPO_ROOT / WEAK_NATIVE_TABLE_RELATIVE
    require_stamp(weak_table, (9016, WEAK_NATIVE_TABLE_SHA256), "weak native table")
    rtti_table = REPO_ROOT / RTTI_TABLE_RELATIVE
    require_stamp(rtti_table, (431350, RTTI_TABLE_SHA256), "RTTI vtable census")
    runtime = REPO_ROOT / APPLY_DAMAGE_RUNTIME_RELATIVE
    require_stamp(runtime, (8924, APPLY_DAMAGE_RUNTIME_SHA256), "ApplyDamage runtime contract")
    return {
        "parent": parent,
        "parentReady": parent_ready,
        "candidate": candidate,
        "historical": historical,
        "police": police,
        "specimen": specimen,
        "auxiliary": {
            "weakNativeTable": stamp(weak_table, relative_to=REPO_ROOT),
            "rttiTable": stamp(rtti_table, relative_to=REPO_ROOT),
            "applyDamageRuntime": stamp(runtime, relative_to=REPO_ROOT),
        },
    }


def _validate_residual_proof(
    proof: dict,
    image: bytes,
    layout: tuple[int, list[tuple[int, int, int, int]]],
    parent_residuals: dict[str, dict[str, str]],
) -> None:
    entity = str(proof.get("entityKey", ""))
    parent = parent_residuals.get(entity)
    if parent is None:
        raise ResealError(f"residual proof does not name a 10R entity: {entity}")
    start = str(proof.get("startVa", ""))
    end = str(proof.get("endVa", ""))
    size = int(proof.get("bytes", -1))
    if (
        start.lower() != parent["startVa"].lower()
        or end.lower() != parent["endVa"].lower()
        or size != int(parent["bytes"])
        or int(end, 16) - int(start, 16) != size
    ):
        raise ResealError(f"residual proof span differs from 10R: {entity}")
    expected_hash = str(proof.get("peBytesSha256", ""))
    if not re.fullmatch(r"[0-9a-f]{64}", expected_hash):
        raise ResealError(f"residual proof lacks a PE byte hash: {entity}")
    actual = sha256_bytes(pe_bytes(image, layout, start, size))
    if actual != expected_hash:
        raise ResealError(f"residual proof PE bytes differ: {entity}")
    proposed = proof.get("proposed")
    if not isinstance(proposed, dict):
        raise ResealError(f"residual proof lacks a field-level proposal: {entity}")
    if not proposed.get("requiresQuestionSupersession") and not str(
        parent.get("terminalState", "")
    ).startswith("TERMINAL_"):
        raise ResealError(
            f"residual proof omits question closure for a nonterminal 10R row: {entity}"
        )


def _validate_function_identity(
    proof: dict,
    image: bytes,
    layout: tuple[int, list[tuple[int, int, int, int]]],
    parent_functions: dict[str, dict[str, str]],
    *,
    require_body_hash: bool,
) -> dict[str, str]:
    entity = str(proof.get("entityKey", ""))
    parent = parent_functions.get(entity)
    if parent is None:
        raise ResealError(f"function proof does not name a 10R entity: {entity}")
    entry = str(proof.get("entryVa", ""))
    size = int(proof.get("bodyBytes", -1))
    if (
        entry.lower() != parent["entryVa"].lower()
        or size != int(parent["bodyBytes"])
        or (
            proof.get("bodyRangeSetSha256") is not None
            and proof.get("bodyRangeSetSha256") != parent["bodyRangeSetSha256"]
        )
    ):
        raise ResealError(f"function proof identity differs from 10R: {entity}")
    expected_hash = str(proof.get("peBodySha256", ""))
    if expected_hash:
        actual = sha256_bytes(pe_bytes(image, layout, entry, size))
        if actual != expected_hash:
            raise ResealError(f"function proof PE bytes differ: {entity}")
    elif require_body_hash:
        raise ResealError(f"C1 proof lacks a PE body hash: {entity}")
    return parent


def _candidate_pack_reference(contract: dict[str, str]) -> list[tuple[str, str]]:
    result: list[tuple[str, str]] = []
    for token in str(contract.get("evidenceRefs", "")).split(";"):
        match = re.search(
            r"(?:^|[\\/])local-lab[\\/]([^\\/]+)[\\/]FORMAL-PACK\.json"
            r"#sha256=([0-9a-f]{64})$",
            token,
            re.IGNORECASE,
        )
        if match:
            result.append((match.group(1), match.group(2).lower()))
    return result


def _pack_ref(stamp_row: dict[str, object]) -> str:
    return f"{stamp_row['path']}#sha256={stamp_row['sha256']}"


def _append_evidence_token(row: dict[str, str], *tokens: str) -> None:
    row["evidenceRefs"] = union_tokens(row.get("evidenceRefs", ""), *tokens)


def derive_projection() -> dict[str, object]:
    fixed = validate_fixed_inputs()
    parent_rows = campaign_rows(fixed["parent"])
    candidate_rows = campaign_rows(fixed["candidate"])
    historical_rows = campaign_rows(fixed["historical"])
    police_ready = read_json(fixed["police"] / "campaign.ready.json")

    parent_maps = {
        name: keyed(rows, LEDGER_KEYS[name], f"10R {name}")
        for name, rows in parent_rows.items()
    }
    candidate_maps = {
        name: keyed(rows, LEDGER_KEYS[name], f"Gen73 {name}")
        for name, rows in candidate_rows.items()
    }
    historical_maps = {
        name: keyed(rows, LEDGER_KEYS[name], f"historical Gen10 {name}")
        for name, rows in historical_rows.items()
    }
    if set(parent_maps["functions"]) != set(candidate_maps["functions"]):
        raise ResealError("Gen73 function entity set differs from 10R")
    if set(parent_maps["residuals"]) != set(candidate_maps["residuals"]):
        raise ResealError("Gen73 residual entity set differs from 10R")

    image = fixed["specimen"].read_bytes()
    layout = _pe_sections(image)
    pack_values: dict[str, dict] = {}
    pack_stamps: dict[str, dict[str, object]] = {}
    pack_profiles: dict[str, str] = {}
    for profile, names in (
        ("residual", RESIDUAL_PACKS),
        ("name", NAME_PACKS),
        ("c1", C1_PACKS),
        ("disposition", DISPOSITION_PACKS),
    ):
        for name in names:
            if name in pack_values:
                raise ResealError(f"proof pack is selected twice: {name}")
            _path, value, stamp_row = load_pack(name, profile)
            pack_values[name] = value
            pack_stamps[name] = stamp_row
            pack_profiles[name] = profile
    if set(pack_values) != set(EXPECTED_PACK_STAMPS):
        raise ResealError("selected proof-pack set differs from the reviewed identity allowlist")

    output_rows = copy.deepcopy(parent_rows)
    output_maps = {
        name: keyed(rows, LEDGER_KEYS[name], f"projection {name}")
        for name, rows in output_rows.items()
    }
    parent_contracts_by_entity = keyed(
        parent_rows["contracts"], "entityKey", "10R contracts by entity"
    )
    candidate_contracts_by_entity = keyed(
        candidate_rows["contracts"], "entityKey", "Gen73 contracts by entity"
    )
    output_contracts_by_entity = keyed(
        output_rows["contracts"], "entityKey", "projection contracts by entity"
    )
    claims: list[dict[str, str]] = []

    residual_proofs: dict[tuple[str, str], dict] = {}
    residual_proof_records = 0
    for name in RESIDUAL_PACKS:
        for index, proof in enumerate(pack_values[name]["proofs"]):
            if not isinstance(proof, dict):
                raise ResealError(f"residual pack contains a non-object proof: {name}[{index}]")
            _validate_residual_proof(
                proof,
                image,
                layout,
                parent_maps["residuals"],
            )
            entity = str(proof["entityKey"])
            residual_proofs[(name, entity)] = proof
            if proof["proposed"].get("requiresQuestionSupersession"):
                residual_proof_records += 1
    if residual_proof_records != 6103:
        raise ResealError(f"selected residual proof count differs: {residual_proof_records}")

    terminal_entities: dict[str, tuple[str, dict]] = {}
    for contract in candidate_rows["contracts"]:
        entity = contract["entityKey"]
        if contract.get("entityKind") != "TEXT_RESIDUAL":
            continue
        selected = [
            (name, residual_proofs[(name, entity)])
            for name, _old_hash in _candidate_pack_reference(contract)
            if (name, entity) in residual_proofs
        ]
        if len(selected) > 1:
            raise ResealError(f"Gen73 residual cites multiple terminal proof packs: {entity}")
        if selected:
            terminal_entities[entity] = selected[0]
    if len(terminal_entities) != 6082:
        raise ResealError(f"terminal residual projection count differs: {len(terminal_entities)}")

    reopened = police_ready.get("advance", {}).get("reopened")
    if not isinstance(reopened, list) or len(reopened) != 21:
        raise ResealError("Gen25 police receipt does not contain the exact 21-row disposition")
    police_entities = {str(row.get("entityKey", "")): row for row in reopened}
    if len(police_entities) != 21:
        raise ResealError("Gen25 police entity set is malformed")
    reclosed = set(police_entities) & set(terminal_entities)
    preserved_police = set(police_entities) - set(terminal_entities)
    if len(reclosed) != 1 or len(preserved_police) != 20:
        raise ResealError("police disposition must preserve 20 and later reclose exactly one")
    reclosed_entity = next(iter(reclosed))
    if ":0x005344FC-0x005345D0" not in reclosed_entity:
        raise ResealError("unexpected police entity was reclosed by later proof")

    for entity, (pack_name, proof) in sorted(terminal_entities.items()):
        proposed = proof["proposed"]
        candidate_residual = candidate_maps["residuals"][entity]
        candidate_contract = candidate_contracts_by_entity[entity]
        parent_residual = parent_maps["residuals"][entity]
        parent_contract = parent_contracts_by_entity[entity]
        output_residual = output_maps["residuals"][entity]
        output_contract = output_contracts_by_entity[entity]
        question_ids = [value for value in parent_contract["questionIds"].split(";") if value]
        if len(question_ids) != 1 or parent_residual["questionIds"] != question_ids[0]:
            raise ResealError(f"terminal residual lacks one exact 10R question: {entity}")
        question = output_maps["questions"].get(question_ids[0])
        if question is None or question.get("state") != "OPEN":
            raise ResealError(f"terminal residual question is not OPEN in 10R: {entity}")
        for field in (
            "classification",
            "classificationVerdict",
            "terminalState",
            "campaignState",
            "bytePattern",
        ):
            if str(candidate_residual.get(field, "")) != str(proposed.get(field, "")):
                raise ResealError(f"Gen73 residual field exceeds proof {field}: {entity}")
            output_residual[field] = str(proposed[field])
        output_residual["lever"] = "NONE"
        output_residual["cheapestFalsifier"] = candidate_residual["cheapestFalsifier"]
        output_residual["questionIds"] = parent_residual["questionIds"]
        output_residual["lastMeasurementDate"] = candidate_residual["lastMeasurementDate"]

        expected_contract_state = str(
            proposed.get("contractState") or proposed.get("terminalState")
        )
        if candidate_contract.get("contractState") != expected_contract_state:
            raise ResealError(f"Gen73 terminal contract state exceeds proof: {entity}")
        output_contract["contractState"] = expected_contract_state
        output_contract["authorVerdict"] = "STATIC_FORMAL_PROOF"
        output_contract["refuterVerdict"] = "SURVIVED"
        output_contract["questionIds"] = parent_contract["questionIds"]
        proof_ref = _pack_ref(pack_stamps[pack_name])
        pe_ref = f"pe-span#sha256={proof['peBytesSha256']}"
        _append_evidence_token(output_contract, proof_ref, pe_ref)
        output_contract["cheapestFalsifier"] = candidate_contract["cheapestFalsifier"]
        output_contract["remainingUncertainty"] = candidate_contract["remainingUncertainty"]
        output_contract["lastMeasurementDate"] = candidate_contract["lastMeasurementDate"]

        question["state"] = "CLOSED_SURVIVED"
        question["attemptCount"] = str(int(question.get("attemptCount", "0")) + 1)
        question["lastOutcome"] = "SURVIVED"
        question["lastMeasurementDate"] = candidate_maps["questions"][question_ids[0]][
            "lastMeasurementDate"
        ]
        claims.append(
            {
                "entityKey": entity,
                "claimKind": "TERMINAL_RESIDUAL",
                "disposition": "ADMITTED",
                "fields": ";".join(
                    [
                        "residual.classification",
                        "residual.classificationVerdict",
                        "residual.terminalState",
                        "residual.campaignState",
                        "contract.contractState",
                        "question.state",
                    ]
                ),
                "evidenceRefs": union_tokens(proof_ref, pe_ref),
                "reason": "current proof pack and pristine span close the exact 10R question",
                "contractId": parent_contract["contractId"],
                "questionId": question_ids[0],
                "terminalState": output_residual["terminalState"],
                "measuredAtUtc": candidate_contract["lastMeasurementDate"],
            }
        )

    for entity in sorted(preserved_police):
        if (
            output_maps["residuals"][entity] != parent_maps["residuals"][entity]
            or output_contracts_by_entity[entity] != parent_contracts_by_entity[entity]
        ):
            raise ResealError(f"police-open entity was modified: {entity}")
        row = police_entities[entity]
        candidate_residual = candidate_maps["residuals"][entity]
        claims.append(
            {
                "entityKey": entity,
                "claimKind": "POLICE_OPEN_DISPOSITION",
                "disposition": "PRESERVE_10R_OPEN",
                "fields": "none",
                "evidenceRefs": f"{POLICE_RELATIVE.as_posix()}/campaign.ready.json#sha256={POLICE_READY_SHA256}",
                "reason": union_tokens(
                    str(row.get("reason", "")),
                    candidate_residual.get("cheapestFalsifier", ""),
                ),
                "contractId": parent_contracts_by_entity[entity]["contractId"],
                "questionId": parent_contracts_by_entity[entity]["questionIds"],
                "terminalState": "OPEN_CLASSIFICATION",
                "measuredAtUtc": police_ready["advance"]["measuredAtUtc"],
            }
        )

    name_claims: dict[str, tuple[str, dict]] = {}
    for name in NAME_PACKS:
        weak = name == "fun-weak-native-name-align-20260805-v1"
        for index, proof in enumerate(pack_values[name]["proofs"]):
            if not isinstance(proof, dict):
                raise ResealError(f"name pack contains a non-object proof: {name}[{index}]")
            _validate_function_identity(
                proof,
                image,
                layout,
                parent_maps["functions"],
                require_body_hash=False,
            )
            proposed = proof.get("proposed")
            if not isinstance(proposed, dict) or not proposed.get("currentName"):
                raise ResealError(f"name proof lacks a field-level proposal: {name}[{index}]")
            entity = str(proof["entityKey"])
            if entity in name_claims:
                raise ResealError(f"function has multiple name proof owners: {entity}")
            if weak and proposed.get("rebuildState") != "NOT_READY":
                raise ResealError(f"weak native proof exceeds name-only authority: {entity}")
            name_claims[entity] = (name, proof)
    if len(name_claims) != 932:
        raise ResealError(f"selected name proof count differs: {len(name_claims)}")

    for entity, (pack_name, proof) in sorted(name_claims.items()):
        proposed = proof["proposed"]
        candidate_function = candidate_maps["functions"][entity]
        output_function = output_maps["functions"][entity]
        output_contract = output_contracts_by_entity[entity]
        if candidate_function.get("currentName") != proposed.get("currentName"):
            raise ResealError(f"Gen73 name differs from current proof: {entity}")
        output_function["currentName"] = str(proposed["currentName"])
        output_function["nameClass"] = str(proposed.get("nameClass") or "NAMED")
        if proposed.get("nativeRegistryStatus"):
            output_function["nativeRegistryStatus"] = str(proposed["nativeRegistryStatus"])
        evidence_token = str(proposed.get("evidenceAppend", ""))
        output_function["evidenceStates"] = union_tokens(
            output_function.get("evidenceStates", ""), evidence_token
        )
        output_function["cheapestFalsifier"] = str(proposed["cheapestFalsifier"])
        output_function["lastMeasurementDate"] = candidate_function["lastMeasurementDate"]
        output_contract["currentName"] = output_function["currentName"]
        proof_ref = _pack_ref(pack_stamps[pack_name])
        _append_evidence_token(output_contract, proof_ref, evidence_token)
        output_contract["lastMeasurementDate"] = candidate_contracts_by_entity[entity][
            "lastMeasurementDate"
        ]
        claims.append(
            {
                "entityKey": entity,
                "claimKind": "FUNCTION_NAME",
                "disposition": "ADMITTED_NAME_ONLY",
                "fields": "function.currentName;function.nameClass;contract.currentName",
                "evidenceRefs": union_tokens(proof_ref, evidence_token),
                "reason": "exact current name pack; no semantic contract promotion",
                "contractId": output_contract["contractId"],
                "questionId": output_contract["questionIds"],
                "terminalState": output_contract["contractState"],
                "measuredAtUtc": output_function["lastMeasurementDate"],
            }
        )

    c1_claims: dict[str, tuple[str, dict]] = {}
    for name in C1_PACKS:
        for index, proof in enumerate(pack_values[name]["proofs"]):
            if not isinstance(proof, dict):
                raise ResealError(f"C1 pack contains a non-object proof: {name}[{index}]")
            if bool(proof.get("holdApply")):
                continue
            require_body = str(proof.get("entityKey")) != APPLY_DAMAGE_ENTITY
            _validate_function_identity(
                proof,
                image,
                layout,
                parent_maps["functions"],
                require_body_hash=require_body,
            )
            if (
                proof.get("proposedSemanticGrade") != "C1_CANDIDATE_PARTIAL"
                or proof.get("proposedContractState") != "CANDIDATE_NEEDS_REFUTER"
                or proof.get("proposedRefuterVerdict") != "UNSCORED"
            ):
                raise ResealError(f"C1 proof exceeds the candidate boundary: {name}[{index}]")
            entity = str(proof["entityKey"])
            previous = c1_claims.get(entity)
            if previous is not None:
                raise ResealError(f"function has multiple admitted C1 proof owners: {entity}")
            c1_claims[entity] = (name, proof)
    if len(c1_claims) != 216:
        raise ResealError(f"selected C1 entity count differs: {len(c1_claims)}")

    semantic_fields = (
        "receiver",
        "inputs",
        "returns",
        "writes",
        "sideEffects",
        "preconditions",
        "failureModes",
    )
    for entity, (pack_name, proof) in sorted(c1_claims.items()):
        candidate_function = candidate_maps["functions"][entity]
        candidate_contract = candidate_contracts_by_entity[entity]
        parent_contract = parent_contracts_by_entity[entity]
        output_function = output_maps["functions"][entity]
        output_contract = output_contracts_by_entity[entity]
        if entity != APPLY_DAMAGE_ENTITY and (
            candidate_contract.get("refuterVerdict") != "UNSCORED"
            or candidate_contract.get("semanticGrade") != "C1_CANDIDATE_PARTIAL"
        ):
            raise ResealError(f"Gen73 C1 row claims a stronger verdict: {entity}")
        output_function["currentName"] = str(proof["currentName"])
        output_function["nameClass"] = "NAMED"
        candidate_tokens = [
            token
            for token in candidate_function.get("evidenceStates", "").split(";")
            if token
            and token not in parent_maps["functions"][entity]["evidenceStates"].split(";")
            and (
                token.startswith("CAMPAIGN_C1_")
                or token == "CAMPAIGN_NATIVE_IDENTITY_RESOLVE_C1"
            )
        ]
        output_function["evidenceStates"] = union_tokens(
            output_function.get("evidenceStates", ""), *candidate_tokens
        )
        output_function["resolutionState"] = "CANDIDATE_CONTRACT"
        output_function["semanticGrade"] = "C1_CANDIDATE_PARTIAL"
        output_function["cheapestFalsifier"] = (
            str(pack_values[pack_name].get("cheapestFalsifier") or candidate_function["cheapestFalsifier"])
        )
        output_function["lastMeasurementDate"] = candidate_function["lastMeasurementDate"]

        output_contract["currentName"] = output_function["currentName"]
        output_contract["contractState"] = "CANDIDATE_NEEDS_REFUTER"
        output_contract["semanticGrade"] = "C1_CANDIDATE_PARTIAL"
        for field in semantic_fields:
            output_contract[field] = str(proof[field])
        output_contract["refuterVerdict"] = "UNSCORED"
        output_contract["questionIds"] = parent_contract["questionIds"]
        proof_ref = _pack_ref(pack_stamps[pack_name])
        output_contract["evidenceRefs"] = union_tokens(parent_contract["evidenceRefs"], proof_ref)
        output_contract["lastMeasurementDate"] = candidate_contract["lastMeasurementDate"]
        if entity == APPLY_DAMAGE_ENTITY:
            output_contract["authorVerdict"] = "SUPPORTED_BY_PE_OR_RUNTIME"
            output_contract["runtimeVerdict"] = "MEASURED_BOUNDED_PATH"
            output_contract["cheapestFalsifier"] = (
                "Independent can-fail refuter scoped to ApplyDamage primary claim"
            )
            output_contract["remainingUncertainty"] = str(proof["scopeNote"])
            output_function["evidenceStates"] = union_tokens(
                output_function["evidenceStates"], "CAMPAIGN_C1_RUNTIME_MEASURED"
            )
        else:
            output_contract["authorVerdict"] = candidate_contract["authorVerdict"]
            output_contract["runtimeVerdict"] = candidate_contract["runtimeVerdict"]
            output_contract["cheapestFalsifier"] = candidate_contract["cheapestFalsifier"]
            output_contract["remainingUncertainty"] = str(
                proof.get("remaining") or candidate_contract["remainingUncertainty"]
            )
        claims.append(
            {
                "entityKey": entity,
                "claimKind": "FUNCTION_C1",
                "disposition": (
                    "ADMITTED_WITH_MISSING_RAW_LOG_LIMITATION"
                    if entity == APPLY_DAMAGE_ENTITY
                    else "ADMITTED"
                ),
                "fields": "function.semanticGrade;contract.C1",
                "evidenceRefs": proof_ref,
                "reason": (
                    "current C1 pack plus surviving runtime-contract summary; raw logs absent"
                    if entity == APPLY_DAMAGE_ENTITY
                    else "current C1 pack and pristine body identity"
                ),
                "contractId": output_contract["contractId"],
                "questionId": output_contract["questionIds"],
                "terminalState": output_contract["contractState"],
                "measuredAtUtc": output_contract["lastMeasurementDate"],
            }
        )

    # Generated coherence is derived from the admitted function name, never from
    # the internally inconsistent candidate contract row.
    for entity, function in output_maps["functions"].items():
        contract = output_contracts_by_entity[entity]
        if contract["currentName"] != function["currentName"]:
            contract["currentName"] = function["currentName"]
        if contract["currentName"] != function["currentName"]:
            raise ResealError(f"function/contract name coherence failed: {entity}")

    nearclone = next(
        (
            entity
            for entity, row in candidate_maps["functions"].items()
            if row.get("entryVa") == "0x0056473e"
        ),
        None,
    )
    if nearclone is None or output_maps["functions"][nearclone] != parent_maps["functions"][nearclone]:
        raise ResealError("NearClone quarantine does not preserve exact 10R")
    claims.append(
        {
            "entityKey": nearclone,
            "claimKind": "FUNCTION_NAME",
            "disposition": "QUARANTINED_MISSING_CURRENT_PROOF",
            "fields": "none",
            "evidenceRefs": "candidate-only#sha256=dd3427e672357e10b2f0d5a538c0ff84e7af9f92e62919ef5303f000e0594e95",
            "reason": "no current exact source pack exists",
            "contractId": output_contracts_by_entity[nearclone]["contractId"],
            "questionId": output_contracts_by_entity[nearclone]["questionIds"],
            "terminalState": output_contracts_by_entity[nearclone]["contractState"],
            "measuredAtUtc": candidate_maps["functions"][nearclone]["lastMeasurementDate"],
        }
    )

    # Candidate C1/C2 excess is recorded, never projected.
    excluded_c1 = {
        entity
        for entity, row in candidate_maps["functions"].items()
        if row.get("semanticGrade") == "C1_CANDIDATE_PARTIAL"
        and entity not in c1_claims
    }
    if len(excluded_c1) != 7:
        raise ResealError(f"unsupported wrapper C1 set differs: {len(excluded_c1)}")
    for entity in sorted(excluded_c1):
        if output_maps["functions"][entity]["semanticGrade"] != "OPAQUE":
            raise ResealError(f"name-only wrapper was semantically promoted: {entity}")
        claims.append(
            {
                "entityKey": entity,
                "claimKind": "FUNCTION_C1",
                "disposition": "QUARANTINED_UNSUPPORTED_WRAPPER_C1",
                "fields": "none",
                "evidenceRefs": "candidate-native-contract#sha256=129bf0192a18539943a12f36b2c99c9b2ba78033309127b5f875f0eece49c076",
                "reason": "name proof exists; no current C1 body/contract proof exists",
                "contractId": output_contracts_by_entity[entity]["contractId"],
                "questionId": output_contracts_by_entity[entity]["questionIds"],
                "terminalState": output_contracts_by_entity[entity]["contractState"],
                "measuredAtUtc": candidate_maps["functions"][entity]["lastMeasurementDate"],
            }
        )
    claims.append(
        {
            "entityKey": APPLY_DAMAGE_ENTITY,
            "claimKind": "FUNCTION_C2",
            "disposition": "QUARANTINED_REFUTER_INCOHERENT",
            "fields": "none",
            "evidenceRefs": _pack_ref(pack_stamps["c2-applydamage-primary-20260805-v1"]),
            "reason": "current C1 is admitted; C2 process authority and holdouts do not close",
            "contractId": output_contracts_by_entity[APPLY_DAMAGE_ENTITY]["contractId"],
            "questionId": output_contracts_by_entity[APPLY_DAMAGE_ENTITY]["questionIds"],
            "terminalState": output_contracts_by_entity[APPLY_DAMAGE_ENTITY]["contractState"],
            "measuredAtUtc": output_contracts_by_entity[APPLY_DAMAGE_ENTITY]["lastMeasurementDate"],
        }
    )

    modified = {}
    for name in ("functions", "residuals", "questions", "scenarios", "levers", "contracts", "supersessions"):
        modified[name] = sum(
            1
            for key, parent in parent_maps[name].items()
            if output_maps[name].get(key) != parent
        )
    if modified != {
        "functions": EXPECTED_MODIFIED["functions"],
        "residuals": EXPECTED_MODIFIED["residuals"],
        "questions": EXPECTED_MODIFIED["questions"],
        "scenarios": 0,
        "levers": 0,
        "contracts": EXPECTED_MODIFIED["contracts"],
        "supersessions": 0,
    }:
        raise ResealError(f"projection modified-row census differs: {modified}")
    if output_rows["adjudications"] != parent_rows["adjudications"]:
        raise ResealError("projection must preserve exact 10R adjudications before generation")
    if output_rows["supersessions"] != parent_rows["supersessions"]:
        raise ResealError("projection must preserve exact 10R supersessions")

    recovery_contract_ids: set[str] = set()
    for contract_id, parent_contract in parent_maps["contracts"].items():
        historical_contract = historical_maps["contracts"][contract_id]
        differing = {
            field
            for field in parent_contract
            if parent_contract.get(field, "") != historical_contract.get(field, "")
        }
        if differing:
            if differing != {"evidenceRefs"}:
                raise ResealError(
                    f"10R recovery contract differs outside evidenceRefs: {contract_id}: {differing}"
                )
            recovery_contract_ids.add(contract_id)
            parent_tokens = set(parent_contract["evidenceRefs"].split(";"))
            output_tokens = set(output_maps["contracts"][contract_id]["evidenceRefs"].split(";"))
            if not parent_tokens <= output_tokens:
                raise ResealError(f"10R recovery provenance was dropped: {contract_id}")
            if not any("8a83b9617de616d6" in token for token in output_tokens):
                raise ResealError(f"rederived Atomic14 identity is absent: {contract_id}")
            if any("a504c24b1eab555d" in token for token in output_tokens):
                raise ResealError(f"lost historical Atomic14 identity was reintroduced: {contract_id}")
    if len(recovery_contract_ids) != 29:
        raise ResealError(f"10R recovery contract census differs: {len(recovery_contract_ids)}")

    grade_counts = Counter(row["semanticGrade"] for row in output_rows["functions"])
    if grade_counts != Counter({"OPAQUE": 7904, "C1_CANDIDATE_PARTIAL": 216, "C2_BOUNDED_RUNTIME": 4}):
        raise ResealError(f"function semantic-grade census differs: {grade_counts}")

    historical_adjudications = historical_maps["adjudications"]
    source_claims = [
        row
        for key, row in candidate_maps["adjudications"].items()
        if key not in historical_adjudications
    ]
    if len(source_claims) != 7294:
        raise ResealError(f"historical source-claim census differs: {len(source_claims)}")

    claim_entities = {row["entityKey"] for row in claims if row["disposition"].startswith("ADMITTED")}
    source_dispositions: list[dict[str, str]] = []
    for row in sorted(source_claims, key=lambda item: item["adjudicationId"]):
        entity = row["entityKey"]
        schema = row["overlaySchema"]
        if entity in police_entities:
            if schema == "bea.re.police-reopen.v1":
                disposition = (
                    "POLICE_REOPEN_OVERRIDDEN_BY_LATER_PROOF"
                    if entity == reclosed_entity
                    else "POLICE_PRESERVE_PARENT_OPEN"
                )
            elif entity == reclosed_entity and schema == (
                "bea.re.open-residual-gen26-unit-split-formal-pack.v1"
            ):
                disposition = "READMITTED_CURRENT_PROOF"
            else:
                disposition = "REFUTED_BY_POLICE"
        elif entity == nearclone:
            disposition = "MISSING_SOURCE_QUARANTINE"
        elif entity == APPLY_DAMAGE_ENTITY and "c2-applydamage" in schema:
            disposition = "REJECT_C2_APPLYDAMAGE"
        elif entity in excluded_c1 and schema == "bea.re.native-contract-candidate.v1":
            disposition = "UNSUPPORTED_C1_WRAPPER"
        elif entity in excluded_c1 and schema == "bea.re.c1-damage-path-entry-evidence.v1":
            disposition = "UNSUPPORTED_DAMAGE_PATH_C1"
        elif entity in claim_entities:
            disposition = "READMITTED_CURRENT_PROOF"
        else:
            disposition = "PRESERVE_10R_OR_QUARANTINE"
        source_dispositions.append(
            {
                "sourceAdjudicationId": row["adjudicationId"],
                "entityKey": entity,
                "overlaySchema": schema,
                "overlayReadySha256": row["overlayReadySha256"],
                "sourceVerdict": row["refuterVerdict"],
                "disposition": disposition,
                "reason": "candidate source row is never copied; effective claim is selected independently",
            }
        )
    source_disposition_counts = Counter(row["disposition"] for row in source_dispositions)
    expected_source_dispositions = Counter(
        {
            "READMITTED_CURRENT_PROOF": 7241,
            "REFUTED_BY_POLICE": 21,
            "POLICE_PRESERVE_PARENT_OPEN": 20,
            "POLICE_REOPEN_OVERRIDDEN_BY_LATER_PROOF": 1,
            "UNSUPPORTED_C1_WRAPPER": 7,
            "UNSUPPORTED_DAMAGE_PATH_C1": 2,
            "REJECT_C2_APPLYDAMAGE": 1,
            "MISSING_SOURCE_QUARANTINE": 1,
        }
    )
    if source_disposition_counts != expected_source_dispositions:
        raise ResealError(
            f"candidate source-disposition census differs: {source_disposition_counts}"
        )

    return {
        "fixed": fixed,
        "parentRows": parent_rows,
        "candidateRows": candidate_rows,
        "historicalRows": historical_rows,
        "outputRows": output_rows,
        "outputMaps": output_maps,
        "claims": sorted(claims, key=lambda row: (row["entityKey"], row["claimKind"])),
        "sourceDispositions": source_dispositions,
        "sourceDispositionCounts": dict(sorted(source_disposition_counts.items())),
        "packStamps": [pack_stamps[name] for name in sorted(pack_stamps)],
        "modified": modified,
        "terminalEntities": terminal_entities,
        "policeEntities": police_entities,
        "preservedPolice": preserved_police,
        "reclosedPolice": reclosed_entity,
        "nameClaims": name_claims,
        "c1Claims": c1_claims,
        "recoveryContractIds": recovery_contract_ids,
    }


def _json_cell(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _render_tsv(schema: str, columns: tuple[str, ...], rows: list[dict[str, object]]) -> bytes:
    lines = [f"# {schema}", "\t".join(columns)]
    for row in rows:
        values: list[str] = []
        for column in columns:
            value = str(row.get(column, ""))
            if "\t" in value or "\r" in value or "\n" in value:
                raise ResealError(f"TSV value contains a control delimiter: {column}")
            values.append(value)
        lines.append("\t".join(values))
    return ("\n".join(lines) + "\n").encode("utf-8")


def _canonical_rows_sha256(rows: list[dict[str, str]], key: str) -> str:
    payload = "".join(
        canonical_row(row) + "\n" for row in sorted(rows, key=lambda item: item[key])
    ).encode("utf-8")
    return sha256_bytes(payload)


def _row_delta_census(
    baseline_rows: dict[str, list[dict[str, str]]],
    candidate_rows: dict[str, list[dict[str, str]]],
) -> dict[str, int]:
    result: dict[str, int] = {}
    for family, key_name in LEDGER_KEYS.items():
        baseline = keyed(baseline_rows[family], key_name, f"delta baseline {family}")
        candidate = keyed(candidate_rows[family], key_name, f"delta candidate {family}")
        result[family] = sum(
            baseline.get(key) != candidate.get(key) for key in set(baseline) | set(candidate)
        )
    return result


def candidate_field_delta(derived: dict[str, object]) -> list[dict[str, object]]:
    result: list[dict[str, object]] = []
    row_census: dict[str, int] = {}
    field_census: dict[str, int] = {}
    for family, key_name in LEDGER_KEYS.items():
        baseline = keyed(derived["parentRows"][family], key_name, f"10R delta {family}")
        candidate = keyed(derived["candidateRows"][family], key_name, f"Gen73 delta {family}")
        effective = keyed(derived["outputRows"][family], key_name, f"effective delta {family}")
        changed_rows = 0
        changed_fields = 0
        for row_key in sorted(set(baseline) | set(candidate)):
            base_row = baseline.get(row_key)
            candidate_row = candidate.get(row_key)
            effective_row = effective.get(row_key)
            if base_row == candidate_row:
                continue
            changed_rows += 1
            if base_row is None or candidate_row is None:
                fields = ("__row__",)
            else:
                fields = tuple(
                    sorted(
                        field
                        for field in set(base_row) | set(candidate_row)
                        if base_row.get(field, "") != candidate_row.get(field, "")
                    )
                )
            for field in fields:
                changed_fields += 1
                if field == "__row__":
                    base_value: object = base_row if base_row is not None else None
                    candidate_value: object = candidate_row if candidate_row is not None else None
                    effective_value: object = effective_row if effective_row is not None else None
                else:
                    base_value = base_row.get(field, "") if base_row is not None else None
                    candidate_value = (
                        candidate_row.get(field, "") if candidate_row is not None else None
                    )
                    effective_value = (
                        effective_row.get(field, "") if effective_row is not None else None
                    )
                if base_row is None and candidate_row is not None and effective_row is None:
                    disposition = "QUARANTINE_CANDIDATE_ROW"
                    reason = "candidate-only row is not carried into the effective projection"
                elif effective_value == base_value:
                    disposition = (
                        "PRESERVE_10R_REMOVED_BY_CANDIDATE"
                        if candidate_row is None
                        else "PRESERVE_10R"
                    )
                    reason = "candidate value was not admitted by the current proof policy"
                elif effective_value == candidate_value:
                    disposition = "ADMIT_CURRENT_PROOF_MATCHES_CANDIDATE"
                    reason = "current allowlisted proof independently produces the candidate value"
                else:
                    disposition = "DERIVE_CURRENT_PROOF_OR_COHERENCE"
                    reason = "effective value is derived from current proof or generated coherence"
                closure_id = "Z-" + sha256_bytes(
                    "|".join((PARENT_READY_SHA256, family, row_key, field)).encode("utf-8")
                )[:16]
                result.append(
                    {
                        "closureId": closure_id,
                        "family": family,
                        "rowKey": row_key,
                        "fieldName": field,
                        "baselinePresent": str(base_row is not None).lower(),
                        "candidatePresent": str(candidate_row is not None).lower(),
                        "effectivePresent": str(effective_row is not None).lower(),
                        "baselineJson": _json_cell(base_value),
                        "candidateJson": _json_cell(candidate_value),
                        "effectiveJson": _json_cell(effective_value),
                        "disposition": disposition,
                        "reason": reason,
                    }
                )
        row_census[family] = changed_rows
        field_census[family] = changed_fields
    if row_census != EXPECTED_PARENT_CANDIDATE_ROW_DELTAS:
        raise ResealError(f"10R-to-Gen73 row-delta census differs: {row_census}")
    if field_census != EXPECTED_PARENT_CANDIDATE_FIELD_DELTAS:
        raise ResealError(f"10R-to-Gen73 field-delta census differs: {field_census}")
    if len({row["closureId"] for row in result}) != len(result):
        raise ResealError("candidate field closure IDs collide")
    return result


def _police_disposition_rows(derived: dict[str, object]) -> list[dict[str, object]]:
    parent_question_ids = {
        row["questionId"] for row in derived["parentRows"]["questions"]
    }
    candidate_questions_by_entity: dict[str, list[dict[str, str]]] = {}
    for row in derived["candidateRows"]["questions"]:
        if row["questionId"] not in parent_question_ids:
            candidate_questions_by_entity.setdefault(row["entityKey"], []).append(row)
    rows: list[dict[str, object]] = []
    for entity, police in sorted(derived["policeEntities"].items()):
        questions = candidate_questions_by_entity.get(entity, [])
        if len(questions) != 1:
            raise ResealError(f"police entity lacks one exact candidate successor question: {entity}")
        question = questions[0]
        disposition = (
            "REOPEN_OVERRIDDEN_BY_LATER_ADMISSIBLE_PROOF"
            if entity == derived["reclosedPolice"]
            else "PRESERVE_EXACT_10R_OPEN_FRONTIER"
        )
        rows.append(
            {
                "entityKey": entity,
                "startVa": police.get("startVa", ""),
                "endVa": police.get("endVa", ""),
                "policeReason": police.get("reason", ""),
                "disposition": disposition,
                "candidateQuestionId": question["questionId"],
                "candidateQuestion": question["question"],
                "candidateRecommendedInstrument": question["recommendedInstrument"],
                "candidateCheapestFalsifier": question["cheapestFalsifier"],
                "candidateState": question["state"],
            }
        )
    if Counter(row["disposition"] for row in rows) != Counter(
        {
            "PRESERVE_EXACT_10R_OPEN_FRONTIER": 20,
            "REOPEN_OVERRIDDEN_BY_LATER_ADMISSIBLE_PROOF": 1,
        }
    ):
        raise ResealError("police disposition census differs")
    return rows


def _semantic_census(derived: dict[str, object]) -> dict[str, object]:
    rows = derived["outputRows"]
    return {
        "functionSemanticGrade": dict(
            sorted(Counter(row["semanticGrade"] for row in rows["functions"]).items())
        ),
        "functionResolutionState": dict(
            sorted(Counter(row["resolutionState"] for row in rows["functions"]).items())
        ),
        "residualTerminalState": dict(
            sorted(Counter(row["terminalState"] for row in rows["residuals"]).items())
        ),
        "residualCampaignState": dict(
            sorted(Counter(row["campaignState"] for row in rows["residuals"]).items())
        ),
        "questionState": dict(
            sorted(Counter(row["state"] for row in rows["questions"]).items())
        ),
        "contractState": dict(
            sorted(Counter(row["contractState"] for row in rows["contracts"]).items())
        ),
        "contractSemanticGrade": dict(
            sorted(Counter(row["semanticGrade"] for row in rows["contracts"]).items())
        ),
        "contractRefuterVerdict": dict(
            sorted(Counter(row["refuterVerdict"] for row in rows["contracts"]).items())
        ),
    }


def build_closure_artifacts(derived: dict[str, object]) -> dict[str, bytes]:
    field_delta = candidate_field_delta(derived)
    police = _police_disposition_rows(derived)
    claims = derived["claims"]
    source = derived["sourceDispositions"]
    packs = derived["packStamps"]
    return {
        "effective-claims.tsv": _render_tsv(
            "bea.re.candidate-chain-post-loss-effective-claims.v1",
            (
                "entityKey", "claimKind", "disposition", "fields", "evidenceRefs",
                "reason", "contractId", "questionId", "terminalState", "measuredAtUtc",
            ),
            claims,
        ),
        "source-dispositions.tsv": _render_tsv(
            "bea.re.candidate-chain-source-dispositions.v1",
            (
                "sourceAdjudicationId", "entityKey", "overlaySchema", "overlayReadySha256",
                "sourceVerdict", "disposition", "reason",
            ),
            source,
        ),
        "candidate-field-delta.tsv": _render_tsv(
            "bea.re.candidate-chain-field-closure.v1",
            (
                "closureId", "family", "rowKey", "fieldName", "baselinePresent",
                "candidatePresent", "effectivePresent", "baselineJson", "candidateJson",
                "effectiveJson", "disposition", "reason",
            ),
            field_delta,
        ),
        "pack-manifest.tsv": _render_tsv(
            "bea.re.candidate-chain-proof-pack-manifest.v1",
            (
                "path", "bytes", "sha256", "schema", "status", "profile", "proofCount",
                "historicalHoldGenerationApply", "specimenSha256",
            ),
            packs,
        ),
        "police-dispositions.tsv": _render_tsv(
            "bea.re.candidate-chain-police-dispositions.v1",
            (
                "entityKey", "startVa", "endVa", "policeReason", "disposition",
                "candidateQuestionId", "candidateQuestion", "candidateRecommendedInstrument",
                "candidateCheapestFalsifier", "candidateState",
            ),
            police,
        ),
    }


def _input_stamps(derived: dict[str, object]) -> dict[str, object]:
    fixed = derived["fixed"]
    return {
        "canonical10R": {
            name: stamp(fixed["parent"] / name, relative_to=REPO_ROOT)
            for name in sorted(PARENT_STAMPS)
        },
        "historicalGen10Baseline": {
            name: stamp(fixed["historical"] / name, relative_to=REPO_ROOT)
            for name in sorted(HISTORICAL_BASELINE_STAMPS)
        },
        "generation73ProjectionOracle": {
            name: stamp(fixed["candidate"] / name, relative_to=REPO_ROOT)
            for name in sorted(CANDIDATE_STAMPS)
        },
        "generation25Police": stamp(
            fixed["police"] / "campaign.ready.json", relative_to=REPO_ROOT
        ),
        "pristineSpecimen": stamp(fixed["specimen"], relative_to=REPO_ROOT),
        "auxiliary": fixed["auxiliary"],
    }


def _receipt_value(
    derived: dict[str, object],
    output_stamps: dict[str, dict[str, object]],
    generated_at: str,
    author_stamp: dict[str, object],
) -> dict[str, object]:
    historical_delta = _row_delta_census(
        derived["historicalRows"], derived["candidateRows"]
    )
    if historical_delta != EXPECTED_HISTORICAL_CANDIDATE_ROW_DELTAS:
        raise ResealError(f"historical Gen10-to-Gen73 row census differs: {historical_delta}")
    parent_delta = _row_delta_census(derived["parentRows"], derived["candidateRows"])
    if parent_delta != EXPECTED_PARENT_CANDIDATE_ROW_DELTAS:
        raise ResealError(f"canonical 10R-to-Gen73 row census differs: {parent_delta}")
    projection = {
        family: {
            "rows": len(derived["outputRows"][family]),
            "canonicalRowsSha256": _canonical_rows_sha256(
                derived["outputRows"][family], LEDGER_KEYS[family]
            ),
        }
        for family in LEDGER_KEYS
    }
    return {
        "schema": SCHEMA,
        "verdict": "READY",
        "claim": "FIELD_SCOPED_RESEAL_PLAN_FROM_CANONICAL_10R",
        "generatedAtUtc": generated_at,
        "author": author_stamp,
        "inputs": _input_stamps(derived),
        "proofPacks": derived["packStamps"],
        "outputs": output_stamps,
        "accounting": {
            "historicalGen10ToGen73ChangedRows": historical_delta,
            "historicalGen10ToGen73ChangedRowsTotal": sum(historical_delta.values()),
            "canonical10RToGen73ChangedRows": parent_delta,
            "canonical10RToGen73ChangedRowsTotal": sum(parent_delta.values()),
            "canonical10RToGen73ChangedFields": EXPECTED_PARENT_CANDIDATE_FIELD_DELTAS,
            "canonical10RToGen73ChangedFieldsTotal": sum(
                EXPECTED_PARENT_CANDIDATE_FIELD_DELTAS.values()
            ),
            "sourceAdjudications": 7294,
            "sourceDispositionCounts": derived["sourceDispositionCounts"],
            "effectiveClaims": len(derived["claims"]),
            "effectiveClaimDispositions": dict(
                sorted(Counter(row["disposition"] for row in derived["claims"]).items())
            ),
        },
        "effectiveProjectionBeforeGeneration11Adjudications": projection,
        "expectedGeneration11": {
            "counts": EXPECTED_COUNTS,
            "modifiedFrom10R": EXPECTED_MODIFIED,
            "newResidualAdjudications": 6082,
            "preserve10RAdjudications": 6,
            "preserve10RSupersessions": 584,
            "functionContractCurrentNameCoherent": True,
            "recoveryContractEvidenceFloorCount": len(derived["recoveryContractIds"]),
        },
        "semanticCensusBeforeGeneration11Adjudications": _semantic_census(derived),
        "policy": {
            "parent": "CANONICAL_10R_ONLY",
            "candidateTip": "PROJECTION_ORACLE_ONLY_NOT_PARENT_NOT_AUTHORITY",
            "packIdentity": "NEW_POST_LOSS_IDENTITY_EXACT_PATH_BYTES_SHA",
            "historicalHoldFlags": "RECORDED_BUT_NOT_BLANKET_AUTHORIZATION",
            "fieldScope": "PROFILE_SPECIFIC_AND_PRISTINE_REVALIDATED",
            "questionPolicy": "PRESERVE_20_EXACT_10R_OPEN_FRONTIERS",
            "candidateAdjudicationIds": "RECORDED_NEVER_REUSED",
            "candidateSupersessionIds": "RECORDED_NEVER_REUSED",
        },
        "limitations": [
            "This is a deterministic closure and projection plan, not a campaign generation.",
            "No game execution, TTD replay, Ghidra mutation, or new runtime experiment occurred.",
            "The historical Atomic14 a504 identity remains lost and is not substituted.",
            "ApplyDamage is admitted only at C1; its direct raw logs remain absent and C2 is rejected.",
            "Twenty police-reopened residuals remain exact 10R OPEN frontier rows.",
            "NearClone 0x0056473e and seven unsupported wrapper C1 grades remain quarantined.",
        ],
    }


def _write_new(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as handle:
        handle.write(data)
        handle.flush()
        os.fsync(handle.fileno())


def verify_closure(root: Path) -> dict[str, object]:
    root = Path(os.path.abspath(root))
    ready_path = require_plain_single_link_file(root / "closure.ready.json", "closure READY")
    receipt = read_json(ready_path)
    generated_at = str(receipt.get("generatedAtUtc", ""))
    try:
        parsed_time = datetime.fromisoformat(generated_at.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ResealError("closure generatedAtUtc is malformed") from exc
    if parsed_time.tzinfo is None:
        raise ResealError("closure generatedAtUtc is not timezone-aware")
    derived = derive_projection()
    artifacts = build_closure_artifacts(derived)
    output_stamps: dict[str, dict[str, object]] = {}
    for name, expected_bytes in artifacts.items():
        path = require_plain_single_link_file(root / name, f"closure output {name}")
        actual_bytes = path.read_bytes()
        if actual_bytes != expected_bytes:
            raise ResealError(f"closure output does not reproduce: {name}")
        output_stamps[name] = stamp(path, relative_to=root)
    author = receipt.get("author")
    if not isinstance(author, dict):
        raise ResealError("closure author stamp is missing")
    actual_author = stamp(SCRIPT, relative_to=REPO_ROOT)
    if (author.get("bytes"), author.get("sha256")) != (
        actual_author["bytes"], actual_author["sha256"]
    ):
        raise ResealError("closure author identity differs from the executing owner")
    expected_author = {**actual_author, "path": "tools/re_gen73_reseal.py"}
    expected = _receipt_value(derived, output_stamps, generated_at, expected_author)
    if receipt != expected:
        raise ResealError("closure READY does not reproduce from exact inputs")
    return receipt


def prepare_closure(root: Path, generated_at: str | None = None) -> dict[str, object]:
    root = Path(os.path.abspath(root))
    if root.exists():
        raise ResealError(f"closure destination already exists: {root}")
    root.parent.mkdir(parents=True, exist_ok=True)
    author_start = stamp(SCRIPT, relative_to=REPO_ROOT)
    author_start["path"] = "tools/re_gen73_reseal.py"
    derived = derive_projection()
    artifacts = build_closure_artifacts(derived)
    stage = Path(tempfile.mkdtemp(prefix=f".{root.name}.partial-", dir=root.parent))
    try:
        for name, data in artifacts.items():
            _write_new(stage / name, data)
        output_stamps = {
            name: stamp(stage / name, relative_to=stage) for name in sorted(artifacts)
        }
        final_author = stamp(SCRIPT, relative_to=REPO_ROOT)
        final_author["path"] = "tools/re_gen73_reseal.py"
        if final_author != author_start:
            raise ResealError("closure author changed during execution")
        timestamp = generated_at or datetime.now(timezone.utc).isoformat()
        receipt = _receipt_value(derived, output_stamps, timestamp, author_start)
        _write_new(
            stage / "closure.ready.json",
            (json.dumps(receipt, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode(
                "utf-8"
            ),
        )
        verify_closure(stage)
        if stamp(SCRIPT, relative_to=REPO_ROOT)["sha256"] != author_start["sha256"]:
            raise ResealError("closure author changed before publication")
        os.replace(stage, root)
    except Exception:
        if stage.exists():
            shutil.rmtree(stage)
        raise
    return verify_closure(root)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    prepare_parser = subparsers.add_parser("prepare", help="publish an immutable closure")
    prepare_parser.add_argument("--output", type=Path, required=True)
    prepare_parser.add_argument("--generated-at")
    verify_parser = subparsers.add_parser("verify", help="rederive and verify a closure")
    verify_parser.add_argument("--root", type=Path, required=True)
    subparsers.add_parser("preview", help="run all gates without writing")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    try:
        if args.command == "prepare":
            value = prepare_closure(args.output, args.generated_at)
            print(
                "CLOSURE_READY "
                + sha256(Path(os.path.abspath(args.output)) / "closure.ready.json")
                + " "
                + value["claim"]
            )
        elif args.command == "verify":
            value = verify_closure(args.root)
            print("CLOSURE_VERIFIED " + value["claim"])
        else:
            derived = derive_projection()
            artifacts = build_closure_artifacts(derived)
            print(
                "CLOSURE_PREVIEW_OK "
                f"claims={len(derived['claims'])} source={len(derived['sourceDispositions'])} "
                f"artifacts={len(artifacts)}"
            )
        return 0
    except (OSError, ResealError, ValueError) as exc:
        print(f"CLOSURE_BLOCKED {exc}")
        return 10


if __name__ == "__main__":
    raise SystemExit(main())
