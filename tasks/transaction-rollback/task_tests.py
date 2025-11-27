import pytest
import sys
import os
import subprocess
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

def test_rollback_pending_transaction():
    """
    Test that a PENDING transaction can be rolled back.
    """
    script = """
    const { TransactionManager, TransactionStatus } = require('../../dist/transaction/TransactionManager');
    
    const manager = new TransactionManager();
    const txn = manager.createTransaction('user1', 'admin');
    
    manager.addOperation(txn.id, { type: 'write', resource: 'data1', action: 'write', data: { value: 1 } });
    
    const rollbackResult = await manager.rollback(txn.id);
    const finalTxn = manager.getTransaction(txn.id);
    
    console.log(JSON.stringify({
        rollbackResult: rollbackResult,
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
        assert data['rollbackResult'] == True
        assert data['status'] == 'ROLLED_BACK'

def test_rollback_committed_transaction():
    """
    Test that a COMMITTED transaction can be rolled back.
    """
    script = """
    const { TransactionManager, TransactionStatus } = require('../../dist/transaction/TransactionManager');
    
    const manager = new TransactionManager();
    const txn = manager.createTransaction('user1', 'admin');
    
    manager.addOperation(txn.id, { type: 'write', resource: 'data1', action: 'write', data: { value: 1 } });
    await manager.commit(txn.id);
    
    const rollbackResult = await manager.rollback(txn.id);
    const finalTxn = manager.getTransaction(txn.id);
    
    console.log(JSON.stringify({
        rollbackResult: rollbackResult,
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
        assert data['rollbackResult'] == True
        assert data['status'] == 'ROLLED_BACK'

def test_rollback_failed_transaction():
    """
    Test that a FAILED transaction cannot be rolled back.
    """
    script = """
    const { TransactionManager } = require('../../dist/transaction/TransactionManager');
    
    const manager = new TransactionManager();
    const txn = manager.createTransaction('user1', 'admin');
    
    manager.addOperation(txn.id, { type: 'write', resource: 'data1', action: 'write', data: { value: 1 } });
    const txnAfterCreate = manager.getTransaction(txn.id);
    txnAfterCreate.status = 'FAILED';
    
    const rollbackResult = await manager.rollback(txn.id);
    const finalTxn = manager.getTransaction(txn.id);
    
    console.log(JSON.stringify({
        rollbackResult: rollbackResult,
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
        assert data['rollbackResult'] == False

def test_rollback_nonexistent_transaction():
    """
    Test that rolling back a non-existent transaction returns false.
    """
    script = """
    const { TransactionManager } = require('../../dist/transaction/TransactionManager');
    
    const manager = new TransactionManager();
    const rollbackResult = await manager.rollback('nonexistent_id');
    
    console.log(JSON.stringify({
        rollbackResult: rollbackResult
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
        assert data['rollbackResult'] == False

def test_rollback_pending_with_operations():
    """
    Test that rolling back a PENDING transaction with multiple operations works correctly.
    """
    script = """
    const { TransactionManager } = require('../../dist/transaction/TransactionManager');
    
    const manager = new TransactionManager();
    const txn = manager.createTransaction('user1', 'admin');
    
    manager.addOperation(txn.id, { type: 'write', resource: 'data1', action: 'write', data: { value: 1 } });
    manager.addOperation(txn.id, { type: 'write', resource: 'data2', action: 'write', data: { value: 2 } });
    manager.addOperation(txn.id, { type: 'write', resource: 'data3', action: 'write', data: { value: 3 } });
    
    const rollbackResult = await manager.rollback(txn.id);
    const finalTxn = manager.getTransaction(txn.id);
    
    console.log(JSON.stringify({
        rollbackResult: rollbackResult,
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
        assert data['rollbackResult'] == True
        assert data['status'] == 'ROLLED_BACK'
        assert data['operationCount'] == 3

def test_rollback_idempotency():
    """
    Test that rolling back an already rolled back transaction returns false.
    """
    script = """
    const { TransactionManager } = require('../../dist/transaction/TransactionManager');
    
    const manager = new TransactionManager();
    const txn = manager.createTransaction('user1', 'admin');
    
    manager.addOperation(txn.id, { type: 'write', resource: 'data1', action: 'write', data: { value: 1 } });
    const firstRollback = await manager.rollback(txn.id);
    const secondRollback = await manager.rollback(txn.id);
    const finalTxn = manager.getTransaction(txn.id);
    
    console.log(JSON.stringify({
        firstRollback: firstRollback,
        secondRollback: secondRollback,
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
        assert data['firstRollback'] == True
        assert data['secondRollback'] == False
        assert data['status'] == 'ROLLED_BACK'

def test_rollback_empty_pending_transaction():
    """
    Test that rolling back an empty PENDING transaction works correctly.
    """
    script = """
    const { TransactionManager } = require('../../dist/transaction/TransactionManager');
    
    const manager = new TransactionManager();
    const txn = manager.createTransaction('user1', 'admin');
    
    const rollbackResult = await manager.rollback(txn.id);
    const finalTxn = manager.getTransaction(txn.id);
    
    console.log(JSON.stringify({
        rollbackResult: rollbackResult,
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
        assert data['rollbackResult'] == True
        assert data['status'] == 'ROLLED_BACK'
        assert data['operationCount'] == 0
