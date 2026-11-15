import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).parent
HTML = (ROOT / "index.html").read_text(encoding="utf-8")
APP = (ROOT / "app.js").read_text(encoding="utf-8")
CSS = (ROOT / "styles.css").read_text(encoding="utf-8")


class PrototypeInteractionContractTests(unittest.TestCase):
    def test_all_visible_controls_have_handlers_or_native_navigation(self):
        required_controls = [
            'data-route="home"',
            'data-route="explore"',
            'data-route="player"',
            'data-route="how-it-works"',
            'data-route="accessibility"',
            'data-route="sources"',
            'data-route-link="explore"',
            'data-route-link="player"',
            "data-select-dataset",
            "data-open-source",
            "data-open-methodology",
            "data-close-methodology",
            "data-preview-restart",
            "data-preview-toggle",
            "data-preview-stop",
            "data-mute-toggle",
            "data-open-selected-source",
            "data-speak-selection",
            "data-speak-welcome",
            "data-start-voice",
        ]
        for control in required_controls:
            self.assertTrue(control in HTML or control in APP, control)
        for handler in [
            "selectDataset(",
            "openSourcePanel(",
            "showModal()",
            "dialog.close()",
            "state.position = 0",
            "state.position >= state.duration",
            "event.key === \"Escape\"",
        ]:
            self.assertIn(handler, APP, handler)

    def test_three_fixed_dataset_ids_and_routes_are_present(self):
        self.assertEqual(len(re.findall(r'number: "0[1-3]"', APP)), 3)
        self.assertIn("data-select-dataset", APP)
        self.assertIn("data-open-source", APP)
        self.assertIn('window.history.pushState({ route: "player", dataset: number }', APP)
        self.assertIn('showView(initialRoute || "home")', APP)
        self.assertIn('"how-it-works"', APP)
        self.assertIn('"accessibility"', APP)
        self.assertIn('"sources"', APP)

    def test_external_links_are_explicit_and_safe(self):
        self.assertIn('href="https://svs.gsfc.nasa.gov/" target="_blank" rel="noreferrer"', HTML)
        self.assertIn('rel="noreferrer">${dataset.source}', APP)

    def test_scientific_playback_remains_disabled_by_contract(self):
        self.assertIn("not calibrated", APP)
        self.assertIn("rendered-pixel proxies", APP)
        self.assertIn("AudioContext", APP)
        self.assertNotIn("<audio", HTML.lower())
        self.assertIn("gated", APP)
        self.assertIn("startVoiceCommands", APP)
        self.assertIn("recognition.start()", APP)
        self.assertIn("validateProxyTimeline", APP)
        self.assertIn("it was not converted to zero", APP)
        self.assertIn("speechSynthesis", APP)
        self.assertIn('id="speed-control"', HTML)
        self.assertIn('state.speed', APP)

    def test_browser_fetch_is_local_and_fixed(self):
        self.assertIn('fetch(dataset.timeline', APP)
        self.assertIn('"../data/processed/lightning-5011/proxy-feature-timeline.json"', APP)
        self.assertIn('"../data/processed/ocean-3912/proxy-feature-timeline.json"', APP)
        self.assertIn('"../data/processed/aerosols-5572/proxy-feature-timeline.json"', APP)
        self.assertNotIn("fetch(`", APP)

    def test_speech_and_failure_paths_are_explicit(self):
        self.assertIn("SpeechSynthesisUtterance", APP)
        self.assertIn("Speech synthesis is not supported", APP)
        self.assertIn("Unable to load proxy timeline", APP)
        self.assertIn("proxy timeline contract rejected", APP)

    def test_accessibility_hardening_contract(self):
        self.assertIn('main id="main-content" tabindex="-1"', HTML)
        self.assertIn('role="status" aria-live="polite"', HTML)
        self.assertIn("focus-visible", CSS)
        self.assertIn("prefers-reduced-motion", CSS)
        self.assertIn("forced-colors", CSS)
        self.assertIn('aria-label="Proxy scan speed"', HTML)


if __name__ == "__main__":
    unittest.main()
