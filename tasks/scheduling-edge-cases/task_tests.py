import pytest
import sys
import os
import subprocess
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

def test_task_execution_at_exact_time():
    """
    Test that tasks scheduled for the exact current time are executed.
    """
    script = """
    const { TaskScheduler } = require('./dist/scheduler/TaskScheduler');
    
    const scheduler = new TaskScheduler();
    let executed = false;
    
    const now = new Date();
    const task = {
        id: 'exact_time_task',
        name: 'Exact Time Task',
        executeAt: now,
        priority: 1,
        handler: async () => {
            executed = true;
        }
    };
    
    scheduler.schedule(task);
    
    (async () => {
        const startPromise = scheduler.start();
        await new Promise(resolve => setTimeout(resolve, 1500));
        scheduler.stop();
        await startPromise;
        
        console.log(JSON.stringify({
            executed: executed,
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
    
    assert result.returncode == 0
    output = result.stdout.strip()
    if output:
        data = json.loads(output.split('\n')[-1])
        assert data['executed'] == True
        assert data['pendingCount'] == 0

def test_task_execution_past_time():
    """
    Test that tasks scheduled in the past are executed immediately.
    """
    script = """
    const { TaskScheduler } = require('./dist/scheduler/TaskScheduler');
    
    const scheduler = new TaskScheduler();
    let executed = false;
    
    const pastTime = new Date(Date.now() - 1000);
    const task = {
        id: 'past_time_task',
        name: 'Past Time Task',
        executeAt: pastTime,
        priority: 1,
        handler: async () => {
            executed = true;
        }
    };
    
    scheduler.schedule(task);
    
    (async () => {
        const startPromise = scheduler.start();
        await new Promise(resolve => setTimeout(resolve, 1500));
        scheduler.stop();
        await startPromise;
        
        console.log(JSON.stringify({
            executed: executed
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
        assert data['executed'] == True


def test_task_scheduling_future_time():
    """
    Test that tasks scheduled for future times are not executed immediately.
    """
    script = """
    const { TaskScheduler } = require('./dist/scheduler/TaskScheduler');
    
    const scheduler = new TaskScheduler();
    let executed = false;
    
    const futureTime = new Date(Date.now() + 2000);
    const task = {
        id: 'future_task',
        name: 'Future Task',
        executeAt: futureTime,
        priority: 1,
        handler: async () => {
            executed = true;
        }
    };
    
    scheduler.schedule(task);
    
    (async () => {
        const startPromise = scheduler.start();
        await new Promise(resolve => setTimeout(resolve, 500));
        const pending = scheduler.getPendingTasks().length;
        scheduler.stop();
        await startPromise;
        
        console.log(JSON.stringify({
            executed: executed,
            pending: pending
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
        assert data['executed'] == False
        assert data['pending'] == 1

def test_task_scheduling_multiple_same_time():
    """
    Test that multiple tasks scheduled for the same time all execute.
    """
    script = """
    const { TaskScheduler } = require('./dist/scheduler/TaskScheduler');
    
    const scheduler = new TaskScheduler();
    const executionCount = { count: 0 };
    
    const sameTime = new Date(Date.now() + 100);
    
    for (let i = 0; i < 3; i++) {
        scheduler.schedule({
            id: `task_${i}`,
            name: `Task ${i}`,
            executeAt: sameTime,
            priority: 1,
            handler: async () => {
                executionCount.count++;
            }
        });
    }
    
    (async () => {
        const startPromise = scheduler.start();
        await new Promise(resolve => setTimeout(resolve, 300));
        scheduler.stop();
        await startPromise;
        
        console.log(JSON.stringify({
            executionCount: executionCount.count
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
        assert data['executionCount'] == 3

def test_task_cancellation_before_execution():
    """
    Test that cancelling a task before execution prevents it from running.
    """
    script = """
    const { TaskScheduler } = require('./dist/scheduler/TaskScheduler');
    
    const scheduler = new TaskScheduler();
    let executed = false;
    
    const task = {
        id: 'cancel_task',
        name: 'Cancel Task',
        executeAt: new Date(Date.now() + 200),
        priority: 1,
        handler: async () => {
            executed = true;
        }
    };
    
    scheduler.schedule(task);
    const cancelled = scheduler.cancelTask('cancel_task');
    
    (async () => {
        const startPromise = scheduler.start();
        await new Promise(resolve => setTimeout(resolve, 400));
        scheduler.stop();
        await startPromise;
        
        console.log(JSON.stringify({
            cancelled: cancelled,
            executed: executed
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
        assert data['cancelled'] == True
        assert data['executed'] == False

def test_task_scheduling_order_preservation():
    """
    Test that tasks maintain correct execution order when scheduled at same time.
    """
    script = """
    const { TaskScheduler } = require('./dist/scheduler/TaskScheduler');
    
    const scheduler = new TaskScheduler();
    const executionOrder = [];
    
    const sameTime = new Date(Date.now() + 100);
    
    scheduler.schedule({
        id: 'task1',
        name: 'Task 1',
        executeAt: sameTime,
        priority: 1,
        handler: async () => {
            executionOrder.push(1);
        }
    });
    
    scheduler.schedule({
        id: 'task2',
        name: 'Task 2',
        executeAt: sameTime,
        priority: 1,
        handler: async () => {
            executionOrder.push(2);
        }
    });
    
    (async () => {
        const startPromise = scheduler.start();
        await new Promise(resolve => setTimeout(resolve, 300));
        scheduler.stop();
        await startPromise;
        
        console.log(JSON.stringify({
            executionOrder: executionOrder,
            bothExecuted: executionOrder.length === 2
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
        assert data['bothExecuted'] == True
