const datasets = [
  {
    number: "01", id: "ocean-3912", type: "ECCO2 · SVS 3912", title: "Ocean currents and temperature", period: "25 Mar 2007 — 3 Mar 2008",
    image: "../data/raw/ocean-3912/flat_global_ecco2_2028x1024.25000.jpg",
    note: "NASA’s ECCO2 visualization pairs surface-current flow with a temperature colour scale. Sound follows rendered image pixels.",
    meta: "NASA ECCO2 visualization", proxy: "Image-derived sound", source: "https://svs.gsfc.nasa.gov/3912/",
    provenance: "NASA/JPL/MIT ECCO2 model visualization; the displayed period is 25 March 2007 to 3 March 2008.",
    verified: "Official SVS 3912 metadata, selected image, model lineage, and visualization period.",
    mapping: "A sine tone (110–470 Hz) follows rendered brightness; display-colour class controls stereo pan.",
    sonificationMapping: { mapping_id: "ocean-rendered-pixel", version: "v1", waveform: "sine", frequency_min_hz: 110, frequency_max_hz: 470, gain_floor: 0.015, gain_brightness_span: 0.09, pan_by_display_color: { warm: 0.25, cool: -0.25, green: 0.1, magenta: -0.1 } },
    blocked: "Underlying ECCO2 numerical fields, current-vector values, exact temperature values per pixel, and temporal frames.",
    timeline: "../data/processed/ocean-3912/proxy-feature-timeline.json",
    gated: false
  },
  {
    number: "02", id: "lightning-5011", type: "ISS LIS · SVS 5011", title: "Lightning events", period: "Jan 2017 — Jul 2023",
    image: "../data/raw/lightning-5011/iss_lightning_preview.jpg",
    note: "ISS LIS visualization with a 10-day roving window. Sound follows rendered image pixels.",
    meta: "NASA LIS visualization", proxy: "Image-derived sound", source: "https://svs.gsfc.nasa.gov/5011/",
    provenance: "ISS LIS quality-controlled visualization; ISS coverage is not continuous global observation.",
    verified: "Official SVS 5011 metadata, preview, and January 2017 through July 2023 display period.",
    mapping: "A soft triangle tone (220–700 Hz) follows rendered brightness; display-colour class controls stereo pan.",
    sonificationMapping: { mapping_id: "lightning-rendered-pixel", version: "v1", waveform: "triangle", frequency_min_hz: 220, frequency_max_hz: 700, gain_floor: 0.015, gain_brightness_span: 0.07, pan_by_display_color: { warm: 0.25, cool: -0.25, green: 0.1, magenta: -0.1 } },
    blocked: "Exact science file schema, record kind, units, quality flags, and SVS source lineage.",
    timeline: "../data/processed/lightning-5011/proxy-feature-timeline.json",
    gated: false
  },
  {
    number: "03", id: "aerosols-5572", type: "GEOS · SVS 5572", title: "Atmospheric aerosols", period: "1 Aug — 14 Sep 2024",
    image: "../data/raw/aerosols-5572/Aerosols_1920x1080_30p_0000.png",
    note: "NASA GEOS visualization for 1 August–14 September 2024. Display colours distinguish aerosol types; sound follows image-derived colour and brightness.",
    meta: "NASA GEOS model visualization", proxy: "Image-derived sound", source: "https://svs.gsfc.nasa.gov/5572/",
    provenance: "NASA Goddard Earth Observing System model visualization, created by NASA GMAO and SVS.",
    verified: "Official SVS 5572 metadata, preview, display categories, and 1 August–14 September 2024 period.",
    mapping: "A sine tone (165–465 Hz) follows rendered brightness; display-colour class controls stereo pan.",
    sonificationMapping: { mapping_id: "aerosols-rendered-pixel", version: "v1", waveform: "sine", frequency_min_hz: 165, frequency_max_hz: 465, gain_floor: 0.015, gain_brightness_span: 0.075, pan_by_display_color: { warm: 0.25, cool: -0.25, green: 0.1, magenta: -0.1 } },
    blocked: "Numerical aerosol fields, concentration units, and exact time-indexed source frames.",
    timeline: "../data/processed/aerosols-5572/proxy-feature-timeline.json",
    gated: false
  }
];

