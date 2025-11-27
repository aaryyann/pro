import pytest
import sys
import os
import subprocess
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

def test_event_collection_with_valid_event():
    """
    Test that valid events are collected successfully and have all required fields.
    """
    script = """
    const { EventCollector } = require('./dist/analytics/EventCollector');
    
    const collector = new EventCollector();
    
    collector.collect({
        id: 'event1',
        type: 'click',
        timestamp: new Date(),
        properties: { button: 'submit' }
    });
    
    const count = collector.getEventCount();
    const events = collector.getEvents('click');
    const event = events.length > 0 ? events[0] : null;
    
    console.log(JSON.stringify({
        count: count,
        eventCount: events.length,
        hasEvent: events.length > 0,
        eventHasId: event ? (event.id !== undefined && event.id !== null) : false,
        eventHasType: event ? (event.type !== undefined && event.type !== null) : false,
        eventHasTimestamp: event ? (event.timestamp !== undefined && event.timestamp !== null) : false,
        allFieldsPresent: event ? (event.id && event.type && event.timestamp) : false
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
        assert data['count'] == 1, f"Expected 1 event, got {data['count']}"
        assert data['hasEvent'] == True, "Event should be collected"
        assert data['allFieldsPresent'] == True, "Collected event must have all required fields (id, type, timestamp)"

def test_event_collection_without_id():
    """
    Test that events without id should still be collected or throw an error, not silently rejected.
    The current implementation silently rejects events, which is incorrect behavior.
    """
    script = """
    const { EventCollector } = require('./dist/analytics/EventCollector');
    
    const collector = new EventCollector();
    let errorThrown = false;
    
    try {
        collector.collect({
            type: 'click',
            timestamp: new Date(),
            properties: { button: 'submit' }
        });
    } catch (e) {
        errorThrown = true;
    }
    
    const count = collector.getEventCount();
    const events = collector.getEvents('click');
    
    console.log(JSON.stringify({
        count: count,
        eventCount: events.length,
        errorThrown: errorThrown,
        shouldHaveErrorOrEvent: errorThrown || events.length > 0
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
        # Event should either be collected OR throw an error, not silently rejected
        assert data['shouldHaveErrorOrEvent'] == True, "Events without id should either be collected or throw an error, not silently rejected"
        assert data['count'] > 0 or data['errorThrown'] == True, "Event should be collected or error should be thrown"

def test_event_collection_without_type():
    """
    Test that events without type should still be collected or throw an error, not silently rejected.
    The current implementation silently rejects events, which is incorrect behavior.
    """
    script = """
    const { EventCollector } = require('./dist/analytics/EventCollector');
    
    const collector = new EventCollector();
    let errorThrown = false;
    
    try {
        collector.collect({
            id: 'event1',
            timestamp: new Date(),
            properties: { button: 'submit' }
        });
    } catch (e) {
        errorThrown = true;
    }
    
    const count = collector.getEventCount();
    const allEvents = collector.getEvents();
    
    console.log(JSON.stringify({
        count: count,
        eventCount: allEvents.length,
        errorThrown: errorThrown,
        shouldHaveErrorOrEvent: errorThrown || allEvents.length > 0
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
        # Event should either be collected OR throw an error, not silently rejected
        assert data['shouldHaveErrorOrEvent'] == True, "Events without type should either be collected or throw an error, not silently rejected"
        assert data['count'] > 0 or data['errorThrown'] == True, "Event should be collected or error should be thrown"


def test_event_collection_with_user_id():
    """
    Test that events with userId are collected and can be filtered by userId correctly.
    Also verifies that events without userId are still collected and filtering works properly.
    """
    script = """
    const { EventCollector } = require('./dist/analytics/EventCollector');
    
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
    
    collector.collect({
        id: 'event3',
        type: 'click',
        timestamp: new Date(),
        properties: { button: 'other' }
    });
    
    const user1Events = collector.getEvents('click', 'user1');
    const user2Events = collector.getEvents('click', 'user2');
    const allClickEvents = collector.getEvents('click');
    const eventsWithoutUserId = allClickEvents.filter(e => !e.userId);
    const totalCount = collector.getEventCount();
    
    console.log(JSON.stringify({
        user1Count: user1Events.length,
        user2Count: user2Events.length,
        allClickCount: allClickEvents.length,
        eventsWithoutUserIdCount: eventsWithoutUserId.length,
        totalCount: totalCount,
        user1HasCorrectId: user1Events.length > 0 ? user1Events[0].id === 'event1' : false,
        user2HasCorrectId: user2Events.length > 0 ? user2Events[0].id === 'event2' : false,
        hasEventWithoutUserId: eventsWithoutUserIdCount > 0
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
        assert data['user1Count'] == 1, f"Expected 1 event for user1, got {data['user1Count']}"
        assert data['user2Count'] == 1, f"Expected 1 event for user2, got {data['user2Count']}"
        assert data['totalCount'] == 3, f"Expected 3 total events, got {data['totalCount']}"
        assert data['allClickCount'] == 3, f"Expected 3 click events total, got {data['allClickCount']}"
        assert data['hasEventWithoutUserId'] == True, "Event without userId should still be collected"
        assert data['user1HasCorrectId'] == True, "User1 event should have correct id"
        assert data['user2HasCorrectId'] == True, "User2 event should have correct id"

def test_event_collection_multiple_types():
    """
    Test that events of different types are collected separately and type filtering works correctly.
    Also tests that events with null/undefined id or type should throw errors, not be silently rejected.
    """
    script = """
    const { EventCollector } = require('./dist/analytics/EventCollector');
    
    const collector = new EventCollector();
    let nullIdError = false;
    let nullTypeError = false;
    
    collector.collect({ id: 'e1', type: 'click', timestamp: new Date(), properties: {} });
    collector.collect({ id: 'e2', type: 'click', timestamp: new Date(), properties: {} });
    collector.collect({ id: 'e3', type: 'view', timestamp: new Date(), properties: {} });
    collector.collect({ id: 'e4', type: 'scroll', timestamp: new Date(), properties: {} });
    
    // Try to collect events with null id or type - should throw error, not silently reject
    try {
        collector.collect({ id: null, type: 'click', timestamp: new Date(), properties: {} });
    } catch (e) {
        nullIdError = true;
    }
    
    try {
        collector.collect({ id: 'e5', type: null, timestamp: new Date(), properties: {} });
    } catch (e) {
        nullTypeError = true;
    }
    
    const clickCount = collector.getEventCount('click');
    const viewCount = collector.getEventCount('view');
    const scrollCount = collector.getEventCount('scroll');
    const totalCount = collector.getEventCount();
    const clickEvents = collector.getEvents('click');
    const viewEvents = collector.getEvents('view');
    const scrollEvents = collector.getEvents('scroll');
    const allEvents = collector.getEvents();
    
    console.log(JSON.stringify({
        clickCount: clickCount,
        viewCount: viewCount,
        scrollCount: scrollCount,
        totalCount: totalCount,
        clickEventsLength: clickEvents.length,
        viewEventsLength: viewEvents.length,
        scrollEventsLength: scrollEvents.length,
        allEventsLength: allEvents.length,
        allClickHaveCorrectType: clickEvents.every(e => e.type === 'click'),
        allViewHaveCorrectType: viewEvents.every(e => e.type === 'view'),
        clickCountMatchesLength: clickCount === clickEvents.length,
        viewCountMatchesLength: viewCount === viewEvents.length,
        totalMatchesAllEvents: totalCount === allEvents.length,
        nullIdError: nullIdError,
        nullTypeError: nullTypeError,
        shouldHaveErrors: nullIdError || nullTypeError
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
        assert data['clickCount'] == 2, f"Expected 2 click events, got {data['clickCount']}"
        assert data['viewCount'] == 1, f"Expected 1 view event, got {data['viewCount']}"
        assert data['scrollCount'] == 1, f"Expected 1 scroll event, got {data['scrollCount']}"
        assert data['totalCount'] == 4, f"Expected 4 total events, got {data['totalCount']}"
        assert data['shouldHaveErrors'] == True, "Events with null id or type should throw errors, not be silently rejected"
        assert data['clickCountMatchesLength'] == True, "getEventCount('click') should match getEvents('click').length"
        assert data['viewCountMatchesLength'] == True, "getEventCount('view') should match getEvents('view').length"
        assert data['totalMatchesAllEvents'] == True, "getEventCount() should match getEvents().length"
        assert data['allClickHaveCorrectType'] == True, "All click events should have type 'click'"
        assert data['allViewHaveCorrectType'] == True, "All view events should have type 'view'"

def test_event_collection_clear():
    """
    Test that clearing events removes all collected events and that events cannot be retrieved after clear.
    Also verifies that after clear, new events can be collected and the collector works normally.
    Also tests that events with missing required fields are handled properly after clear.
    """
    script = """
    const { EventCollector } = require('./dist/analytics/EventCollector');
    
    const collector = new EventCollector();
    
    collector.collect({ id: 'e1', type: 'click', timestamp: new Date(), properties: {} });
    collector.collect({ id: 'e2', type: 'view', timestamp: new Date(), properties: {} });
    collector.collect({ id: 'e3', type: 'scroll', timestamp: new Date(), properties: {} });
    
    const countBefore = collector.getEventCount();
    const eventsBefore = collector.getEvents();
    const clickEventsBefore = collector.getEvents('click');
    
    collector.clear();
    
    const countAfter = collector.getEventCount();
    const eventsAfter = collector.getEvents();
    const clickEventsAfter = collector.getEvents('click');
    const clickCountAfter = collector.getEventCount('click');
    
    // After clear, collect new events to verify collector still works
    collector.collect({ id: 'e4', type: 'click', timestamp: new Date(), properties: {} });
    collector.collect({ id: 'e5', type: 'view', timestamp: new Date(), properties: {} });
    
    // Try to collect invalid event after clear - should throw error or be properly handled
    let invalidEventError = false;
    try {
        collector.collect({ type: 'click', timestamp: new Date(), properties: {} });
    } catch (e) {
        invalidEventError = true;
    }
    
    const countAfterNew = collector.getEventCount();
    const eventsAfterNew = collector.getEvents();
    const clickCountAfterNew = collector.getEventCount('click');
    
    console.log(JSON.stringify({
        countBefore: countBefore,
        countAfter: countAfter,
        eventsBeforeLength: eventsBefore.length,
        eventsAfterLength: eventsAfter.length,
        clickEventsBeforeLength: clickEventsBefore.length,
        clickEventsAfterLength: clickEventsAfter.length,
        clickCountAfter: clickCountAfter,
        countAfterNew: countAfterNew,
        eventsAfterNewLength: eventsAfterNew.length,
        clickCountAfterNew: clickCountAfterNew,
        invalidEventError: invalidEventError,
        allCleared: countAfter === 0 && eventsAfter.length === 0 && clickEventsAfter.length === 0 && clickCountAfter === 0,
        worksAfterClear: countAfterNew === 2 && eventsAfterNew.length === 2 && clickCountAfterNew === 1,
        invalidEventHandled: invalidEventError || countAfterNew === 2
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
        assert data['countBefore'] == 3, f"Expected 3 events before clear, got {data['countBefore']}"
        assert data['countAfter'] == 0, f"Expected 0 events after clear, got {data['countAfter']}"
        assert data['allCleared'] == True, "All events and filtered results should be empty after clear"
        assert data['worksAfterClear'] == True, "Collector should work normally after clear - new events should be collectable"
        assert data['invalidEventError'] == True, "Invalid events (without id) should throw an error, not be silently rejected. Silent rejection is incorrect behavior."
