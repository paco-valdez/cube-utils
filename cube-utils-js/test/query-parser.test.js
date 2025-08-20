import { test } from 'node:test';
import assert from 'node:assert';
import {
    extractCubes,
    extractMembers,
    extractFiltersMembers,
    extractFiltersMembersWithValues
} from '../src/query-parser.js';

// Test ExtractCubes
test('extractCubes with all fields', () => {
    const payload = {
        dimensions: ['test_a.city', 'test_a.country', 'test_a.state'],
        measures: ['test_b.count'],
        filters: [
            { values: ['US'], member: 'test_a.country', operator: 'equals' }
        ],
        segments: ['test_d.us_segment'],
        timeDimensions: [
            {
                dimension: 'test_c.time',
                dateRange: ['2021-01-01', '2021-12-31'],
                granularity: 'month'
            }
        ]
    };
    const expectedCubes = ['test_a', 'test_b', 'test_c', 'test_d'];
    assert.deepStrictEqual(extractCubes(payload).sort(), expectedCubes.sort());
});

test('extractCubes complex boolean logic', () => {
    const payload = {
        segments: [],
        filters: [
            {
                or: [
                    {
                        and: [
                            {
                                values: ['Corpus Christi'],
                                member: 'test_a.city',
                                operator: 'equals'
                            },
                            {
                                member: 'test_b.age_bucket',
                                operator: 'equals',
                                values: ['Senior adult']
                            }
                        ]
                    },
                    {
                        member: 'test_c.city',
                        operator: 'equals',
                        values: ['Sacramento']
                    }
                ]
            },
            { or: [{ member: 'test_d.city', operator: 'set' }] }
        ]
    };
    const expectedCubes = ['test_a', 'test_b', 'test_c', 'test_d'];
    assert.deepStrictEqual(extractCubes(payload).sort(), expectedCubes.sort());
});

test('extractCubes pushed down query with measures', () => {
    const payload = {
        segments: [],
        timezone: 'UTC',
        measures: [
            {
                cubeName: 'test_a',
                name: 'foo',
                expressionName: 'foo',
                definition: '{"cubeName":"test_a","alias":"foo","expr":{"type":"SqlFunction","cubeParams":["test_a"],"sql":"MIN(${test_a.active_from_at})"},"groupingSet":null}',
                expression: [
                    'test_a',
                    'return `MIN(${test_a.active_from_at})`'
                ],
                groupingSet: null
            },
            {
                definition: '{"cubeName":"test_b","alias":"bar","expr":{"type":"SqlFunction","cubeParams":["test_b"],"sql":"MAX(${test_b.active_from_at})"},"groupingSet":null}',
                groupingSet: null,
                expression: [
                    'test_b',
                    'return `MAX(${test_b.active_from_at})`'
                ],
                name: 'bar',
                cubeName: 'test_b',
                expressionName: 'bar'
            },
            {
                name: 'count_uint8_1__',
                expressionName: 'count_uint8_1__',
                groupingSet: null,
                cubeName: 'test_c',
                expression: [
                    'test_c',
                    'return `${test_c.count}`'
                ],
                definition: '{"cubeName":"test_c","alias":"count_uint8_1__","expr":{"type":"SqlFunction","cubeParams":["test_c"],"sql":"${test_c.count}"},"groupingSet":null}'
            }
        ],
        filters: [],
        timeDimensions: [],
        order: [],
        dimensions: [],
        subqueryJoins: [],
        limit: null
    };
    const expectedCubes = ['test_a', 'test_b', 'test_c'];
    assert.deepStrictEqual(extractCubes(payload).sort(), expectedCubes.sort());
});

test('extractCubes with dimensions only', () => {
    const payload = { dimensions: ['test_a.city', 'test_a.country', 'test_a.state'] };
    const expectedCubes = ['test_a'];
    assert.deepStrictEqual(extractCubes(payload).sort(), expectedCubes.sort());
});

