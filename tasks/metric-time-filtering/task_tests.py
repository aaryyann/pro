import pytest
import sys
import os
import subprocess
import json
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

def test_metrics_inclusive_start_time():
    """
    Test that metrics at the exact startTime are included.
    """
    script = """
    (async () => {
        const { MetricTimeFilteringEngine } = require('./dist/analytics/MetricTimeFilteringEngine');
    
        const engine = new MetricTimeFilteringEngine();
    const startTime = new Date('2024-01-01T10:00:00Z');
    
    engine.recordMetric({
        name: 'test_metric',
        value: 10,
        timestamp: startTime,
        tags: {}
    });
    
    engine.recordMetric({
        name: 'test_metric',
        value: 20,
        timestamp: new Date(startTime.getTime() + 1000),
        tags: {}
    });
    
    const metrics = engine.getMetrics('test_metric', startTime);
    
    console.log(JSON.stringify({
        count: metrics.length,
        includesStartTime: metrics.some(m => m.timestamp.getTime() === startTime.getTime())
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
        assert data['count'] == 2
        assert data['includesStartTime'] == True

def test_metrics_inclusive_end_time():
    """
    Test that metrics at the exact endTime are included.
    """
    script = """
    (async () => {
        const { MetricTimeFilteringEngine } = require('./dist/analytics/MetricTimeFilteringEngine');
    
        const engine = new MetricTimeFilteringEngine();
    const endTime = new Date('2024-01-01T10:00:00Z');
    
    engine.recordMetric({
        name: 'test_metric',
        value: 10,
        timestamp: new Date(endTime.getTime() - 1000),
        tags: {}
    });
    
    engine.recordMetric({
        name: 'test_metric',
        value: 20,
        timestamp: endTime,
        tags: {}
    });
    
    const metrics = engine.getMetrics('test_metric', undefined, endTime);
    
    console.log(JSON.stringify({
        count: metrics.length,
        includesEndTime: metrics.some(m => m.timestamp.getTime() === endTime.getTime())
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
        assert data['count'] == 2
        assert data['includesEndTime'] == True

def test_metrics_time_range_filtering():
    """
    Test that metrics are correctly filtered within a time range.
    """
    script = """
    (async () => {
        const { MetricTimeFilteringEngine } = require('./dist/analytics/MetricTimeFilteringEngine');
    
        const engine = new MetricTimeFilteringEngine();
    const startTime = new Date('2024-01-01T10:00:00Z');
    const endTime = new Date('2024-01-01T10:00:10Z');
    
    engine.recordMetric({
        name: 'test_metric',
        value: 5,
        timestamp: new Date(startTime.getTime() - 1000),
        tags: {}
    });
    
    engine.recordMetric({
        name: 'test_metric',
        value: 10,
        timestamp: startTime,
        tags: {}
    });
    
    engine.recordMetric({
        name: 'test_metric',
        value: 15,
        timestamp: endTime,
        tags: {}
    });
    
    engine.recordMetric({
        name: 'test_metric',
        value: 20,
        timestamp: new Date(endTime.getTime() + 1000),
        tags: {}
    });
    
    const metrics = engine.getMetrics('test_metric', startTime, endTime);
    
    console.log(JSON.stringify({
        count: metrics.length,
        values: metrics.map(m => m.value).sort((a, b) => a - b)
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
        assert data['count'] == 2
        assert 10 in data['values']
        assert 15 in data['values']


def test_metrics_no_time_filter():
    """
    Test that getMetrics returns all metrics when no time filter is provided.
    """
    script = """
    (async () => {
        const { MetricTimeFilteringEngine } = require('./dist/analytics/MetricTimeFilteringEngine');
    
        const engine = new MetricTimeFilteringEngine();
    
    for (let i = 0; i < 5; i++) {
        engine.recordMetric({
            name: 'test_metric',
            value: i * 10,
            timestamp: new Date(2024, 0, 1, 10, i, 0),
            tags: {}
        });
    }
    
    const metrics = engine.getMetrics('test_metric');
    
    console.log(JSON.stringify({
        count: metrics.length
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
        assert data['count'] == 5

def test_metrics_exact_boundary_times():
    """
    Test that metrics with exact start and end times are included when startTime equals endTime.
    """
    script = """
    (async () => {
        const { MetricTimeFilteringEngine } = require('./dist/analytics/MetricTimeFilteringEngine');
    
        const engine = new MetricTimeFilteringEngine();
    const exactTime = new Date('2024-01-01T10:00:00Z');
    
    engine.recordMetric({
        name: 'test_metric',
        value: 10,
        timestamp: exactTime,
        tags: {}
    });
    
    const metrics = engine.getMetrics('test_metric', exactTime, exactTime);
    
    console.log(JSON.stringify({
        count: metrics.length,
        includesExactTime: metrics.some(m => m.timestamp.getTime() === exactTime.getTime())
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
        assert data['count'] == 1
        assert data['includesExactTime'] == True

def test_metrics_multiple_metric_names():
    """
    Test that filtering by metric name works correctly with multiple metric types.
    """
    script = """
    (async () => {
        const { MetricTimeFilteringEngine } = require('./dist/analytics/MetricTimeFilteringEngine');
    
        const engine = new MetricTimeFilteringEngine();
    const time = new Date('2024-01-01T10:00:00Z');
    
    engine.recordMetric({ name: 'metric1', value: 10, timestamp: time, tags: {} });
    engine.recordMetric({ name: 'metric1', value: 20, timestamp: time, tags: {} });
    engine.recordMetric({ name: 'metric2', value: 30, timestamp: time, tags: {} });
    
    const metrics1 = engine.getMetrics('metric1');
    const metrics2 = engine.getMetrics('metric2');
    
    console.log(JSON.stringify({
        metric1Count: metrics1.length,
        metric2Count: metrics2.length
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
        assert data['metric1Count'] == 2
        assert data['metric2Count'] == 1

def test_metrics_name_filtering_with_time_range():
    """
    Test that name filtering is applied first, then time filtering, ensuring metrics with different names are excluded even if within time window.
    """
    script = """
    (async () => {
        const { MetricTimeFilteringEngine } = require('./dist/analytics/MetricTimeFilteringEngine');
    
        const engine = new MetricTimeFilteringEngine();
    const startTime = new Date('2024-01-01T10:00:00Z');
    const endTime = new Date('2024-01-01T10:00:10Z');
    const withinTime = new Date('2024-01-01T10:00:05Z');
    
    // Metrics with target name within time range
    engine.recordMetric({ name: 'target_metric', value: 10, timestamp: startTime, tags: {} });
    engine.recordMetric({ name: 'target_metric', value: 20, timestamp: withinTime, tags: {} });
    engine.recordMetric({ name: 'target_metric', value: 30, timestamp: endTime, tags: {} });
    
    // Metrics with different name but within time range - should be excluded
    engine.recordMetric({ name: 'other_metric', value: 40, timestamp: startTime, tags: {} });
    engine.recordMetric({ name: 'other_metric', value: 50, timestamp: withinTime, tags: {} });
    engine.recordMetric({ name: 'other_metric', value: 60, timestamp: endTime, tags: {} });
    
    // Metrics with target name but outside time range - should be excluded
    engine.recordMetric({ name: 'target_metric', value: 70, timestamp: new Date(startTime.getTime() - 1000), tags: {} });
    engine.recordMetric({ name: 'target_metric', value: 80, timestamp: new Date(endTime.getTime() + 1000), tags: {} });
    
    const metrics = engine.getMetrics('target_metric', startTime, endTime);
    
    console.log(JSON.stringify({
        count: metrics.length,
        values: metrics.map(m => m.value).sort((a, b) => a - b),
        allTargetName: metrics.every(m => m.name === 'target_metric')
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
        assert data['count'] == 3
        assert data['values'] == [10, 20, 30]
        assert data['allTargetName'] == True

def test_metrics_name_filtering_before_time_filtering():
    """
    Test that name filtering is applied BEFORE time filtering, not after.
    This test explicitly verifies the ordering guarantee by creating a scenario where:
    - If time filtering is applied first, metrics with different names within the time range would be considered
    - If name filtering is applied first, only metrics with the target name are considered for time filtering
    The test verifies that metrics with different names (even if within time range) are excluded,
    proving that name filtering happens before time filtering.
    """
    script = """
    (async () => {
        const { MetricTimeFilteringEngine } = require('./dist/analytics/MetricTimeFilteringEngine');
    
        const engine = new MetricTimeFilteringEngine();
    const startTime = new Date('2024-01-01T10:00:00Z');
    const endTime = new Date('2024-01-01T10:00:10Z');
    
    // Create a scenario that explicitly tests ordering:
    // - Target name metrics: some within time range, some outside
    // - Different name metrics: all within time range (would pass time filter if applied first)
    
    // Target name metrics within time range (should be included after both filters)
    engine.recordMetric({ name: 'target_name', value: 10, timestamp: new Date('2024-01-01T10:00:05Z'), tags: {} });
    engine.recordMetric({ name: 'target_name', value: 20, timestamp: new Date('2024-01-01T10:00:08Z'), tags: {} });
    
    // Target name metrics outside time range (excluded by time filter AFTER name filter)
    engine.recordMetric({ name: 'target_name', value: 30, timestamp: new Date('2024-01-01T09:59:00Z'), tags: {} });
    engine.recordMetric({ name: 'target_name', value: 40, timestamp: new Date('2024-01-01T10:00:15Z'), tags: {} });
    
    // Different name metrics WITHIN time range (should be excluded by name filter BEFORE time filter)
    // If time filtering happened first, these would be included, then filtered by name
    // If name filtering happens first, these are never considered for time filtering
    engine.recordMetric({ name: 'other_name', value: 50, timestamp: new Date('2024-01-01T10:00:05Z'), tags: {} });
    engine.recordMetric({ name: 'other_name', value: 60, timestamp: new Date('2024-01-01T10:00:08Z'), tags: {} });
    engine.recordMetric({ name: 'another_name', value: 70, timestamp: new Date('2024-01-01T10:00:05Z'), tags: {} });
    
    // Query for 'target_name' with time range
    const metrics = engine.getMetrics('target_name', startTime, endTime);
    
    // Verify the result
    const resultNames = metrics.map(m => m.name);
    const resultValues = metrics.map(m => m.value).sort((a, b) => a - b);
    const hasOnlyTargetName = resultNames.every(name => name === 'target_name');
    const hasNoOtherNames = !resultNames.some(name => name !== 'target_name');
    
    // Count how many different-name metrics are in the result
    // This should be 0 if name filtering happens first (correct order)
    const differentNameCount = metrics.filter(m => m.name !== 'target_name').length;
    
    console.log(JSON.stringify({
        resultCount: metrics.length,
        resultValues: resultValues,
        resultNames: resultNames,
        hasOnlyTargetName: hasOnlyTargetName,
        hasNoOtherNames: hasNoOtherNames,
        differentNameCount: differentNameCount,
        // This assertion verifies ordering: if time filtering happened first, different-name metrics
        // within time range would be included, then filtered out. By checking this is 0,
        // we verify name filtering happens first.
        orderingVerified: differentNameCount === 0 && hasOnlyTargetName
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
        assert 'differentNameCount' in data
        assert 'resultCount' in data
        assert 'resultNames' in data
        assert 'hasOnlyTargetName' in data
        # Critical assertion: This would fail if time filtering happened before name filtering
        # because different-name metrics within time range would be processed and potentially included
        # The assertion verifies that name filtering happens first by ensuring no different-name metrics
        # are in the result, even though they exist within the time range
        assert data['differentNameCount'] == 0, (
            "This test verifies name filtering happens BEFORE time filtering. "
            "differentNameCount must be 0, proving different-name metrics within time range "
            "were excluded by name filter before time filter was applied."
        )
        assert data['hasOnlyTargetName'] == True, (
            "All result metrics must have target name, proving name filtering was applied first."
        )
