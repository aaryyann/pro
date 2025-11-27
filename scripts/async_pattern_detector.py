#!/usr/bin/env python3
import sys
import re

def detect_async_patterns(file_path):
    """Detect async/await patterns in TypeScript files."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        return
    
    async_functions = len(re.findall(r'async\s+(?:function\s+\w+|\([^)]*\)\s*=>)', content))
    await_calls = len(re.findall(r'\bawait\s+', content))
    promise_returns = len(re.findall(r':\s*Promise<', content))
    unhandled_promises = max(0, promise_returns - await_calls)
    
    print("ASYNC_PATTERNS:")
    print(f"async_functions: {async_functions}")
    print(f"await_calls: {await_calls}")
    print(f"promise_returns: {promise_returns}")
    print(f"potential_unhandled: {unhandled_promises}")

def main():
    if len(sys.argv) < 2:
        print("Usage: async_pattern_detector.py <typescript_file>")
        sys.exit(1)
    
    detect_async_patterns(sys.argv[1])

if __name__ == "__main__":
    main()