test('extractCubes with measures only', () => {
    const payload = { measures: ['test_b.count'] };
    const expectedCubes = ['test_b'];
    assert.deepStrictEqual(extractCubes(payload).sort(), expectedCubes.sort());
});

test('extractCubes with filters only', () => {
    const payload = {
        filters: [
            { values: ['US'], member: 'test_a.country', operator: 'equals' }
        ]
    };
    const expectedCubes = ['test_a'];
    assert.deepStrictEqual(extractCubes(payload).sort(), expectedCubes.sort());
});

test('extractCubes with segments only', () => {
    const payload = { segments: ['test_a.us_segment'] };
    const expectedCubes = ['test_a'];
    assert.deepStrictEqual(extractCubes(payload).sort(), expectedCubes.sort());
});

test('extractCubes with timeDimensions only', () => {
    const payload = {
        timeDimensions: [
            {
                dimension: 'test_c.time',
                dateRange: ['2021-01-01', '2021-12-31'],
                granularity: 'month'
            }
        ]
    };
    const expectedCubes = ['test_c'];
    assert.deepStrictEqual(extractCubes(payload).sort(), expectedCubes.sort());
});

test('extractCubes with empty payload', () => {
    const payload = {};
    const expectedCubes = [];
    assert.deepStrictEqual(extractCubes(payload), expectedCubes);
});

test('extractCubes with invalid keywords', () => {
    const payload = { invalid: ['test_a.city', 'test_a.country', 'test_a.state'] };
    const expectedCubes = [];
    assert.deepStrictEqual(extractCubes(payload), expectedCubes);
});

// Test ExtractMembers
test('extractMembers with all fields', () => {
    const payload = {
        dimensions: ['test_a.city', 'test_a.country', 'test_a.state'],
        measures: ['test_b.count'],
        filters: [
            { values: ['US'], member: 'test_a.country', operator: 'equals' }
        ],
        segments: ['test_d.us_segment'],
        timeDimensions: [
            {
                dimension: 'test_c.time',
                dateRange: ['2021-01-01', '2021-12-31'],
                granularity: 'month'
            }
        ]
    };
    const expectedMembers = [
        'test_a.city',
        'test_a.country',
        'test_a.state',
        'test_b.count',
        'test_c.time',
        'test_d.us_segment'
    ];
    assert.deepStrictEqual(extractMembers(payload).sort(), expectedMembers.sort());
});

test('extractMembers complex boolean logic', () => {
    const payload = {
        segments: [],
        filters: [
            {
                or: [
                    {
                        and: [
                            {
                                values: ['Corpus Christi'],
                                member: 'test_a.city',
                                operator: 'equals'
                            },
                            {
                                member: 'test_b.age_bucket',
                                operator: 'equals',
                                values: ['Senior adult']
                            }
                        ]
                    },
                    {
                        member: 'test_c.city',
                        operator: 'equals',
                        values: ['Sacramento']
                    }
                ]
            },
            { or: [{ member: 'test_d.city', operator: 'set' }] }
        ]
    };
    const expectedMembers = [
        'test_a.city',
        'test_b.age_bucket',
        'test_c.city',
        'test_d.city'
    ];
    assert.deepStrictEqual(extractMembers(payload).sort(), expectedMembers.sort());
});

test('extractMembers with dimensions only', () => {
    const payload = { dimensions: ['test_a.city', 'test_a.country', 'test_a.state'] };
    const expectedMembers = ['test_a.city', 'test_a.country', 'test_a.state'];
    assert.deepStrictEqual(extractMembers(payload).sort(), expectedMembers.sort());
});

test('extractMembers with measures only', () => {
    const payload = { measures: ['test_b.count'] };
    const expectedMembers = ['test_b.count'];
    assert.deepStrictEqual(extractMembers(payload).sort(), expectedMembers.sort());
});

