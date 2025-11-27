#!/usr/bin/env python3
import sys
import re

def analyze_scheduler_file(file_path):
    """Analyze TaskScheduler.ts for task scheduling patterns."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        return
    
    tasks_scheduled = len(re.findall(r'\.schedule\(', content))
    async_handlers = len(re.findall(r'handler:\s*\(\)\s*=>\s*Promise', content))
    priority_usage = len(re.findall(r'priority', content))
    cancel_operations = len(re.findall(r'cancelTask', content))
    
    print("SCHEDULER_STATS:")
    print(f"tasks_scheduled: {tasks_scheduled}")
    print(f"async_handlers: {async_handlers}")
    print(f"priority_usage: {priority_usage}")
    print(f"cancel_operations: {cancel_operations}")

def main():
    if len(sys.argv) < 2:
        print("Usage: scheduler_analyzer.py <TaskScheduler.ts>")
        sys.exit(1)
    
    analyze_scheduler_file(sys.argv[1])

if __name__ == "__main__":
    main()

