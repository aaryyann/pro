#!/bin/bash

cd "$(dirname "$0")/../.."
python3 -m pytest tasks/metric-time-filtering/task_tests.py -v