const state = {
  selected: null,
  features: [],
  duration: 24,
  position: 0,
  playing: false,
  muted: false,
  volume: 0.45,
  speed: 1,
  audio: null,
  lastFrame: 0,
  raf: 0,
  previewError: null,
  voiceRecognition: null,
  voiceOn: false,
  narratorOn: true,
  previewStatusLastAnnouncedAt: 0
};

function cardMarkup(dataset, row = false) {
  return `<article class="${row ? "dataset-row" : "dataset-card"}" data-dataset="${dataset.number}">
    <div class="dataset-image" style="background-image:url('${dataset.image}')">${row ? "" : `<span class="dataset-number">${dataset.number}</span>`}</div>
    <div class="${row ? "" : "dataset-body"}">
      <span class="dataset-type">${dataset.type}</span><h3>${dataset.title}</h3>
      <p class="dataset-period">${dataset.period}</p><p>${dataset.note}</p>
      ${row ? "" : `<div class="card-meta"><span>${dataset.meta}</span><span class="proxy">${dataset.proxy}</span></div>`}
      <div class="dataset-actions">
        <button type="button" class="dataset-select" data-select-dataset="${dataset.number}">${row ? "Review in player" : "Open player"} <span aria-hidden="true">→</span></button>
        <button type="button" class="dataset-source" data-open-source="${dataset.number}">Source notes</button>
      </div>
    </div>
  </article>`;
}

document.querySelector("#home-datasets").innerHTML = datasets.map((dataset) => cardMarkup(dataset)).join("");
document.querySelector("#explore-datasets").innerHTML = datasets.map((dataset) => cardMarkup(dataset, true)).join("");

function showView(route) {
  const validRoute = ["home", "explore", "player", "how-it-works", "accessibility", "sources"].includes(route) ? route : "home";
  if ("speechSynthesis" in window) window.speechSynthesis.cancel();
  const dialog = document.querySelector("#methodology-dialog");
  if (dialog.open) dialog.close();
  document.querySelectorAll("[data-view]").forEach((view) => {
    const active = view.dataset.view === validRoute;
    view.hidden = !active;
    view.classList.toggle("active", active);
  });
  document.querySelectorAll(".nav-link").forEach((link) => {
    const active = link.dataset.route === validRoute;
    link.classList.toggle("active", active);
    if (active) link.setAttribute("aria-current", "page");
    else link.removeAttribute("aria-current");
  });
  window.scrollTo({ top: 0, behavior: "smooth" });
  const view = document.querySelector(`[data-view="${validRoute}"]`);
  const heading = view?.querySelector("h1");
  const dataset = selectedDataset();
  const summary = validRoute === "player" && dataset
    ? `${dataset.title}. Press Space to play, H for help.`
    : `${heading?.textContent.trim() || "Earth Jukebox"}. Press H for help.`;
  const announcer = document.querySelector("#page-announcer");
  if (announcer && announcer.textContent !== summary) announcer.textContent = summary;
  if (heading) heading.focus({ preventScroll: true });
}

function selectedDataset() {
  return datasets.find((dataset) => dataset.number === state.selected) || null;
}

function formatTime(seconds) {
  return `00:${String(Math.floor(seconds)).padStart(2, "0")}`;
}

function validateProxyTimeline(payload, dataset) {
  const timeline = payload?.timeline;
  const features = payload?.features;
  if (!Array.isArray(features) || !features.length || features.length > 256) throw new Error("feature list is missing or outside the allowed size");
  if (!Number.isFinite(timeline?.duration_seconds) || timeline.duration_seconds <= 0 || timeline.duration_seconds > 3600 ||
      timeline.segment_count !== features.length) throw new Error("timeline bounds or segment count are invalid");
  const colors = new Set(["warm", "cool", "green", "magenta", "neutral", "mixed", "unclassified"]);
  let previousTime = -1;
  features.forEach((feature, index) => {
    if (feature?.index !== index || !Number.isFinite(feature.time_seconds) || feature.time_seconds < 0 ||
        feature.time_seconds >= timeline.duration_seconds || feature.time_seconds <= previousTime) {
      throw new Error(`feature ${index} has an invalid timeline position`);
    }
    if (typeof feature.rendered_brightness_proxy !== "number" || !Number.isFinite(feature.rendered_brightness_proxy) ||
        feature.rendered_brightness_proxy < 0 || feature.rendered_brightness_proxy > 1) {
      throw new Error(`feature ${index} has missing or invalid brightness; it was not converted to zero`);
    }
    if (!colors.has(feature.color_class_proxy)) throw new Error(`feature ${index} has an unknown display-color class`);
    for (const name of ["low_signal_share", "unclassified_share", "excluded_share"]) {
      if (typeof feature[name] !== "number" || !Number.isFinite(feature[name]) || feature[name] < 0 || feature[name] > 1) {
        throw new Error(`feature ${index} has invalid ${name}`);
      }
    }
    previousTime = feature.time_seconds;
  });
}

