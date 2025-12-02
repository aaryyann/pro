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
        const { PermissionSecurityCheckManager } = require('./dist/transaction/PermissionSecurityCheckManager');
    
        const manager = new PermissionSecurityCheckManager();
    const txn = manager.createTransaction('user1', 'hacker_role');
    
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
        assert data['readAllowed'] == False
        assert data['writeAllowed'] == False

def test_empty_role_permission_denied():
    """
    Test that empty or null roles are denied permissions.
    """
    script = """
        const { PermissionSecurityCheckManager } = require('./dist/transaction/PermissionSecurityCheckManager');
    
        const manager = new PermissionSecurityCheckManager();
    const txn = manager.createTransaction('user1', '');
    
    const result = manager.addOperation(txn.id, {
        type: 'read',
        resource: 'data1',
        action: 'read',
        data: {}
    });
    
    console.log(JSON.stringify({
        operationAllowed: result
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
        assert data['operationAllowed'] == False


def test_null_role_permission_denied():
    """
    Test that null role values are denied permissions.
    """
    script = """
        const { PermissionSecurityCheckManager } = require('./dist/transaction/PermissionSecurityCheckManager');
    
        const manager = new PermissionSecurityCheckManager();
    const txn = manager.createTransaction('user1', null);
    
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

def test_whitespace_role_permission_denied():
    """
    Test that roles with only whitespace are denied permissions.
    """
    script = """
        const { PermissionSecurityCheckManager } = require('./dist/transaction/PermissionSecurityCheckManager');
    
        const manager = new PermissionSecurityCheckManager();
    const txn = manager.createTransaction('user1', '   ');
    
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

def test_case_sensitive_role_matching():
    """
    Test that role matching is case-sensitive and case variations are denied.
    """
    script = """
        const { PermissionSecurityCheckManager } = require('./dist/transaction/PermissionSecurityCheckManager');
    
        const manager = new PermissionSecurityCheckManager();
    const txn1 = manager.createTransaction('user1', 'Admin');
    const txn2 = manager.createTransaction('user2', 'ADMIN');
    const txn3 = manager.createTransaction('user3', 'admin');
    
    const result1 = manager.addOperation(txn1.id, { type: 'read', resource: 'data1', action: 'read', data: {} });
    const result2 = manager.addOperation(txn2.id, { type: 'read', resource: 'data1', action: 'read', data: {} });
    const result3 = manager.addOperation(txn3.id, { type: 'read', resource: 'data1', action: 'read', data: {} });
    
    console.log(JSON.stringify({
        adminCase: result1,
        ADMINCase: result2,
        adminLower: result3
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
        assert data['adminCase'] == False
        assert data['ADMINCase'] == False
        assert data['adminLower'] == True

def test_permission_check_all_actions():
    """
    Test that permission checks work for all action types.
    """
    script = """
        const { PermissionSecurityCheckManager } = require('./dist/transaction/PermissionSecurityCheckManager');
    
        const manager = new PermissionSecurityCheckManager();
    const txn = manager.createTransaction('user1', 'unknown_role');
    
    const readResult = manager.addOperation(txn.id, { type: 'read', resource: 'data1', action: 'read', data: {} });
    const writeResult = manager.addOperation(txn.id, { type: 'write', resource: 'data1', action: 'write', data: {} });
    const deleteResult = manager.addOperation(txn.id, { type: 'delete', resource: 'data1', action: 'delete', data: {} });
    const executeResult = manager.addOperation(txn.id, { type: 'execute', resource: 'data1', action: 'execute', data: {} });
    
    console.log(JSON.stringify({
        readDenied: !readResult,
        writeDenied: !writeResult,
        deleteDenied: !deleteResult,
        executeDenied: !executeResult
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
        assert data['readDenied'] == True
        assert data['writeDenied'] == True
        assert data['deleteDenied'] == True
        assert data['executeDenied'] == True
