import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi.testclient import TestClient
from api.app import app


class ApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_health_and_fixed_dataset_list(self):
        self.assertEqual(self.client.get("/api/v1/health").status_code, 200)
        response = self.client.get("/api/v1/datasets")
        self.assertEqual(response.status_code, 200)
        self.assertEqual({item["id"] for item in response.json()["items"]}, {"ocean-3912", "lightning-5011", "aerosols-5572"})

    def test_all_dataset_routes_are_bounded_and_proxy_labeled(self):
        for dataset_id in ("ocean-3912", "lightning-5011", "aerosols-5572"):
            self.assertEqual(self.client.get(f"/api/v1/datasets/{dataset_id}").status_code, 200)
            timeline = self.client.get(f"/api/v1/datasets/{dataset_id}/timeline").json()
            self.assertEqual(timeline["timeline"]["segment_count"], 24)
            features = self.client.get(f"/api/v1/datasets/{dataset_id}/features?start=0&limit=2")
            self.assertEqual(features.status_code, 200)
            self.assertEqual(len(features.json()["items"]), 2)
            self.assertEqual(self.client.get(f"/api/v1/datasets/{dataset_id}/statistics").json()["source_vs_proxy"], "image_derived_proxy")

    def test_invalid_ids_ranges_and_no_file_or_url_endpoint(self):
        self.assertEqual(self.client.get("/api/v1/datasets/nope").status_code, 404)
        self.assertEqual(self.client.get("/api/v1/datasets/lightning-5011/features?limit=9999").status_code, 422)
        self.assertEqual(self.client.get("/api/v1/raw/C:/secret").status_code, 404)
        self.assertEqual(self.client.get("/api/v1/fetch?url=https://example.com").status_code, 404)


if __name__ == "__main__":
    unittest.main()