function updatePlayer() {
  const dataset = selectedDataset();
  if (!dataset) return;
  document.querySelector(".player-info h2").textContent = `${dataset.title} / image-derived sonification`;
  document.querySelector(".player-copy").textContent =
    `${dataset.verified} ${dataset.mapping} The sound is an artistic, image-derived mapping, not calibrated NASA measurements.`;
  document.querySelector(".player-art-label").innerHTML = `${dataset.number}<br>${dataset.gated ? "SOURCE<br>BLOCKED" : "PROXY<br>FEATURES"}`;
  const image = document.querySelector("#source-preview-image");
  image.src = dataset.image;
  image.alt = `Official NASA SVS preview for ${dataset.title}`;
  document.querySelector("#player-title").textContent = `The listening room / ${dataset.title}`;
  document.title = `Earth Jukebox — ${dataset.title}`;
  const controls = document.querySelectorAll("[data-audio-control], #timeline-seek, #volume-control, #speed-control, [data-mute-toggle]");
  controls.forEach((control) => { control.disabled = !state.features.length; });
  document.querySelector(".unavailable-note").innerHTML = dataset.gated
    ? '<span class="status-dot"></span> Source preview is not ready for playback'
    : '<span class="status-dot"></span> Image-derived sound uses rendered-pixel proxies and is ready to explore';
  updateTransportUi();
}

function updateTransportUi() {
  const cursor = document.querySelector("#scan-cursor");
  if (cursor) cursor.style.left = `${Math.min(100, Math.max(0, state.position / state.duration * 100))}%`;
  document.querySelector("#preview-elapsed").textContent = formatTime(state.position);
  const seek = document.querySelector("#timeline-seek");
  seek.value = state.position;
  seek.setAttribute("aria-valuetext", `${Math.round(state.position)} seconds of ${Math.round(state.duration)}`);
  const toggle = document.querySelector("[data-preview-toggle]");
  toggle.textContent = state.playing ? "Ⅱ" : "▶";
  toggle.setAttribute("aria-label", state.playing ? "Pause proxy sonification" : "Play proxy sonification");
  const status = state.previewError
    ? `Unable to load proxy timeline: ${state.previewError}`
    : !state.features.length
      ? "Playback unavailable — the prepared proxy timeline is missing."
      : state.playing
          ? `Playing image-derived scan at ${formatTime(state.position)}.`
        : state.position >= state.duration
          ? "Image-derived sonification complete."
          : "Ready — explore rendered brightness and colour features.";
  document.querySelector("[data-mute-toggle]").textContent = state.muted ? "🔇" : "🔊";
  document.querySelector("[data-mute-toggle]").setAttribute("aria-pressed", String(state.muted));
  setPreviewStatus(status, !state.playing);
}

function setPreviewStatus(text, force = false) {
  const status = document.querySelector("#preview-status");
  if (!status || status.textContent === text) return;
  const now = performance.now();
  if (state.playing && !force && now - state.previewStatusLastAnnouncedAt < 5000) return;
  status.textContent = text;
  state.previewStatusLastAnnouncedAt = now;
}

async function loadFeatures() {
  try {
    const dataset = selectedDataset();
    const response = await fetch(dataset.timeline, { cache: "no-store" });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const payload = await response.json();
    if (payload.dataset_id !== dataset.id || payload.verification?.source_vs_proxy !== "image_derived_proxy" ||
        JSON.stringify(payload.sonification_mapping) !== JSON.stringify(dataset.sonificationMapping) || !Array.isArray(payload.features)) {
      throw new Error("proxy timeline contract rejected");
    }
    validateProxyTimeline(payload, dataset);
    state.features = payload.features;
    state.duration = payload.timeline.duration_seconds;
    document.querySelector("#timeline-seek").max = state.duration;
    document.querySelector("#preview-duration").textContent = formatTime(state.duration);
  } catch (error) {
    state.previewError = error.message;
  }
  updatePlayer();
}

