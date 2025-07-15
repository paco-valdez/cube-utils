# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview
Cube Utils is a Python library for parsing and extracting information from Cube.js query payloads. It provides utilities to extract cubes, members, filters, and URL parameters from query data structures.

## Development Commands

### Running Tests
```bash
python -m unittest discover tests
```

### Building and Distribution
This project uses PDM for dependency management:
```bash
pdm build
```

## Code Architecture

### Core Modules

**cube_utils/query_parser.py** - Main parsing functionality:
- `extract_cubes()` - Extracts unique cube names from query payloads
- `extract_members()` - Extracts all members (dimensions, measures, filters, segments, timeDimensions)
- `extract_filters_members()` - Extracts only members from filters and segments
- `extract_filters_members_with_values()` - Extracts filter members with their values as tuples
- `extract_members_from_expression()` - Parses SQL expressions to find ${cube.member} patterns
- `extract_members_from_filter()` - Handles nested boolean logic (AND/OR) in filters

**cube_utils/url_parser.py** - URL parameter extraction:
- `extract_url_params()` - Extracts and URL-decodes query parameters from URLs

### Key Data Structures

**Query Payloads** contain these keys:
- `dimensions` - Array of dimension members like "cube.dimension"
- `measures` - Array of measure members like "cube.measure"  
- `filters` - Array of filter objects with member, operator, values
- `segments` - Array of segment identifiers
- `timeDimensions` - Array of time dimension objects with dimension, dateRange, granularity

**Pushdown Members** are dictionaries with:
- `cubeName` - The cube name
- `expressionName` - The expression name
- `expression` - Array containing SQL expressions
- `definition` - JSON string with SQL function definition

### Boolean Logic Handling
Filters support nested boolean logic with `and` and `or` operators. The parser recursively extracts members from these nested structures.

### SQL Expression Parsing
The library can parse SQL expressions to extract member references in the format `${cube.member}` and extract member-value pairs from equality conditions.

## Testing Structure
- `tests/test_query_parser.py` - Comprehensive tests for all query parsing functions
- `tests/test_url_parser.py` - Tests for URL parameter extraction
- Tests cover edge cases including empty payloads, complex boolean logic, and pushdown queries