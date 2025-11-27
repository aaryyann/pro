#!/bin/bash

cd "$(dirname "$0")/../.."
python3 -m pytest tasks/permission-security-check/task_tests.py -v