function ensureAudio() {
  if (!window.AudioContext && !window.webkitAudioContext) throw new Error("Web Audio is not supported in this browser");
  if (!state.audio) {
    const Context = window.AudioContext || window.webkitAudioContext;
    const context = new Context();
    const oscillator = context.createOscillator();
    const padOscillator = context.createOscillator();
    const gain = context.createGain();
    const padGain = context.createGain();
    const filter = context.createBiquadFilter();
    const pan = context.createStereoPanner ? context.createStereoPanner() : null;
    const masterGain = context.createGain();
    oscillator.type = "sine";
    padOscillator.type = "sine";
    filter.type = "lowpass";
    filter.frequency.value = 400;
    filter.Q.value = 0.4;
    masterGain.gain.value = 2 / 3;
    oscillator.connect(gain);
    gain.connect(filter);
    padOscillator.connect(padGain);
    if (pan) {
      filter.connect(pan);
      padGain.connect(pan);
      pan.connect(masterGain);
    } else {
      filter.connect(masterGain);
      padGain.connect(masterGain);
    }
    masterGain.connect(context.destination);
    gain.gain.value = 0;
    padGain.gain.value = 0;
    oscillator.start();
    padOscillator.start();
    state.audio = { context, oscillator, padOscillator, gain, padGain, filter, pan, masterGain };
  }
  return state.audio;
}

function applyAudioFeature() {
  if (!state.audio || !state.features.length) return;
  const feature = EarthJukeboxAudio.timelineValueAt(state.features, state.position);
  const params = EarthJukeboxAudio.featureToAudioParams(feature, state.volume, state.muted, selectedDataset().sonificationMapping);
  const quantizedFrequency = EarthJukeboxAudio.quantizeToPentatonic(params.frequency);
  const now = state.audio.context.currentTime;
  state.audio.oscillator.type = params.waveform;
  state.audio.oscillator.frequency.setTargetAtTime(quantizedFrequency, now, 0.12);
  state.audio.padOscillator.frequency.setTargetAtTime(quantizedFrequency * 1.5, now, 0.12);
  state.audio.gain.gain.setTargetAtTime(state.playing ? params.gain : 0, now, 0.12);
  state.audio.padGain.gain.setTargetAtTime(state.playing ? params.gain * 0.5 : 0, now, 0.12);
  state.audio.filter.frequency.setTargetAtTime(400 + feature.rendered_brightness_proxy * 3600, now, 0.12);
  if (state.audio.pan) state.audio.pan.pan.setTargetAtTime(params.pan, now, 0.12);
}

function frame(timestamp) {
  if (!state.lastFrame) state.lastFrame = timestamp;
  if (state.playing) {
    state.position = Math.min(state.duration, state.position + ((timestamp - state.lastFrame) / 1000) * state.speed);
    applyAudioFeature();
    if (state.position >= state.duration) stopPlayback(true);
    else updateTransportUi();
  }
  state.lastFrame = timestamp;
  state.raf = requestAnimationFrame(frame);
}

async function playPlayback() {
  if (!state.features.length) return;
  try {
    const audio = ensureAudio();
    await audio.context.resume();
    if (state.position >= state.duration) state.position = 0;
    state.playing = true;
    state.previewStatusLastAnnouncedAt = 0;
    applyAudioFeature();
    updateTransportUi();
  } catch (error) {
    state.previewError = error.message;
    updateTransportUi();
  }
}

function pausePlayback() {
  state.playing = false;
  applyAudioFeature();
  updateTransportUi();
}

function stopPlayback(completed = false) {
  state.playing = false;
  if (!completed) state.position = 0;
  applyAudioFeature();
  updateTransportUi();
}

function seekPlayback(value) {
  state.position = Math.max(0, Math.min(state.duration, Number(value)));
  applyAudioFeature();
  updateTransportUi();
}

function speak(text, force = false) {
  if (!force && !state.narratorOn) return;
  if (!("speechSynthesis" in window) || typeof SpeechSynthesisUtterance !== "function") return;
  window.speechSynthesis.cancel();
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.rate = 0.95;
  window.speechSynthesis.speak(utterance);
}

