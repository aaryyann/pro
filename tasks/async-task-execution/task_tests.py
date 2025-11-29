import pytest
import sys
import os
import time
import subprocess
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

def test_task_handler_execution():
    """
    Test that scheduled task handlers are properly executed and awaited.
    Verifies that handlers complete before tasks are removed from queue.
    """
    script = """
    const { AsyncTaskScheduler } = require('./dist/scheduler/AsyncTaskScheduler');
    
    const scheduler = new AsyncTaskScheduler();
    const executionOrder = [];
    let handler1Completed = false;
    let handler2Completed = false;
    
    const task1 = {
        id: 'task1',
        name: 'Test Task 1',
        executeAt: new Date(Date.now() + 100),
        priority: 1,
        handler: async () => {
            await new Promise(resolve => setTimeout(resolve, 50));
            executionOrder.push('task1');
            handler1Completed = true;
        }
    };
    
    const task2 = {
        id: 'task2',
        name: 'Test Task 2',
        executeAt: new Date(Date.now() + 100),
        priority: 2,
        handler: async () => {
            await new Promise(resolve => setTimeout(resolve, 50));
            executionOrder.push('task2');
            handler2Completed = true;
        }
    };
    
    scheduler.schedule(task1);
    scheduler.schedule(task2);
    
    (async () => {
        const startPromise = scheduler.start();
        await new Promise(resolve => setTimeout(resolve, 300));
        scheduler.stop();
        await startPromise;
        
        console.log(JSON.stringify({
            executionOrder: executionOrder,
            handler1Completed: handler1Completed,
            handler2Completed: handler2Completed,
            pendingCount: scheduler.getPendingTasks().length
        }));
    })();
    """
    
    result = subprocess.run(
        ['node', '-e', script],
        capture_output=True,
        text=True,
        timeout=5,
        cwd=os.path.join(os.path.dirname(__file__), '../..')
    )
    
    assert result.returncode == 0, f"Script failed: {result.stderr}"
    output = result.stdout.strip()
    if output:
        data = json.loads(output.split('\n')[-1])
        assert len(data['executionOrder']) == 2
        assert data['handler1Completed'] == True
        assert data['handler2Completed'] == True
        assert data['pendingCount'] == 0

def test_task_handler_error_handling():
    """
    Test that errors in task handlers are properly caught and don't crash the scheduler.
    Scheduler must continue processing other tasks even after one fails.
    """
    script = """
    const { AsyncTaskScheduler } = require('./dist/scheduler/AsyncTaskScheduler');
    
    const scheduler = new AsyncTaskScheduler();
    let schedulerRunning = true;
    let errorTaskExecuted = false;
    let successTaskExecuted = false;
    
    const errorTask = {
        id: 'error_task',
        name: 'Error Task',
        executeAt: new Date(Date.now() + 100),
        priority: 1,
        handler: async () => {
            errorTaskExecuted = true;
            throw new Error('Test error');
        }
    };
    
    const successTask = {
        id: 'success_task',
        name: 'Success Task',
        executeAt: new Date(Date.now() + 150),
        priority: 1,
        handler: async () => {
            await new Promise(resolve => setTimeout(resolve, 50));
            successTaskExecuted = true;
        }
    };
    
    scheduler.schedule(errorTask);
    scheduler.schedule(successTask);
    
    (async () => {
        try {
            const startPromise = scheduler.start();
            await new Promise(resolve => setTimeout(resolve, 400));
            scheduler.stop();
            await startPromise;
            schedulerRunning = true;
        } catch (e) {
            schedulerRunning = false;
        }
        
        console.log(JSON.stringify({ 
            schedulerRunning: schedulerRunning,
            errorTaskExecuted: errorTaskExecuted,
            successTaskExecuted: successTaskExecuted,
            bothTasksProcessed: errorTaskExecuted && successTaskExecuted
        }));
    })();
    """
    
    result = subprocess.run(
        ['node', '-e', script],
        capture_output=True,
        text=True,
        timeout=5,
        cwd=os.path.join(os.path.dirname(__file__), '../..')
    )
    
    assert result.returncode == 0
    output = result.stdout.strip()
    if output:
        data = json.loads(output.split('\n')[-1])
        assert data['schedulerRunning'] == True, "Scheduler must continue running after error"
        assert data['errorTaskExecuted'] == True, "Error task must be executed"
        assert data['successTaskExecuted'] == True, "Success task must execute even after error task fails"
        assert data['bothTasksProcessed'] == True, "Both tasks must be processed - scheduler should not stop on error"

