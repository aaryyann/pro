#!/bin/bash

if [ -z "$1" ]; then
    echo "Usage: ./run_tests.sh [task-id]"
    echo "Example: ./run_tests.sh async-task-execution"
    exit 1
fi

TASK_ID=$1
TASK_DIR="tasks/${TASK_ID}"

if [ ! -d "$TASK_DIR" ]; then
    echo "Error: Task directory $TASK_DIR does not exist"
    exit 1
fi

cd "$(dirname "$0")"

if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install
fi

echo "Building TypeScript..."
npm run build

echo "Running tests for $TASK_ID..."
python3 -m pytest "$TASK_DIR/task_tests.py" -v

