import pytest
import sys
import os
import subprocess
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

def test_transaction_commit_success():
    """
    Test that a transaction with all successful operations commits correctly.
    """
    script = """
    const { TransactionManager, TransactionStatus } = require('./dist/transaction/TransactionManager');
    
    const manager = new TransactionManager();
    const txn = manager.createTransaction('user1', 'admin');
    
    manager.addOperation(txn.id, { type: 'write', resource: 'data1', action: 'write', data: { value: 1 } });
    manager.addOperation(txn.id, { type: 'write', resource: 'data2', action: 'write', data: { value: 2 } });
    
    const commitResult = await manager.commit(txn.id);
    const finalTxn = manager.getTransaction(txn.id);
    
    console.log(JSON.stringify({
        commitResult: commitResult,
        status: finalTxn.status,
        operationCount: finalTxn.operations.length
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
        assert data['commitResult'] == True
        assert data['status'] == 'COMMITTED'

def test_transaction_commit_with_multiple_operations():
    """
    Test that a transaction with multiple operations commits atomically.
    """
    script = """
    const { TransactionManager, TransactionStatus } = require('./dist/transaction/TransactionManager');
    
    const manager = new TransactionManager();
    const txn = manager.createTransaction('user1', 'admin');
    
    manager.addOperation(txn.id, { type: 'write', resource: 'data1', action: 'write', data: { value: 1 } });
    manager.addOperation(txn.id, { type: 'write', resource: 'data2', action: 'write', data: { value: 2 } });
    manager.addOperation(txn.id, { type: 'write', resource: 'data3', action: 'write', data: { value: 3 } });
    
    const commitResult = await manager.commit(txn.id);
    const finalTxn = manager.getTransaction(txn.id);
    
    console.log(JSON.stringify({
        commitResult: commitResult,
        status: finalTxn.status,
        operationCount: finalTxn.operations.length
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
        assert data['commitResult'] == True
        assert data['status'] == 'COMMITTED'
        assert data['operationCount'] == 3

def test_transaction_empty_operations():
    """
    Test that a transaction with no operations can be committed.
    """
    script = """
    const { TransactionManager } = require('./dist/transaction/TransactionManager');
    
    const manager = new TransactionManager();
    const txn = manager.createTransaction('user1', 'admin');
    
    const commitResult = await manager.commit(txn.id);
    const finalTxn = manager.getTransaction(txn.id);
    
    console.log(JSON.stringify({
        commitResult: commitResult,
        status: finalTxn.status,
        operationCount: finalTxn.operations.length
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
        assert data['commitResult'] == True
        assert data['status'] == 'COMMITTED'
        assert data['operationCount'] == 0

def test_transaction_operation_order():
    """
    Test that operations execute in the order they were added.
    """
    script = """
    const { TransactionManager } = require('./dist/transaction/TransactionManager');
    
    const manager = new TransactionManager();
    const txn = manager.createTransaction('user1', 'admin');
    const executionOrder = [];
    
    manager.addOperation(txn.id, { 
        type: 'write', 
        resource: 'data1', 
        action: 'write', 
        data: { order: 1 } 
    });
    manager.addOperation(txn.id, { 
        type: 'write', 
        resource: 'data2', 
        action: 'write', 
        data: { order: 2 } 
    });
    manager.addOperation(txn.id, { 
        type: 'write', 
        resource: 'data3', 
        action: 'write', 
        data: { order: 3 } 
    });
    
    const commitResult = await manager.commit(txn.id);
    const finalTxn = manager.getTransaction(txn.id);
    
    console.log(JSON.stringify({
        commitResult: commitResult,
        status: finalTxn.status,
        operations: finalTxn.operations.map(op => op.data.order)
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
        assert data['commitResult'] == True
        assert data['operations'] == [1, 2, 3]

def test_transaction_commit_idempotency():
    """
    Test that committing an already committed transaction returns false.
    """
    script = """
    const { TransactionManager } = require('./dist/transaction/TransactionManager');
    
    const manager = new TransactionManager();
    const txn = manager.createTransaction('user1', 'admin');
    
    manager.addOperation(txn.id, { type: 'write', resource: 'data1', action: 'write', data: { value: 1 } });
    const firstCommit = await manager.commit(txn.id);
    const secondCommit = await manager.commit(txn.id);
    const finalTxn = manager.getTransaction(txn.id);
    
    console.log(JSON.stringify({
        firstCommit: firstCommit,
        secondCommit: secondCommit,
        status: finalTxn.status
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
        assert data['firstCommit'] == True
        assert data['secondCommit'] == False
        assert data['status'] == 'COMMITTED'

def test_transaction_large_number_operations():
    """
    Test that transactions with many operations commit correctly.
    """
    script = """
    const { TransactionManager } = require('./dist/transaction/TransactionManager');
    
    const manager = new TransactionManager();
    const txn = manager.createTransaction('user1', 'admin');
    
    for (let i = 0; i < 10; i++) {
        manager.addOperation(txn.id, { 
            type: 'write', 
            resource: `data${i}`, 
            action: 'write', 
            data: { value: i } 
        });
    }
    
    const commitResult = await manager.commit(txn.id);
    const finalTxn = manager.getTransaction(txn.id);
    
    console.log(JSON.stringify({
        commitResult: commitResult,
        status: finalTxn.status,
        operationCount: finalTxn.operations.length
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
        assert data['commitResult'] == True
        assert data['status'] == 'COMMITTED'
        assert data['operationCount'] == 10

def test_transaction_nonexistent_id():
    """
    Test that committing a non-existent transaction returns false.
    """
    script = """
    const { TransactionManager } = require('./dist/transaction/TransactionManager');
    
    const manager = new TransactionManager();
    const commitResult = await manager.commit('nonexistent_id');
    
    console.log(JSON.stringify({
        commitResult: commitResult
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
        assert data['commitResult'] == False

