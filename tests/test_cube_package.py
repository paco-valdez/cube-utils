import unittest
import tempfile
import os
from cube_utils import (
    config,
    settings,
    TemplateContext,
    context_func,
    SafeString,
    file_repository,
    Configuration,
    ConfigurationException,
    TemplateException,
    RequestContext,
    AttrRef,
    TemplateFunctionRef,
    TemplateFilterRef,
)


class TestConfiguration(unittest.TestCase):
    def setUp(self):
        self.config = Configuration()

    def test_configuration_initialization(self):
        """Test Configuration class initializes with None values."""
        self.assertIsNone(self.config.base_path)
        self.assertIsNone(self.config.api_secret)
        self.assertIsNone(self.config.context_to_app_id)

    def test_direct_property_assignment(self):
        """Test direct property assignment like config.base_path = '/cube-api'."""
        self.config.base_path = '/cube-api'
        self.assertEqual(self.config.base_path, '/cube-api')
        
        self.config.api_secret = 'secret123'
        self.assertEqual(self.config.api_secret, 'secret123')

    def test_lambda_function_assignment(self):
        """Test lambda function assignment to configuration."""
        self.config.context_to_app_id = lambda ctx: ctx['securityContext']['tenant_id']
        self.assertTrue(callable(self.config.context_to_app_id))
        
        # Test the lambda function
        test_ctx = {'securityContext': {'tenant_id': 'tenant123'}}
        result = self.config.context_to_app_id(test_ctx)
        self.assertEqual(result, 'tenant123')

    def test_decorator_style_configuration_with_function_name(self):
        """Test decorator-style configuration using @config with function name."""
        @self.config
        def context_to_app_id(ctx):
            return ctx['securityContext']['tenant_id']
        
        self.assertTrue(callable(self.config.context_to_app_id))
        
        # Test the configured function
        test_ctx = {'securityContext': {'tenant_id': 'tenant456'}}
        result = self.config.context_to_app_id(test_ctx)
        self.assertEqual(result, 'tenant456')

    def test_decorator_style_configuration_with_string_attr(self):
        """Test decorator-style configuration using @config('property_name')."""
        @self.config('context_to_app_id')
        def app_id(ctx):
            return ctx['securityContext']['tenant_id']
        
        self.assertTrue(callable(self.config.context_to_app_id))
        
        # Test the configured function
        test_ctx = {'securityContext': {'tenant_id': 'tenant789'}}
        result = self.config.context_to_app_id(test_ctx)
        self.assertEqual(result, 'tenant789')

    def test_decorator_with_unknown_property_raises_exception(self):
        """Test that using @config with unknown property raises ConfigurationException."""
        with self.assertRaises(ConfigurationException) as cm:
            @self.config
            def unknown_property(ctx):
                return 'test'
        
        self.assertIn("Unknown configuration property: 'unknown_property'", str(cm.exception))

    def test_decorator_with_string_unknown_property_raises_exception(self):
        """Test that using @config('unknown') raises ConfigurationException."""
        with self.assertRaises(ConfigurationException) as cm:
            @self.config('unknown_property')
            def test_func(ctx):
                return 'test'
        
        self.assertIn("Unknown configuration property: 'test_func'", str(cm.exception))

    def test_decorator_with_non_callable_raises_exception(self):
        """Test that using @config with non-callable raises ConfigurationException."""
        # When calling config() with a string, it returns AttrRef, not raise an exception
        # The exception is raised when AttrRef is called with non-callable
        attr_ref = self.config("base_path")
        
        with self.assertRaises(ConfigurationException) as cm:
            attr_ref("not a function")
        
        self.assertIn("@config decorator must be used with functions", str(cm.exception))

    def test_global_config_instance(self):
        """Test that global config instance works."""
        config.base_path = '/test-api'
        self.assertEqual(config.base_path, '/test-api')

    def test_settings_backward_compatibility(self):
        """Test that settings is an alias for config."""
        self.assertIs(settings, config)
        settings.base_path = '/settings-test'
        self.assertEqual(config.base_path, '/settings-test')


