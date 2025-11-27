#!/bin/bash

cd "$(dirname "$0")/../.."
python3 -m pytest tasks/rbac-permission-check/task_tests.py -v

