#!/usr/bin/env python3
"""Validate approved preview files and emit provenance-only metadata."""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "configs" / "datasets.json"
RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"


def load_config() -> dict[str, Any]:
    with CONFIG_PATH.open(encoding="utf-8") as handle:
        return json.load(handle)


def image_metadata(path: Path) -> dict[str, Any]:
    data = path.read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    metadata: dict[str, Any] = {
        "bytes": len(data),
        "sha256": digest,
        "format": "unknown",
        "width": None,
        "height": None,
    }
    if data.startswith(b"\x89PNG\r\n\x1a\n") and len(data) >= 24:
        metadata.update(
            {
                "format": "image/png",
                "width": struct.unpack(">I", data[16:20])[0],
                "height": struct.unpack(">I", data[20:24])[0],
            }
        )
    elif data.startswith(b"\xff\xd8"):
        metadata["format"] = "image/jpeg"
        index = 2
        while index + 9 < len(data):
            if data[index] != 0xFF:
                index += 1
                continue
            marker = data[index + 1]
            index += 2
            if marker in (0xD8, 0xD9):
                continue
            if index + 2 > len(data):
                break
            segment_size = struct.unpack(">H", data[index:index + 2])[0]
            if marker in range(0xC0, 0xC4) and index + 7 <= len(data):
                metadata["width"] = struct.unpack(">H", data[index + 5:index + 7])[0]
                metadata["height"] = struct.unpack(">H", data[index + 3:index + 5])[0]
                break
            index += segment_size
    return metadata


def preprocess(dataset_id: str) -> dict[str, Any]:
    config = load_config()
    dataset = next((item for item in config["datasets"] if item["id"] == dataset_id), None)
    if dataset is None:
        raise ValueError(f"dataset is not in the fixed allowlist: {dataset_id}")
    source = RAW_DIR / dataset_id / dataset["preview_filename"]
    if not source.is_file():
        raise FileNotFoundError(
            f"approved preview is absent: {source}; run acquire_assets.py --download-preview first"
        )
    metadata = image_metadata(source)
    if metadata["format"] != dataset["preview_format"]:
        raise ValueError(
            f"content signature {metadata['format']} does not match configured "
            f"format {dataset['preview_format']}"
        )
    result = {
        "schema_version": "phase2-preprocessed-preview.v1",
        "dataset_id": dataset_id,
        "source_url": dataset["preview_url"],
        "source_status": dataset["source_status"],
        "source_vs_proxy": dataset["source_vs_proxy"],
        "scientific_variables": dataset["known_variables"],
        "scientific_units": dataset["known_units"],
        "scientific_verification": "not_verified_by_preview_processing",
        "input": metadata,
        "feature_extraction": "none; provenance and image envelope only",
    }
    output = PROCESSED_DIR / dataset_id / "preview-metadata.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", required=True)
    args = parser.parse_args()
    try:
        print(json.dumps(preprocess(args.dataset), indent=2))
        return 0
    except (OSError, ValueError) as error:
        print(f"preprocessing error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
