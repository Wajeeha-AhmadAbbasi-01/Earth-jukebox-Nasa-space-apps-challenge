const assert = require("assert");
const { timelineValueAt, featureToAudioParams, quantizeToPentatonic } = require("./audio_math.js");

const features = [
  { time_seconds: 0, rendered_brightness_proxy: 0.1, color_class_proxy: "cool" },
  { time_seconds: 10, rendered_brightness_proxy: 0.9, color_class_proxy: "warm" }
];

const midpoint = timelineValueAt(features, 5);
assert(Math.abs(midpoint.rendered_brightness_proxy - 0.5) < 0.0001);
assert(featureToAudioParams(midpoint, 0.5, false).frequency >= 180);
assert.strictEqual(timelineValueAt(features, -1).index, undefined);
assert.strictEqual(timelineValueAt(features, 99).rendered_brightness_proxy, 0.9);

const quiet = featureToAudioParams(features[0], 0.5, false);
const bright = featureToAudioParams(features[1], 0.5, false);
assert(bright.frequency > quiet.frequency);
assert(bright.gain > quiet.gain);
assert.strictEqual(featureToAudioParams(features[1], 0.5, true).gain, 0);
assert(featureToAudioParams(features[0], 0.5, false).pan < 0);
assert(featureToAudioParams(features[1], 0.5, false).pan > 0);
const ocean = featureToAudioParams(features[0], 0.5, false, { frequency_min_hz: 110, frequency_max_hz: 470, gain_floor: 0.015, gain_brightness_span: 0.09, waveform: "sine", pan_by_display_color: { cool: -0.25 } });
const lightning = featureToAudioParams(features[0], 0.5, false, { frequency_min_hz: 220, frequency_max_hz: 700, gain_floor: 0.015, gain_brightness_span: 0.07, waveform: "triangle", pan_by_display_color: { cool: -0.25 } });
const aerosols = featureToAudioParams(features[0], 0.5, false, { frequency_min_hz: 165, frequency_max_hz: 465, gain_floor: 0.015, gain_brightness_span: 0.075, waveform: "sine", pan_by_display_color: { cool: -0.25 } });
assert(ocean.frequency !== lightning.frequency && lightning.frequency !== aerosols.frequency);
assert.strictEqual(lightning.waveform, "triangle");
assert.throws(() => featureToAudioParams({ ...features[0], rendered_brightness_proxy: null }, 0.5, false), /finite number/);
assert.throws(() => featureToAudioParams({ ...features[0], rendered_brightness_proxy: Number.NaN }, 0.5, false), /finite number/);
for (const params of [ocean, lightning, aerosols]) {
  assert(params.frequency >= 100 && params.frequency <= 800);
  assert(params.gain >= 0 && params.gain <= 0.12);
  assert(params.pan >= -1 && params.pan <= 1);
}
for (const frequency of [55, 110, 130, 220, 440, 880]) {
  const quantized = quantizeToPentatonic(frequency);
  assert(Number.isFinite(quantized) && quantized > 0);
  assert.strictEqual(quantizeToPentatonic(quantized), quantized);
}
assert.strictEqual(quantizeToPentatonic(110), 110);
assert.strictEqual(quantizeToPentatonic(220), 220);
assert(Math.abs(quantizeToPentatonic(123) - 110 * 2 ** (2 / 12)) < 0.0001);
assert(Math.abs(quantizeToPentatonic(150) - 110 * 2 ** (4 / 12)) < 0.0001);
assert.throws(() => quantizeToPentatonic(0), /finite positive/);
assert.throws(() => quantizeToPentatonic(Number.NaN), /finite positive/);
console.log("audio math tests passed");
