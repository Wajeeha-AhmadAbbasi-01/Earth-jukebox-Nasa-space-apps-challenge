# Shared contract boundary

The contracts directory defines data shapes that future adapters must satisfy.
It is not a source adapter and contains no NASA records.

## Provenance envelope

`feature-envelope.schema.json` is the shared boundary between trusted
offline processing and future playback/API code. Every derived feature must
carry:

- a fixed dataset ID and source URL;
- source verification status;
- source/schema/processing/mapping versions;
- source-vs-proxy classification;
- explicit units only when verified;
- limitations and missing-value policy;
- a feature payload whose scientific meaning is documented separately.

`metadata_verified_source_unverified` is valid for audit metadata but is not
valid input for a scientific feature or audio output. A future adapter must
promote a dataset only after the actual source file and schema are inspected.

## Mapping boundary

`mapping-contract.schema.json` and `mapping.py` define only a deterministic
linear normalization contract. They do not choose a scientific feature,
interpret a NASA unit, or produce audio. Missing values are preserved or
rejected according to an explicit policy; they are never converted to zero.
Out-of-range values are clamped only when the contract says `clamp: true`.

## Playback timeline boundary

`playback-timeline.schema.json` and `timeline.py` define a bounded shared
clock for future visualization and audio consumers. The state machine supports
play, pause, resume, stop, restart, seek, speed changes, and deterministic
elapsed-time advancement. It has no frontend, media, browser, or Web Audio
dependency. Duration is limited to 24 hours and speed to 0.125x–8x; time
never advances while paused/stopped and completion clamps at the duration.

## Feature-event boundary

`feature-events.schema.json` and `feature_events.py` compose a verified
feature envelope, a mapping contract, and a timeline snapshot into immutable
timestamped events. They require provenance and mapping-version agreement,
preserve missing values, reject unordered or out-of-bounds timestamps, and cap
event counts. They do not sort source data silently, infer scientific meaning,
or provide an audio/runtime implementation.

## Lightning boundary

`lightning.py` remains deliberately fail-closed. It accepts no real LIS data
until an adapter supplies explicit schema verification and record semantics.
The current NASA investigation identified the official V3 collection and
granule metadata but did not obtain science bytes.
