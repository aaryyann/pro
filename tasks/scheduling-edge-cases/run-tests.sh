#!/bin/bash

cd "$(dirname "$0")/../.."
python3 -m pytest tasks/scheduling-edge-cases/task_tests.py -v

