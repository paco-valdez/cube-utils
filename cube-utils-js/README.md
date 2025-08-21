# Cube Utils JS

JavaScript utilities for parsing and extracting information from Cube.js query payloads.

This is a JavaScript port of the Python `cube-utils` library, providing the same core parsing functionality for working with Cube.js query data structures.

## Installation

```bash
npm install cube-utils-js
```

## Features

- **Query parsing** - Extract cubes, members, filters from Cube.js query data structures
- **URL parameter extraction** - Parse and decode query parameters from URLs
- **SQL expression parsing** - Find member references in `${cube.member}` format
- **Boolean logic handling** - Process nested AND/OR filter conditions
- **Dual module support** - Works with both ES6 imports and CommonJS requires

## Usage

The package supports both ES6 imports and CommonJS requires:

### ES6 Import (Recommended)

```javascript
import { 
  extractCubes,
  extractMembers,
  extractFiltersMembers,
  extractFiltersMembersWithValues
} from 'cube-utils-js';
```

### CommonJS Require

```javascript
const { 
  extractCubes,
  extractMembers,
  extractFiltersMembers,
  extractFiltersMembersWithValues
} = require('cube-utils-js');
```

### Query Parser

```javascript
// Works with either import style above

const payload = {
  dimensions: ['sales.city', 'sales.country'],
  measures: ['sales.count'],
  filters: [
    { values: ['US'], member: 'sales.country', operator: 'equals' }
  ],
  segments: ['sales.active_users'],
  timeDimensions: [
    {
      dimension: 'sales.date',
      dateRange: ['2021-01-01', '2021-12-31'],
      granularity: 'month'
    }
  ]
};

// Extract unique cube names
const cubes = extractCubes(payload);
// Returns: ['sales']

// Extract all members
const members = extractMembers(payload);
// Returns: ['sales.city', 'sales.country', 'sales.count', 'sales.date', 'sales.active_users']

// Extract only filter and segment members
const filterMembers = extractFiltersMembers(payload);
// Returns: ['sales.country', 'sales.active_users']

// Extract filter members with their values
const membersWithValues = extractFiltersMembersWithValues(payload);
// Returns: [['sales.country', ['US']], ['sales.active_users', null]]
```

### URL Parser

```javascript
// ES6 import
import { extractUrlParams } from 'cube-utils-js';

// Or CommonJS require  
const { extractUrlParams } = require('cube-utils-js');

const url = '/cubejs-api/v1/load?query=%7B%22measures%22%3A%5B%22sales.count%22%5D%7D&foo=bar';
const params = extractUrlParams(url);
// Returns: { query: '{"measures":["sales.count"]}', foo: 'bar' }
```

## API Reference

### Query Parser Functions

#### `extractCubes(payload)`
Extracts unique cube names from a query payload.
- **Parameters**: `payload` (Object) - The Cube.js query payload
- **Returns**: Array of unique cube names

#### `extractMembers(payload, queryKeys?)`
Extracts unique members from a query payload.
- **Parameters**: 
  - `payload` (Object) - The Cube.js query payload
  - `queryKeys` (Array, optional) - Keys to extract from (defaults to all query types)
- **Returns**: Array of unique member names

#### `extractFiltersMembers(payload)`
Extracts members from filters and segments only.
- **Parameters**: `payload` (Object) - The Cube.js query payload
- **Returns**: Array of filter/segment member names

#### `extractFiltersMembersWithValues(payload)`
Extracts filter members along with their values.
- **Parameters**: `payload` (Object) - The Cube.js query payload
- **Returns**: Array of [member, values] tuples

### URL Parser Functions

#### `extractUrlParams(url)`
Extracts and URL-decodes query parameters from a URL.
- **Parameters**: `url` (string) - The URL to parse
- **Returns**: Object with parameter key-value pairs

## Testing

```bash
npm test
```

## License

MIT
