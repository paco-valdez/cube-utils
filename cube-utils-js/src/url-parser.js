/**
 * Extract query parameters from a URL using built-in URL APIs.
 * 
 * @param {string} url - The input URL string.
 * @returns {Object} A dictionary of query parameters with URL-decoded values.
 */
function extractUrlParams(url) {
    try {
        // Handle relative URLs by using a dummy base
        const urlObj = new URL(url, 'https://example.com');
        const params = {};
        
        for (const [key, value] of urlObj.searchParams) {
            // Skip empty values
            if (value === '') {
                continue;
            }
            
            if (params[key]) {
                // If key already exists, convert to array or append to existing array
                if (Array.isArray(params[key])) {
                    params[key].push(value);
                } else {
                    params[key] = [params[key], value];
                }
            } else {
                params[key] = value;
            }
        }
        
        return params;
    } catch (error) {
        // If URL parsing fails, return empty object
        return {};
    }
}

export { extractUrlParams };