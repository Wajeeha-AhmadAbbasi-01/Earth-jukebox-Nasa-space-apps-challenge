# Earth Jukebox repository and implementation audit

**Updated:** 2026-11-15. This report supersedes the earlier Phase 0 snapshot in this file.

## Current repository

The repository now contains a separate `earth-jukebox/` application alongside the original unrelated storefront artifacts. The Earth Jukebox code is not a modification of the storefront. Its browser application is a static HTML/CSS/JavaScript app with a read-only FastAPI service and Python scripts for controlled preview acquisition, metadata processing, feature extraction, and local artifact promotion.

## PRD source scope

The supplied `Earth_Jukebox_PRD_AI_Build_Brief.docx` defines Ocean currents and temperature (SVS 3912), ISS Lightning (5011), and GEOS Aerosols (5572). Current catalog, config, source page, local preview files, prepared timelines, and API config align with those identifiers.

## Evidence-backed boundary

Each experience has an official preview image, source checksum, provenance manifest, 24-strip local image-feature timeline, and versioned browser audio mapping. The browser uses a shared clock for feature interpolation, synthesized audio, seek state, and a visible image scan cursor. Playback does not call NASA. A read-only local `/api/v1` service exposes metadata and prepared timelines.

These are **image-derived proxy features**, not verified numerical source fields. The included images are stills. Playback scans image space; it is not source chronology. The current application does not extract lightning records, ECCO2 current vectors/temperatures, or GEOS concentration fields.

## Remaining release gates

- Obtain and verify source-time science fields for the three experiences if scientific measurement sonification is required.
- Replace spatial still-image scans with time-indexed frames or numerical features for a source-time experience.
- Verify speech/voice and transport behavior in target browsers.
- Complete a keyboard and NVDA screen-reader run; do not claim WCAG conformance without evidence.
- Select a production host and complete deployment, security, performance, outage, and smoke checks.

Requirement-level status and verified source details are maintained in [the PRD traceability matrix](REQUIREMENTS_TRACEABILITY.md), [the resource manifest](RESOURCE_MANIFEST.md), and [the delivery gap matrix](FINAL_COMPLIANCE_GAP_MATRIX.md).
