import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from extract_visual_proxy_features import extract


class VisualProxyFeatureTests(unittest.TestCase):
    def test_both_preview_timelines_are_deterministic_and_non_scientific(self):
        for dataset_id in ("ocean-3912", "lightning-5011", "aerosols-5572"):
            first = extract(dataset_id)
            second = extract(dataset_id)
            self.assertEqual(first, second)
            self.assertEqual(len(first["features"]), 24)
            self.assertEqual(first["verification"]["temporal_claim"], "none")
            self.assertEqual(first["verification"]["source_vs_proxy"], "image_derived_proxy")
            self.assertIn("spatial scan", first["timeline"]["semantics"])
            self.assertTrue(all(0 <= item["rendered_brightness_proxy"] <= 1 for item in first["features"]))
            self.assertTrue(all(0 <= item["low_signal_share"] <= 1 for item in first["features"]))
            self.assertNotIn("event_count", json.dumps(first).lower())
            self.assertNotIn("concentration_value", json.dumps(first).lower())


if __name__ == "__main__":
    unittest.main()
