from typing import List, Dict, Any


# Function to extract cubes from a query payload
def extract_cubes(payload: Dict[str, Any]) -> List[str]:
    cubes = set()
    members = extract_members(payload)
    for member in members:
        cube = member.split(".")[0]
        cubes.add(cube)
    return list(cubes)


# Function to extract cube members
def extract_members(payload: Dict[str, Any]) -> List[str]:
    members = set()  # Use a set to ensure uniqueness

    # Extract cubes from dimensions
    if "dimensions" in payload:
        for dimension in payload["dimensions"]:
            if type(dimension) is dict and 'cubeName' in dimension and 'expressionName' in dimension:
                members.add(f"{dimension['cubeName']}.{dimension['expressionName']}")
                continue

            members.add(dimension)

    # Extract cubes from measures
    if "measures" in payload:
        for measure in payload["measures"]:
            if type(measure) is dict and 'cubeName' in measure and 'expressionName' in measure:
                members.add(f"{measure['cubeName']}.{measure['expressionName']}")
                continue

            members.add(measure)

    # Extract cubes from filters
    if "filters" in payload:
        for filter_item in payload["filters"]:
            if type(filter_item) is dict and 'cubeName' in filter_item and 'expressionName' in filter_item:
                members.add(f"{filter_item['cubeName']}.{filter_item['expressionName']}")
                continue

            members.update(extract_members_from_filter(filter_item))

    # Extract cubes from segments
    if "segments" in payload:
        for segment in payload["segments"]:
            if type(segment) is dict and 'cubeName' in segment and 'expressionName' in segment:
                members.add(f"{segment['cubeName']}.{segment['expressionName']}")
                continue

            members.add(segment)

    # Extract cubes from timeDimensions
    if "timeDimensions" in payload:
        for time_dimension in payload["timeDimensions"]:
            if "dimension" in time_dimension:
                members.add(time_dimension["dimension"])
            elif 'cubeName' in time_dimension and 'expressionName' in time_dimension:
                members.add(f"{time_dimension['cubeName']}.{time_dimension['expressionName']}")

    return list(members)


# Extracts filters and handles boolean logic recursively
def extract_members_from_filter(filter_item):
    members = set()

    # Handle direct member filters
    if "member" in filter_item:
        members.add(filter_item["member"])

    # Handle AND conditions
    if "and" in filter_item:
        for condition in filter_item["and"]:
            members.update(extract_members_from_filter(condition))

    # Handle OR conditions
    if "or" in filter_item:
        for condition in filter_item["or"]:
            members.update(extract_members_from_filter(condition))

    return members
