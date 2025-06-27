from collections import defaultdict
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
                    if (
                        not expr_members
                        and "definition" in item
                        and isinstance(item["definition"], str)
                    ):
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


def extract_member_value_from_sql(sql: str):
    # Matches patterns like ${cube.member} = value or (${cube.member} = value)
    pattern = re.compile(r"\${([a-zA-Z0-9_]+\.[a-zA-Z0-9_]+)}\s*=\s*([^)\s]+)")
    return pattern.findall(sql)


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


def extract_filters_members_with_values(payload: Dict[str, Any]) -> List[tuple]:
    """
    Extracts (member, value) tuples from filters and segments in the given query payload.
    For filters, value is the 'values' field if present, otherwise None.
    For segments, value is always None unless a value can be extracted from a pushdown SQL expression.
    Handles nested boolean logic in filters.
    Ensures unique members and unique values per member.
    """
    result = defaultdict(set)

    def extract_from_filter(filter_item):
        if "member" in filter_item:
            value = filter_item.get("values")
            if value is not None:
                if isinstance(value, list):
                    for v in value:
                        result[filter_item["member"]].add(v)
                else:
                    result[filter_item["member"]].add(value)
            else:
                result[filter_item["member"]]
        if "and" in filter_item:
            for cond in filter_item["and"]:
                extract_from_filter(cond)
        if "or" in filter_item:
            for cond in filter_item["or"]:
                extract_from_filter(cond)

    if "filters" in payload:
        for filter_item in payload["filters"]:
            extract_from_filter(filter_item)
    if "segments" in payload:
        for seg in payload["segments"]:
            if isinstance(seg, dict) and is_pushdown_member(seg):
                expr_members = defaultdict(set)
                sqls = []
                if "expression" in seg and isinstance(seg["expression"], list):
                    for expr in seg["expression"]:
                        if isinstance(expr, str):
                            sqls.append(expr)
                if "definition" in seg and isinstance(seg["definition"], str):
                    sqls.append(seg["definition"])
                found = False
                for sql in sqls:
                    for member, value in extract_member_value_from_sql(sql):
                        found = True
                        # Remove quotes from value if present
                        if value.startswith("`") and value.endswith("`"):
                            value = value[1:-1]
                        try:
                            value = int(value)
                        except Exception:
                            pass
                        expr_members[member].add(value)
                if found:
                    for m, vals in expr_members.items():
                        result[m].update(vals)
                else:
                    # fallback to just extracting members
                    for sql in sqls:
                        for member in extract_members_from_expression(sql):
                            result[member]
                if not sqls:
                    result[f"{seg['cubeName']}.{seg['expressionName']}"]
            elif isinstance(seg, dict):
                name = seg.get("name") or seg.get("expressionName")
                if name:
                    result[name]
            else:
                result[seg]
    # Convert sets to sorted lists or None if empty
    out = []
    for k, v in result.items():
        if v:
            out.append((k, sorted(v)))
        else:
            out.append((k, None))
    return out