test('extractMembers with filters only', () => {
    const payload = {
        filters: [
            { values: ['US'], member: 'test_a.country', operator: 'equals' }
        ]
    };
    const expectedMembers = ['test_a.country'];
    assert.deepStrictEqual(extractMembers(payload).sort(), expectedMembers.sort());
});

test('extractMembers with segments only', () => {
    const payload = { segments: ['test_a.us_segment'] };
    const expectedMembers = ['test_a.us_segment'];
    assert.deepStrictEqual(extractMembers(payload).sort(), expectedMembers.sort());
});

test('extractMembers with timeDimensions only', () => {
    const payload = {
        timeDimensions: [
            {
                dimension: 'test_c.time',
                dateRange: ['2021-01-01', '2021-12-31'],
                granularity: 'month'
            }
        ]
    };
    const expectedMembers = ['test_c.time'];
    assert.deepStrictEqual(extractMembers(payload).sort(), expectedMembers.sort());
});

test('extractMembers with empty payload', () => {
    const payload = {};
    const expectedMembers = [];
    assert.deepStrictEqual(extractMembers(payload), expectedMembers);
});

test('extractMembers with invalid keywords', () => {
    const payload = { invalid: ['test_a.city', 'test_a.country', 'test_a.state'] };
    const expectedMembers = [];
    assert.deepStrictEqual(extractMembers(payload), expectedMembers);
});

// Test ExtractFiltersMembers
test('extractFiltersMembers with all fields', () => {
    const payload = {
        dimensions: ['test_a.city', 'test_a.country', 'test_a.state'],
        measures: ['test_b.count'],
        filters: [
            { values: ['US'], member: 'test_a.country', operator: 'equals' }
        ],
        segments: ['test_d.us_segment'],
        timeDimensions: [
            {
                dimension: 'test_c.time',
                dateRange: ['2021-01-01', '2021-12-31'],
                granularity: 'month'
            }
        ]
    };
    const expectedMembers = ['test_a.country', 'test_d.us_segment'];
    assert.deepStrictEqual(extractFiltersMembers(payload).sort(), expectedMembers.sort());
});

test('extractFiltersMembers complex boolean logic', () => {
    const payload = {
        segments: [],
        filters: [
            {
                or: [
                    {
                        and: [
                            {
                                values: ['Corpus Christi'],
                                member: 'test_a.city',
                                operator: 'equals'
                            },
                            {
                                member: 'test_b.age_bucket',
                                operator: 'equals',
                                values: ['Senior adult']
                            }
                        ]
                    },
                    {
                        member: 'test_c.city',
                        operator: 'equals',
                        values: ['Sacramento']
                    }
                ]
            },
            { or: [{ member: 'test_d.city', operator: 'set' }] }
        ]
    };
    const expectedMembers = [
        'test_a.city',
        'test_b.age_bucket',
        'test_c.city',
        'test_d.city'
    ];
    assert.deepStrictEqual(extractFiltersMembers(payload).sort(), expectedMembers.sort());
});

test('extractFiltersMembers with dimensions only', () => {
    const payload = { dimensions: ['test_a.city', 'test_a.country', 'test_a.state'] };
    const expectedMembers = [];
    assert.deepStrictEqual(extractFiltersMembers(payload).sort(), expectedMembers.sort());
});

test('extractFiltersMembers with measures only', () => {
    const payload = { measures: ['test_b.count'] };
    const expectedMembers = [];
    assert.deepStrictEqual(extractFiltersMembers(payload).sort(), expectedMembers.sort());
});

test('extractFiltersMembers with filters only', () => {
    const payload = {
        filters: [
            { values: ['US'], member: 'test_a.country', operator: 'equals' }
        ]
    };
    const expectedMembers = ['test_a.country'];
    assert.deepStrictEqual(extractFiltersMembers(payload).sort(), expectedMembers.sort());
});

test('extractFiltersMembers with segments only', () => {
    const payload = { segments: ['test_a.us_segment'] };
    const expectedMembers = ['test_a.us_segment'];
    assert.deepStrictEqual(extractFiltersMembers(payload).sort(), expectedMembers.sort());
});

