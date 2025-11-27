#!/usr/bin/env python3
import sys
import re

def analyze_analytics_file(file_path):
    """Analyze AnalyticsEngine.ts for metrics collection patterns."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        return
    
    metric_records = len(re.findall(r'recordMetric', content))
    aggregation_calls = len(re.findall(r'\.aggregate\(', content))
    period_types = set()
    period_matches = re.findall(r"period:\s*['\"](hour|day|week)['\"]", content)
    period_types.update(period_matches)
    top_metric_queries = len(re.findall(r'getTopMetrics', content))
    
    print("ANALYTICS_STATS:")
    print(f"metric_records: {metric_records}")
    print(f"aggregation_calls: {aggregation_calls}")
    print(f"period_types: {', '.join(sorted(period_types))}")
    print(f"top_metric_queries: {top_metric_queries}")

def main():
    if len(sys.argv) < 2:
        print("Usage: analytics_analyzer.py <AnalyticsEngine.ts>")
        sys.exit(1)
    
    analyze_analytics_file(sys.argv[1])

if __name__ == "__main__":
    main()