class TestTemplateContext(unittest.TestCase):
    def setUp(self):
        self.template = TemplateContext()

    def test_template_context_initialization(self):
        """Test TemplateContext initializes with empty dictionaries."""
        self.assertEqual(self.template.functions, {})
        self.assertEqual(self.template.variables, {})
        self.assertEqual(self.template.filters, {})

    def test_add_variable(self):
        """Test add_variable method."""
        self.template.add_variable('my_var', 123)
        self.assertEqual(self.template.variables['my_var'], 123)
        
        self.template.add_variable('string_var', 'hello')
        self.assertEqual(self.template.variables['string_var'], 'hello')

    def test_add_variable_conflict_with_function_raises_exception(self):
        """Test that adding variable with same name as function raises TemplateException."""
        def test_func():
            return 'test'
        
        self.template.add_function('test_name', test_func)
        
        with self.assertRaises(TemplateException) as cm:
            self.template.add_variable('test_name', 'value')
        
        self.assertIn("unable to register variable: name 'test_name' is already in use for function", str(cm.exception))

    def test_add_function_direct(self):
        """Test add_function method."""
        def get_data():
            return 42
        
        self.template.add_function('get_data', get_data)
        self.assertEqual(self.template.functions['get_data'], get_data)
        self.assertEqual(self.template.functions['get_data'](), 42)

    def test_add_function_with_non_callable_raises_exception(self):
        """Test that add_function with non-callable raises TemplateException."""
        with self.assertRaises(TemplateException) as cm:
            self.template.add_function('test', 'not a function')
        
        self.assertIn("function registration must be used with functions", str(cm.exception))

    def test_function_decorator_direct(self):
        """Test @template.function decorator without string argument."""
        @self.template.function
        def get_data():
            return 100
        
        self.assertIn('get_data', self.template.functions)
        self.assertEqual(self.template.functions['get_data'](), 100)

    def test_function_decorator_with_string_name(self):
        """Test @template.function('name') decorator with custom name."""
        @self.template.function('get_more_data')
        def custom_function():
            return 200
        
        self.assertIn('get_more_data', self.template.functions)
        self.assertEqual(self.template.functions['get_more_data'](), 200)

    def test_add_filter_direct(self):
        """Test add_filter method."""
        def wrap_data(data):
            return f"< {data} >"
        
        self.template.add_filter('wrap', wrap_data)
        self.assertEqual(self.template.filters['wrap'], wrap_data)
        self.assertEqual(self.template.filters['wrap']('test'), '< test >')

    def test_add_filter_with_non_callable_raises_exception(self):
        """Test that add_filter with non-callable raises TemplateException."""
        with self.assertRaises(TemplateException) as cm:
            self.template.add_filter('test', 'not a function')
        
        self.assertIn("function registration must be used with functions", str(cm.exception))

    def test_filter_decorator_direct(self):
        """Test @template.filter decorator without string argument."""
        @self.template.filter
        def wrap_data(data):
            return f"[{data}]"
        
        self.assertIn('wrap_data', self.template.filters)
        self.assertEqual(self.template.filters['wrap_data']('test'), '[test]')

    def test_filter_decorator_with_string_name(self):
        """Test @template.filter('name') decorator with custom name."""
        @self.template.filter('wrap_more')
        def custom_filter(data):
            return f"<<< {data} >>>"
        
        self.assertIn('wrap_more', self.template.filters)
        self.assertEqual(self.template.filters['wrap_more']('test'), '<<< test >>>')


class TestAttrRef(unittest.TestCase):
    def setUp(self):
        self.config = Configuration()

    def test_attr_ref_with_valid_attribute(self):
        """Test AttrRef with valid configuration attribute."""
        attr_ref = AttrRef(self.config, 'base_path')
        self.assertEqual(attr_ref.config, self.config)
        self.assertEqual(attr_ref.attribute, 'base_path')

    def test_attr_ref_call_with_function(self):
        """Test calling AttrRef with a function."""
        attr_ref = AttrRef(self.config, 'context_to_app_id')
        
        @attr_ref
        def test_func(ctx):
            return 'test_value'
        
        self.assertEqual(self.config.context_to_app_id, test_func)
        self.assertEqual(self.config.context_to_app_id({}), 'test_value')

    def test_attr_ref_call_with_non_callable_raises_exception(self):
        """Test calling AttrRef with non-callable raises ConfigurationException."""
        attr_ref = AttrRef(self.config, 'base_path')
        
        with self.assertRaises(ConfigurationException) as cm:
            attr_ref('not a function')
        
        self.assertIn("@config decorator must be used with functions", str(cm.exception))


class TestTemplateFunctionRef(unittest.TestCase):
    def setUp(self):
        self.template = TemplateContext()

    def test_template_function_ref_call(self):
        """Test TemplateFunctionRef calling functionality."""
        func_ref = TemplateFunctionRef(self.template, 'test_func')
        
        @func_ref
        def my_function():
            return 'function_result'
        
        self.assertIn('test_func', self.template.functions)
        self.assertEqual(self.template.functions['test_func'](), 'function_result')