def test_task_removal_after_execution():
    """
    Test that tasks are removed from the queue only after handler execution completes.
    """
    script = """
    const { AsyncTaskScheduler } = require('./dist/scheduler/AsyncTaskScheduler');
    
    const scheduler = new AsyncTaskScheduler();
    let handlerCompleted = false;
    
    const task = {
        id: 'completion_task',
        name: 'Completion Task',
        executeAt: new Date(Date.now() + 100),
        priority: 1,
        handler: async () => {
            await new Promise(resolve => setTimeout(resolve, 200));
            handlerCompleted = true;
        }
    };
    
    scheduler.schedule(task);
    
    (async () => {
        const startPromise = scheduler.start();
        await new Promise(resolve => setTimeout(resolve, 50));
        const pendingBefore = scheduler.getPendingTasks().length;
        await new Promise(resolve => setTimeout(resolve, 300));
        const pendingAfter = scheduler.getPendingTasks().length;
        scheduler.stop();
        await startPromise;
        
        console.log(JSON.stringify({
            pendingBefore: pendingBefore,
            pendingAfter: pendingAfter,
            handlerCompleted: handlerCompleted
        }));
    })();
    """
    
    result = subprocess.run(
        ['node', '-e', script],
        capture_output=True,
        text=True,
        timeout=5,
        cwd=os.path.join(os.path.dirname(__file__), '../..')
    )
    
    assert result.returncode == 0
    output = result.stdout.strip()
    if output:
        data = json.loads(output.split('\n')[-1])
        assert data['pendingBefore'] > 0
        assert data['handlerCompleted'] == True
        assert data['pendingAfter'] == 0

def test_concurrent_task_execution():
    """
    Test that multiple concurrent tasks execute correctly with proper await handling.
    """
    script = """
    const { AsyncTaskScheduler } = require('./dist/scheduler/AsyncTaskScheduler');
    
    const scheduler = new AsyncTaskScheduler();
    const executionResults = [];
    
    for (let i = 0; i < 5; i++) {
        scheduler.schedule({
            id: `task_${i}`,
            name: `Task ${i}`,
            executeAt: new Date(Date.now() + 100),
            priority: i,
            handler: async () => {
                await new Promise(resolve => setTimeout(resolve, 50));
                executionResults.push(i);
            }
        });
    }
    
    (async () => {
        const startPromise = scheduler.start();
        await new Promise(resolve => setTimeout(resolve, 500));
        scheduler.stop();
        await startPromise;
        
        console.log(JSON.stringify({
            executionCount: executionResults.length,
            results: executionResults.sort((a, b) => a - b)
        }));
    })();
    """
    
    result = subprocess.run(
        ['node', '-e', script],
        capture_output=True,
        text=True,
        timeout=5,
        cwd=os.path.join(os.path.dirname(__file__), '../..')
    )
    
    assert result.returncode == 0
    output = result.stdout.strip()
    if output:
        data = json.loads(output.split('\n')[-1])
        assert data['executionCount'] == 5
        assert data['results'] == [0, 1, 2, 3, 4]

