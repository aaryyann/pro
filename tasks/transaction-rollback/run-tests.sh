#!/bin/bash

cd "$(dirname "$0")/../.."
python3 -m pytest tasks/transaction-rollback/task_tests.py -v

