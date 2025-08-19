# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview
Cube Utils is a library for parsing and extracting information from Cube.js query payloads. It provides utilities to extract cubes, members, filters, and URL parameters from query data structures.

This repository contains two implementations:
- **Python package** (`cube_utils/`) - Original Python implementation
- **JavaScript package** (`cube-utils-js/`) - JavaScript port with identical functionality

## Development Commands

### Running Tests

**Python:**
```bash
python -m unittest discover tests
```

**JavaScript:**
```bash
cd cube-utils-js
npm test
```

### Building and Distribution

**Python** - Uses PDM for dependency management:
```bash
pdm build
```

**JavaScript:**
```bash
cd cube-utils-js
npm publish
```

## Code Architecture

### Core Modules

Both Python and JavaScript implementations provide identical functionality:

**Query Parser** (`cube_utils/query_parser.py` & `cube-utils-js/src/query-parser.js`):
- `extract_cubes()` / `extractCubes()` - Extracts unique cube names from query payloads
- `extract_members()` / `extractMembers()` - Extracts all members (dimensions, measures, filters, segments, timeDimensions)
- `extract_filters_members()` / `extractFiltersMembers()` - Extracts only members from filters and segments
- `extract_filters_members_with_values()` / `extractFiltersMembersWithValues()` - Extracts filter members with their values as tuples
- `extract_members_from_expression()` / `extractMembersFromExpression()` - Parses SQL expressions to find ${cube.member} patterns
- `extract_members_from_filter()` / `extractMembersFromFilter()` - Handles nested boolean logic (AND/OR) in filters

**URL Parser** (`cube_utils/url_parser.py` & `cube-utils-js/src/url-parser.js`):
- `extract_url_params()` / `extractUrlParams()` - Extracts and URL-decodes query parameters from URLs

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

**Python Tests:**
- `tests/test_query_parser.py` - Comprehensive tests for all query parsing functions
- `tests/test_url_parser.py` - Tests for URL parameter extraction
- `tests/test_cube_package.py` - Tests for Cube.js framework integration (Python only)

**JavaScript Tests:**
- `cube-utils-js/test/query-parser.test.js` - Equivalent tests for query parsing functions
- `cube-utils-js/test/url-parser.test.js` - Equivalent tests for URL parameter extraction

Tests cover edge cases including empty payloads, complex boolean logic, and pushdown queries. Both implementations pass identical test suites to ensure functional equivalence.

## GitHub Actions

The repository includes automated workflows:
- **Tests workflow** - Runs both Python and JavaScript tests on every push/PR
- **Publish workflow** - Publishes to both PyPI (Python) and npm (JavaScript) on GitHub releases