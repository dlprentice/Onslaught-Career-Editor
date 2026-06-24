#!/usr/bin/env python3
"""Build a host-authority runtime-delivery proof bundle from private artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import winui_safe_copy_online_host_authority_runtime_delivery_check as delivery


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("host_authority_two_client_proof", type=Path)
    parser.add_argument("live_runtime_artifact", type=Path)
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()

    output = args.output or args.host_authority_two_client_proof.with_name("host-authority-runtime-delivery-proof.json")
    print(json.dumps(delivery.build_bundle(
        args.host_authority_two_client_proof,
        args.live_runtime_artifact,
        output,
        enforce_private_output=True,
    ), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
