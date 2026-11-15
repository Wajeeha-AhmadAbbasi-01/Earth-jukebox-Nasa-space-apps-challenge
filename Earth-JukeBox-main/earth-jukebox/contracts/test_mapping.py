import unittest

from contracts.mapping import (
    MappingContractError,
    normalize_values,
    parse_mapping_contract,
)


def contract(**overrides):
    payload = {
        "schema_version": "mapping-contract.v1",
        "mapping_id": "synthetic-linear",
        "version": "v1",
        "input": {
            "feature_name": "synthetic_feature",
            "source_min": 0,
            "source_max": 10,
            "unit": None,
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
    payload.update(overrides)
    return parse_mapping_contract(payload)


class MappingContractTests(unittest.TestCase):
    def test_linear_normalization_is_deterministic(self):
        result = normalize_values([0, 5, 10], contract())
        self.assertEqual(result.values, (20.0, 30.0, 40.0))
        self.assertEqual(result.missing_indices, ())

    def test_clamping_is_explicit_and_bounded(self):
        result = normalize_values([-5, 15], contract())
        self.assertEqual(result.values, (20.0, 40.0))

    def test_missing_is_preserved_not_zeroed(self):
        result = normalize_values([None, 5], contract())
        self.assertEqual(result.values, (None, 30.0))
        self.assertEqual(result.missing_indices, (0,))

    def test_reject_missing_policy_fails_closed(self):
        mapping = contract(missing_value_policy="reject_missing")
        with self.assertRaisesRegex(MappingContractError, "missing"):
            normalize_values([None], mapping)

    def test_invalid_contract_range_is_rejected(self):
        with self.assertRaisesRegex(MappingContractError, "source_min"):
            contract(
                input={
                    "feature_name": "synthetic_feature",
                    "source_min": 10,
                    "source_max": 10,
                    "unit": None,
                }
            )

    def test_non_finite_input_is_rejected(self):
        with self.assertRaisesRegex(MappingContractError, "finite"):
            normalize_values([float("nan")], contract())


if __name__ == "__main__":
    unittest.main()
