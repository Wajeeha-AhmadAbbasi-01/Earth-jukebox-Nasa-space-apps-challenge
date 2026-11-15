#!/usr/bin/env python3
"""Bounded acquisition and access checks for approved Earth Jukebox previews."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "configs" / "datasets.json"
RAW_DIR = ROOT / "data" / "raw"


def load_config() -> dict[str, Any]:
    with CONFIG_PATH.open(encoding="utf-8") as handle:
        config = json.load(handle)
    if not isinstance(config.get("datasets"), list) or not config["datasets"]:
        raise ValueError("configuration must contain a non-empty datasets list")
    return config


def dataset_by_id(config: dict[str, Any], dataset_id: str) -> dict[str, Any]:
    for dataset in config["datasets"]:
        if dataset.get("id") == dataset_id:
            return dataset
    raise ValueError(f"dataset is not in the fixed allowlist: {dataset_id}")


def validate_url(url: str, allowed_hosts: list[str]) -> None:
    parsed = urlparse(url)
    if parsed.scheme != "https" or parsed.hostname not in allowed_hosts:
        raise ValueError("only HTTPS URLs on configured NASA SVS hosts are allowed")
    if parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise ValueError("credentials, query strings, and fragments are not allowed")


def request_preview(
    dataset: dict[str, Any], config: dict[str, Any], download: bool
) -> dict[str, Any]:
    policy = config["retrieval_policy"]
    validate_url(dataset["preview_url"], policy["allowed_hosts"])
    request = urllib.request.Request(
        dataset["preview_url"],
        method="GET" if download else "HEAD",
        headers={"User-Agent": policy["user_agent"]},
    )
    with urllib.request.urlopen(request, timeout=policy["connect_timeout_seconds"]) as response:
        content_length = response.headers.get("Content-Length")
        declared_size = int(content_length) if content_length else None
        if declared_size is not None and declared_size > policy["max_preview_bytes"]:
            raise ValueError("preview exceeds configured byte limit")
        result: dict[str, Any] = {
            "url": dataset["preview_url"],
            "http_status": response.status,
            "content_type": response.headers.get_content_type(),
            "declared_bytes": declared_size,
            "downloaded": False,
        }
        if not download:
            return result

        target = RAW_DIR / dataset["id"] / dataset["preview_filename"]
        target.parent.mkdir(parents=True, exist_ok=True)
        digest = hashlib.sha256()
        total = 0
        with target.open("wb") as output:
            while True:
                chunk = response.read(64 * 1024)
                if not chunk:
                    break
                total += len(chunk)
                if total > policy["max_preview_bytes"]:
                    output.close()
                    target.unlink(missing_ok=True)
                    raise ValueError("preview exceeded configured byte limit while reading")
                digest.update(chunk)
                output.write(chunk)
        result.update(
            {
                "downloaded": True,
                "path": str(target.relative_to(ROOT)),
                "bytes": total,
                "sha256": digest.hexdigest(),
            }
        )
        return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", help="allowlisted dataset ID")
    parser.add_argument("--validate-config", action="store_true")
    parser.add_argument("--check-access", action="store_true")
    parser.add_argument("--download-preview", action="store_true")
    args = parser.parse_args()
    if not (args.validate_config or args.check_access or args.download_preview):
        parser.error("choose --validate-config, --check-access, or --download-preview")
    try:
        config = load_config()
        if args.validate_config:
            for dataset in config["datasets"]:
                validate_url(dataset["preview_url"], config["retrieval_policy"]["allowed_hosts"])
            print(f"validated {len(config['datasets'])} allowlisted datasets")
        if args.check_access or args.download_preview:
            if not args.dataset:
                parser.error("--dataset is required for access or download")
            dataset = dataset_by_id(config, args.dataset)
            print(json.dumps(request_preview(dataset, config, args.download_preview), indent=2))
        return 0
    except (OSError, ValueError, urllib.error.URLError) as error:
        print(f"acquisition error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
