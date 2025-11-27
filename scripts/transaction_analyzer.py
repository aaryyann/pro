#!/usr/bin/env python3
import sys
import re

def analyze_transaction_file(file_path):
    """Analyze TransactionManager.ts for transaction patterns."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        return
    
    transaction_creates = len(re.findall(r'createTransaction', content))
    commit_operations = len(re.findall(r'\.commit\(', content))
    rollback_operations = len(re.findall(r'\.rollback\(', content))
    role_checks = len(re.findall(r'hasPermission', content))
    
    print("TRANSACTION_STATS:")
    print(f"transaction_creates: {transaction_creates}")
    print(f"commit_operations: {commit_operations}")
    print(f"rollback_operations: {rollback_operations}")
    print(f"role_checks: {role_checks}")

def main():
    if len(sys.argv) < 2:
        print("Usage: transaction_analyzer.py <TransactionManager.ts>")
        sys.exit(1)
    
    analyze_transaction_file(sys.argv[1])

if __name__ == "__main__":
    main()

