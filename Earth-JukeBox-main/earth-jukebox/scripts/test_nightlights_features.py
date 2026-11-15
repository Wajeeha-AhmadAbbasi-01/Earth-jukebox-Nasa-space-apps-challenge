import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from extract_nightlights_features import EXCLUDED_REGIONS, OUTPUT, MANIFEST, _excluded, extract


class NightlightsFeatureTests(unittest.TestCase):
    def test_extract_is_bounded_deterministic_and_proxy_labeled(self):
        first = extract()
        second = extract()
        self.assertEqual(first, second)
        self.assertEqual(len(first["features"]), 24)
        self.assertEqual(first["timeline"]["duration_seconds"], 24.0)
        self.assertEqual(first["verification"]["source_vs_proxy"], "image_derived_proxy")
        self.assertTrue(all(0 <= item["rendered_brightness_proxy"] <= 1 for item in first["features"]))
        self.assertTrue(all("radiance" not in json.dumps(item).lower() for item in first["features"]))
        self.assertEqual(first["verification"]["temporal_claim"], "none")
        self.assertIn("spatial scan", first["timeline"]["semantics"])
        self.assertGreater(len(first["verification"]["excluded_regions"]), 0)
        self.assertTrue(all(0 <= item["unclassified_share"] <= 1 for item in first["features"]))
        self.assertTrue(any(item["unclassified_share"] > 0 for item in first["features"]))
        self.assertTrue(all(item["color_class_proxy"] in {"neutral", "warm", "cool", "mixed", "unclassified"} for item in first["features"]))
        self.assertEqual(first["source"]["sha256"], "6e3e92eae49ca666f2f694efaf17f342bf10c113ead2118f959e48d26e2581bc")

    def test_composite_mask_excludes_insets_and_legend(self):
        self.assertTrue(_excluded(100, 100))
        self.assertTrue(_excluded(500, 160))
        self.assertFalse(_excluded(10, 10))
        self.assertEqual(len(EXCLUDED_REGIONS), 5)

    def test_outputs_and_manifest_exist(self):
        extract()
        self.assertTrue(OUTPUT.is_file())
        self.assertTrue(MANIFEST.is_file())
        payload = json.loads(OUTPUT.read_text(encoding="utf-8"))
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        self.assertEqual(payload["dataset_id"], manifest["dataset_id"])
        self.assertEqual(payload["source"]["sha256"], manifest["acquisition"]["sha256"])


if __name__ == "__main__":
    unittest.main()
