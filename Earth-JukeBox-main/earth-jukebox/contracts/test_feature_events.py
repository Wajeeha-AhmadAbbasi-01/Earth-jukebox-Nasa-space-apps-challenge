import unittest

from contracts.feature_events import (
    FeatureEventContractError,
    build_feature_event_timeline,
)
from contracts.mapping import parse_mapping_contract
from contracts.timeline import PlaybackTimeline


def mapping():
    return parse_mapping_contract(
        {
            "schema_version": "mapping-contract.v1",
            "mapping_id": "synthetic-linear",
            "version": "v1",
            "input": {
                "feature_name": "synthetic_feature",
                "source_min": 0,
                "source_max": 10,
                "unit": "synthetic-units",
            },
            "output": {
                "parameter_name": "synthetic_parameter",
                "target_min": 20,
                "target_max": 40,
            },
            "transform": "linear",
            "clamp": True,
            "missing_value_policy": "preserve_missing",
        }
    )


def envelope(**overrides):
    result = {
        "schema_version": "feature-envelope.v1",
        "dataset_id": "lightning-5011",
        "source": {
            "official_url": "https://example.invalid/source",
            "retrieval_timestamp": "2026-11-14T00:00:00Z",
            "source_version": "synthetic-source-v1",
            "source_vs_proxy": "verified_source",
        },
        "verification": {
            "status": "verified",
            "schema_verified": True,
            "record_semantics_verified": True,
            "limitations": [],
        },
        "processing": {
            "version": "processing-v1",
            "method": "synthetic fixture",
            "missing_value_policy": "preserve_missing",
        },
        "mapping": {"version": "v1", "name": "synthetic-linear"},
        "features": [
            {
                "name": "synthetic_feature",
                "values": [0, None, 10],
                "unit": "synthetic-units",
                "meaning": "test-only value",
            }
        ],
    }
    result.update(overrides)
    return result


class FeatureEventTimelineTests(unittest.TestCase):
    def test_orders_events_and_carries_provenance_versions(self):
        result = build_feature_event_timeline(
            envelope(), mapping(), PlaybackTimeline(10).snapshot(),
            "synthetic_feature", [0, 2, 10]
        )
        self.assertEqual(
            [event.timestamp_seconds for event in result.events], [0.0, 2.0, 10.0]
        )
        self.assertEqual(result.source_version, "synthetic-source-v1")
        self.assertEqual(result.processing_version, "processing-v1")
        self.assertEqual(result.mapping_version, "v1")
        self.assertEqual(result.schema_version, "feature-events.v1")

    def test_missing_value_is_preserved(self):
        result = build_feature_event_timeline(
            envelope(), mapping(), PlaybackTimeline(10).snapshot(),
            "synthetic_feature", [0, 2, 10]
        )
        self.assertIsNone(result.events[1].source_value)
        self.assertIsNone(result.events[1].mapped_value)

    def test_out_of_order_timestamps_are_rejected(self):
        with self.assertRaisesRegex(FeatureEventContractError, "non-decreasing"):
            build_feature_event_timeline(
                envelope(), mapping(), PlaybackTimeline(10).snapshot(),
                "synthetic_feature", [0, 3, 2]
            )

    def test_unverified_provenance_is_rejected(self):
        invalid = envelope(
            verification={
                "status": "metadata_verified_source_unverified",
                "schema_verified": False,
                "record_semantics_verified": False,
                "limitations": ["synthetic only"],
            }
        )
        with self.assertRaisesRegex(FeatureEventContractError, "status=verified"):
            build_feature_event_timeline(
                invalid, mapping(), PlaybackTimeline(10).snapshot(),
                "synthetic_feature", [0, 2, 10]
            )

    def test_mapping_provenance_mismatch_is_rejected(self):
        invalid = envelope(mapping={"version": "v2", "name": "synthetic-linear"})
        with self.assertRaisesRegex(FeatureEventContractError, "version"):
            build_feature_event_timeline(
                invalid, mapping(), PlaybackTimeline(10).snapshot(),
                "synthetic_feature", [0, 2, 10]
            )

    def test_timestamp_bounds_and_count_are_enforced(self):
        with self.assertRaisesRegex(FeatureEventContractError, "within"):
            build_feature_event_timeline(
                envelope(), mapping(), PlaybackTimeline(10).snapshot(),
                "synthetic_feature", [0, 11, 12]
            )
        invalid = envelope(
            features=[
                {
                    "name": "synthetic_feature",
                    "values": list(range(100001)),
                    "unit": "synthetic-units",
                    "meaning": "test-only value",
                }
            ]
        )
        with self.assertRaisesRegex(FeatureEventContractError, "event count"):
            build_feature_event_timeline(
                invalid, mapping(), PlaybackTimeline(86400).snapshot(),
                "synthetic_feature", [0.0 for _ in range(100001)]
            )

    def test_selected_feature_and_value_lengths_must_match(self):
        invalid = envelope(
            features=[
                {
                    "name": "synthetic_feature",
                    "values": [1],
                    "unit": "synthetic-units",
                    "meaning": "test-only value",
                }
            ]
        )
        with self.assertRaisesRegex(FeatureEventContractError, "equal length"):
            build_feature_event_timeline(
                invalid, mapping(), PlaybackTimeline(10).snapshot(),
                "synthetic_feature", [0, 1]
            )


if __name__ == "__main__":
    unittest.main()
