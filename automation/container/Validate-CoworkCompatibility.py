#!/usr/bin/env python3
"""Apply orchestration-level guards that are outside the Cowork v0.1.0 validator."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

EXPECTED_ENTITIES = {
    "entity-Bridge_CoworkPlugin.csv",
    "entity-Bridge_CoworkResource.csv",
    "entity-CoworkClassification.csv",
    "entity-Dim_CoworkSkill.csv",
    "entity-Dim_ModelProvider.csv",
    "entity-Dim_User.csv",
    "entity-Dim_UserOrg.csv",
    "entity-Fact_Consumption.csv",
    "entity-Fact_CopilotAuditRaw.csv",
    "entity-Fact_CoworkThread.csv",
    "entity-Fact_CoworkUsage.csv",
    "entity-Fact_CoworkUserDayModel.csv",
    "entity-Fact_Tasks.csv",
}


def validate(output: Path) -> dict[str, object]:
    manifest_path = output / "manifest.json"
    if not manifest_path.is_file():
        raise ValueError(f"Manifest not found: {manifest_path}")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("format") != "cowork-python-preprocessor-manifest-v1":
        raise ValueError("Unsupported Cowork manifest format")

    actual = {path.name for path in output.glob("entity-*.csv") if path.is_file()}
    missing = sorted(EXPECTED_ENTITIES - actual)
    unexpected = sorted(actual - EXPECTED_ENTITIES)
    if missing or unexpected:
        raise ValueError(
            f"Entity inventory mismatch; missing={missing}, unexpected={unexpected}"
        )

    audit_path = output / "entity-Fact_CopilotAuditRaw.csv"
    cowork_rows = 0
    blank_thread_rows = 0
    incompatible_hosts: set[str] = set()
    with audit_path.open("r", encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream)
        required = {"RecordId", "AppHost", "ThreadId"}
        if not required.issubset(reader.fieldnames or []):
            raise ValueError(f"{audit_path.name} is missing required compatibility columns")
        for row in reader:
            host = (row.get("AppHost") or "").strip()
            if host.casefold() != "cowork":
                continue
            cowork_rows += 1
            if host != "cowork":
                incompatible_hosts.add(host)
            if not (row.get("ThreadId") or "").strip():
                blank_thread_rows += 1

    if incompatible_hosts:
        raise ValueError(
            "Cowork AppHost must be the lowercase literal 'cowork'; found "
            + ", ".join(repr(value) for value in sorted(incompatible_hosts))
        )
    if blank_thread_rows:
        raise ValueError(
            f"{blank_thread_rows} Cowork audit rows have blank ThreadId values"
        )

    manifest_cowork_rows = manifest.get("reconciliation", {}).get("cowork_detail_rows")
    if manifest_cowork_rows != cowork_rows:
        raise ValueError(
            f"Cowork row mismatch: manifest={manifest_cowork_rows}, audit={cowork_rows}"
        )

    return {
        "status": "valid",
        "entityFileCount": len(actual),
        "coworkAuditRows": cowork_rows,
        "blankCoworkThreadRows": blank_thread_rows,
        "appHostContract": "cowork",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        print(json.dumps(validate(args.output.resolve()), indent=2))
        return 0
    except (OSError, csv.Error, json.JSONDecodeError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