test('extractFiltersMembers with timeDimensions only', () => {
    const payload = {
        timeDimensions: [
            {
                dimension: 'test_c.time',
                dateRange: ['2021-01-01', '2021-12-31'],
                granularity: 'month'
            }
        ]
    };
    const expectedMembers = [];
    assert.deepStrictEqual(extractFiltersMembers(payload).sort(), expectedMembers.sort());
});

test('extractFiltersMembers with empty payload', () => {
    const payload = {};
    const expectedMembers = [];
    assert.deepStrictEqual(extractFiltersMembers(payload), expectedMembers);
});

test('extractFiltersMembers with invalid keywords', () => {
    const payload = { invalid: ['test_a.city', 'test_a.country', 'test_a.state'] };
    const expectedMembers = [];
    assert.deepStrictEqual(extractFiltersMembers(payload), expectedMembers);
});

test('extractFiltersMembers pushdown filters', () => {
    const payload = {
        timezone: 'UTC',
        timeDimensions: [],
        filters: [],
        measures: [
            {
                name: 'count_case_when_',
                expression: [
                    'internet_sales',
                    'return `COUNT(CASE WHEN (${internet_sales.salesterritorykey} = 1) THEN 1 END)`'
                ],
                definition: '{"cubeName":"internet_sales","alias":"count_case_when_","expr":{"type":"SqlFunction","cubeParams":["internet_sales"],"sql":"COUNT(CASE WHEN (${internet_sales.salesterritorykey} = 1) THEN 1 END)"},"groupingSet":null}',
                cubeName: 'internet_sales',
                groupingSet: null,
                expressionName: 'count_case_when_'
            }
        ],
        order: [],
        limit: null,
        segments: [
            {
                expression: [
                    'internet_sales',
                    'return `CASE WHEN ((${internet_sales.salesterritorykey} = 1) OR (${internet_sales.salesterritorykey} = 9)) THEN TRUE END`'
                ],
                groupingSet: null,
                definition: '{"cubeName":"internet_sales","alias":"case_when_s_sale","expr":{"type":"SqlFunction","cubeParams":["internet_sales"],"sql":"CASE WHEN ((${internet_sales.salesterritorykey} = 1) OR (${internet_sales.salesterritorykey} = 9)) THEN TRUE END"},"groupingSet":null}',
                cubeName: 'internet_sales',
                name: 'case_when_s_sale',
                expressionName: 'case_when_s_sale'
            }
        ],
        dimensions: [
            {
                cubeName: 'internet_sales',
                expressionName: 'productkey',
                groupingSet: null,
                name: 'productkey',
                definition: '{"cubeName":"internet_sales","alias":"productkey","expr":{"type":"SqlFunction","cubeParams":["internet_sales"],"sql":"${internet_sales.productkey}"},"groupingSet":null}',
                expression: [
                    'internet_sales',
                    'return `${internet_sales.productkey}`'
                ]
            }
        ],
        subqueryJoins: []
    };
    const expectedMembers = ['internet_sales.salesterritorykey'];
    assert.deepStrictEqual(extractFiltersMembers(payload).sort(), expectedMembers.sort());
});

// Test ExtractFiltersMembersWithValues
test('extractFiltersMembersWithValues with all fields', () => {
    const payload = {
        dimensions: ['test_a.city', 'test_a.country', 'test_a.state'],
        measures: ['test_b.count'],
        filters: [
            { values: ['US'], member: 'test_a.country', operator: 'equals' }
        ],
        segments: ['test_d.us_segment'],
        timeDimensions: [
            {
                dimension: 'test_c.time',
                dateRange: ['2021-01-01', '2021-12-31'],
                granularity: 'month'
            }
        ]
    };
    const expectedMembers = [['test_a.country', ['US']], ['test_d.us_segment', null]];
    assert.deepStrictEqual(extractFiltersMembersWithValues(payload).sort(), expectedMembers.sort());
});

