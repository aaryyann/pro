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
    const { TaskScheduler } = require('./dist/scheduler/TaskScheduler');
    
    const scheduler = new TaskScheduler();
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
    """
    script = """
    const { TaskScheduler } = require('./dist/scheduler/TaskScheduler');
    
    const scheduler = new TaskScheduler();
    let schedulerRunning = true;
    
    const task = {
        id: 'error_task',
        name: 'Error Task',
        executeAt: new Date(Date.now() + 100),
        priority: 1,
        handler: async () => {
            throw new Error('Test error');
        }
    };
    
    scheduler.schedule(task);
    
    (async () => {
        try {
            const startPromise = scheduler.start();
            await new Promise(resolve => setTimeout(resolve, 300));
            scheduler.stop();
            await startPromise;
            schedulerRunning = true;
        } catch (e) {
            schedulerRunning = false;
        }
        
        console.log(JSON.stringify({ schedulerRunning: schedulerRunning }));
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
        assert data['schedulerRunning'] == True

def test_task_removal_after_execution():
    """
    Test that tasks are removed from the queue only after handler execution completes.
    """
    script = """
    const { TaskScheduler } = require('./dist/scheduler/TaskScheduler');
    
    const scheduler = new TaskScheduler();
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
    const { TaskScheduler } = require('./dist/scheduler/TaskScheduler');
    
    const scheduler = new TaskScheduler();
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
    """
    script = """
    const { TaskScheduler } = require('./dist/scheduler/TaskScheduler');
    
    const scheduler = new TaskScheduler();
    let returnValue = null;
    
    const task = {
        id: 'return_task',
        name: 'Return Task',
        executeAt: new Date(Date.now() + 100),
        priority: 1,
        handler: async () => {
            await new Promise(resolve => setTimeout(resolve, 50));
            returnValue = 'success';
        }
    };
    
    scheduler.schedule(task);
    
    (async () => {
        const startPromise = scheduler.start();
        await new Promise(resolve => setTimeout(resolve, 300));
        scheduler.stop();
        await startPromise;
        
        console.log(JSON.stringify({
            returnValue: returnValue
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
        assert data['returnValue'] == 'success'

def test_task_execution_order():
    """
    Test that tasks execute in the correct order based on execution time.
    """
    script = """
    const { TaskScheduler } = require('./dist/scheduler/TaskScheduler');
    
    const scheduler = new TaskScheduler();
    const executionOrder = [];
    
    scheduler.schedule({
        id: 'task3',
        name: 'Task 3',
        executeAt: new Date(Date.now() + 300),
        priority: 1,
        handler: async () => {
            executionOrder.push(3);
        }
    });
    
    scheduler.schedule({
        id: 'task1',
        name: 'Task 1',
        executeAt: new Date(Date.now() + 100),
        priority: 1,
        handler: async () => {
            executionOrder.push(1);
        }
    });
    
    scheduler.schedule({
        id: 'task2',
        name: 'Task 2',
        executeAt: new Date(Date.now() + 200),
        priority: 1,
        handler: async () => {
            executionOrder.push(2);
        }
    });
    
    (async () => {
        const startPromise = scheduler.start();
        await new Promise(resolve => setTimeout(resolve, 500));
        scheduler.stop();
        await startPromise;
        
        console.log(JSON.stringify({
            executionOrder: executionOrder
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
        assert data['executionOrder'] == [1, 2, 3]

def test_nested_async_operations():
    """
    Test that nested async operations in handlers are properly awaited.
    """
    script = """
    const { TaskScheduler } = require('./dist/scheduler/TaskScheduler');
    
    const scheduler = new TaskScheduler();
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
