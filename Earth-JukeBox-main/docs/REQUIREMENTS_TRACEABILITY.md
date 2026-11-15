# PRD requirements and current evidence

Source: `Earth_Jukebox_PRD_AI_Build_Brief.docx` supplied for this project. The project uses the PRD’s expressly permitted image-derived fallback where numerical source files are unavailable. “Implemented” means implemented for that labeled fallback; it does not mean scientifically calibrated.

| PRD requirement | Current implementation and evidence | Status |
|---|---|---|
| FR-01 Show three experiences | Catalog contains Ocean 3912, Lightning 5011, Aerosols 5572 | Implemented |
| FR-02 Select an experience | Explore cards select the matching player and prepared timeline | Implemented |
| FR-03 Show its NASA visualization/preview | Official previews load from checked-in local assets | Implemented |
| FR-04 Play, pause, resume, stop, replay | Shared Web Audio transport controls | Implemented; browser manual verification still needed |
| FR-05 Volume | Slider and mute control update bounded Web Audio gain | Implemented |
| FR-06 Description, period, attribution | Dataset cards, player notes, source links, manifests | Implemented |
| FR-07 Supported time-window/segment selection | Seek selects position across a 24-strip spatial scan | Partial; not scientific time-window selection |
| FR-08 Explain mapping | Per-experience sound mapping and limitations appear in the player/source panel | Implemented for image proxies |
| FR-09 Spoken welcome/menu | User-activated SpeechSynthesis welcome and options | Implemented; verify on target browsers |
| FR-10 Keyboard and screen-reader navigation | Semantic controls, visible focus styles, status regions, escape-close dialog | Partial; formal NVDA and WCAG 2.2 AA evidence absent |
| FR-11 Optional voice commands | Explicit user-activated SpeechRecognition with unsupported/denied fallback | Implemented where browser supports it; not end-to-end tested here |
| FR-12 Spoken category/playback commands | Commands cover category selection, play, pause, stop, replay, volume, help | Implemented where supported; not end-to-end tested here |
| FR-13 Announce selection and playback state | `aria-live` player and voice status regions | Implemented; screen-reader behavior not formally verified |
| FR-14 Request/replay explanation | User-activated selected explanation speech | Implemented |
| FR-15 Category-specific mapping | Versioned bounded frequency/gain/waveform/pan presets per experience | Implemented for preview proxies |
| FR-16 Sound responds to source changes over time | Sound responds as the shared scan traverses differing preview strips | Partial; the scan is spatial over one still, not source chronology or animation time |
| FR-17 Missing/invalid data safety | Feature ranges and ordering are validated before playback; audio mapping throws for missing/nonfinite/out-of-range brightness rather than substituting zero; explicit load errors | Partial; broad malformed/missing-value matrix remains |
| FR-18 Controlled NASA ingestion | Fixed-host, fixed-asset, bounded acquisition script and provenance records | Implemented for approved preview images, not science products |
| FR-19 Playback independent of NASA | Local images, timelines, and API data; no NASA request in normal playback | Implemented |
| FR-20 Provenance and processing version | Source checksums, processing record, mapping ID/version in timeline and provenance | Implemented for image-proxy artifacts |
| FR-21 Retain last known-good data on ingestion failure | Checksum-gated promotion manifests; checked-in previous artifacts remain in repository | Partial; no remote ingestion service or automated rollback |

## Acceptance criteria

| Acceptance test | Current result |
|---|---|
| AT-01 Categories selectable and described | Pass by implementation; UI contract test covers selection routes |
| AT-02 Offline prepared experiences | Local references and files are present; verify by running with network disconnected |
| AT-03 Visualization/category/period match | Correct PRD source IDs and source periods; each local image is a still, so it does not show the complete source-time sequence |
| AT-04 Documented category mapping | Pass for image-derived mapping, not numerical science variables |
| AT-05 Controlled feature changes alter sound | Pure mapping function is deterministic; three presets and invalid brightness rejection were checked in Node runtime | Pass for proxy inputs; not a scientific calibration test |
| AT-06 Transport and volume | Implemented; browser interaction run remains required |
| AT-07 Audio/visual sync | One clock updates audio, progress, seek, and scan cursor; source-animation synchronization is not implemented |
| AT-08 Spoken guidance/interrupt | Welcome and explanation use SpeechSynthesis; actual target-browser verification remains |
| AT-09 Keyboard/screen reader | Keyboard semantics implemented; NVDA test remains |
| AT-10 Missing/invalid input | Rejected timeline contract and error feedback implemented; broader invalid-data cases remain |
| AT-11 Source/data/mapping traceability | Source checksum, processing and mapping versions are attached to prepared proxy timelines |
| AT-12 NASA outage, mic denial, missing asset | NASA-independent playback is local; speech/microphone/missing-asset paths are coded but require browser verification |

## Delivery boundary

This repository now implements the correct three PRD experiences as a runnable, locally prepared visual-proxy application. It is a valid candidate for a hackathon demo **if clearly described as image-derived sonification**. It is not yet the PRD’s scientifically grounded, source-time product: no numerical ECCO2 temperature/current fields, LIS event records, or GEOS aerosol concentration fields are packaged, and no full NASA animation is synchronized to playback. Formal screen-reader evidence and production deployment checks also remain outstanding.