function describeSpot(fx, fy, feature) {
  const dataset = selectedDataset();
  const brightness = feature?.rendered_brightness_proxy ?? 0;
  const tone = brightness > 0.6 ? "high and bright" : brightness > 0.3 ? "in the middle" : "low and soft";
  const colourDescriptions = {
    warm: "warm colours, reds and oranges",
    cool: "cool blue colours",
    green: "green colours",
    magenta: "magenta colours",
    neutral: "grey tones",
    mixed: "mixed colours",
    unclassified: "mostly dark pixels"
  };
  const colour = colourDescriptions[feature?.color_class_proxy] || "mostly dark pixels";
  let place;
  if (dataset.id === "ocean-3912") {
    const longitude = fx * 360 - 180;
    const direction = longitude < 0 ? "west" : longitude > 0 ? "east" : "";
    const longitudeText = Math.abs(longitude) < 0.5
      ? "0 degrees"
      : `${Math.round(Math.abs(longitude))} degrees ${direction}`;
    place = `the ${fy < 0.5 ? "northern" : "southern"} half, longitude about ${longitudeText}`;
  } else {
    place = `${Math.round(fx * 100)} percent across the image`;
  }
  return `Now you are listening to ${dataset.title}, ${place}. This area is drawn in ${colour}, so the tone is ${tone}.`;
}

function describeCurrentPosition() {
  if (!state.features.length) {
    const message = "No prepared timeline is available to describe.";
    setPreviewStatus(message, true);
    return message;
  }
  const feature = EarthJukeboxAudio.timelineValueAt(state.features, state.position);
  const fx = state.duration ? state.position / state.duration : 0;
  const description = describeSpot(fx, 0.5, feature);
  setPreviewStatus(description);
  speak(description);
  return description;
}

function moveScanByStrip(direction) {
  if (!state.features.length) return setPreviewStatus("No prepared timeline is available to scan.", true);
  const stripDuration = state.duration / state.features.length;
  seekPlayback(state.position + direction * stripDuration);
  const feature = EarthJukeboxAudio.timelineValueAt(state.features, state.position);
  const description = feature
    ? describeSpot(state.duration ? state.position / state.duration : 0, 0.5, feature)
    : `Scan position ${Math.round(state.position)} seconds of ${Math.round(state.duration)}.`;
  setPreviewStatus(description);
}

function openSourcePanel(number) {
  const dataset = datasets.find((item) => item.number === number);
  if (!dataset) return;
  const dialog = document.querySelector("#methodology-dialog");
  dialog.querySelector("#methodology-title").textContent = `${dataset.title} / source notes`;
  dialog.querySelector(".dialog-content").innerHTML = `<p>${dataset.note}</p>
    <div class="methodology-grid"><div><strong>Provenance</strong><span>${dataset.provenance}</span></div>
    <div><strong>Verified metadata</strong><span>${dataset.verified}</span></div>
    <div><strong>Sound mapping</strong><span>${dataset.mapping}</span></div>
    <div><strong>Mapping configuration</strong><span>${dataset.sonificationMapping.mapping_id} ${dataset.sonificationMapping.version}</span></div>
    <div><strong>Unresolved</strong><span>${dataset.blocked}</span></div>
    <div><strong>Official source</strong><span><a href="${dataset.source}" target="_blank" rel="noreferrer">${dataset.source} ↗</a></span></div></div>
    <p class="dialog-warning"><span class="status-dot"></span> Status: ${dataset.gated ? "metadata verified, source data unverified. Playback is unavailable." : "local preview acquired; audio is an image-derived proxy only."}</p>`;
  dialog.showModal();
}

function speakSelection() {
  if (!("speechSynthesis" in window)) {
    state.previewError = "Speech synthesis is not supported in this browser";
    return updateTransportUi();
  }
  const dataset = selectedDataset();
  window.speechSynthesis.cancel();
  const utterance = new SpeechSynthesisUtterance(
    `${dataset.title}, ${dataset.period}. ${dataset.note} The sound is an artistic, image-derived mapping, not calibrated NASA measurements.`
  );
  utterance.onstart = () => { setPreviewStatus("Reading selected explanation aloud."); };
  utterance.onend = updateTransportUi;
  utterance.onerror = () => {
    state.previewError = "Speech synthesis could not start";
    updateTransportUi();
  };
  window.speechSynthesis.speak(utterance);
}

function speakWelcome() {
  if (!("speechSynthesis" in window)) {
    document.querySelector("#voice-status").textContent = "Spoken guidance is unavailable in this browser. Use the keyboard-accessible Explore and Player controls.";
    return;
  }
  window.speechSynthesis.cancel();
  const message = "Welcome to Earth Jukebox. Choose Ocean Currents and Temperature, Lightning Events, or Atmospheric Aerosols from Explore. Use the keyboard to navigate, or select Start optional voice command to use speech recognition where supported. Select an experience, then press Play.";
  window.speechSynthesis.speak(new SpeechSynthesisUtterance(message));
  document.querySelector("#voice-status").textContent = "Speaking the welcome and menu options.";
}

