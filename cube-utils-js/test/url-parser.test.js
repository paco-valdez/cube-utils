import { test } from 'node:test';
import assert from 'node:assert';
import { extractUrlParams } from '../src/url-parser.js';

test('single param', () => {
    const url = 'https://example.com/?foo=bar';
    const expected = { foo: 'bar' };
    assert.deepStrictEqual(extractUrlParams(url), expected);
});

test('multiple params', () => {
    const url = 'https://example.com/?foo=bar&baz=qux';
    const expected = { foo: 'bar', baz: 'qux' };
    assert.deepStrictEqual(extractUrlParams(url), expected);
});

test('repeated keys', () => {
    const url = 'https://example.com/?foo=bar&foo=baz';
    const expected = { foo: ['bar', 'baz'] };
    assert.deepStrictEqual(extractUrlParams(url), expected);
});

test('url encoded value', () => {
    const url = 'https://example.com/?foo=hello%20world';
    const expected = { foo: 'hello world' };
    assert.deepStrictEqual(extractUrlParams(url), expected);
});

test('empty query', () => {
    const url = 'https://example.com/';
    const expected = {};
    assert.deepStrictEqual(extractUrlParams(url), expected);
});

test('param with empty value', () => {
    const url = 'https://example.com/?foo=';
    const expected = {};
    assert.deepStrictEqual(extractUrlParams(url), expected);
});

test('long encoded query param', () => {
    const url = '/cubejs-api/v1/dry-run?query=%7B%22measures%22%3A%5B%22sales.net_sales_amount%22%5D%2C%22dimensions%22%3A%5B%22sales.currency_code%22%2C%22sales.region%22%2C%22sales.currency_type_code%22%5D%2C%22timeDimensions%22%3A%5B%7B%22dimension%22%3A%22sales.date_financial_ds%22%2C%22dateRange%22%3A%22last+month%22%2C%22granularity%22%3A%22month%22%7D%5D%2C%22filters%22%3A%5B%7B%22values%22%3A%5B%22GBP%22%2C%22USD%22%5D%2C%22member%22%3A%22sales.currency_code%22%2C%22operator%22%3A%22equals%22%7D%5D%7D';
    const expectedQuery = '{"measures":["sales.net_sales_amount"],"dimensions":["sales.currency_code","sales.region","sales.currency_type_code"],"timeDimensions":[{"dimension":"sales.date_financial_ds","dateRange":"last month","granularity":"month"}],"filters":[{"values":["GBP","USD"],"member":"sales.currency_code","operator":"equals"}]}';
    const result = extractUrlParams(url);
    assert.ok('query' in result);
    assert.strictEqual(result.query, expectedQuery);
});

test('multiple long encoded urls', () => {
    const urls = [
        '/cubejs-api/v1/sql?query=%7B%22measures%22%3A%5B%22sales.net_sales_amount%22%5D%2C%22dimensions%22%3A%5B%22sales.currency_code%22%2C%22sales.region%22%2C%22sales.currency_type_code%22%5D%2C%22timeDimensions%22%3A%5B%7B%22dimension%22%3A%22sales.date_financial_ds%22%2C%22dateRange%22%3A%22last+month%22%2C%22granularity%22%3A%22month%22%7D%5D%2C%22filters%22%3A%5B%7B%22values%22%3A%5B%22GBP%22%2C%22USD%22%5D%2C%22member%22%3A%22sales.currency_code%22%2C%22operator%22%3A%22equals%22%7D%5D%7D',
        '/cubejs-api/v1/load?query=%7B%22measures%22%3A%5B%22sales.net_sales_amount%22%5D%2C%22dimensions%22%3A%5B%22sales.currency_code%22%2C%22sales.region%22%2C%22sales.currency_type_code%22%5D%2C%22timeDimensions%22%3A%5B%7B%22dimension%22%3A%22sales.date_financial_ds%22%2C%22dateRange%22%3A%22last+month%22%2C%22granularity%22%3A%22month%22%7D%5D%2C%22filters%22%3A%5B%7B%22values%22%3A%5B%22GBP%22%2C%22USD%22%5D%2C%22member%22%3A%22sales.currency_code%22%2C%22operator%22%3A%22equals%22%7D%5D%7D&queryType=multi'
    ];
    const expectedQuery = '{"measures":["sales.net_sales_amount"],"dimensions":["sales.currency_code","sales.region","sales.currency_type_code"],"timeDimensions":[{"dimension":"sales.date_financial_ds","dateRange":"last month","granularity":"month"}],"filters":[{"values":["GBP","USD"],"member":"sales.currency_code","operator":"equals"}]}';
    for (const url of urls) {
        const result = extractUrlParams(url);
        assert.ok('query' in result);
        assert.strictEqual(result.query, expectedQuery);
    }
});