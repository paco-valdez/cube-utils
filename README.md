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
print(cubes)  # Output: ['test_a', 'test_b', 'test_c']

# Extract members
members = extract_members(payload)
print(members)  # Output: ['test_a.city', 'test_a.country', 'test_a.state', 'test_b.count', 'test_c.time']
```

## Running Tests
To run the tests, use the following command:
    
```sh
python -m unittest discover tests
```

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
