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
    const { AnalyticsEngine } = require('./dist/analytics/AnalyticsEngine');
    
    const engine = new AnalyticsEngine();
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
    const { AnalyticsEngine } = require('./dist/analytics/AnalyticsEngine');
    
    const engine = new AnalyticsEngine();
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
    const { AnalyticsEngine } = require('./dist/analytics/AnalyticsEngine');
    
    const engine = new AnalyticsEngine();
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
    const { AnalyticsEngine } = require('./dist/analytics/AnalyticsEngine');
    
    const engine = new AnalyticsEngine();
    
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
    const { AnalyticsEngine } = require('./dist/analytics/AnalyticsEngine');
    
    const engine = new AnalyticsEngine();
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
    const { AnalyticsEngine } = require('./dist/analytics/AnalyticsEngine');
    
    const engine = new AnalyticsEngine();
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
