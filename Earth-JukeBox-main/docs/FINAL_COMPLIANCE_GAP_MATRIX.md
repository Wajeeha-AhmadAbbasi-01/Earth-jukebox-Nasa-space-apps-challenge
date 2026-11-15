# Earth Jukebox delivery and PRD gap matrix

**Assessment date:** 2026-11-15. The collection and interface now match the attached PRD’s Ocean 3912, Lightning 5011, and Aerosols 5572 scope. This is a functional local image-derived sonification application; it is not a numerical science product or production deployment.

## Implemented and packaged

| Area | Evidence | Boundary |
|---|---|---|
| PRD dataset scope | Three correct NASA SVS sources in the UI, API, fixed config, source page, and processed artifact registry | Static previews; the science fields are not bundled |
| Prepared local assets | Checksummed official preview images and per-source acquisition manifests | No large movies, full frame sets, or numerical science files |
| Image-derived feature path | 24-strip feature timelines with brightness/color proxies, uncertainty shares, source pixel ranges, and `temporal_claim: none` | A spatial scan of a still, not source chronology |
| Interactive sonification | Per-experience versioned frequency, gain, waveform, and pan maps; Web Audio starts on user action | Artistic proxy mapping, not calibrated science measurement |
| Synchronized controls | Shared playback clock updates audio, seek, status, and visible scan cursor | No synchronized NASA animation |
| Accessibility features | Keyboard-operable selection/transport, semantic controls, live status, user-triggered speech guidance, optional voice commands | NVDA/WCAG verification not completed |
| API and asset safety | Local read-only `/api/v1`, fixed dataset allowlist, bounded pagination, no arbitrary URL or raw-file route | Local only; no production CORS/auth/rate-limit or deployment validation |
| Provenance/recovery | Source SHA-256, processing record, sonification mapping ID/version, checksum-gated local last-known-good manifests | No remote scheduled-ingestion/automatic rollback service |

## Unmet requirements and why

| Gap | Why it remains | What would close it |
|---|---|---|
| Numerical ocean sonification | The acquired SVS 3912 image is a rendered output. Its visual color bar is not a per-pixel numerical temperature/current file. | Obtain the exact ECCO2 model fields used for the visualization and verify grid, units, cadence, and time range; implement a field reader and science mapping. |
| Lightning event sonification | The local preview is a raster image. The project’s documented Earthdata source path did not yield representative LIS science bytes/schema. | Obtain a representative official final LIS file and verify format, record semantics, flags, time, position, and observation coverage. |
| Numerical GEOS aerosol concentration | SVS 5572 documents display categories but its preview does not contain calibrated concentration values. | Obtain matching GEOS fields for the visualization’s period and verify variables, units, grid, layer, and cadence. |
| Source-time dynamic playback | Current playback advances across spatial strips from a single still per experience. | Prepare a bounded official frame sequence or compatible numerical feature series and synchronize media/audio time. |
| Formal accessibility acceptance | Automated/source inspection cannot establish real screen-reader usability or WCAG conformance. | Test keyboard-only plus NVDA workflows with evidence and remediate findings. |
| Production release | No production host, deployment configuration, smoke test, performance report, or hosted API exists. | Select and configure hosting/storage, deploy, then run release, security, outage, and performance checks. |

## Suitability

The local build is runnable and can be presented as an interactive hackathon prototype that follows the PRD’s permitted visualization-derived fallback. Label it clearly as image-derived and do not claim accurate NASA measurements, lightning events, ocean currents, temperatures, or aerosol concentrations. It is **not ready to be represented as the complete scientific product defined by the PRD** until the source-time and science-data gaps above are closed. The software functionality also needs a browser run and target screen-reader verification before claiming acceptance.

See [requirements traceability](REQUIREMENTS_TRACEABILITY.md) and [the resource manifest](RESOURCE_MANIFEST.md) for requirement-level status and checksums.
