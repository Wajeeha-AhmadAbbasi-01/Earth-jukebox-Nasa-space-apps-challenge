# Local run and release boundary

## Browser application

From the repository root:

```powershell
python -m http.server 4180 --directory .
```

Open <http://localhost:4180/earth-jukebox/prototype/>. All experience previews and feature timelines are local assets. The app can play with NASA endpoints offline.

## Read-only API

Install the API dependencies and run FastAPI from the repository root:

```powershell
python -m pip install -r earth-jukebox\requirements-api.txt
python -m uvicorn api.app:app --app-dir earth-jukebox --host 127.0.0.1 --port 8001
```

The versioned routes provide health, dataset metadata, source/proxy verification, timeline, bounded feature pagination, and statistics under `/api/v1`. Dataset IDs are allowlisted. The API has no arbitrary URL, upload, raw-file, or write endpoint.

## Rebuild and promote local assets

```powershell
python -m pip install -r earth-jukebox\requirements-pipeline.txt
python earth-jukebox\scripts\extract_visual_proxy_features.py --dataset ocean-3912
python earth-jukebox\scripts\extract_visual_proxy_features.py --dataset lightning-5011
python earth-jukebox\scripts\extract_visual_proxy_features.py --dataset aerosols-5572
python earth-jukebox\scripts\promote_proxy_assets.py --dataset ocean-3912
python earth-jukebox\scripts\promote_proxy_assets.py --dataset lightning-5011
python earth-jukebox\scripts\promote_proxy_assets.py --dataset aerosols-5572
```

Promotion requires an acquired-source checksum manifest and a valid image-derived timeline. Promotion does not certify scientific measurements.

## Release boundary

This is a functional local application and local read-only API using an explicit image-derived fallback. It is not a verified numerical-data sonification product and has not been deployed to production. No numerical LIS, ECCO2, or GEOS science fields are packaged. Formal NVDA/WCAG 2.2 AA evidence, production hosting, and deployment performance measurements are not claimed.
