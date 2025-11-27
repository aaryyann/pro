#!/bin/bash

cd "$(dirname "$0")/../.."
python3 -m pytest tasks/event-collection-validation/task_tests.py -v

