import unittest
from cube_utils.query_parser import (
    extract_cubes,
    extract_members,
    extract_filters_members,
)


class TestExtractCubes(unittest.TestCase):

    def test_extract_cubes_with_all_fields(self):
        payload = {
            "dimensions": ["test_a.city", "test_a.country", "test_a.state"],
            "measures": ["test_b.count"],
            "filters": [
                {"values": ["US"], "member": "test_a.country", "operator": "equals"}
            ],
            "segments": ["test_d.us_segment"],
            "timeDimensions": [
                {
                    "dimension": "test_c.time",
                    "dateRange": ["2021-01-01", "2021-12-31"],
                    "granularity": "month",
                }
            ],
        }
        expected_cubes = ["test_a", "test_b", "test_c", "test_d"]
        self.assertEqual(sorted(extract_cubes(payload)), sorted(expected_cubes))

    def test_complex_boolean_logic(self):
        payload = {
            "segments": [],
            "filters": [
                {
                    "or": [
                        {
                            "and": [
                                {
                                    "values": ["Corpus Christi"],
                                    "member": "test_a.city",
                                    "operator": "equals",
                                },
                                {
                                    "member": "test_b.age_bucket",
                                    "operator": "equals",
                                    "values": ["Senior adult"],
                                },
                            ]
                        },
                        {
                            "member": "test_c.city",
                            "operator": "equals",
                            "values": ["Sacramento"],
                        },
                    ]
                },
                {"or": [{"member": "test_d.city", "operator": "set"}]},
            ],
        }
        expected_cubes = ["test_a", "test_b", "test_c", "test_d"]
        self.assertEqual(sorted(extract_cubes(payload)), sorted(expected_cubes))

    def test_pushed_down_query_with_measures(self):
        payload = {
            "segments": [],
            "timezone": "UTC",
            "measures": [
                {
                    "cubeName": "test_a",
                    "name": "foo",
                    "expressionName": "foo",
                    "definition": '{"cubeName":"test_a","alias":"foo","expr":{"type":"SqlFunction","cubeParams":["test_a"],"sql":"MIN(${test_a.active_from_at})"},"groupingSet":null}',
                    "expression": [
                        "test_a",
                        "return `MIN(${test_a.active_from_at})`",
                    ],
                    "groupingSet": None,
                },
                {
                    "definition": '{"cubeName":"test_b","alias":"bar","expr":{"type":"SqlFunction","cubeParams":["test_b"],"sql":"MAX(${test_b.active_from_at})"},"groupingSet":null}',
                    "groupingSet": None,
                    "expression": [
                        "test_b",
                        "return `MAX(${test_b.active_from_at})`",
                    ],
                    "name": "bar",
                    "cubeName": "test_b",
                    "expressionName": "bar",
                },
                {
                    "name": "count_uint8_1__",
                    "expressionName": "count_uint8_1__",
                    "groupingSet": None,
                    "cubeName": "test_c",
                    "expression": [
                        "test_c",
                        "return `${test_c.count}`",
                    ],
                    "definition": '{"cubeName":"test_c","alias":"count_uint8_1__","expr":{"type":"SqlFunction","cubeParams":["test_c"],"sql":"${test_c.count}"},"groupingSet":null}',
                },
            ],
            "filters": [],
            "timeDimensions": [],
            "order": [],
            "dimensions": [],
            "subqueryJoins": [],
            "limit": None,
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

    def test_extract_cubes_with_segments_only(self):
        payload = {"segments": ["test_a.us_segment"]}
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


class TestExtractMembers(unittest.TestCase):

    def test_extract_members_with_all_fields(self):
        payload = {
            "dimensions": ["test_a.city", "test_a.country", "test_a.state"],
            "measures": ["test_b.count"],
            "filters": [
                {"values": ["US"], "member": "test_a.country", "operator": "equals"}
            ],
            "segments": ["test_d.us_segment"],
            "timeDimensions": [
                {
                    "dimension": "test_c.time",
                    "dateRange": ["2021-01-01", "2021-12-31"],
                    "granularity": "month",
                }
            ],
        }
        expected_members = [
            "test_a.city",
            "test_a.country",
            "test_a.state",
            "test_b.count",
            "test_c.time",
            "test_d.us_segment",
        ]
        self.assertEqual(sorted(extract_members(payload)), sorted(expected_members))

    def test_complex_boolean_logic_members(self):
        payload = {
            "segments": [],
            "filters": [
                {
                    "or": [
                        {
                            "and": [
                                {
                                    "values": ["Corpus Christi"],
                                    "member": "test_a.city",
                                    "operator": "equals",
                                },
                                {
                                    "member": "test_b.age_bucket",
                                    "operator": "equals",
                                    "values": ["Senior adult"],
                                },
                            ]
                        },
                        {
                            "member": "test_c.city",
                            "operator": "equals",
                            "values": ["Sacramento"],
                        },
                    ]
                },
                {"or": [{"member": "test_d.city", "operator": "set"}]},
            ],
        }
        expected_members = [
            "test_a.city",
            "test_b.age_bucket",
            "test_c.city",
            "test_d.city",
        ]
        self.assertEqual(sorted(extract_members(payload)), sorted(expected_members))

    def test_extract_members_with_dimensions_only(self):
        payload = {"dimensions": ["test_a.city", "test_a.country", "test_a.state"]}
        expected_members = ["test_a.city", "test_a.country", "test_a.state"]
        self.assertEqual(sorted(extract_members(payload)), sorted(expected_members))

    def test_extract_members_with_measures_only(self):
        payload = {"measures": ["test_b.count"]}
        expected_members = ["test_b.count"]
        self.assertEqual(sorted(extract_members(payload)), sorted(expected_members))

    def test_extract_members_with_filters_only(self):
        payload = {
            "filters": [
                {"values": ["US"], "member": "test_a.country", "operator": "equals"}
            ]
        }
        expected_members = ["test_a.country"]
        self.assertEqual(sorted(extract_members(payload)), sorted(expected_members))

    def test_extract_members_with_segments_only(self):
        payload = {"segments": ["test_a.us_segment"]}
        expected_members = ["test_a.us_segment"]
        self.assertEqual(sorted(extract_members(payload)), sorted(expected_members))

    def test_extract_members_with_timeDimensions_only(self):
        payload = {
            "timeDimensions": [
                {
                    "dimension": "test_c.time",
                    "dateRange": ["2021-01-01", "2021-12-31"],
                    "granularity": "month",
                }
            ]
        }
        expected_members = ["test_c.time"]
        self.assertEqual(sorted(extract_members(payload)), sorted(expected_members))

    def test_extract_members_with_empty_payload(self):
        payload = {}
        expected_members = []
        self.assertEqual(extract_members(payload), expected_members)

    def test_extract_members_with_invalid_keywords(self):
        payload = {"invalid": ["test_a.city", "test_a.country", "test_a.state"]}
        expected_members = []
        self.assertEqual(extract_members(payload), expected_members)


class TestExtractFiletrMembers(unittest.TestCase):
    def test_extract_filters_members_with_all_fields(self):
        payload = {
            "dimensions": ["test_a.city", "test_a.country", "test_a.state"],
            "measures": ["test_b.count"],
            "filters": [
                {"values": ["US"], "member": "test_a.country", "operator": "equals"}
            ],
            "segments": ["test_d.us_segment"],
            "timeDimensions": [
                {
                    "dimension": "test_c.time",
                    "dateRange": ["2021-01-01", "2021-12-31"],
                    "granularity": "month",
                }
            ],
        }
        expected_members = ["test_a.country", "test_d.us_segment"]
        self.assertEqual(
            sorted(extract_filters_members(payload)), sorted(expected_members)
        )

    def test_filters_complex_boolean_logic_members(self):
        payload = {
            "segments": [],
            "filters": [
                {
                    "or": [
                        {
                            "and": [
                                {
                                    "values": ["Corpus Christi"],
                                    "member": "test_a.city",
                                    "operator": "equals",
                                },
                                {
                                    "member": "test_b.age_bucket",
                                    "operator": "equals",
                                    "values": ["Senior adult"],
                                },
                            ]
                        },
                        {
                            "member": "test_c.city",
                            "operator": "equals",
                            "values": ["Sacramento"],
                        },
                    ]
                },
                {"or": [{"member": "test_d.city", "operator": "set"}]},
            ],
        }
        expected_members = [
            "test_a.city",
            "test_b.age_bucket",
            "test_c.city",
            "test_d.city",
        ]
        self.assertEqual(
            sorted(extract_filters_members(payload)), sorted(expected_members)
        )

    def test_extract_filters_members_with_dimensions_only(self):
        payload = {"dimensions": ["test_a.city", "test_a.country", "test_a.state"]}
        expected_members = []
        self.assertEqual(
            sorted(extract_filters_members(payload)), sorted(expected_members)
        )

    def test_extract_filters_members_with_measures_only(self):
        payload = {"measures": ["test_b.count"]}
        expected_members = []
        self.assertEqual(
            sorted(extract_filters_members(payload)), sorted(expected_members)
        )

    def test_extract_filters_members_with_filters_only(self):
        payload = {
            "filters": [
                {"values": ["US"], "member": "test_a.country", "operator": "equals"}
            ]
        }
        expected_members = ["test_a.country"]
        self.assertEqual(
            sorted(extract_filters_members(payload)), sorted(expected_members)
        )

    def test_extract_filters_members_with_segments_only(self):
        payload = {"segments": ["test_a.us_segment"]}
        expected_members = ["test_a.us_segment"]
        self.assertEqual(
            sorted(extract_filters_members(payload)), sorted(expected_members)
        )

    def test_extract_filters_members_with_timeDimensions_only(self):
        payload = {
            "timeDimensions": [
                {
                    "dimension": "test_c.time",
                    "dateRange": ["2021-01-01", "2021-12-31"],
                    "granularity": "month",
                }
            ]
        }
        expected_members = []
        self.assertEqual(
            sorted(extract_filters_members(payload)), sorted(expected_members)
        )

    def test_extract_filters_members_with_empty_payload(self):
        payload = {}
        expected_members = []
        self.assertEqual(extract_filters_members(payload), expected_members)

    def test_extract_filters_members_with_invalid_keywords(self):
        payload = {"invalid": ["test_a.city", "test_a.country", "test_a.state"]}
        expected_members = []
        self.assertEqual(extract_filters_members(payload), expected_members)

    def test_pushdown_filters(self):
        payload = {
            "timezone": "UTC",
            "timeDimensions": [],
            "filters": [],
            "measures": [
                {
                    "name": "count_case_when_",
                    "expression": [
                        "internet_sales",
                        "return `COUNT(CASE WHEN (${internet_sales.salesterritorykey} = 1) THEN 1 END)`",
                    ],
                    "definition": '{"cubeName":"internet_sales","alias":"count_case_when_","expr":{"type":"SqlFunction","cubeParams":["internet_sales"],"sql":"COUNT(CASE WHEN (${internet_sales.salesterritorykey} = 1) THEN 1 END)"},"groupingSet":null}',
                    "cubeName": "internet_sales",
                    "groupingSet": None,
                    "expressionName": "count_case_when_",
                }
            ],
            "order": [],
            "limit": None,
            "segments": [
                {
                    "expression": [
                        "internet_sales",
                        "return `CASE WHEN ((${internet_sales.salesterritorykey} = 1) OR (${internet_sales.salesterritorykey} = 9)) THEN TRUE END`",
                    ],
                    "groupingSet": None,
                    "definition": '{"cubeName":"internet_sales","alias":"case_when_s_sale","expr":{"type":"SqlFunction","cubeParams":["internet_sales"],"sql":"CASE WHEN ((${internet_sales.salesterritorykey} = 1) OR (${internet_sales.salesterritorykey} = 9)) THEN TRUE END"},"groupingSet":null}',
                    "cubeName": "internet_sales",
                    "name": "case_when_s_sale",
                    "expressionName": "case_when_s_sale",
                }
            ],
            "dimensions": [
                {
                    "cubeName": "internet_sales",
                    "expressionName": "productkey",
                    "groupingSet": None,
                    "name": "productkey",
                    "definition": '{"cubeName":"internet_sales","alias":"productkey","expr":{"type":"SqlFunction","cubeParams":["internet_sales"],"sql":"${internet_sales.productkey}"},"groupingSet":null}',
                    "expression": [
                        "internet_sales",
                        "return `${internet_sales.productkey}`",
                    ],
                }
            ],
            "subqueryJoins": [],
        }
        expected_members = ["internet_sales.salesterritorykey"]
        self.assertEqual(
            sorted(extract_filters_members(payload)), sorted(expected_members)
        )

        payload = {
            "timezone": "UTC",
            "subqueryJoins": [],
            "limit": 50000,
            "order": [],
            "dimensions": [
                {
                    "definition": '{"cubeName":"internet_sales","alias":"productkey","expr":{"type":"SqlFunction","cubeParams":["internet_sales"],"sql":"${internet_sales.productkey}"},"groupingSet":null}',
                    "expression": [
                        "internet_sales",
                        "return `${internet_sales.productkey}`",
                    ],
                    "groupingSet": None,
                    "cubeName": "internet_sales",
                    "expressionName": "productkey",
                    "name": "productkey",
                }
            ],
            "timeDimensions": [],
            "filters": [],
            "segments": [
                {
                    "groupingSet": None,
                    "name": "case_when_s_sale",
                    "expression": [
                        "internet_sales",
                        "return `CASE WHEN ((${internet_sales.salesterritorykey} = 1) OR (${internet_sales.salesterritorykey} = 9)) THEN TRUE END`",
                    ],
                    "expressionName": "case_when_s_sale",
                    "definition": '{"cubeName":"internet_sales","alias":"case_when_s_sale","expr":{"type":"SqlFunction","cubeParams":["internet_sales"],"sql":"CASE WHEN ((${internet_sales.salesterritorykey} = 1) OR (${internet_sales.salesterritorykey} = 9)) THEN TRUE END"},"groupingSet":null}',
                    "cubeName": "internet_sales",
                }
            ],
            "measures": [
                {
                    "expression": [
                        "internet_sales",
                        "return `COUNT(CASE WHEN (${internet_sales.salesterritorykey} = 1) THEN 1 END)`",
                    ],
                    "expressionName": "count_case_when_",
                    "groupingSet": None,
                    "name": "count_case_when_",
                    "cubeName": "internet_sales",
                    "definition": '{"cubeName":"internet_sales","alias":"count_case_when_","expr":{"type":"SqlFunction","cubeParams":["internet_sales"],"sql":"COUNT(CASE WHEN (${internet_sales.salesterritorykey} = 1) THEN 1 END)"},"groupingSet":null}',
                }
            ],
        }
        expected_members = ["internet_sales.salesterritorykey"]
        self.assertEqual(
            sorted(extract_filters_members(payload)), sorted(expected_members)
        )


if __name__ == "__main__":
    unittest.main()
