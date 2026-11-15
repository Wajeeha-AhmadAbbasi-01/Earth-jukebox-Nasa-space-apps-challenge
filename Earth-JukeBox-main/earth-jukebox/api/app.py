"""Constrained read-only API for prepared Earth Jukebox proxy artifacts.

The API never fetches URLs or exposes raw filesystem paths. It serves only
fixed dataset metadata and checked-in processed artifacts.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse

ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / "configs" / "datasets.json").read_text(encoding="utf-8"))
DATASETS = {item["id"]: item for item in CONFIG["datasets"]}
MAX_FEATURES = 256

app = FastAPI(title="Earth Jukebox API", version="1.0.0", docs_url=None, redoc_url=None)


def _dataset(dataset_id: str) -> dict[str, Any]:
    dataset = DATASETS.get(dataset_id)
    if dataset is None:
        raise HTTPException(status_code=404, detail="unknown dataset")
    return dataset


def _timeline(dataset_id: str) -> dict[str, Any]:
    path = ROOT / "data" / "processed" / dataset_id / "proxy-feature-timeline.json"
    if not path.is_file():
        raise HTTPException(status_code=503, detail="prepared timeline unavailable")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        raise HTTPException(status_code=503, detail="prepared timeline invalid")
    if payload.get("dataset_id") != dataset_id or payload.get("verification", {}).get("source_vs_proxy") != "image_derived_proxy":
        raise HTTPException(status_code=503, detail="prepared timeline contract rejected")
    return payload


def _public_metadata(dataset_id: str) -> dict[str, Any]:
    dataset = _dataset(dataset_id)
    return {
        "id": dataset["id"],
        "svs_id": dataset["svs_id"],
        "title": dataset["title"],
        "source_page": dataset["source_page"],
        "source_period": dataset["source_period"],
        "source_status": dataset["source_status"],
        "source_vs_proxy": dataset["source_vs_proxy"],
        "known_variables": dataset["known_variables"],
        "known_units": dataset["known_units"],
        "sonification_mapping": dataset["sonification_mapping"],
        "notes": dataset["notes"],
    }


@app.get("/api/v1/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "earth-jukebox-api", "contract": "v1"}


@app.get("/api/v1/datasets")
def datasets() -> dict[str, Any]:
    return {"items": [_public_metadata(dataset_id) for dataset_id in DATASETS]}


@app.get("/api/v1/datasets/{dataset_id}")
def dataset(dataset_id: str) -> dict[str, Any]:
    return _public_metadata(dataset_id)


@app.get("/api/v1/datasets/{dataset_id}/sources")
def sources(dataset_id: str) -> dict[str, Any]:
    payload = _timeline(dataset_id)
    return {"dataset_id": dataset_id, "source": payload["source"], "verification": payload["verification"]}


@app.get("/api/v1/datasets/{dataset_id}/timeline")
def timeline(dataset_id: str) -> dict[str, Any]:
    payload = _timeline(dataset_id)
    return {"dataset_id": dataset_id, "schema_version": payload["schema_version"], "timeline": payload["timeline"]}


@app.get("/api/v1/datasets/{dataset_id}/features")
def features(
    dataset_id: str,
    start: int = Query(0, ge=0),
    limit: int = Query(24, ge=1, le=MAX_FEATURES),
) -> dict[str, Any]:
    payload = _timeline(dataset_id)
    items = payload["features"][start : start + limit]
    return {"dataset_id": dataset_id, "schema_version": payload["schema_version"], "items": items, "count": len(items)}


@app.get("/api/v1/datasets/{dataset_id}/statistics")
def statistics(dataset_id: str) -> dict[str, Any]:
    payload = _timeline(dataset_id)
    items = payload["features"]
    return {
        "dataset_id": dataset_id,
        "feature_count": len(items),
        "duration_seconds": payload["timeline"]["duration_seconds"],
        "max_low_signal_share": max(item.get("low_signal_share", 0) for item in items),
        "max_excluded_share": max(item.get("excluded_share", 0) for item in items),
        "temporal_claim": payload["verification"]["temporal_claim"],
        "source_vs_proxy": payload["verification"]["source_vs_proxy"],
    }


@app.exception_handler(HTTPException)
async def explicit_errors(_, exc: HTTPException) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={"error": exc.detail})