def test_task_handler_return_value():
    """
    Test that task handlers can return values and these are properly handled.
    Also verifies handler completes before task is removed.
    """
    script = """
    const { AsyncTaskScheduler } = require('./dist/scheduler/AsyncTaskScheduler');
    
    const scheduler = new AsyncTaskScheduler();
    let returnValue = null;
    let handlerStarted = false;
    let handlerCompleted = false;
    let taskRemovedBeforeCompletion = false;
    
    const task = {
        id: 'return_task',
        name: 'Return Task',
        executeAt: new Date(Date.now() + 100),
        priority: 1,
        handler: async () => {
            handlerStarted = true;
            await new Promise(resolve => setTimeout(resolve, 150));
            returnValue = 'success';
            handlerCompleted = true;
        }
    };
    
    scheduler.schedule(task);
    
    (async () => {
        const startPromise = scheduler.start();
        await new Promise(resolve => setTimeout(resolve, 120));
        const pendingBefore = scheduler.getPendingTasks().length;
        if (pendingBefore === 0 && !handlerCompleted) {
            taskRemovedBeforeCompletion = true;
        }
        await new Promise(resolve => setTimeout(resolve, 200));
        scheduler.stop();
        await startPromise;
        
        console.log(JSON.stringify({
            returnValue: returnValue,
            handlerStarted: handlerStarted,
            handlerCompleted: handlerCompleted,
            taskRemovedBeforeCompletion: taskRemovedBeforeCompletion,
            pendingAfter: scheduler.getPendingTasks().length
        }));
    })();
    """
    
    result = subprocess.run(
        ['node', '-e', script],
        capture_output=True,
        text=True,
        timeout=5,
        cwd=os.path.join(os.path.dirname(__file__), '../..')
    )
    
    assert result.returncode == 0
    output = result.stdout.strip()
    if output:
        data = json.loads(output.split('\n')[-1])
        assert data['returnValue'] == 'success', f"Handler must complete and set return value. Got: {data['returnValue']}"
        assert data['handlerCompleted'] == True, "Handler must complete execution"
        assert data['taskRemovedBeforeCompletion'] == False, "Task must not be removed before handler completes"
        assert data['pendingAfter'] == 0, "Task must be removed after handler completes"

def test_task_execution_order():
    """
    Test that tasks execute in the correct order based on execution time.
    Tasks scheduled for exact current time should also execute.
    """
    script = """
    const { AsyncTaskScheduler } = require('./dist/scheduler/AsyncTaskScheduler');
    
    const scheduler = new AsyncTaskScheduler();
    const executionOrder = [];
    const now = Date.now();
    
    scheduler.schedule({
        id: 'task3',
        name: 'Task 3',
        executeAt: new Date(now + 300),
        priority: 1,
        handler: async () => {
            await new Promise(resolve => setTimeout(resolve, 10));
            executionOrder.push(3);
        }
    });
    
    scheduler.schedule({
        id: 'task1',
        name: 'Task 1',
        executeAt: new Date(now + 100),
        priority: 1,
        handler: async () => {
            await new Promise(resolve => setTimeout(resolve, 10));
            executionOrder.push(1);
        }
    });
    
    scheduler.schedule({
        id: 'task0',
        name: 'Task 0',
        executeAt: new Date(now),
        priority: 1,
        handler: async () => {
            await new Promise(resolve => setTimeout(resolve, 10));
            executionOrder.push(0);
        }
    });
    
    scheduler.schedule({
        id: 'task2',
        name: 'Task 2',
        executeAt: new Date(now + 200),
        priority: 1,
        handler: async () => {
            await new Promise(resolve => setTimeout(resolve, 10));
            executionOrder.push(2);
        }
    });
    
    (async () => {
        const startPromise = scheduler.start();
        await new Promise(resolve => setTimeout(resolve, 500));
        scheduler.stop();
        await startPromise;
        
        console.log(JSON.stringify({
            executionOrder: executionOrder,
            expectedOrder: [0, 1, 2, 3],
            isCorrect: JSON.stringify(executionOrder) === JSON.stringify([0, 1, 2, 3])
        }));
    })();
    """
    
    result = subprocess.run(
        ['node', '-e', script],
        capture_output=True,
        text=True,
        timeout=5,
        cwd=os.path.join(os.path.dirname(__file__), '../..')
    )
    
    assert result.returncode == 0
    output = result.stdout.strip()
    if output:
        data = json.loads(output.split('\n')[-1])
        assert data['isCorrect'] == True, f"Tasks must execute in order. Expected [0, 1, 2, 3], got {data['executionOrder']}"
        assert len(data['executionOrder']) == 4, f"All 4 tasks must execute. Got {len(data['executionOrder'])}"

