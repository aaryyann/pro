#!/usr/bin/env node
import * as fs from 'fs';
import { Tokenizer } from './tokenizer';

function percentile(counts: number[], p: number): number {
    if (counts.length === 0) return -1;
    const sorted = [...counts].sort((a, b) => a - b);
    let idx = Math.floor((p * sorted.length) / 100);
    if (idx >= sorted.length) idx = sorted.length - 1;
    return sorted[idx];
}

function main() {
    let input = '';
    
    if (process.argv.length > 2) {
        input = fs.readFileSync(process.argv[2], 'utf-8');
    } else {
        input = fs.readFileSync(0, 'utf-8');
    }

    const tk = new Tokenizer();
    const toks = tk.tokenize(input);

    const freq: Map<string, number> = new Map();
    for (const t of toks) {
        freq.set(t.text, (freq.get(t.text) || 0) + 1);
    }

    const counts: number[] = [];
    freq.forEach((count) => {
        counts.push(count);
    });

    const p50 = percentile(counts, 50);
    const p90 = percentile(counts, 90);
    const p99 = percentile(counts, 99);

    console.log('PERCENTILES');
    console.log(`50=${p50}\n90=${p90}\n99=${p99}`);
}

if (require.main === module) {
    main();
}

