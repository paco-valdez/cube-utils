from typing import List, Dict, Any
from typing import Sequence
import re


def is_pushdown_member(member: Any) -> bool:
    """
    Check if a member is a pushdown member.
    A pushdown member is a dictionary with 'cubeName' and 'expressionName' keys.
    :param member: The member to check.
    :return: True if the member is a pushdown member, False otherwise.
    """
    return (
        isinstance(member, dict) and "cubeName" in member and "expressionName" in member
    )


# Function to extract cubes from a query payload
def extract_cubes(payload: Dict[str, Any]) -> List[str]:
    """
    Extracts unique cubes from the given query payload.
    :param payload: The query payload containing dimensions, measures, filters, segments, and time dimensions.
    :return: A list of unique cube names.
    """
    cubes = set()
    members = extract_members(payload)
    for member in members:
        cube = member.split(".")[0]
        cubes.add(cube)
    return list(cubes)


# Function to extract cube members
def extract_members(
    payload: Dict[str, Any],
    query_keys: Sequence[str] = (
        "dimensions",
        "measures",
        "filters",
        "segments",
        "timeDimensions",
    ),
) -> List[str]:
    """
    Extracts unique members from the given query payload.
    :param payload: The query payload containing dimensions, measures, filters, segments, and time dimensions.
    :return: A list of unique members in the format 'cubeName.expressionName'.
    """
    members = set()  # Use a set to ensure uniqueness

    for key in query_keys:
        if key in payload:
            for item in payload[key]:
                if is_pushdown_member(item):
                    # Try to extract from expression or definition
                    expr_members = set()
                    if "expression" in item and isinstance(item["expression"], list):
                        for expr in item["expression"]:
                            if isinstance(expr, str):
                                member = extract_members_from_expression(expr)
                                if member:
                                    expr_members.update(member)
                    if not expr_members and "definition" in item and isinstance(item["definition"], str):
                        member = extract_members_from_expression(item["definition"])
                        if member:
                            expr_members.update(member)
                    if expr_members:
                        members.update(expr_members)
                    else:
                        members.add(f"{item['cubeName']}.{item['expressionName']}")
                elif key == "filters":
                    members.update(extract_members_from_filter(item))
                elif (
                    key == "timeDimensions"
                    and isinstance(item, dict)
                    and "dimension" in item
                ):
                    members.add(item["dimension"])
                else:
                    members.add(item)

    return list(members)


def extract_members_from_expression(expr: str) -> List[str]:
    """
    Extracts all members in the format ${cube.member} from a string expression.
    """
    return re.findall(r"\${([a-zA-Z0-9_]+\.[a-zA-Z0-9_]+)}", expr)


# Extracts filters and handles boolean logic recursively
def extract_members_from_filter(filter_item: Dict[str, Any]) -> set:
    """
    Extracts members from a filter item, handling boolean logic (AND/OR) recursively.
    :param filter_item: The filter item to extract members from.
    :return: A set of unique members extracted from the filter item.
    """
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


# Function to extract filters only from a query payload
def extract_filters_members(payload: Dict[str, Any]) -> List[str]:
    """
    Extracts the members from filters from the given query payload.
    :param payload: The query payload containing dimensions, measures, filters, segments, and time dimensions.
    :return: A list of members(str).
    """
    query_keys = [
        "filters",
        "segments",
    ]

    return extract_members(payload, query_keys=query_keys)
