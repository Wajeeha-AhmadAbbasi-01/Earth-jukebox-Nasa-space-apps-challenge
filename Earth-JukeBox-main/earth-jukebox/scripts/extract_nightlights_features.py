#!/usr/bin/env python3
"""Extract deterministic display proxies from the composite SVS 5313 preview.

The acquired asset is one rendered composite, not a time-ordered frame set.
Playback time below is an interface scan position only; it is not source time.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
RAW_IMAGE = ROOT / "data" / "raw" / "nightlights-5313" / (
    "nightlights_flat_series_and_change_wZooms_13_EIC.02599_print.jpg"
)
OUTPUT_DIR = ROOT / "data" / "processed" / "nightlights-5313"
OUTPUT = OUTPUT_DIR / "proxy-feature-timeline.json"
MANIFEST = ROOT / "data" / "manifests" / "nightlights-5313-provenance.json"
SEGMENTS = 24
DURATION_SECONDS = 24.0
EXCLUDED_REGIONS = (
    # Four labeled regional inset panels visible in the print preview.
    {"name": "western_europe_inset", "left": 89, "top": 97, "right": 267, "bottom": 276},
    {"name": "eastern_mediterranean_inset", "left": 314, "top": 0, "right": 431, "bottom": 171},
    {"name": "ukraine_inset", "left": 618, "top": 8, "right": 767, "bottom": 122},
    {"name": "india_inset", "left": 806, "top": 137, "right": 945, "bottom": 280},
    # Centered change-color legend and its label.
    {"name": "change_legend", "left": 494, "top": 153, "right": 587, "bottom": 177},
)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(64 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _color_class(red: float, green: float, blue: float) -> str:
    maximum = max(red, green, blue)
    minimum = min(red, green, blue)
    if maximum - minimum < 18:
        return "neutral"
    if red >= green * 1.16 and red >= blue * 1.16:
        return "warm"
    if blue >= red * 1.12 and blue >= green * 1.05:
        return "cool"
    return "mixed"


def _excluded(x: int, y: int) -> bool:
    return any(
        region["left"] <= x < region["right"] and region["top"] <= y < region["bottom"]
        for region in EXCLUDED_REGIONS
    )


def extract() -> dict[str, Any]:
    if not RAW_IMAGE.is_file():
        raise FileNotFoundError(f"official preview is absent: {RAW_IMAGE}")
    source_hash = _sha256(RAW_IMAGE)
    with Image.open(RAW_IMAGE) as image:
        rgb = image.convert("RGB")
        width, height = rgb.size
        features = []
        for index in range(SEGMENTS):
            left = math.floor(width * index / SEGMENTS)
            right = math.floor(width * (index + 1) / SEGMENTS)
            pixels = [
                rgb.getpixel((x, y))
                for y in range(height)
                for x in range(left, right)
                if not _excluded(x, y)
            ]
            if not pixels:
                raise ValueError(f"mask removed every pixel from segment {index}")
            mean_red = sum(pixel[0] for pixel in pixels) / len(pixels)
            mean_green = sum(pixel[1] for pixel in pixels) / len(pixels)
            mean_blue = sum(pixel[2] for pixel in pixels) / len(pixels)
            rendered_brightness = (0.2126 * mean_red + 0.7152 * mean_green + 0.0722 * mean_blue) / 255
            signal_pixels = [pixel for pixel in pixels if max(pixel) >= 35]
            low_signal = 1 - len(signal_pixels) / len(pixels)
            if signal_pixels:
                signal_red = sum(pixel[0] for pixel in signal_pixels) / len(signal_pixels)
                signal_green = sum(pixel[1] for pixel in signal_pixels) / len(signal_pixels)
                signal_blue = sum(pixel[2] for pixel in signal_pixels) / len(signal_pixels)
                color_class = _color_class(signal_red, signal_green, signal_blue)
            else:
                color_class = "unclassified"
            excluded_count = sum(
                _excluded(x, y)
                for y in range(height)
                for x in range(left, right)
            )
            features.append(
                {
                    "index": index,
                    "time_seconds": round(DURATION_SECONDS * index / SEGMENTS, 6),
                    "rendered_brightness_proxy": round(rendered_brightness, 6),
                    "color_class_proxy": color_class,
                    "low_signal_share": round(low_signal, 6),
                    "unclassified_share": round(low_signal, 6),
                    "excluded_share": round(excluded_count / ((right - left) * height), 6),
                    "source_pixel_region": {
                        "left": left,
                        "top": 0,
                        "right": right,
                        "bottom": height,
                    },
                }
            )
    result = {
        "schema_version": "nightlights-proxy-timeline.v1",
        "dataset_id": "nightlights-5313",
        "source": {
            "title": "Change in Night Lights between 2012 and 2023 - EIC Version",
            "page_url": "https://svs.gsfc.nasa.gov/5313/",
            "asset_url": "https://svs.gsfc.nasa.gov/vis/a000000/a005300/a005313/nightlights_flat_series_and_change_wZooms_13_EIC.02599_print.jpg",
            "local_path": "earth-jukebox/data/raw/nightlights-5313/nightlights_flat_series_and_change_wZooms_13_EIC.02599_print.jpg",
            "sha256": source_hash,
            "format": "image/jpeg",
            "width": width,
            "height": height,
        },
        "verification": {
            "status": "metadata_verified_source_unverified",
            "source_vs_proxy": "image_derived_proxy",
            "scientific_claims": [
                "Rendered brightness is a proxy derived from preview pixels.",
                "Color classes are deterministic display-color proxies.",
                "No calibrated radiance, physical units, or numerical Black Marble values are inferred.",
                "The playback timeline is a spatial scan of one composite render, not annual source time.",
            ],
            "temporal_claim": "none",
            "excluded_regions": list(EXCLUDED_REGIONS),
        },
        "timeline": {
            "duration_seconds": DURATION_SECONDS,
            "segment_count": len(features),
            "sampling": "equal-width vertical strips across the acquired composite after masking inset panels and legend",
            "semantics": "spatial scan playback position only; not source chronology or annual frame timing",
        },
        "features": features,
    }
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    MANIFEST.write_text(
        json.dumps(
            {
                "schema_version": "provenance-manifest.v1",
                "dataset_id": "nightlights-5313",
                "acquisition": {
                    "url": result["source"]["asset_url"],
                    "local_path": result["source"]["local_path"],
                    "sha256": source_hash,
                    "bytes": RAW_IMAGE.stat().st_size,
                    "accessed_at": "2026-11-14",
                    "status": "acquired_and_checksum_verified",
                },
                "processing": {
                    "script": "earth-jukebox/scripts/extract_nightlights_features.py",
                    "output": str(OUTPUT.relative_to(ROOT)),
                    "feature_status": "image_derived_proxy_only",
                },
                "attribution": "NASA/NOAA Suomi NPP VIIRS provenance as credited by NASA SVS 5313; NASA SVS preview asset.",
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
    parser.add_argument("--verify", action="store_true", help="extract and write the checked-in proxy timeline")
    args = parser.parse_args()
    if not args.verify:
        parser.error("--verify is required")
    result = extract()
    print(json.dumps({"output": str(OUTPUT.relative_to(ROOT)), "segments": len(result["features"]), "sha256": result["source"]["sha256"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
