#!/bin/bash

cd "$(dirname "$0")/../.."
python3 -m pytest tasks/async-task-execution/task_tests.py -v

