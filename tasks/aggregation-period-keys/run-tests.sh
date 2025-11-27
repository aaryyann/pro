#!/bin/bash

cd "$(dirname "$0")/../.."
python3 -m pytest tasks/aggregation-period-keys/task_tests.py -v

