import json
import tempfile
import unittest
from pathlib import Path

import preprocess_assets


class PipelineTests(unittest.TestCase):
    def test_config_has_three_allowlisted_datasets_and_https_previews(self):
        config = preprocess_assets.load_config()
        self.assertEqual(
            {item["id"] for item in config["datasets"]},
            {"ocean-3912", "lightning-5011", "aerosols-5572"},
        )
        for item in config["datasets"]:
            self.assertTrue(item["preview_url"].startswith("https://svs.gsfc.nasa.gov/"))
            self.assertEqual(item["source_status"], "metadata_verified_source_unverified")

    def test_png_metadata_is_provenance_only(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sample.png"
            path.write_bytes(
                b"\x89PNG\r\n\x1a\n"
                + b"\x00\x00\x00\rIHDR"
                + (3).to_bytes(4, "big")
                + (2).to_bytes(4, "big")
                + b"\x08\x06\x00\x00\x00"
            )
            result = preprocess_assets.image_metadata(path)
        self.assertEqual(result["format"], "image/png")
        self.assertEqual(result["width"], 3)
        self.assertEqual(result["height"], 2)
        self.assertIsNotNone(result["sha256"])
        self.assertNotIn("value", json.dumps(result))


if __name__ == "__main__":
    unittest.main()
