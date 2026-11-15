import unittest

from contracts.lightning import LightningContractError, parse_verified_payload


class LightningContractTests(unittest.TestCase):
    def test_unverified_source_is_rejected_before_records_are_read(self):
        with self.assertRaisesRegex(LightningContractError, "not explicitly verified"):
            parse_verified_payload(
                {
                    "source_schema_verified": False,
                    "records": [{"latitude": 0, "longitude": 0, "detection_time": "2023-01-01T00:00:00Z"}],
                }
            )

    def test_record_kind_must_be_explicit(self):
        with self.assertRaisesRegex(LightningContractError, "source_record_type"):
            parse_verified_payload(
                {
                    "source_schema_verified": True,
                    "source_schema_id": "synthetic-contract-fixture",
                    "records": [],
                }
            )

    def test_verified_contract_normalizes_timestamp_and_coordinates(self):
        result = parse_verified_payload(
            {
                "source_schema_verified": True,
                "source_schema_id": "synthetic-contract-fixture",
                "source_record_type": "fixture-record",
                "records": [
                    {
                        "latitude": 12,
                        "longitude": -45.5,
                        "detection_time": "2023-01-01T03:00:00+03:00",
                    }
                ],
            }
        )
        self.assertEqual(len(result.records), 1)
        self.assertEqual(result.records[0].detection_time.isoformat(), "2023-01-01T00:00:00+00:00")

    def test_invalid_coordinate_is_rejected(self):
        with self.assertRaisesRegex(LightningContractError, "latitude"):
            parse_verified_payload(
                {
                    "source_schema_verified": True,
                    "source_schema_id": "synthetic-contract-fixture",
                    "source_record_type": "fixture-record",
                    "records": [
                        {
                            "latitude": 91,
                            "longitude": 0,
                            "detection_time": "2023-01-01T00:00:00Z",
                        }
                    ],
                }
            )


if __name__ == "__main__":
    unittest.main()
