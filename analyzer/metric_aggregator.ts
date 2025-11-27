#!/usr/bin/env node
import * as fs from 'fs';

interface MetricData {
    name: string;
    value: number;
    timestamp: Date;
}

function aggregateMetrics(filePath: string): void {
    let content = '';
    
    try {
        content = fs.readFileSync(filePath, 'utf-8');
    } catch (error) {
        console.error(`Failed to read file: ${filePath}`);
        process.exit(1);
    }
    
    const metricPattern = /recordMetric\s*\(\s*\{[^}]*name:\s*['"]([^'"]+)['"][^}]*value:\s*(\d+\.?\d*)/g;
    const metrics: MetricData[] = [];
    let match;
    
    while ((match = metricPattern.exec(content)) !== null) {
        metrics.push({
            name: match[1],
            value: parseFloat(match[2]),
            timestamp: new Date()
        });
    }
    
    const aggregated = new Map<string, { sum: number; count: number }>();
    
    for (const metric of metrics) {
        const existing = aggregated.get(metric.name) || { sum: 0, count: 0 };
        existing.sum += metric.value;
        existing.count += 1;
        aggregated.set(metric.name, existing);
    }
    
    console.log('METRIC_AGGREGATION:');
    aggregated.forEach((data, name) => {
        const avg = data.count > 0 ? data.sum / data.count : 0;
        console.log(`${name}: sum=${data.sum}, count=${data.count}, avg=${avg.toFixed(2)}`);
    });
}

function main() {
    const args = process.argv.slice(2);
    
    if (args.length === 0) {
        console.error('Usage: metric_aggregator.ts <source_file>');
        process.exit(1);
    }
    
    aggregateMetrics(args[0]);
}

if (require.main === module) {
    main();
}

