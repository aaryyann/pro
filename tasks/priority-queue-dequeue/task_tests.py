import pytest
import sys
import os
import subprocess
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

def test_priority_queue_dequeue_highest_priority():
    """
    Test that dequeue returns the highest priority item first.
    """
    script = """
    const { PriorityQueue } = require('./dist/scheduler/PriorityQueue');
    
    const queue = new PriorityQueue();
    queue.enqueue('low', 1);
    queue.enqueue('high', 10);
    queue.enqueue('medium', 5);
    
    const first = queue.dequeue();
    const second = queue.dequeue();
    const third = queue.dequeue();
    
    console.log(JSON.stringify({
        first: first,
        second: second,
        third: third
    }));
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
        assert data['first'] == 'high'
        assert data['second'] == 'medium'
        assert data['third'] == 'low'

def test_priority_queue_dequeue_empty():
    """
    Test that dequeue returns null when queue is empty.
    """
    script = """
    const { PriorityQueue } = require('./dist/scheduler/PriorityQueue');
    
    const queue = new PriorityQueue();
    const first = queue.dequeue();
    const second = queue.dequeue();
    
    console.log(JSON.stringify({
        first: first,
        second: second
    }));
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
        assert data['first'] == None
        assert data['second'] == None

def test_priority_queue_peek_consistency():
    """
    Test that peek() returns the same item that dequeue() would return.
    """
    script = """
    const { PriorityQueue } = require('./dist/scheduler/PriorityQueue');
    
    const queue = new PriorityQueue();
    queue.enqueue('item1', 5);
    queue.enqueue('item2', 10);
    
    const peeked = queue.peek();
    const dequeued = queue.dequeue();
    
    console.log(JSON.stringify({
        peeked: peeked,
        dequeued: dequeued,
        match: peeked === dequeued
    }));
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
        assert data['match'] == True
        assert data['peeked'] == 'item2'

def test_priority_queue_multiple_same_priority():
    """
    Test that items with the same priority are handled correctly.
    """
    script = """
    const { PriorityQueue } = require('./dist/scheduler/PriorityQueue');
    
    const queue = new PriorityQueue();
    queue.enqueue('item1', 5);
    queue.enqueue('item2', 5);
    queue.enqueue('item3', 5);
    
    const first = queue.dequeue();
    const second = queue.dequeue();
    const third = queue.dequeue();
    
    console.log(JSON.stringify({
        dequeued: [first, second, third],
        allDequeued: first !== null && second !== null && third !== null
    }));
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
        assert data['allDequeued'] == True
        assert len(data['dequeued']) == 3

def test_priority_queue_negative_priorities():
    """
    Test that negative priorities work correctly.
    """
    script = """
    const { PriorityQueue } = require('./dist/scheduler/PriorityQueue');
    
    const queue = new PriorityQueue();
    queue.enqueue('low', -10);
    queue.enqueue('high', 10);
    queue.enqueue('medium', 0);
    
    const first = queue.dequeue();
    const second = queue.dequeue();
    const third = queue.dequeue();
    
    console.log(JSON.stringify({
        first: first,
        second: second,
        third: third
    }));
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
        assert data['first'] == 'high'
        assert data['second'] == 'medium'
        assert data['third'] == 'low'

def test_priority_queue_size_after_dequeue():
    """
    Test that queue size decreases correctly after dequeue operations.
    """
    script = """
    const { PriorityQueue } = require('./dist/scheduler/PriorityQueue');
    
    const queue = new PriorityQueue();
    queue.enqueue('item1', 1);
    queue.enqueue('item2', 2);
    queue.enqueue('item3', 3);
    
    const sizeBefore = queue.size();
    queue.dequeue();
    const sizeAfter = queue.size();
    
    console.log(JSON.stringify({
        sizeBefore: sizeBefore,
        sizeAfter: sizeAfter,
        correctDecrease: sizeBefore - sizeAfter === 1
    }));
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
        assert data['sizeBefore'] == 3
        assert data['sizeAfter'] == 2
        assert data['correctDecrease'] == True

def test_priority_queue_interleaved_operations():
    """
    Test interleaved enqueue and dequeue operations maintain correct priority order.
    """
    script = """
    const { PriorityQueue } = require('./dist/scheduler/PriorityQueue');
    
    const queue = new PriorityQueue();
    queue.enqueue('item1', 1);
    queue.enqueue('item2', 5);
    const first = queue.dequeue();
    queue.enqueue('item3', 10);
    queue.enqueue('item4', 3);
    const second = queue.dequeue();
    const third = queue.dequeue();
    
    console.log(JSON.stringify({
        first: first,
        second: second,
        third: third
    }));
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
        assert data['first'] == 'item2'
        assert data['second'] == 'item3'
        assert data['third'] == 'item4'

