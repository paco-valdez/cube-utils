/**
 * Check if a member is a pushdown member.
 * A pushdown member is an object with 'cubeName' and 'expressionName' properties.
 * @param {any} member - The member to check.
 * @returns {boolean} True if the member is a pushdown member, false otherwise.
 */
/**
 * Ensure the payload is an object, converting string payloads to an empty object.
 * This mirrors Cube.js's behaviour where metadata queries are represented as strings.
 * @param {any} payload
 * @returns {Object}
 */
function ensureObjectPayload(payload) {
    if (typeof payload === 'object' && payload !== null) {
        return payload;
    }
    if (typeof payload === 'string') {
        return {};
    }
    throw new TypeError('payload must be an object or string');
}

function isPushdownMember(member) {
    return (
        typeof member === 'object' &&
        member !== null &&
        'cubeName' in member &&
        'expressionName' in member
    );
}

/**
 * Extracts unique cubes from the given query payload.
 * @param {Object} payload - The query payload containing dimensions, measures, filters, segments, and time dimensions.
 * @returns {string[]} A list of unique cube names.
 */
function extractCubes(payload) {
    const payloadObj = ensureObjectPayload(payload);
    const cubes = new Set();
    const members = extractMembers(payloadObj);
    for (const member of members) {
        const cube = member.split('.')[0];
        cubes.add(cube);
    }
    return Array.from(cubes);
}

/**
 * Extracts unique members from the given query payload.
 * @param {Object} payload - The query payload containing dimensions, measures, filters, segments, and time dimensions.
 * @param {string[]} queryKeys - The keys to extract from (defaults to all query types).
 * @returns {string[]} A list of unique members in the format 'cubeName.expressionName'.
 */
function extractMembers(
    payload,
    queryKeys = ['dimensions', 'measures', 'filters', 'segments', 'timeDimensions']
) {
    const payloadObj = ensureObjectPayload(payload);
    const members = new Set();

    for (const key of queryKeys) {
        if (key in payloadObj) {
            for (const item of payloadObj[key]) {
                if (isPushdownMember(item)) {
                    // Try to extract from expression or definition
                    let exprMembers = new Set();
                    if ('expression' in item && Array.isArray(item.expression)) {
                        for (const expr of item.expression) {
                            if (typeof expr === 'string') {
                                const member = extractMembersFromExpression(expr);
                                if (member.length > 0) {
                                    member.forEach(m => exprMembers.add(m));
                                }
                            }
                        }
                    }
                    if (
                        exprMembers.size === 0 &&
                        'definition' in item &&
                        typeof item.definition === 'string'
                    ) {
                        const member = extractMembersFromExpression(item.definition);
                        if (member.length > 0) {
                            member.forEach(m => exprMembers.add(m));
                        }
                    }
                    if (exprMembers.size > 0) {
                        exprMembers.forEach(m => members.add(m));
                    } else {
                        members.add(`${item.cubeName}.${item.expressionName}`);
                    }
                } else if (key === 'filters') {
                    const filterMembers = extractMembersFromFilter(item);
                    filterMembers.forEach(m => members.add(m));
                } else if (
                    key === 'timeDimensions' &&
                    typeof item === 'object' &&
                    item !== null &&
                    'dimension' in item
                ) {
                    members.add(item.dimension);
                } else {
                    members.add(item);
                }
            }
        }
    }

    return Array.from(members);
}

/**
 * Extracts all members in the format ${cube.member} from a string expression.
 * @param {string} expr - The expression to extract members from.
 * @returns {string[]} Array of member names.
 */
function extractMembersFromExpression(expr) {
    const matches = expr.match(/\$\{([a-zA-Z0-9_]+\.[a-zA-Z0-9_]+)\}/g);
    if (!matches) return [];
    return matches.map(match => match.slice(2, -1)); // Remove ${ and }
}

/**
 * Extracts member-value pairs from SQL expressions.
 * @param {string} sql - The SQL expression to parse.
 * @returns {Array<[string, string]>} Array of [member, value] pairs.
 */
function extractMemberValueFromSql(sql) {
    const pattern = /\$\{([a-zA-Z0-9_]+\.[a-zA-Z0-9_]+)\}\s*=\s*([^)\s]+)/g;
    const matches = [];
    let match;
    while ((match = pattern.exec(sql)) !== null) {
        matches.push([match[1], match[2]]);
    }
    return matches;
}

/**
 * Extracts members from a filter item, handling boolean logic (AND/OR) recursively.
 * @param {Object} filterItem - The filter item to extract members from.
 * @returns {Set<string>} A set of unique members extracted from the filter item.
 */
function extractMembersFromFilter(filterItem) {
    const members = new Set();

    // Handle direct member filters
    if ('member' in filterItem) {
        members.add(filterItem.member);
    }

    // Handle AND conditions
    if ('and' in filterItem) {
        for (const condition of filterItem.and) {
            const conditionMembers = extractMembersFromFilter(condition);
            conditionMembers.forEach(m => members.add(m));
        }
    }

    // Handle OR conditions
    if ('or' in filterItem) {
        for (const condition of filterItem.or) {
            const conditionMembers = extractMembersFromFilter(condition);
            conditionMembers.forEach(m => members.add(m));
        }
    }

    return members;
}