test('extractFiltersMembersWithValues complex boolean logic', () => {
    const payload = {
        segments: [],
        filters: [
            {
                or: [
                    {
                        and: [
                            {
                                values: ['Corpus Christi'],
                                member: 'test_a.city',
                                operator: 'equals'
                            },
                            {
                                member: 'test_b.age_bucket',
                                operator: 'equals',
                                values: ['Senior adult']
                            }
                        ]
                    },
                    {
                        member: 'test_c.city',
                        operator: 'equals',
                        values: ['Sacramento']
                    }
                ]
            },
            { or: [{ member: 'test_d.city', operator: 'set' }] }
        ]
    };
    const expectedMembers = [
        ['test_a.city', ['Corpus Christi']],
        ['test_b.age_bucket', ['Senior adult']],
        ['test_c.city', ['Sacramento']],
        ['test_d.city', null]
    ];
    assert.deepStrictEqual(extractFiltersMembersWithValues(payload).sort(), expectedMembers.sort());
});

test('extractFiltersMembersWithValues pushdown filters', () => {
    const payload = {
        timezone: 'UTC',
        timeDimensions: [],
        filters: [],
        measures: [
            {
                name: 'count_case_when_',
                expression: [
                    'internet_sales',
                    'return `COUNT(CASE WHEN (${internet_sales.salesterritorykey} = 1) THEN 1 END)`'
                ],
                definition: '{"cubeName":"internet_sales","alias":"count_case_when_","expr":{"type":"SqlFunction","cubeParams":["internet_sales"],"sql":"COUNT(CASE WHEN (${internet_sales.salesterritorykey} = 1) THEN 1 END)"},"groupingSet":null}',
                cubeName: 'internet_sales',
                groupingSet: null,
                expressionName: 'count_case_when_'
            }
        ],
        order: [],
        limit: null,
        segments: [
            {
                expression: [
                    'internet_sales',
                    'return `CASE WHEN ((${internet_sales.salesterritorykey} = 1) OR (${internet_sales.salesterritorykey} = 9)) THEN TRUE END`'
                ],
                groupingSet: null,
                definition: '{"cubeName":"internet_sales","alias":"case_when_s_sale","expr":{"type":"SqlFunction","cubeParams":["internet_sales"],"sql":"CASE WHEN ((${internet_sales.salesterritorykey} = 1) OR (${internet_sales.salesterritorykey} = 9)) THEN TRUE END"},"groupingSet":null}',
                cubeName: 'internet_sales',
                name: 'case_when_s_sale',
                expressionName: 'case_when_s_sale'
            }
        ],
        dimensions: [
            {
                cubeName: 'internet_sales',
                expressionName: 'productkey',
                groupingSet: null,
                name: 'productkey',
                definition: '{"cubeName":"internet_sales","alias":"productkey","expr":{"type":"SqlFunction","cubeParams":["internet_sales"],"sql":"${internet_sales.productkey}"},"groupingSet":null}',
                expression: [
                    'internet_sales',
                    'return `${internet_sales.productkey}`'
                ]
            }
        ],
        subqueryJoins: []
    };
    const expectedMembers = [['internet_sales.salesterritorykey', [1, 9]]];
    assert.deepStrictEqual(extractFiltersMembersWithValues(payload).sort(), expectedMembers.sort());
});

test('extractFiltersMembersWithValues with empty payload', () => {
    const payload = {};
    const expectedMembers = [];
    assert.deepStrictEqual(extractFiltersMembersWithValues(payload), expectedMembers);
});

test('extractFiltersMembersWithValues with invalid keywords', () => {
    const payload = { invalid: ['test_a.city', 'test_a.country', 'test_a.state'] };
    const expectedMembers = [];
    assert.deepStrictEqual(extractFiltersMembersWithValues(payload), expectedMembers);
});