#!/bin/bash

cd "$(dirname "$0")/../.."

# Install dependencies with pinned versions
npm ci

# Build TypeScript
npm run build

# Run tests
python3 -m pytest tasks/event-collection-validation/task_tests.py -v

