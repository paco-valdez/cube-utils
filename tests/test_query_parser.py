import unittest
from cube_utils.query_parser import extract_cubes


class TestExtractCubes(unittest.TestCase):

    def test_extract_cubes_with_all_fields(self):
        payload = {
            "dimensions": ["test_a.city", "test_a.country", "test_a.state"],
            "measures": ["test_b.count"],
            "filters": [
                {"values": ["US"], "member": "test_a.country", "operator": "equals"}
            ],
            "timeDimensions": [
                {
                    "dimension": "test_c.time",
                    "dateRange": ["2021-01-01", "2021-12-31"],
                    "granularity": "month",
                }
            ],
        }
        expected_cubes = ["test_a", "test_b", "test_c"]
        self.assertEqual(sorted(extract_cubes(payload)), sorted(expected_cubes))

    def test_extract_cubes_with_dimensions_only(self):
        payload = {"dimensions": ["test_a.city", "test_a.country", "test_a.state"]}
        expected_cubes = ["test_a"]
        self.assertEqual(sorted(extract_cubes(payload)), sorted(expected_cubes))

    def test_extract_cubes_with_measures_only(self):
        payload = {"measures": ["test_b.count"]}
        expected_cubes = ["test_b"]
        self.assertEqual(sorted(extract_cubes(payload)), sorted(expected_cubes))

    def test_extract_cubes_with_filters_only(self):
        payload = {
            "filters": [
                {"values": ["US"], "member": "test_a.country", "operator": "equals"}
            ]
        }
        expected_cubes = ["test_a"]
        self.assertEqual(sorted(extract_cubes(payload)), sorted(expected_cubes))

    def test_extract_cubes_with_timeDimensions_only(self):
        payload = {
            "timeDimensions": [
                {
                    "dimension": "test_c.time",
                    "dateRange": ["2021-01-01", "2021-12-31"],
                    "granularity": "month",
                }
            ]
        }
        expected_cubes = ["test_c"]
        self.assertEqual(sorted(extract_cubes(payload)), sorted(expected_cubes))

    def test_extract_cubes_with_empty_payload(self):
        payload = {}
        expected_cubes = []
        self.assertEqual(extract_cubes(payload), expected_cubes)


    def test_extract_cubes_with_invalid_keywords(self):
        payload = {"invalid": ["test_a.city", "test_a.country", "test_a.state"]}
        expected_cubes = []
        self.assertEqual(extract_cubes(payload), expected_cubes)


if __name__ == "__main__":
    unittest.main()
