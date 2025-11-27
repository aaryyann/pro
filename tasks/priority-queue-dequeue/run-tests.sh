#!/bin/bash

cd "$(dirname "$0")/../.."
python3 -m pytest tasks/priority-queue-dequeue/task_tests.py -v

