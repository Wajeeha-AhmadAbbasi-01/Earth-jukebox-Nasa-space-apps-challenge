(function (root, factory) {
  if (typeof module === "object" && module.exports) module.exports = factory();
  else root.EarthJukeboxAudio = factory();
}(typeof self !== "undefined" ? self : this, function () {
  function clamp(value, minimum, maximum) {
    return Math.min(maximum, Math.max(minimum, value));
  }

  function quantizeToPentatonic(frequencyHz, rootHz = 110) {
    if (!Number.isFinite(frequencyHz) || frequencyHz <= 0 || !Number.isFinite(rootHz) || rootHz <= 0) {
      throw new TypeError("frequency and root must be finite positive numbers");
    }
    const semitoneOffsets = [0, 2, 4, 7, 9, 12];
    const relativeSemitones = 12 * Math.log2(frequencyHz / rootHz);
    const octave = Math.floor(relativeSemitones / 12);
    let nearest = rootHz;
    let smallestDistance = Number.POSITIVE_INFINITY;
    for (const candidateOctave of [octave - 1, octave, octave + 1]) {
      for (const offset of semitoneOffsets) {
        const semitones = candidateOctave * 12 + offset;
        const candidate = rootHz * 2 ** (semitones / 12);
        const distance = Math.abs(relativeSemitones - semitones);
        if (distance < smallestDistance) {
          nearest = candidate;
          smallestDistance = distance;
        }
      }
    }
    return nearest;
  }

  function timelineValueAt(features, seconds) {
    if (!features.length) return null;
    if (seconds <= features[0].time_seconds) return features[0];
    const last = features[features.length - 1];
    if (seconds >= last.time_seconds) return last;
    for (let index = 1; index < features.length; index += 1) {
      const right = features[index];
      const left = features[index - 1];
      if (seconds <= right.time_seconds) {
        const ratio = (seconds - left.time_seconds) / (right.time_seconds - left.time_seconds);
        const brightness = left.rendered_brightness_proxy
          + (right.rendered_brightness_proxy - left.rendered_brightness_proxy) * ratio;
        return { ...right, rendered_brightness_proxy: brightness };
      }
    }
    return last;
  }

  function featureToAudioParams(feature, volume, muted, mapping = null) {
    const rawBrightness = feature?.rendered_brightness_proxy;
    if (typeof rawBrightness !== "number" || !Number.isFinite(rawBrightness) || rawBrightness < 0 || rawBrightness > 1) {
      throw new TypeError("rendered brightness proxy must be a finite number between 0 and 1");
    }
    const brightness = rawBrightness;
    const preset = mapping || { frequency_min_hz: 180, frequency_max_hz: 720, gain_floor: 0.015, gain_brightness_span: 0.12, waveform: "sine", pan_by_display_color: { warm: 0.25, cool: -0.25 } };
    const frequency = preset.frequency_min_hz + brightness * (preset.frequency_max_hz - preset.frequency_min_hz);
    const gain = muted ? 0 : clamp(volume, 0, 1) * (preset.gain_floor + brightness * preset.gain_brightness_span);
    const pan = preset.pan_by_display_color?.[feature.color_class_proxy] || 0;
    return { frequency, gain: clamp(gain, 0, 0.12), pan: clamp(pan, -1, 1), waveform: preset.waveform };
  }

  return { clamp, timelineValueAt, featureToAudioParams, quantizeToPentatonic };
}));