/**
 * Extracts the members from filters from the given query payload.
 * @param {Object} payload - The query payload containing dimensions, measures, filters, segments, and time dimensions.
 * @returns {string[]} A list of members.
 */
function extractFiltersMembers(payload) {
    const payloadObj = ensureObjectPayload(payload);
    const queryKeys = ['filters', 'segments'];
    return extractMembers(payloadObj, queryKeys);
}

/**
 * Extracts (member, value) tuples from filters and segments in the given query payload.
 * For filters, value is the 'values' field if present, otherwise null.
 * For segments, value is always null unless a value can be extracted from a pushdown SQL expression.
 * Handles nested boolean logic in filters.
 * Ensures unique members and unique values per member.
 * @param {Object} payload - The query payload.
 * @returns {Array<[string, any]>} Array of [member, values] tuples.
 */
function extractFiltersMembersWithValues(payload) {
    const payloadObj = ensureObjectPayload(payload);
    const result = new Map();

    function extractFromFilter(filterItem) {
        if ('member' in filterItem) {
            const value = filterItem.values;
            if (value !== undefined && value !== null) {
                if (!result.has(filterItem.member)) {
                    result.set(filterItem.member, new Set());
                }
                if (Array.isArray(value)) {
                    value.forEach(v => result.get(filterItem.member).add(v));
                } else {
                    result.get(filterItem.member).add(value);
                }
            } else {
                if (!result.has(filterItem.member)) {
                    result.set(filterItem.member, new Set());
                }
            }
        }
        if ('and' in filterItem) {
            for (const cond of filterItem.and) {
                extractFromFilter(cond);
            }
        }
        if ('or' in filterItem) {
            for (const cond of filterItem.or) {
                extractFromFilter(cond);
            }
        }
    }

    if ('filters' in payloadObj) {
        for (const filterItem of payload.filters) {
            extractFromFilter(filterItem);
        }
    }

    if ('segments' in payloadObj) {
        for (const seg of payload.segments) {
            if (typeof seg === 'object' && seg !== null && isPushdownMember(seg)) {
                const exprMembers = new Map();
                const sqls = [];
                if ('expression' in seg && Array.isArray(seg.expression)) {
                    for (const expr of seg.expression) {
                        if (typeof expr === 'string') {
                            sqls.push(expr);
                        }
                    }
                }
                if ('definition' in seg && typeof seg.definition === 'string') {
                    sqls.push(seg.definition);
                }
                let found = false;
                for (const sql of sqls) {
                    for (const [member, value] of extractMemberValueFromSql(sql)) {
                        found = true;
                        // Remove quotes from value if present
                        let cleanValue = value;
                        if (cleanValue.startsWith('`') && cleanValue.endsWith('`')) {
                            cleanValue = cleanValue.slice(1, -1);
                        }
                        try {
                            cleanValue = parseInt(cleanValue, 10);
                            if (isNaN(cleanValue)) {
                                cleanValue = value;
                            }
                        } catch {
                            // Keep original value if parsing fails
                        }
                        if (!exprMembers.has(member)) {
                            exprMembers.set(member, new Set());
                        }
                        exprMembers.get(member).add(cleanValue);
                    }
                }
                if (found) {
                    for (const [m, vals] of exprMembers) {
                        if (!result.has(m)) {
                            result.set(m, new Set());
                        }
                        vals.forEach(v => result.get(m).add(v));
                    }
                } else {
                    // fallback to just extracting members
                    for (const sql of sqls) {
                        for (const member of extractMembersFromExpression(sql)) {
                            if (!result.has(member)) {
                                result.set(member, new Set());
                            }
                        }
                    }
                }
                if (sqls.length === 0) {
                    const memberName = `${seg.cubeName}.${seg.expressionName}`;
                    if (!result.has(memberName)) {
                        result.set(memberName, new Set());
                    }
                }
            } else if (typeof seg === 'object' && seg !== null) {
                const name = seg.name || seg.expressionName;
                if (name) {
                    if (!result.has(name)) {
                        result.set(name, new Set());
                    }
                }
            } else {
                if (!result.has(seg)) {
                    result.set(seg, new Set());
                }
            }
        }
    }

    // Convert sets to sorted arrays or null if empty
    const output = [];
    for (const [k, v] of result) {
        if (v.size > 0) {
            output.push([k, Array.from(v).sort()]);
        } else {
            output.push([k, null]);
        }
    }
    return output;
}

export {
    isPushdownMember,
    extractCubes,
    extractMembers,
    extractMembersFromExpression,
    extractMemberValueFromSql,
    extractMembersFromFilter,
    extractFiltersMembers,
    extractFiltersMembersWithValues
};
