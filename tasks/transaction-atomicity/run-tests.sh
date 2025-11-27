#!/bin/bash

cd "$(dirname "$0")/../.."
python3 -m pytest tasks/transaction-atomicity/task_tests.py -v

