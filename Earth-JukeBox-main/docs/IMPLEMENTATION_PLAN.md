# Earth Jukebox implementation and remaining work

## Completed in the local PRD-aligned build

The application now selects the PRD’s three source experiences: Ocean 3912, Lightning 5011, and GEOS Aerosols 5572. It uses checksummed NASA previews, local image-derived feature timelines, category-specific versioned Web Audio mappings, synchronized transport/scan controls, local read-only API endpoints, provenance records, and user-activated speech/optional voice controls. Existing playback architecture and its shared clock are retained.

The PRD permits an image-analysis fallback when exact numerical fields cannot be obtained. The application uses that fallback and labels the proxy status and its limitations in the UI and output metadata.

## Completion gates

1. Acquire representative source files for ECCO2, ISS LIS, and GEOS that match the stated NASA SVS experiences.
2. Verify file schema, source lineage, variables, units, time/spatial coverage, quality flags/missing values, and usage/attribution conditions before scientific interpretation.
3. Add source-specific processors and time-indexed feature contracts. Keep the image-proxy path available as a documented fallback.
4. Use actual source-time frames/records so the visualization and sonification share meaningful time, not a still-image spatial scan.
5. Run scientific mapping tests, audio listening evaluation, browser transport checks, keyboard-only checks, and NVDA screen-reader workflows.
6. Decide deployment and storage. Run offline/outage, security, performance, and production smoke tests before claiming production readiness.

## Non-claims

Current outputs are not calibrated measurements. The source image does not establish per-pixel temperature or current speed, lightning events are not extracted from pixels, aerosol colors are not concentrations, and the scan index is not source chronology. These boundaries remain explicit until matching source data and validation evidence are available.
