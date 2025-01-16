from typing import List, Dict, Any


# Function to extract cube names, updated for timeDimensions
def extract_cubes(payload: Dict[str, Any]) -> List[str]:
    cubes = set()  # Use a set to ensure uniqueness

    # Extract cubes from dimensions
    if "dimensions" in payload:
        for dimension in payload["dimensions"]:
            cube = dimension.split(".")[0]
            cubes.add(cube)

    # Extract cubes from measures
    if "measures" in payload:
        for measure in payload["measures"]:
            cube = measure.split(".")[0]
            cubes.add(cube)

    # Extract cubes from filters
    if "filters" in payload:
        for filter_item in payload["filters"]:
            cubes.update(extract_members_from_filter(filter_item))

    # Extract cubes from segments
    if "segments" in payload:
        for segment in payload["segments"]:
            cube = segment.split(".")[0]
            cubes.add(cube)

    # Extract cubes from timeDimensions
    if "timeDimensions" in payload:
        for time_dimension in payload["timeDimensions"]:
            if "dimension" in time_dimension:
                cube = time_dimension["dimension"].split(".")[0]
                cubes.add(cube)

    return list(cubes)


# Extracts filters and handles boolean logic recursively
def extract_members_from_filter(filter_item):
    members = set()

    # Handle direct member filters
    if "member" in filter_item:
        cube = filter_item["member"].split(".")[0]
        members.add(cube)

    # Handle AND conditions
    if "and" in filter_item:
        for condition in filter_item["and"]:
            members.update(extract_members_from_filter(condition))

    # Handle OR conditions
    if "or" in filter_item:
        for condition in filter_item["or"]:
            members.update(extract_members_from_filter(condition))

    return members
