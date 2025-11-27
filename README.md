# ProjectZ Base Repository

A systematic base repository with three core systems: Scheduler, Multi-role Transaction, and Analytics.

## Systems

1. **Scheduler System** - Task scheduling and execution
2. **Multi-role Transaction System** - Role-based transaction management
3. **Analytics Base System** - Metrics collection and aggregation

## Project Structure

```
.
├── src/
│   ├── scheduler/
│   │   ├── TaskScheduler.ts
│   │   └── PriorityQueue.ts
│   ├── transaction/
│   │   ├── TransactionManager.ts
│   │   └── RoleBasedAccessControl.ts
│   ├── analytics/
│   │   ├── AnalyticsEngine.ts
│   │   └── EventCollector.ts
│   └── index.ts
├── tasks/
│   ├── async-task-execution/
│   ├── priority-queue-dequeue/
│   ├── transaction-atomicity/
│   └── ...
└── package.json
```

## Setup

```bash
npm install
npm run build
```

## Tasks

Each task folder contains:
- `task_description.txt` - Description of the bug to fix
- `task_tests.py` - Python pytest tests
- `task_diff.txt` - Git diff after fixing bugs (generated)
- `run_tests.sh` - Script to run tests
- `docker-compose.yaml` - Docker test environment

## Running Tests

```bash
cd tasks/async-task-execution
./run-tests.sh
```

Or from root:
```bash
./run_tests.sh async-task-execution
```

Or run all tests:
```bash
python3 -m pytest tasks/ -v
```

## Workflow

1. Initial commit contains buggy code (90%+ failure rate)
2. Fix bugs to achieve 0% failure rate
3. Generate task_diff.txt: `git diff -- . ':!tasks/' > tasks/<task-id>/task_diff.txt`