function setVoiceStatus(message) {
  document.querySelector("#voice-status").textContent = message;
}

function updateVoiceButton() {
  const button = document.querySelector("[data-start-voice]");
  if (!button) return;
  button.textContent = state.voiceOn ? "Stop voice command" : "Start optional voice command";
  button.setAttribute("aria-pressed", String(state.voiceOn));
}

function stopVoiceCommands(message = "Voice commands stopped. Keyboard controls remain available.") {
  state.voiceOn = false;
  const recognition = state.voiceRecognition;
  state.voiceRecognition = null;
  if (recognition) {
    try { recognition.stop(); } catch (error) { /* recognition may already be stopped */ }
  }
  updateVoiceButton();
  setVoiceStatus(message);
}

function changeVoiceSpeed(direction) {
  const speeds = [0.5, 1, 2];
  const currentIndex = speeds.indexOf(state.speed);
  const current = currentIndex === -1 ? 1 : currentIndex;
  const next = (current + direction + speeds.length) % speeds.length;
  state.speed = speeds[next];
  document.querySelector("#speed-control").value = String(state.speed);
  updateTransportUi();
  setVoiceStatus(`Playback speed set to ${state.speed} times.`);
}

function selectVoiceDataset(number, shouldPlay) {
  const loading = state.selected === number ? Promise.resolve() : selectDataset(number);
  loading.then(() => {
    if (shouldPlay) {
      setVoiceStatus(`Selected ${selectedDataset().title}. Starting playback.`);
      playPlayback();
    } else {
      setVoiceStatus(`Selected ${selectedDataset().title}. Say play to start.`);
    }
  });
}

function runVoiceCommand(command) {
  const text = command.trim().toLowerCase();
  if (/\b(stop listening|stop voice|turn off voice)\b/.test(text)) return stopVoiceCommands();

  const datasetMatch = text.match(/\b(ocean|sea|currents|lightning|lightening|thunder|storm|aerosols?|dust|smoke)\b/);
  if (datasetMatch) {
    const word = datasetMatch[1];
    const match = ["ocean", "sea", "currents"].includes(word) ? "01"
      : ["lightning", "lightening", "thunder", "storm"].includes(word) ? "02" : "03";
    return selectVoiceDataset(match, /\b(play|start)\b/.test(text));
  }

  if (/\b(next|next dataset)\b/.test(text)) {
    const next = String((Number(state.selected || "01") % 3) + 1).padStart(2, "0");
    return selectVoiceDataset(next, false);
  }
  if (/\b(previous|previous dataset|back)\b/.test(text)) {
    const current = Number(state.selected || "01");
    const previous = String(current === 1 ? 3 : current - 1).padStart(2, "0");
    return selectVoiceDataset(previous, false);
  }
  if (/\b(read explanation|read the explanation)\b/.test(text)) {
    speakSelection();
    return setVoiceStatus("Reading the selected explanation aloud.");
  }
  if (/\b(what is this|where am i|describe)\b/.test(text)) {
    const description = describeCurrentPosition();
    return setVoiceStatus(description);
  }
  if (/\b(unmute|turn sound on)\b/.test(text)) {
    state.muted = false;
    applyAudioFeature();
    updateTransportUi();
    return setVoiceStatus("Sound unmuted.");
  }
  if (/\b(mute|silence|turn sound off)\b/.test(text)) {
    state.muted = true;
    applyAudioFeature();
    updateTransportUi();
    return setVoiceStatus("Sound muted.");
  }
  if (/\b(faster|speed up)\b/.test(text)) return changeVoiceSpeed(1);
  if (/\b(slower|slow down)\b/.test(text)) return changeVoiceSpeed(-1);
  if (/\b(pause|wait)\b/.test(text)) {
    pausePlayback();
    return setVoiceStatus("Playback paused.");
  }
  if (/\b(stop|end)\b/.test(text)) {
    stopPlayback();
    return setVoiceStatus("Playback stopped.");
  }
  if (/\b(replay|restart|again)\b/.test(text)) {
    seekPlayback(0);
    return setVoiceStatus("Playback restarted.");
  }
  if (/\b(play|resume|continue)\b/.test(text)) {
    playPlayback();
    return setVoiceStatus("Playback started.");
  }
  if (/\b(volume up|louder)\b/.test(text)) {
    state.volume = Math.min(1, state.volume + 0.1);
    document.querySelector("#volume-control").value = state.volume;
    applyAudioFeature();
    return setVoiceStatus("Volume increased.");
  }
  if (/\b(volume down|quieter)\b/.test(text)) {
    state.volume = Math.max(0, state.volume - 0.1);
    document.querySelector("#volume-control").value = state.volume;
    applyAudioFeature();
    return setVoiceStatus("Volume decreased.");
  }
  if (/\b(help|options|repeat)\b/.test(text)) return speakWelcome();
  setVoiceStatus("Command not recognized. Try play ocean, pause, describe, next dataset, faster, mute, or stop listening.");
}

