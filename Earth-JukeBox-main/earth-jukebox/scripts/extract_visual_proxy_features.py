#!/usr/bin/env python3
"""Extract bounded image-derived proxy timelines from approved SVS previews."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / "configs" / "datasets.json").read_text(encoding="utf-8"))
SEGMENTS = 24
DURATION_SECONDS = 24.0


def _classify(red: float, green: float, blue: float) -> str:
    maximum = max(red, green, blue)
    minimum = min(red, green, blue)
    if maximum - minimum < 18:
        return "neutral"
    if red >= green * 1.16 and red >= blue * 1.16:
        return "warm"
    if blue >= red * 1.12 and blue >= green * 1.05:
        return "cool"
    if green >= red * 1.12 and green >= blue * 1.05:
        return "green"
    if red >= green * 1.05 and blue >= green * 1.05:
        return "magenta"
    return "mixed"


def extract(dataset_id: str) -> dict[str, Any]:
    dataset = next(item for item in CONFIG["datasets"] if item["id"] == dataset_id)
    source_path = ROOT / "data" / "raw" / dataset_id / dataset["preview_filename"]
    if not source_path.is_file():
        raise FileNotFoundError(source_path)
    with Image.open(source_path) as image:
        source_width, source_height = image.size
        # A fixed analysis grid keeps preprocessing bounded on full-size media.
        # It remains a rendered-pixel proxy and does not recover source variables.
        rgb = image.convert("RGB")
        rgb.thumbnail((320, 180), Image.Resampling.LANCZOS)
        width, height = rgb.size
        features = []
        for index in range(SEGMENTS):
            left = math.floor(width * index / SEGMENTS)
            right = math.floor(width * (index + 1) / SEGMENTS)
            pixels = [rgb.getpixel((x, y)) for y in range(height) for x in range(left, right)]
            signal = [pixel for pixel in pixels if max(pixel) >= 35]
            red = sum(pixel[0] for pixel in pixels) / len(pixels)
            green = sum(pixel[1] for pixel in pixels) / len(pixels)
            blue = sum(pixel[2] for pixel in pixels) / len(pixels)
            signal_red = sum(pixel[0] for pixel in signal) / len(signal) if signal else 0
            signal_green = sum(pixel[1] for pixel in signal) / len(signal) if signal else 0
            signal_blue = sum(pixel[2] for pixel in signal) / len(signal) if signal else 0
            low_signal = 1 - len(signal) / len(pixels)
            features.append(
                {
                    "index": index,
                    "time_seconds": round(DURATION_SECONDS * index / SEGMENTS, 6),
                    "rendered_brightness_proxy": round(
                        (0.2126 * red + 0.7152 * green + 0.0722 * blue) / 255, 6
                    ),
                    "color_class_proxy": _classify(signal_red, signal_green, signal_blue)
                    if signal
                    else "unclassified",
                    "low_signal_share": round(low_signal, 6),
                    "unclassified_share": round(low_signal, 6),
                    "excluded_share": 0.0,
                    "source_pixel_region": {
                        "left": math.floor(source_width * left / width),
                        "top": 0,
                        "right": math.floor(source_width * right / width),
                        "bottom": source_height,
                    },
                }
            )
    data = source_path.read_bytes()
    result = {
        "schema_version": "visual-proxy-timeline.v1",
        "dataset_id": dataset_id,
        "source": {
            "title": dataset["title"],
            "page_url": dataset["source_page"],
            "asset_url": dataset["preview_url"],
            "local_path": f"earth-jukebox/data/raw/{dataset_id}/{dataset['preview_filename']}",
            "sha256": hashlib.sha256(data).hexdigest(),
            "bytes": len(data),
            "format": dataset["preview_format"],
            "width": source_width,
            "height": source_height,
            "analysis_width": rgb.width,
            "analysis_height": rgb.height,
        },
        "verification": {
            "status": dataset["source_status"],
            "source_vs_proxy": "image_derived_proxy",
            "scientific_claims": [
                "Features are derived from rendered preview pixels only.",
                "Color classes are display-color proxies, not scientific categories or concentration units.",
                "The playback position is a spatial scan of one still/preview, not source chronology.",
                "No event counts, physical units, calibrated radiance, or numerical model values are inferred.",
            ],
            "temporal_claim": "none",
            "source_notes": dataset["notes"],
        },
        "timeline": {
            "duration_seconds": DURATION_SECONDS,
            "segment_count": len(features),
            "sampling": "equal-width vertical strips across a bounded 320x180-or-smaller resampling of the approved local preview",
            "semantics": "spatial scan playback position only; not source chronology",
        },
        "sonification_mapping": dataset["sonification_mapping"],
        "features": features,
    }
    output = ROOT / "data" / "processed" / dataset_id / "proxy-feature-timeline.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    manifest = ROOT / "data" / "manifests" / f"{dataset_id}-provenance.json"
    manifest.write_text(
        json.dumps(
            {
                "schema_version": "provenance-manifest.v1",
                "dataset_id": dataset_id,
                "acquisition": {
                    "url": dataset["preview_url"],
                    "local_path": result["source"]["local_path"],
                    "sha256": result["source"]["sha256"],
                    "bytes": len(data),
                    "accessed_at": "2026-11-14",
                    "status": "acquired_and_checksum_verified",
                },
                "processing": {
                    "script": "earth-jukebox/scripts/extract_visual_proxy_features.py",
                    "output": str(output.relative_to(ROOT)),
                    "feature_status": "image_derived_proxy_only",
                    "sonification_mapping": dataset["sonification_mapping"],
                },
                "attribution": dataset["notes"],
                "limitations": result["verification"]["scientific_claims"],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dataset",
        choices=[item["id"] for item in CONFIG["datasets"]],
        required=True,
    )
    result = extract(parser.parse_args().dataset)
    print(json.dumps({"dataset_id": result["dataset_id"], "segments": len(result["features"]), "sha256": result["source"]["sha256"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
