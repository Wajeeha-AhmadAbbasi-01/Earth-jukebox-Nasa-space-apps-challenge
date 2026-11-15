# Earth Jukebox browser application

The browser application presents the PRD’s NASA SVS 3912 Ocean, SVS 5011 Lightning, and SVS 5572 Aerosols experiences. Official local previews are paired with checked-in image-derived features. Play starts synthesized Web Audio after a user gesture; one clock drives the sound, elapsed time, seek control, and preview scan cursor.

The sonification is a documented visual proxy. It does not decode numerical science data, recover source chronology, or infer physical units, lightning events, temperatures, or aerosol concentrations. The app’s source notes explain what the pixels do and do not represent.

## Run locally

From the repository root:

```powershell
python -m http.server 4180 --directory .
```

Open <http://localhost:4180/earth-jukebox/prototype/>. NASA is not contacted during playback.

## Accessibility controls

- All core browsing and player controls work by keyboard.
- Speech synthesis for the welcome menu and selected explanation is user-activated.
- Voice commands are optional and request microphone access only after the user activates **Start optional voice command**.
- If speech recognition is unsupported or permission is denied, keyboard controls remain available.

## Feature regeneration

Install Pillow with `python -m pip install -r earth-jukebox/requirements-pipeline.txt`, then run the three commands in [the Earth Jukebox README](../README.md). Each command reads only the matching checked-in preview and writes its feature timeline and provenance manifest.
