#!/usr/bin/env python3
"""Promote verified proxy artifacts to a last-known-good manifest."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "configs" / "datasets.json"
MANIFEST_DIR = ROOT / "data" / "manifests"
PROCESSED_DIR = ROOT / "data" / "processed"


def promote(dataset_id: str) -> dict:
    timeline_path = PROCESSED_DIR / dataset_id / "proxy-feature-timeline.json"
    provenance_path = MANIFEST_DIR / f"{dataset_id}-provenance.json"
    if not timeline_path.is_file() or not provenance_path.is_file():
        raise FileNotFoundError(f"verified artifacts missing for {dataset_id}")
    timeline = json.loads(timeline_path.read_text(encoding="utf-8"))
    provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
    if timeline.get("dataset_id") != dataset_id or timeline.get("verification", {}).get("source_vs_proxy") != "image_derived_proxy":
        raise ValueError("timeline is not an accepted image-derived proxy")
    if provenance.get("acquisition", {}).get("status") != "acquired_and_checksum_verified":
        raise ValueError("provenance is not checksum-verified")
    digest = hashlib.sha256(timeline_path.read_bytes()).hexdigest()
    result = {
        "schema_version": "last-known-good.v1",
        "dataset_id": dataset_id,
        "status": "promoted",
        "promoted_at": datetime.now(timezone.utc).isoformat(),
        "timeline": str(timeline_path.relative_to(ROOT)),
        "timeline_sha256": digest,
        "source_sha256": timeline["source"]["sha256"],
        "source_vs_proxy": timeline["verification"]["source_vs_proxy"],
        "temporal_claim": timeline["verification"]["temporal_claim"],
    }
    output = MANIFEST_DIR / f"{dataset_id}-last-known-good.json"
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    parser.add_argument("--dataset", choices=[item["id"] for item in config["datasets"]], required=True)
    print(json.dumps(promote(parser.parse_args().dataset), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
