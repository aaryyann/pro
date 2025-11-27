import pytest
import sys
import os
import subprocess
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

def test_event_collection_with_valid_event():
    """
    Test that valid events are collected successfully.
    """
    script = """
    const { EventCollector } = require('../../dist/analytics/EventCollector');
    
    const collector = new EventCollector();
    
    collector.collect({
        id: 'event1',
        type: 'click',
        timestamp: new Date(),
        properties: { button: 'submit' }
    });
    
    const count = collector.getEventCount();
    const events = collector.getEvents('click');
    
    console.log(JSON.stringify({
        count: count,
        eventCount: events.length,
        hasEvent: events.length > 0
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
        assert data['count'] == 1
        assert data['hasEvent'] == True

def test_event_collection_without_id():
    """
    Test behavior when collecting event without id.
    """
    script = """
    const { EventCollector } = require('../../dist/analytics/EventCollector');
    
    const collector = new EventCollector();
    
    collector.collect({
        type: 'click',
        timestamp: new Date(),
        properties: { button: 'submit' }
    });
    
    const count = collector.getEventCount();
    
    console.log(JSON.stringify({
        count: count
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
        assert data['count'] == 0

def test_event_collection_without_type():
    """
    Test behavior when collecting event without type.
    """
    script = """
    const { EventCollector } = require('../../dist/analytics/EventCollector');
    
    const collector = new EventCollector();
    
    collector.collect({
        id: 'event1',
        timestamp: new Date(),
        properties: { button: 'submit' }
    });
    
    const count = collector.getEventCount();
    
    console.log(JSON.stringify({
        count: count
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
        assert data['count'] == 0


def test_event_collection_with_user_id():
    """
    Test that events with userId are collected and can be filtered by userId.
    """
    script = """
    const { EventCollector } = require('../../dist/analytics/EventCollector');
    
    const collector = new EventCollector();
    
    collector.collect({
        id: 'event1',
        type: 'click',
        userId: 'user1',
        timestamp: new Date(),
        properties: { button: 'submit' }
    });
    
    collector.collect({
        id: 'event2',
        type: 'click',
        userId: 'user2',
        timestamp: new Date(),
        properties: { button: 'cancel' }
    });
    
    const user1Events = collector.getEvents('click', 'user1');
    const user2Events = collector.getEvents('click', 'user2');
    
    console.log(JSON.stringify({
        user1Count: user1Events.length,
        user2Count: user2Events.length
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
        assert data['user1Count'] == 1
        assert data['user2Count'] == 1

def test_event_collection_multiple_types():
    """
    Test that events of different types are collected separately.
    """
    script = """
    const { EventCollector } = require('../../dist/analytics/EventCollector');
    
    const collector = new EventCollector();
    
    collector.collect({ id: 'e1', type: 'click', timestamp: new Date(), properties: {} });
    collector.collect({ id: 'e2', type: 'click', timestamp: new Date(), properties: {} });
    collector.collect({ id: 'e3', type: 'view', timestamp: new Date(), properties: {} });
    
    const clickCount = collector.getEventCount('click');
    const viewCount = collector.getEventCount('view');
    const totalCount = collector.getEventCount();
    
    console.log(JSON.stringify({
        clickCount: clickCount,
        viewCount: viewCount,
        totalCount: totalCount
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
        assert data['clickCount'] == 2
        assert data['viewCount'] == 1
        assert data['totalCount'] == 3

def test_event_collection_clear():
    """
    Test that clearing events removes all collected events.
    """
    script = """
    const { EventCollector } = require('../../dist/analytics/EventCollector');
    
    const collector = new EventCollector();
    
    collector.collect({ id: 'e1', type: 'click', timestamp: new Date(), properties: {} });
    collector.collect({ id: 'e2', type: 'view', timestamp: new Date(), properties: {} });
    
    const countBefore = collector.getEventCount();
    collector.clear();
    const countAfter = collector.getEventCount();
    
    console.log(JSON.stringify({
        countBefore: countBefore,
        countAfter: countAfter
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
        assert data['countBefore'] == 2
        assert data['countAfter'] == 0
