import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Read the ES module files
const srcDir = path.join(__dirname, '..', 'src');
const distDir = path.join(__dirname, '..', 'dist');

// Ensure dist directory exists
if (!fs.existsSync(distDir)) {
    fs.mkdirSync(distDir, { recursive: true });
}

// Read and transform the ES modules to CommonJS
function transformToCommonJS(content, filename) {
    // Replace ES6 import statements with require statements
    content = content.replace(/import\s+\{([^}]+)\}\s+from\s+['"]([^'"]+)['"]/g, 
        (match, imports, modulePath) => {
            const cleanImports = imports.split(',').map(imp => imp.trim()).join(', ');
            return `const { ${cleanImports} } = require('${modulePath}')`;
        });
    
    // Replace ES6 export statements with module.exports
    content = content.replace(/export\s+\{([^}]+)\}/g, (match, exports) => {
        const cleanExports = exports.split(',').map(exp => exp.trim());
        const exportObj = cleanExports.map(exp => `    ${exp}`).join(',\n');
        return `module.exports = {\n${exportObj}\n}`;
    });
    
    // Replace export * from statements
    content = content.replace(/export\s+\*\s+from\s+['"]([^'"]+)['"]/g, 
        (match, modulePath) => {
            return `const ${path.basename(modulePath, '.js')}Exports = require('${modulePath}');\nObject.assign(module.exports, ${path.basename(modulePath, '.js')}Exports);`;
        });
    
    return content;
}

// Transform each source file
const sourceFiles = ['index.js', 'query-parser.js', 'url-parser.js'];

for (const filename of sourceFiles) {
    const sourcePath = path.join(srcDir, filename);
    const content = fs.readFileSync(sourcePath, 'utf8');
    
    let transformedContent = transformToCommonJS(content, filename);
    
    // Handle the index.js file specially to properly re-export everything
    if (filename === 'index.js') {
        transformedContent = `const queryParserExports = require('./query-parser.cjs');
const urlParserExports = require('./url-parser.cjs');

module.exports = {
    ...queryParserExports,
    ...urlParserExports
};`;
    }
    
    const outputFilename = filename.replace('.js', '.cjs');
    const outputPath = path.join(distDir, outputFilename);
    
    fs.writeFileSync(outputPath, transformedContent);
    console.log(`Generated ${outputFilename}`);
}

console.log('Build completed successfully!');