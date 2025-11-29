import pytest
import sys
import os
import subprocess
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

def test_unknown_role_permission_denied():
    """
    Test that unknown roles are denied all permissions.
    """
    script = """
    const { TransactionManager } = require('./dist/transaction/TransactionManager');
    
    const manager = new TransactionManager();
    const txn = manager.createTransaction('user1', 'unknown_role');
    
    const result = manager.addOperation(txn.id, {
        type: 'read',
        resource: 'data1',
        action: 'read',
        data: {}
    });
    
    console.log(JSON.stringify({
        operationAdded: result
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
        assert data['operationAdded'] == False

def test_known_role_permission_allowed():
    """
    Test that known roles with permissions are allowed.
    """
    script = """
    const { TransactionManager } = require('./dist/transaction/TransactionManager');
    
    const manager = new TransactionManager();
    const txn = manager.createTransaction('user1', 'admin');
    
    const result = manager.addOperation(txn.id, {
        type: 'write',
        resource: 'data1',
        action: 'write',
        data: { value: 1 }
    });
    
    console.log(JSON.stringify({
        operationAdded: result
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
        assert data['operationAdded'] == True

def test_guest_role_read_only():
    """
    Test that guest role can only perform read operations.
    """
    script = """
    const { TransactionManager } = require('./dist/transaction/TransactionManager');
    
    const manager = new TransactionManager();
    const txn = manager.createTransaction('user1', 'guest');
    
    const readResult = manager.addOperation(txn.id, {
        type: 'read',
        resource: 'data1',
        action: 'read',
        data: {}
    });
    
    const writeResult = manager.addOperation(txn.id, {
        type: 'write',
        resource: 'data1',
        action: 'write',
        data: { value: 1 }
    });
    
    console.log(JSON.stringify({
        readAllowed: readResult,
        writeAllowed: writeResult
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
        assert data['readAllowed'] == True
        assert data['writeAllowed'] == False

def test_empty_role_permission_denied():
    """
    Test that empty string role is denied all permissions.
    """
    script = """
    const { TransactionManager } = require('./dist/transaction/TransactionManager');
    
    const manager = new TransactionManager();
    const txn = manager.createTransaction('user1', '');
    
    const result = manager.addOperation(txn.id, {
        type: 'read',
        resource: 'data1',
        action: 'read',
        data: {}
    });
    
    console.log(JSON.stringify({
        operationAdded: result
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
        assert data['operationAdded'] == False

def test_admin_role_all_permissions():
    """
    Test that admin role has all permissions (read, write, delete, execute).
    """
    script = """
    const { TransactionManager } = require('./dist/transaction/TransactionManager');
    
    const manager = new TransactionManager();
    const txn = manager.createTransaction('user1', 'admin');
    
    const readResult = manager.addOperation(txn.id, { type: 'read', resource: 'data1', action: 'read', data: {} });
    const writeResult = manager.addOperation(txn.id, { type: 'write', resource: 'data1', action: 'write', data: {} });
    const deleteResult = manager.addOperation(txn.id, { type: 'delete', resource: 'data1', action: 'delete', data: {} });
    const executeResult = manager.addOperation(txn.id, { type: 'execute', resource: 'data1', action: 'execute', data: {} });
    
    console.log(JSON.stringify({
        readAllowed: readResult,
        writeAllowed: writeResult,
        deleteAllowed: deleteResult,
        executeAllowed: executeResult
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
        assert data['readAllowed'] == True
        assert data['writeAllowed'] == True
        assert data['deleteAllowed'] == True
        assert data['executeAllowed'] == True

def test_user_role_limited_permissions():
    """
    Test that user role has only read and write permissions.
    """
    script = """
    const { TransactionManager } = require('./dist/transaction/TransactionManager');
    
    const manager = new TransactionManager();
    const txn = manager.createTransaction('user1', 'user');
    
    const readResult = manager.addOperation(txn.id, { type: 'read', resource: 'data1', action: 'read', data: {} });
    const writeResult = manager.addOperation(txn.id, { type: 'write', resource: 'data1', action: 'write', data: {} });
    const deleteResult = manager.addOperation(txn.id, { type: 'delete', resource: 'data1', action: 'delete', data: {} });
    
    console.log(JSON.stringify({
        readAllowed: readResult,
        writeAllowed: writeResult,
        deleteAllowed: deleteResult
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
        assert data['readAllowed'] == True
        assert data['writeAllowed'] == True
        assert data['deleteAllowed'] == False

def test_special_characters_role():
    """
    Test that roles with special characters are handled correctly.
    """
    script = """
    const { TransactionManager } = require('./dist/transaction/TransactionManager');
    
    const manager = new TransactionManager();
    const txn = manager.createTransaction('user1', 'role@123');
    
    const result = manager.addOperation(txn.id, {
        type: 'read',
        resource: 'data1',
        action: 'read',
        data: {}
    });
    
    console.log(JSON.stringify({
        operationAdded: result
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
        assert data['operationAdded'] == False

