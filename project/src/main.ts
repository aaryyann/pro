#!/usr/bin/env node
import * as fs from 'fs';
import { Tokenizer } from './tokenizer';
import { Parser } from './parser';

function main() {
    const args = process.argv.slice(2);
    
    if (args.length < 1) {
        console.error('Usage: projectz-cli <source-file>');
        process.exit(1);
    }

    const filePath = args[0];
    let content = '';

    try {
        content = fs.readFileSync(filePath, 'utf-8');
    } catch (error) {
        console.error(`Failed to open ${filePath}`);
        process.exit(2);
    }

    const tokenizer = new Tokenizer(content);
    const tokens = tokenizer.tokenize();

    console.log(`Total tokens: ${tokens.length}`);
    
    const parser = new Parser(tokens);
    const ast = parser.parse();
    
    console.log(`Total statements: ${ast.length}`);
    
    for (let i = 0; i < tokens.length && i < 10; i++) {
        const token = tokens[i];
        console.log(`${token.type}: ${token.value} (line ${token.line}, col ${token.column})`);
    }
}

if (require.main === module) {
    main();
}