function startVoiceCommands() {
  if (state.voiceOn) return stopVoiceCommands();
  const Recognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!Recognition) {
    setVoiceStatus("Voice commands are not supported in this browser. Keyboard controls remain available.");
    return;
  }
  try {
    const recognition = new Recognition();
    recognition.lang = "en-US";
    recognition.continuous = true;
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;
    recognition.onresult = (event) => {
      const command = event.results[event.results.length - 1][0].transcript;
      setVoiceStatus(`Heard: ${command}`);
      runVoiceCommand(command);
    };
    recognition.onerror = (event) => {
      if (event.error === "not-allowed") {
        state.voiceOn = false;
        state.voiceRecognition = null;
        updateVoiceButton();
        setVoiceStatus("Microphone access was denied. Use the keyboard controls instead.");
      } else {
        setVoiceStatus(`Voice command unavailable (${event.error}). Use the keyboard controls instead.`);
      }
    };
    recognition.onend = () => {
      state.voiceRecognition = null;
      if (!state.voiceOn) return updateVoiceButton();
      window.setTimeout(() => {
        if (!state.voiceOn) return;
        try {
          state.voiceRecognition = recognition;
          recognition.start();
        } catch (error) {
          state.voiceRecognition = null;
          setVoiceStatus(`Could not restart voice commands: ${error.message}`);
        }
      }, 100);
    };
    state.voiceRecognition = recognition;
    state.voiceOn = true;
    updateVoiceButton();
    recognition.start();
    setVoiceStatus("Listening for voice commands. Microphone access was started by your request.");
  } catch (error) {
    state.voiceOn = false;
    state.voiceRecognition = null;
    updateVoiceButton();
    document.querySelector("#voice-status").textContent = `Could not start voice commands: ${error.message}`;
  }
}

function toggleNarrator() {
  state.narratorOn = !state.narratorOn;
  if (!state.narratorOn && "speechSynthesis" in window) window.speechSynthesis.cancel();
  setPreviewStatus(`Narrator ${state.narratorOn ? "on" : "off"}.`, true);
}

function showKeyboardHelp() {
  if (window.location.hash !== "#accessibility") {
    window.history.pushState({ route: "accessibility" }, "", "#accessibility");
  }
  showView("accessibility");
  const message = "Keyboard shortcuts: 1, 2, or 3 selects and plays an experience. Space plays or pauses. Left and right arrows scan one strip. D describes the current position. N toggles the narrator. V starts or stops voice commands. M mutes. H or question mark speaks help.";
  const announcer = document.querySelector("#page-announcer");
  if (announcer) announcer.textContent = message;
  speak(message, true);
}

function handleGlobalKeyboardShortcuts(event) {
  const target = event.target;
  if (["INPUT", "SELECT", "TEXTAREA", "BUTTON"].includes(target.tagName)) return;
  if (event.ctrlKey || event.altKey || event.metaKey || (event.shiftKey && event.key !== "?")) return;

  if (event.key === "1" || event.key === "2" || event.key === "3") {
    event.preventDefault();
    return selectVoiceDataset(event.key.padStart(2, "0"), true);
  }
  if (event.key === " " || event.key === "Spacebar") {
    event.preventDefault();
    return state.playing ? pausePlayback() : playPlayback();
  }
  if (event.key === "ArrowLeft" || event.key === "ArrowRight") {
    event.preventDefault();
    return moveScanByStrip(event.key === "ArrowRight" ? 1 : -1);
  }
  if (event.key.toLowerCase() === "d") return describeCurrentPosition();
  if (event.key.toLowerCase() === "n") return toggleNarrator();
  if (event.key.toLowerCase() === "v") return startVoiceCommands();
  if (event.key.toLowerCase() === "m") {
    state.muted = !state.muted;
    applyAudioFeature();
    updateTransportUi();
    return setPreviewStatus(state.muted ? "Sound muted." : "Sound unmuted.", true);
  }
  if (event.key.toLowerCase() === "h" || event.key === "?") return showKeyboardHelp();
}

