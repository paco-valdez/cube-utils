import unittest
from cube_utils.url_parser import extract_url_params


class TestExtractUrlParams(unittest.TestCase):
    def test_single_param(self):
        url = "https://example.com/?foo=bar"
        expected = {"foo": "bar"}
        self.assertEqual(extract_url_params(url), expected)

    def test_multiple_params(self):
        url = "https://example.com/?foo=bar&baz=qux"
        expected = {"foo": "bar", "baz": "qux"}
        self.assertEqual(extract_url_params(url), expected)

    def test_repeated_keys(self):
        url = "https://example.com/?foo=bar&foo=baz"
        expected = {"foo": ["bar", "baz"]}
        self.assertEqual(extract_url_params(url), expected)

    def test_url_encoded_value(self):
        url = "https://example.com/?foo=hello%20world"
        expected = {"foo": "hello world"}
        self.assertEqual(extract_url_params(url), expected)

    def test_empty_query(self):
        url = "https://example.com/"
        expected = {}
        self.assertEqual(extract_url_params(url), expected)

    def test_param_with_empty_value(self):
        url = "https://example.com/?foo="
        expected = {}
        self.assertEqual(extract_url_params(url), expected)

    def test_long_encoded_query_param(self):
        url = "/cubejs-api/v1/dry-run?query=%7B%22measures%22%3A%5B%22sales.net_sales_amount%22%5D%2C%22dimensions%22%3A%5B%22sales.currency_code%22%2C%22sales.region%22%2C%22sales.currency_type_code%22%5D%2C%22timeDimensions%22%3A%5B%7B%22dimension%22%3A%22sales.date_financial_ds%22%2C%22dateRange%22%3A%22last+month%22%2C%22granularity%22%3A%22month%22%7D%5D%2C%22filters%22%3A%5B%7B%22values%22%3A%5B%22GBP%22%2C%22USD%22%5D%2C%22member%22%3A%22sales.currency_code%22%2C%22operator%22%3A%22equals%22%7D%5D%7D"
        expected_query = '{"measures":["sales.net_sales_amount"],"dimensions":["sales.currency_code","sales.region","sales.currency_type_code"],"timeDimensions":[{"dimension":"sales.date_financial_ds","dateRange":"last month","granularity":"month"}],"filters":[{"values":["GBP","USD"],"member":"sales.currency_code","operator":"equals"}]}'
        result = extract_url_params(url)
        self.assertIn("query", result)
        self.assertEqual(result["query"], expected_query)

    def test_multiple_long_encoded_urls(self):
        urls = [
            "/cubejs-api/v1/sql?query=%7B%22measures%22%3A%5B%22sales.net_sales_amount%22%5D%2C%22dimensions%22%3A%5B%22sales.currency_code%22%2C%22sales.region%22%2C%22sales.currency_type_code%22%5D%2C%22timeDimensions%22%3A%5B%7B%22dimension%22%3A%22sales.date_financial_ds%22%2C%22dateRange%22%3A%22last+month%22%2C%22granularity%22%3A%22month%22%7D%5D%2C%22filters%22%3A%5B%7B%22values%22%3A%5B%22GBP%22%2C%22USD%22%5D%2C%22member%22%3A%22sales.currency_code%22%2C%22operator%22%3A%22equals%22%7D%5D%7D",
            "/cubejs-api/v1/load?query=%7B%22measures%22%3A%5B%22sales.net_sales_amount%22%5D%2C%22dimensions%22%3A%5B%22sales.currency_code%22%2C%22sales.region%22%2C%22sales.currency_type_code%22%5D%2C%22timeDimensions%22%3A%5B%7B%22dimension%22%3A%22sales.date_financial_ds%22%2C%22dateRange%22%3A%22last+month%22%2C%22granularity%22%3A%22month%22%7D%5D%2C%22filters%22%3A%5B%7B%22values%22%3A%5B%22GBP%22%2C%22USD%22%5D%2C%22member%22%3A%22sales.currency_code%22%2C%22operator%22%3A%22equals%22%7D%5D%7D&queryType=multi",
        ]
        expected_query = '{"measures":["sales.net_sales_amount"],"dimensions":["sales.currency_code","sales.region","sales.currency_type_code"],"timeDimensions":[{"dimension":"sales.date_financial_ds","dateRange":"last month","granularity":"month"}],"filters":[{"values":["GBP","USD"],"member":"sales.currency_code","operator":"equals"}]}'
        for url in urls:
            result = extract_url_params(url)
            self.assertIn("query", result)
            self.assertEqual(result["query"], expected_query)


if __name__ == "__main__":
    unittest.main()
