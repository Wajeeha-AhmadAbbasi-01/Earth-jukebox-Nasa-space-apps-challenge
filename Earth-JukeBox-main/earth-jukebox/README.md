# Earth Jukebox

This application is aligned to the attached PRD’s three initial experiences:

- Ocean currents and temperature, NASA SVS 3912
- Lightning detected from the ISS, NASA SVS 5011
- GEOS aerosols, NASA SVS 5572

## Current data boundary

The application includes locally prepared official NASA preview images and checksummed, versioned image-derived timelines. It generates non-speech Web Audio from rendered brightness and display-color proxies. A synchronized scan cursor shows which preview strip is currently driving the sound. The sound mappings use bounded frequency, gain, waveform, and stereo-pan values, but they do not reconstruct source numerical values or source time.

No LIS science records, ECCO2 numerical fields, or GEOS numerical aerosol fields are included. Accordingly, the app never presents pixel color as calibrated temperature, current speed, lightning event count, or aerosol concentration. The PRD explicitly permits a documented visualization-derived fallback when the exact numerical source cannot be obtained.

Earlier experimental SVS 5669 and 5313 files remain in the repository as legacy artifacts; they are not in the active dataset allowlist, frontend collection, or API dataset list.

## Layout

- `configs/datasets.json`: fixed PRD collection and exact official preview URLs
- `scripts/acquire_assets.py`: bounded allowlist-based preview acquisition
- `scripts/preprocess_assets.py`: image signature, dimensions, and checksum validation
- `scripts/extract_visual_proxy_features.py`: reproducible 24-strip preview proxy extraction
- `scripts/promote_proxy_assets.py`: checksum-gated local last-known-good manifest promotion
- `data/raw/`: official preview images
- `data/processed/`: metadata and feature timeline JSON
- `data/manifests/`: provenance, source status, and promotion records
- `contracts/`: versioned contracts and fail-closed science adapters
- `prototype/`: accessible browser experience and Web Audio player
- `api/`: bounded read-only `/api/v1` metadata and timeline service

## Rebuild the prepared feature timelines

Install the pipeline dependency from the repository root:

```powershell
python -m pip install -r earth-jukebox\requirements-pipeline.txt
python earth-jukebox\scripts\extract_visual_proxy_features.py --dataset ocean-3912
python earth-jukebox\scripts\extract_visual_proxy_features.py --dataset lightning-5011
python earth-jukebox\scripts\extract_visual_proxy_features.py --dataset aerosols-5572
```

See [the release guide](RELEASE_README.md) for app and API startup steps. See [the repository-level resource manifest](../docs/RESOURCE_MANIFEST.md) for verified source facts and unresolved scientific-data details.
