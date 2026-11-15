# The Earth Information Jukebox

An accessible browser experience for NASA Earth visualizations. The current PRD-aligned collection is Ocean currents and temperature (SVS 3912), ISS lightning (SVS 5011), and GEOS aerosols (SVS 5572). It prepares small official previews locally and generates deterministic Web Audio from rendered-pixel features.

The current sound is **image-derived sonification**, not calibrated scientific measurement sonification. Preview color and brightness do not recover underlying numerical fields, events, currents, or aerosol concentrations. This limitation and each mapping are shown in the application.

## Run the application

From the repository root, start the local static server:

```powershell
python -m http.server 4180 --directory .
```

Open <http://localhost:4180/earth-jukebox/prototype/>. Prepared previews and timelines are served locally; playback does not contact NASA.

## Run the read-only API

Install the API dependencies and run FastAPI from the repository root:

```powershell
python -m pip install -r earth-jukebox\requirements-api.txt
python -m uvicorn api.app:app --app-dir earth-jukebox --host 127.0.0.1 --port 8001
```

API routes are documented in [the release instructions](earth-jukebox/RELEASE_README.md).

## Source and delivery status

See [the resource manifest](docs/RESOURCE_MANIFEST.md), [PRD traceability](docs/REQUIREMENTS_TRACEABILITY.md), and [delivery gap matrix](docs/FINAL_COMPLIANCE_GAP_MATRIX.md). The proxy application is runnable and offline-ready. The PRD's numerical source-data option remains incomplete; where official source schemas or fields are not available, this build uses the PRD-permitted visualization-derived fallback and labels it explicitly.
