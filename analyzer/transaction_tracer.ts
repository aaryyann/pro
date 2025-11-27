#!/usr/bin/env node
import * as fs from 'fs';

interface TransactionTrace {
    id: string;
    operations: number;
    status: string;
}

function traceTransactions(filePath: string): void {
    let content = '';
    
    try {
        content = fs.readFileSync(filePath, 'utf-8');
    } catch (error) {
        console.error(`Failed to read file: ${filePath}`);
        process.exit(1);
    }
    
    const transactionPattern = /createTransaction\s*\([^)]+\)/g;
    const commitPattern = /\.commit\s*\(/g;
    const rollbackPattern = /\.rollback\s*\(/g;
    const operationPattern = /addOperation\s*\(/g;
    
    const transactions = (content.match(transactionPattern) || []).length;
    const commits = (content.match(commitPattern) || []).length;
    const rollbacks = (content.match(rollbackPattern) || []).length;
    const operations = (content.match(operationPattern) || []).length;
    
    console.log('TRANSACTION_TRACE:');
    console.log(`transactions_created: ${transactions}`);
    console.log(`operations_added: ${operations}`);
    console.log(`commits: ${commits}`);
    console.log(`rollbacks: ${rollbacks}`);
    console.log(`avg_operations_per_txn: ${transactions > 0 ? (operations / transactions).toFixed(2) : '0.00'}`);
}

function main() {
    const args = process.argv.slice(2);
    
    if (args.length === 0) {
        console.error('Usage: transaction_tracer.ts <source_file>');
        process.exit(1);
    }
    
    traceTransactions(args[0]);
}

if (require.main === module) {
    main();
}

