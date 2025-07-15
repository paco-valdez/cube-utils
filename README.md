# Cube Utils

Cube Utils is a Python library for parsing and extracting information from query payloads.

## Installation

You can install Cube Utils using pip:

```sh
pip install cube-utils
```

If you are using Cube, just add `cube-utils` to your requirements.txt file. e.g.

```sh
cube-utils
```

## Usage
Here is an example of how to use the `extract_cubes` and `extract_members` functions from the `cube_utils.query_parser` module:

```python
from cube_utils.query_parser import extract_cubes, extract_members

# Example payload
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

# Extract cubes
cubes = extract_cubes(payload)
print(cubes)  # Output: ['test_a', 'test_b', 'test_c', 'test_d']

# Extract members
members = extract_members(payload)
print(members)  # Output: ['test_a.city', 'test_a.country', 'test_a.state', 'test_b.count', 'test_a.country', 'test_d.us_segment', 'test_c.time']

# Extract members from specific query keys only
dimensions_and_measures = extract_members(payload, query_keys=["dimensions", "measures"])
print(dimensions_and_measures)  # Output: ['test_a.city', 'test_a.country', 'test_a.state', 'test_b.count']
```

## Filter Members and Values
You can extract filter members along with their values using the `extract_filters_members_with_values` function:

```python
from cube_utils.query_parser import extract_filters_members_with_values

# Example payload with complex filters
payload = {
    "filters": [
        {"values": ["US", "CA"], "member": "test_a.country", "operator": "equals"},
        {
            "or": [
                {"values": ["New York"], "member": "test_a.city", "operator": "equals"},
                {"member": "test_a.state", "operator": "set"}
            ]
        }
    ],
    "segments": ["test_b.premium_users"]
}

# Extract filter members with their values
filter_members = extract_filters_members_with_values(payload)
print(filter_members)  
# Output: [('test_a.country', ['CA', 'US']), ('test_a.city', ['New York']), ('test_a.state', None), ('test_b.premium_users', None)]
```

## URL Parameter Extraction
You can extract query parameters from a URL using the `extract_url_params` function from the `cube_utils.url_parser` module:

```python
from cube_utils.url_parser import extract_url_params

url = "https://example.com/?foo=bar&baz=qux"
params = extract_url_params(url)
print(params)  # Output: {'foo': 'bar', 'baz': 'qux'}
```

## Running Tests
To run the tests, use the following command:
    
```sh
python -m unittest discover tests
```

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
