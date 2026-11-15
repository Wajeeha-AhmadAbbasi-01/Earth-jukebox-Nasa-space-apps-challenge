import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from promote_proxy_assets import MANIFEST_DIR, promote


class PromotionTests(unittest.TestCase):
    def test_promotes_all_verified_proxy_outputs(self):
        for dataset_id in ("ocean-3912", "lightning-5011", "aerosols-5572"):
            result = promote(dataset_id)
            self.assertEqual(result["status"], "promoted")
            self.assertEqual(result["source_vs_proxy"], "image_derived_proxy")
            self.assertEqual(result["temporal_claim"], "none")
            self.assertTrue((MANIFEST_DIR / f"{dataset_id}-last-known-good.json").is_file())


if __name__ == "__main__":
    unittest.main()
