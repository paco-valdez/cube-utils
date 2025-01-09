

# Function to extract cube names, updated for timeDimensions
def extract_cubes(payload):
    cubes = set()  # Use a set to ensure uniqueness
    
    # Extract cubes from dimensions
    if "dimensions" in payload:
        for dimension in payload["dimensions"]:
            cube = dimension.split('.')[0]
            cubes.add(cube)
    
    # Extract cubes from measures
    if "measures" in payload:
        for measure in payload["measures"]:
            cube = measure.split('.')[0]
            cubes.add(cube)
    
    # Extract cubes from filters
    if "filters" in payload:
        for filter_item in payload["filters"]:
            if "member" in filter_item:
                cube = filter_item["member"].split('.')[0]
                cubes.add(cube)
    
    # Extract cubes from timeDimensions
    if "timeDimensions" in payload:
        for time_dimension in payload["timeDimensions"]:
            if "dimension" in time_dimension:
                cube = time_dimension["dimension"].split('.')[0]
                cubes.add(cube)
    
    return list(cubes)


if __name__ == '__main__':
    # Payload examples
    query_payload_1 = {
        "dimensions": [
            "test_a.city",
            "test_a.country",
            "test_a.state"
        ],
        "measures": [
            "test_b.count"
        ],
        "filters": [
            {
                "values": [
                    "US"
                ],
                "member": "test_a.country",
                "operator": "equals"
            }
        ]
    }

    query_payload_2 = {
        "measures": ["stories.count"],
        "dimensions": ["stories.category"],
        "filters": [
            {
                "member": "stories.isDraft",
                "operator": "equals",
                "values": ["No"]
            }
        ],
        "timeDimensions": [
            {
                "dimension": "stories.time",
                "dateRange": ["2015-01-01", "2015-12-31"],
                "granularity": "month"
            }
        ],
        "limit": 100,
        "offset": 50,
        "order": {
            "stories.time": "asc",
            "stories.count": "desc"
        },
        "timezone": "America/Los_Angeles"
    }

    # Test the function with both payloads
    cubes_used_1 = extract_cubes(query_payload_1)
    cubes_used_2 = extract_cubes(query_payload_2)

    print("Cubes in Query 1:", cubes_used_1)
    assert sorted(cubes_used_1) == ['test_a', 'test_b']
    print("Cubes in Query 2:", cubes_used_2)
    assert sorted(cubes_used_2) == ['stories']