class TestTemplateFilterRef(unittest.TestCase):
    def setUp(self):
        self.template = TemplateContext()

    def test_template_filter_ref_call(self):
        """Test TemplateFilterRef calling functionality."""
        filter_ref = TemplateFilterRef(self.template, 'test_filter')
        
        @filter_ref
        def my_filter(data):
            return f"filtered: {data}"
        
        self.assertIn('test_filter', self.template.filters)
        self.assertEqual(self.template.filters['test_filter']('input'), 'filtered: input')


class TestContextFunc(unittest.TestCase):
    def test_context_func_decorator(self):
        """Test context_func decorator adds cube_context_func attribute."""
        @context_func
        def test_function():
            return 'test'
        
        self.assertTrue(hasattr(test_function, 'cube_context_func'))
        self.assertTrue(test_function.cube_context_func)
        self.assertEqual(test_function(), 'test')


class TestSafeString(unittest.TestCase):
    def test_safe_string_creation(self):
        """Test SafeString class creation and is_safe attribute."""
        safe_str = SafeString('test string')
        self.assertEqual(str(safe_str), 'test string')
        self.assertTrue(safe_str.is_safe)

    def test_safe_string_inheritance(self):
        """Test SafeString inherits from str."""
        safe_str = SafeString('hello')
        self.assertIsInstance(safe_str, str)
        self.assertEqual(safe_str.upper(), 'HELLO')


class TestFileRepository(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_file_repository_with_supported_files(self):
        """Test file_repository function with supported file types."""
        # Create test files
        test_files = {
            'test.js': 'console.log("hello");',
            'config.yml': 'key: value',
            'data.yaml': 'data: test',
            'template.jinja': '{{ variable }}',
            'script.py': 'print("hello")',
        }
        
        for filename, content in test_files.items():
            file_path = os.path.join(self.temp_dir, filename)
            with open(file_path, 'w') as f:
                f.write(content)
        
        # Test file_repository function
        result = file_repository(self.temp_dir)
        
        # Check that all files are found
        self.assertEqual(len(result), 5)
        
        # Check file contents
        result_dict = {item['fileName']: item['content'] for item in result}
        for filename, expected_content in test_files.items():
            self.assertIn(filename, result_dict)
            self.assertEqual(result_dict[filename], expected_content)

    def test_file_repository_ignores_unsupported_files(self):
        """Test file_repository ignores unsupported file types."""
        # Create unsupported files
        unsupported_files = ['test.txt', 'image.png', 'doc.pdf']
        for filename in unsupported_files:
            file_path = os.path.join(self.temp_dir, filename)
            with open(file_path, 'w') as f:
                f.write('content')
        
        # Create one supported file
        js_file = os.path.join(self.temp_dir, 'app.js')
        with open(js_file, 'w') as f:
            f.write('var x = 1;')
        
        result = file_repository(self.temp_dir)
        
        # Should only find the JS file
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['fileName'], 'app.js')
        self.assertEqual(result[0]['content'], 'var x = 1;')

    def test_file_repository_with_subdirectories(self):
        """Test file_repository recursively searches subdirectories."""
        # Create subdirectory structure
        sub_dir = os.path.join(self.temp_dir, 'subdir')
        os.makedirs(sub_dir)
        
        # Create files in main directory and subdirectory
        with open(os.path.join(self.temp_dir, 'main.js'), 'w') as f:
            f.write('main file')
        
        with open(os.path.join(sub_dir, 'sub.py'), 'w') as f:
            f.write('sub file')
        
        result = file_repository(self.temp_dir)
        
        self.assertEqual(len(result), 2)
        filenames = [item['fileName'] for item in result]
        self.assertIn('main.js', filenames)
        self.assertIn('sub.py', filenames)


class TestRequestContext(unittest.TestCase):
    def test_request_context_attributes(self):
        """Test RequestContext has required attributes."""
        context = RequestContext()
        # RequestContext is defined with type annotations but no __init__
        # The attributes exist as annotations but not as instance attributes
        # Check that the class has the annotations instead
        self.assertTrue(hasattr(RequestContext, '__annotations__'))
        self.assertIn('url', RequestContext.__annotations__)
        self.assertIn('method', RequestContext.__annotations__)
        self.assertIn('headers', RequestContext.__annotations__)


class TestExceptions(unittest.TestCase):
    def test_configuration_exception_inheritance(self):
        """Test ConfigurationException inherits from Exception."""
        exc = ConfigurationException('test message')
        self.assertIsInstance(exc, Exception)
        self.assertEqual(str(exc), 'test message')

    def test_template_exception_inheritance(self):
        """Test TemplateException inherits from Exception."""
        exc = TemplateException('template error')
        self.assertIsInstance(exc, Exception)
        self.assertEqual(str(exc), 'template error')


if __name__ == '__main__':
    unittest.main()