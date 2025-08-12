# Cube Utils

Cube Utils is a Python library for parsing and extracting information from [Cube](https://cube.dev) query payloads. It provides utilities to extract cubes, members, filters, and URL parameters from query data structures. Additionally, it includes the complete Cube package functionality for configuration management and template context handling, making it compatible with both open-source Cube deployments and Cube Cloud.

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

## Cube Package API

Cube Utils now includes the complete Cube package functionality, providing configuration management and template context handling capabilities.

### Configuration Management

The `config` object allows you to set configuration options for your Cube deployment. You can import it directly from `cube_utils`:

```python
from cube_utils import config
```

#### Direct Property Assignment

Set configuration properties directly:

```python
config.base_path = '/cube-api'
config.api_secret = 'your-secret-key'
config.telemetry = False
```

#### Function-based Configuration

Assign functions to configuration properties:

```python
config.context_to_app_id = lambda ctx: ctx['securityContext']['tenant_id']

# Or using a regular function
def get_app_id(context):
    return context['securityContext']['tenant_id']

config.context_to_app_id = get_app_id
```

#### Decorator-style Configuration

Use the `@config` decorator to configure properties:

```python
# Using function name as property name
@config
def context_to_app_id(ctx):
    return ctx['securityContext']['tenant_id']

# Using custom property name
@config('context_to_app_id')
def app_id(ctx):
    return ctx['securityContext']['tenant_id']
```

#### Available Configuration Options

The configuration object supports numerous options including:

- **API Settings**: `base_path`, `api_secret`, `telemetry`
- **Database**: `db_type`, `driver_factory`
- **Authentication**: `check_auth`, `check_sql_auth`, `context_to_app_id`
- **Caching**: `sql_cache`, `compiler_cache_size`
- **WebSockets**: `web_sockets`, `web_sockets_base_path`
- **Scheduled Refresh**: `scheduled_refresh_timer`, `scheduled_refresh_concurrency`
- **Advanced**: `query_rewrite`, `pre_aggregations_schema`, `orchestrator_options`

### Template Context Management

The `TemplateContext` class provides template variable, function, and filter management for Jinja templates:

```python
from cube_utils import TemplateContext

template = TemplateContext()
```

#### Variable Registration

Register variables that can be used in Jinja templates:

```python
template.add_variable('my_var', 123)
template.add_variable('api_version', '2.0')
template.add_variable('feature_flags', {'new_ui': True})
```

#### Function Registration

Register functions that can be called from templates:

```python
# Method 1: Direct registration
def get_user_data():
    return {'name': 'John', 'role': 'admin'}

template.add_function('get_user_data', get_user_data)

# Method 2: Using decorator
@template.function
def get_current_time():
    from datetime import datetime
    return datetime.now().isoformat()

# Method 3: Using decorator with custom name
@template.function('get_status')
def check_system_status():
    return 'active'
```

#### Filter Registration

Register custom Jinja filters:

```python
# Method 1: Direct registration
def wrap_in_quotes(value):
    return f'"{value}"'

template.add_filter('quote', wrap_in_quotes)

# Method 2: Using decorator
@template.filter
def uppercase(value):
    return str(value).upper()

# Method 3: Using decorator with custom name
@template.filter('currency')
def format_currency(value):
    return f'${value:.2f}'
```

### Context Functions

Mark functions as context functions using the `context_func` decorator:

```python
from cube_utils import context_func

@context_func
def my_context_function():
    return 'This is a context function'
```

### Safe Strings

Create safe strings for template rendering:

```python
from cube_utils import SafeString

safe_html = SafeString('<b>Bold text</b>')
print(safe_html.is_safe)  # True
```

### Backward Compatibility

The `settings` object is provided as an alias to `config` for backward compatibility:

```python
from cube_utils import settings

settings.base_path = '/api'  # Same as config.base_path = '/api'
```

### Additional Utilities

#### File Repository

Access file repository functionality for reading configuration files:

```python
from cube_utils import file_repository

# Read all supported files from a directory
files = file_repository('/path/to/cube/schema')
# Returns list of dictionaries with 'fileName' and 'content' keys
# Supports: .js, .yml, .yaml, .jinja, .py files
```

#### Exception Handling

Handle configuration and template-related errors:

```python
from cube_utils import ConfigurationException, TemplateException

try:
    @config('unknown_property')
    def invalid_config():
        pass
except ConfigurationException as e:
    print(f"Configuration error: {e}")

try:
    template.add_function('test', 'not a function')
except TemplateException as e:
    print(f"Template error: {e}")
```

## API Reference

### Query Parsing Functions

| Function | Description | Module |
|----------|-------------|--------|
| `extract_cubes` | Extract unique cube names from query payload | `cube_utils.query_parser` |
| `extract_members` | Extract all members from query payload | `cube_utils.query_parser` |
| `extract_filters_members` | Extract members from filters and segments only | `cube_utils.query_parser` |
| `extract_filters_members_with_values` | Extract filter members with their values | `cube_utils.query_parser` |
| `extract_members_from_expression` | Parse SQL expressions for member references | `cube_utils.query_parser` |
| `extract_url_params` | Extract URL query parameters | `cube_utils.url_parser` |

### Cube Package Classes

| Class/Object | Description | Import |
|--------------|-------------|---------|
| `config` | Global configuration object | `from cube_utils import config` |
| `TemplateContext` | Template management class | `from cube_utils import TemplateContext` |
| `context_func` | Context function decorator | `from cube_utils import context_func` |
| `SafeString` | Safe string class for templates | `from cube_utils import SafeString` |
| `settings` | Alias for config (backward compatibility) | `from cube_utils import settings` |

## Running Tests
To run the tests, use the following command:
    
```sh
python -m unittest discover tests
```

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
