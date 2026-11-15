# Earth Jukebox resource manifest

**Checked:** 2026-11-15. NASA facts below were verified against the official SVS pages and APIs. Local preview hashes were computed from the acquired files. Page/API metadata and image-derived features do not certify the underlying numerical science fields.

| Experience | Official source and period | Prepared local asset | What is verified | What is not verified / represented |
|---|---|---|---|---|
| Ocean | [SVS 3912](https://svs.gsfc.nasa.gov/3912/), ECCO2 visualization from 2007-03-25 12:00 UTC to 2008-03-03 12:00 UTC | `earth-jukebox/data/raw/ocean-3912/flat_global_ecco2_2028x1024.25000.jpg`; JPEG, 2048×1024, 1,026,047 bytes; SHA-256 `dcfd17864c2940f9ce1cf406e866818379991d57b0e900f9b8812f0c7cf72e3c` | Official image, ECCO2 provenance, displayed period, and SVS temperature color-scale description | No ECCO2 numerical temperature/current fields are included. Pixels do not recover calibrated temperature, current direction/speed, or source chronology. |
| Lightning | [SVS 5011](https://svs.gsfc.nasa.gov/5011/), quality-controlled ISS LIS visualization from January 2017 through July 2023 | `earth-jukebox/data/raw/lightning-5011/iss_lightning_preview.jpg`; JPEG, 1024×576, 266,956 bytes; SHA-256 `34814a64183e515909f414051c17d30209ea1e30cd941c2e7c8f50ff1e884580` | Official preview, described dates, ISS LIS context, and known latitude/longitude/detection-time descriptions | No source records are included. Event/group/flash semantics, numerical schema, units, quality flags, exact SVS lineage, and event-level timing are not verified. ISS observations are not continuous global coverage. |
| Aerosols | [SVS 5572](https://svs.gsfc.nasa.gov/5572/), GEOS visualization from August 1 to September 14, 2024 | `earth-jukebox/data/raw/aerosols-5572/Aerosols_1920x1080_30p_0000.png`; PNG, 1920×1080, 3,697,656 bytes; SHA-256 `5c4b8dea8edc9cb5b805e3d04718364ae2d1434c9cd028afec63a640a7d8d90f` | Official preview, time coverage, GEOS model basis, and documented type colors (sea salt, dust, smoke, sulfates) | No numerical GEOS concentration fields or time-indexed frames are included. Display colors are categories, not concentration units. |

## Processing and sound mapping

The fixed allowlist is in `earth-jukebox/configs/datasets.json`. Acquisition is bounded to NASA SVS media and configured at 5 MiB maximum per preview. The image feature processor makes a 320×180-or-smaller analysis copy and calculates 24 equal-width strip summaries: rendered brightness, display-color proxy, low-signal share, source-pixel bounds, and checksums/provenance. It does not treat preview pixels as numerical science measurements.

Web Audio maps each dataset’s bounded brightness proxy to its documented frequency/gain range and color class to stereo pan. Ocean uses a sine tone, Lightning a soft triangle tone, and Aerosols a sine tone. The playback index is a left-to-right spatial scan across one prepared preview, not the NASA source timeline. The scan cursor, seek control, and audio share one playback clock.

## Attribution

Credit each visualization to its NASA SVS source page and the associated NASA teams/credits listed there. Ocean 3912 depicts ECCO2 model output; Lightning 5011 uses an ISS LIS quality-controlled science visualization; Aerosols 5572 was developed by NASA GMAO and SVS from GEOS model output. The locally acquired files are preview media; no numerical datasets are redistributed by this project.

## Acquisition record

The exact official asset URLs and IDs are recorded in the dataset config and each per-dataset provenance manifest. Asset requests were made to the official `svs.gsfc.nasa.gov` media host; the application serves the resulting local files and does not contact NASA during playback. No large movies, frame sets, credentials, or numerical science files were downloaded.
