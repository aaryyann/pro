import pytest
import sys
import os
import subprocess
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

def test_period_key_consistency():
    """
    Test that the same period generates the same key consistently.
    """
    script = """
    const { AnalyticsEngine } = require('./dist/analytics/AnalyticsEngine');
    
    const engine = new AnalyticsEngine();
    const timestamp1 = new Date('2024-01-05T10:00:00Z');
    const timestamp2 = new Date('2024-01-05T10:30:00Z');
    
    engine.recordMetric({
        name: 'test_metric',
        value: 10,
        timestamp: timestamp1,
        tags: {}
    });
    
    engine.recordMetric({
        name: 'test_metric',
        value: 20,
        timestamp: timestamp2,
        tags: {}
    });
    
    const aggregation = engine.aggregate('test_metric', 'hour');
    
    console.log(JSON.stringify({
        aggregationCount: aggregation.length,
        periodKeys: aggregation.map(a => a.period)
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
        assert data['aggregationCount'] == 1
        assert len(data['periodKeys']) == 1

def test_period_key_sortable():
    """
    Test that period keys are sortable chronologically.
    This test uses dates that expose the sorting bug when padding is missing.
    """
    script = """
    const { AnalyticsEngine } = require('./dist/analytics/AnalyticsEngine');
    
    const engine = new AnalyticsEngine();
    
    engine.recordMetric({
        name: 'test_metric',
        value: 10,
        timestamp: new Date('2024-01-01T10:00:00Z'),
        tags: {}
    });
    
    engine.recordMetric({
        name: 'test_metric',
        value: 20,
        timestamp: new Date('2024-01-02T10:00:00Z'),
        tags: {}
    });
    
    engine.recordMetric({
        name: 'test_metric',
        value: 30,
        timestamp: new Date('2024-01-10T10:00:00Z'),
        tags: {}
    });
    
    const aggregation = engine.aggregate('test_metric', 'day');
    const sortedKeys = aggregation.map(a => a.period).sort();
    const originalKeys = aggregation.map(a => a.period);
    
    console.log(JSON.stringify({
        keys: originalKeys,
        sortedKeys: sortedKeys,
        isSorted: JSON.stringify(sortedKeys) === JSON.stringify(originalKeys),
        chronologicalOrder: originalKeys[0] < originalKeys[1] && originalKeys[1] < originalKeys[2]
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
        assert data['isSorted'] == True, f"Keys must be in chronological order. Got: {data['keys']}"
        assert data['chronologicalOrder'] == True, f"Keys must sort correctly. Got: {data['keys']}, Sorted: {data['sortedKeys']}"


def test_period_key_month_boundary():
    """
    Test that period keys handle month boundaries correctly.
    """
    script = """
    const { AnalyticsEngine } = require('./dist/analytics/AnalyticsEngine');
    
    const engine = new AnalyticsEngine();
    
    engine.recordMetric({
        name: 'test_metric',
        value: 10,
        timestamp: new Date('2024-01-31T23:00:00Z'),
        tags: {}
    });
    
    engine.recordMetric({
        name: 'test_metric',
        value: 20,
        timestamp: new Date('2024-02-01T01:00:00Z'),
        tags: {}
    });
    
    const aggregation = engine.aggregate('test_metric', 'day');
    
    console.log(JSON.stringify({
        aggregationCount: aggregation.length
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
        assert data['aggregationCount'] == 2

def test_period_key_year_boundary():
    """
    Test that period keys handle year boundaries correctly with proper formatting.
    """
    script = """
    const { AnalyticsEngine } = require('./dist/analytics/AnalyticsEngine');
    
    const engine = new AnalyticsEngine();
    
    engine.recordMetric({
        name: 'test_metric',
        value: 10,
        timestamp: new Date('2023-12-31T10:00:00Z'),
        tags: {}
    });
    
    engine.recordMetric({
        name: 'test_metric',
        value: 20,
        timestamp: new Date('2024-01-01T10:00:00Z'),
        tags: {}
    });
    
    const aggregation = engine.aggregate('test_metric', 'day');
    const keys = aggregation.map(a => a.period);
    
    console.log(JSON.stringify({
        aggregationCount: aggregation.length,
        keys: keys,
        hasProperFormat: keys.every(k => {
            const parts = k.split('-');
            return parts.length === 3 && 
                   parts[0].length === 4 && 
                   parts[1].length === 2 && 
                   parts[2].length === 2;
        })
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
        assert data['aggregationCount'] == 2
        assert data['hasProperFormat'] == True, f"Keys must have proper format (YYYY-MM-DD). Got: {data['keys']}"

def test_period_key_week_calculation():
    """
    Test that week period keys are calculated correctly with proper formatting.
    Monday and Tuesday should be in the same week, next Monday in a different week.
    """
    script = """
    const { AnalyticsEngine } = require('./dist/analytics/AnalyticsEngine');
    
    const engine = new AnalyticsEngine();
    
    const monday = new Date('2024-01-01T10:00:00Z');
    const tuesday = new Date('2024-01-02T10:00:00Z');
    const nextMonday = new Date('2024-01-08T10:00:00Z');
    
    engine.recordMetric({ name: 'test_metric', value: 10, timestamp: monday, tags: {} });
    engine.recordMetric({ name: 'test_metric', value: 20, timestamp: tuesday, tags: {} });
    engine.recordMetric({ name: 'test_metric', value: 30, timestamp: nextMonday, tags: {} });
    
    const aggregation = engine.aggregate('test_metric', 'week');
    const keys = aggregation.map(a => a.period);
    const uniqueKeys = [...new Set(keys)];
    
    console.log(JSON.stringify({
        aggregationCount: aggregation.length,
        keys: keys,
        uniqueKeyCount: uniqueKeys.length,
        hasProperFormat: keys.every(k => {
            const parts = k.split('-');
            return parts.length === 3 && 
                   parts[0].length === 4 && 
                   parts[1].length === 2 && 
                   parts[2].length === 2;
        }),
        mondayAndTuesdaySameWeek: keys.filter(k => {
            const idx = aggregation.findIndex(a => a.period === k);
            return idx < 2;
        }).length === 1
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
        assert data['aggregationCount'] >= 1
        assert data['hasProperFormat'] == True, f"Week keys must have proper format (YYYY-MM-DD). Got: {data['keys']}"
        assert data['uniqueKeyCount'] >= 1, f"Should have at least 1 unique week key. Got: {data['uniqueKeyCount']}"

def test_period_key_single_digit_dates():
    """
    Test that single digit dates and months are handled correctly with zero-padding.
    This test verifies that dates like 01-05 are properly formatted as 01-05, not 1-5.
    """
    script = """
    const { AnalyticsEngine } = require('./dist/analytics/AnalyticsEngine');
    
    const engine = new AnalyticsEngine();
    
    engine.recordMetric({
        name: 'test_metric',
        value: 10,
        timestamp: new Date('2024-01-05T10:00:00Z'),
        tags: {}
    });
    
    engine.recordMetric({
        name: 'test_metric',
        value: 20,
        timestamp: new Date('2024-01-05T11:00:00Z'),
        tags: {}
    });
    
    const aggregation = engine.aggregate('test_metric', 'hour');
    const dayAggregation = engine.aggregate('test_metric', 'day');
    const hourKeys = aggregation.map(a => a.period);
    const dayKeys = dayAggregation.map(a => a.period);
    
    // Check that all keys have proper zero-padding (YYYY-MM-DD-HH format for hours, YYYY-MM-DD for days)
    const hourFormatValid = hourKeys.every(k => {
        const parts = k.split('-');
        return parts.length === 4 && 
               parts[0].length === 4 && 
               parts[1].length === 2 && 
               parts[2].length === 2 &&
               parts[3].length === 2;
    });
    
    const dayFormatValid = dayKeys.every(k => {
        const parts = k.split('-');
        return parts.length === 3 && 
               parts[0].length === 4 && 
               parts[1].length === 2 && 
               parts[2].length === 2;
    });
    
    console.log(JSON.stringify({
        hourCount: aggregation.length,
        dayCount: dayAggregation.length,
        hourKeys: hourKeys,
        dayKeys: dayKeys,
        hourFormatValid: hourFormatValid,
        dayFormatValid: dayFormatValid
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
        assert data['hourCount'] == 2
        assert data['dayCount'] == 1
        assert data['hourFormatValid'] == True, f"Hour keys must have proper format (YYYY-MM-DD-HH with zero-padding). Got: {data['hourKeys']}"
        assert data['dayFormatValid'] == True, f"Day keys must have proper format (YYYY-MM-DD with zero-padding). Got: {data['dayKeys']}"