def test_nested_async_operations():
    """
    Test that nested async operations in handlers are properly awaited.
    """
    script = """
    const { AsyncTaskScheduler } = require('./dist/scheduler/AsyncTaskScheduler');
    
    const scheduler = new AsyncTaskScheduler();
    let nestedCompleted = false;
    
    const task = {
        id: 'nested_task',
        name: 'Nested Task',
        executeAt: new Date(Date.now() + 100),
        priority: 1,
        handler: async () => {
            await new Promise(resolve => setTimeout(resolve, 50));
            await new Promise(async (resolve) => {
                await new Promise(r => setTimeout(r, 50));
                nestedCompleted = true;
                resolve();
            });
        }
    };
    
    scheduler.schedule(task);
    
    (async () => {
        const startPromise = scheduler.start();
        await new Promise(resolve => setTimeout(resolve, 300));
        scheduler.stop();
        await startPromise;
        
        console.log(JSON.stringify({
            nestedCompleted: nestedCompleted
        }));
    })();
    """
    
    result = subprocess.run(
        ['node', '-e', script],
        capture_output=True,
        text=True,
        timeout=5,
        cwd=os.path.join(os.path.dirname(__file__), '../..')
    )
    
    assert result.returncode == 0
    output = result.stdout.strip()
    if output:
        data = json.loads(output.split('\n')[-1])
        assert data['nestedCompleted'] == True

def test_scheduler_polling_frequency():
    """
    Test that the scheduler checks for ready tasks more frequently (reduced sleep interval).
    Verifies that tasks are picked up quickly after their execution time, indicating frequent polling.
    """
    script = """
    const { AsyncTaskScheduler } = require('./dist/scheduler/AsyncTaskScheduler');
    
    const scheduler = new AsyncTaskScheduler();
    let taskExecuted = false;
    let executionTime = null;
    const scheduledTime = Date.now() + 150;
    
    const task = {
        id: 'polling_test_task',
        name: 'Polling Test Task',
        executeAt: new Date(scheduledTime),
        priority: 1,
        handler: async () => {
            executionTime = Date.now();
            taskExecuted = true;
        }
    };
    
    scheduler.schedule(task);
    
    (async () => {
        const startPromise = scheduler.start();
        await new Promise(resolve => setTimeout(resolve, 400));
        scheduler.stop();
        await startPromise;
        
        const delay = executionTime ? executionTime - scheduledTime : null;
        const maxAcceptableDelay = 200;
        const pollingFrequent = delay !== null && delay <= maxAcceptableDelay;
        
        console.log(JSON.stringify({
            taskExecuted: taskExecuted,
            scheduledTime: scheduledTime,
            executionTime: executionTime,
            delay: delay,
            maxAcceptableDelay: maxAcceptableDelay,
            pollingFrequent: pollingFrequent
        }));
    })();
    """
    
    result = subprocess.run(
        ['node', '-e', script],
        capture_output=True,
        text=True,
        timeout=5,
        cwd=os.path.join(os.path.dirname(__file__), '../..')
    )
    
    assert result.returncode == 0
    output = result.stdout.strip()
    if output:
        data = json.loads(output.split('\n')[-1])
        assert data['taskExecuted'] == True, "Task must be executed"
        assert data['pollingFrequent'] == True, f"Scheduler must check frequently. Task executed with delay of {data['delay']}ms, but should be <= {data['maxAcceptableDelay']}ms. This indicates the sleep interval is too long."
        assert data['delay'] is not None, "Execution time must be recorded"