function selectDataset(number) {
  pausePlayback();
  state.position = 0;
  state.features = [];
  state.previewError = null;
  state.selected = number;
  window.history.pushState({ route: "player", dataset: number }, "", `#player/${number}`);
  updatePlayer();
  const loading = loadFeatures();
  showView("player");
  return loading;
}

document.addEventListener("click", (event) => {
  const sourceButton = event.target.closest("[data-open-source]");
  if (sourceButton) return openSourcePanel(sourceButton.dataset.openSource);
  const selectButton = event.target.closest("[data-select-dataset]");
  if (selectButton) return selectDataset(selectButton.dataset.selectDataset);
  if (event.target.closest("[data-open-methodology]")) return document.querySelector("#methodology-dialog").showModal();
  if (event.target.closest("[data-open-selected-source]")) return openSourcePanel(state.selected || "01");
  if (event.target.closest("[data-speak-selection]")) return speakSelection();
  if (event.target.closest("[data-describe-position]")) return describeCurrentPosition();
  if (event.target.closest("[data-speak-welcome]")) return speakWelcome();
  if (event.target.closest("[data-start-voice]")) return startVoiceCommands();
  if (event.target.closest("[data-close-methodology]")) return document.querySelector("#methodology-dialog").close();
  if (event.target.closest("[data-preview-stop]")) return stopPlayback();
  if (event.target.closest("[data-preview-restart]")) return seekPlayback(0);
  if (event.target.closest("[data-preview-toggle]")) return state.playing ? pausePlayback() : playPlayback();
  if (event.target.closest("[data-mute-toggle]")) { state.muted = !state.muted; applyAudioFeature(); return updateTransportUi(); }
  const playerArt = event.target.closest(".player-art");
  if (playerArt) {
    if (!state.features.length) return;
    const bounds = playerArt.getBoundingClientRect();
    const fx = Math.min(1, Math.max(0, (event.clientX - bounds.left) / bounds.width));
    const fy = Math.min(1, Math.max(0, (event.clientY - bounds.top) / bounds.height));
    seekPlayback(fx * state.duration);
    const description = describeSpot(fx, fy, EarthJukeboxAudio.timelineValueAt(state.features, state.position));
    setPreviewStatus(description);
    speak(description);
    return;
  }
  const link = event.target.closest("[data-route], [data-route-link]");
  if (!link) return;
  event.preventDefault();
  const route = link.dataset.route || link.dataset.routeLink;
  window.history.pushState({ route }, "", `#${route}`);
  showView(route);
});

document.querySelector("#timeline-seek").addEventListener("input", (event) => seekPlayback(event.target.value));
document.querySelector("#volume-control").addEventListener("input", (event) => {
  state.volume = Number(event.target.value);
  applyAudioFeature();
});
document.querySelector("#speed-control").addEventListener("change", (event) => {
  state.speed = Number(event.target.value);
  updateTransportUi();
});
function closeMethodologyOnEscape(event) {
  if (event.key === "Escape" && document.querySelector("#methodology-dialog").open) document.querySelector("#methodology-dialog").close();
}
document.addEventListener("keydown", closeMethodologyOnEscape);
document.addEventListener("keydown", handleGlobalKeyboardShortcuts);
document.querySelector("#methodology-dialog").addEventListener("keydown", closeMethodologyOnEscape);
window.addEventListener("popstate", () => {
  const [route, number] = window.location.hash.slice(1).split("/");
  if (route === "player") {
    state.selected = number || state.selected || "01";
    state.features = [];
    state.previewError = null;
    updatePlayer();
    loadFeatures();
  }
  showView(route);
});

const [initialRoute, initialDataset] = window.location.hash.slice(1).split("/");
state.selected = initialDataset || (initialRoute === "player" ? "01" : "01");
showView(initialRoute || "home");
loadFeatures();
requestAnimationFrame(frame);
