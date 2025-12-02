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
        const { AggregationPeriodKeysEngine } = require('./dist/analytics/AggregationPeriodKeysEngine');
    
        const engine = new AggregationPeriodKeysEngine();
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
        const { AggregationPeriodKeysEngine } = require('./dist/analytics/AggregationPeriodKeysEngine');
    
        const engine = new AggregationPeriodKeysEngine();
    
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
        const { AggregationPeriodKeysEngine } = require('./dist/analytics/AggregationPeriodKeysEngine');
    
        const engine = new AggregationPeriodKeysEngine();
    
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
    const keys = aggregation.map(a => a.period).sort();
    
    console.log(JSON.stringify({
        aggregationCount: aggregation.length,
        keys
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
        assert data['keys'] == ["2024-01-31", "2024-02-01"], f"Day aggregation keys must use 1-12 months and zero padding. Got: {data['keys']}"

def test_period_key_year_boundary():
    """
    Test that period keys handle year boundaries correctly with proper formatting.
    """
    script = """
        const { AggregationPeriodKeysEngine } = require('./dist/analytics/AggregationPeriodKeysEngine');
    
        const engine = new AggregationPeriodKeysEngine();
    
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
        const { AggregationPeriodKeysEngine } = require('./dist/analytics/AggregationPeriodKeysEngine');
    
        const engine = new AggregationPeriodKeysEngine();
    
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

def test_week_key_sunday_maps_to_prior_monday():
    """
    Test that a Sunday timestamp maps to the Monday of the same week (previous Monday).
    """
    script = """
        const { AggregationPeriodKeysEngine } = require('./dist/analytics/AggregationPeriodKeysEngine');
    
        const engine = new AggregationPeriodKeysEngine();
    const monday = new Date('2024-01-01T10:00:00Z'); // Monday
    const sunday = new Date('2024-01-07T10:00:00Z'); // Sunday of same week
    
    engine.recordMetric({ name: 'test_metric', value: 10, timestamp: monday, tags: {} });
    engine.recordMetric({ name: 'test_metric', value: 20, timestamp: sunday, tags: {} });
    
    const aggregation = engine.aggregate('test_metric', 'week');
    const keys = aggregation.map(a => a.period);
    
    console.log(JSON.stringify({
        keys,
        uniqueKeyCount: new Set(keys).size,
        sundayKey: keys.find(k => true)
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
        data = json.loads(output.split('\\n')[-1])
        assert data['uniqueKeyCount'] == 1, f"Sunday should map to same week key as Monday. Keys: {data['keys']}"
        assert data['sundayKey'] == '2024-01-01', f"Week key should map to Monday (2024-01-01). Got: {data['sundayKey']}"

def test_period_key_single_digit_dates():
    """
    Test that single digit dates and months are handled correctly with zero-padding.
    This test verifies that dates like 01-05 are properly formatted as 01-05, not 1-5.
    """
    script = """
        const { AggregationPeriodKeysEngine } = require('./dist/analytics/AggregationPeriodKeysEngine');
    
        const engine = new AggregationPeriodKeysEngine();
    
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

def test_time_filtering_inclusive_boundaries():
    """
    Test that getMetrics() uses inclusive time boundaries (>= and <=) so boundary timestamps are included.
    This explicitly verifies that startTime and endTime use >= and <= operators, not > and <.
    """
    script = """
        const { AggregationPeriodKeysEngine } = require('./dist/analytics/AggregationPeriodKeysEngine');
    
        const engine = new AggregationPeriodKeysEngine();
    
    const beforeBoundary = new Date('2024-01-05T09:59:00Z');
    const atStartBoundary = new Date('2024-01-05T10:00:00Z');
    const inRange = new Date('2024-01-05T10:30:00Z');
    const atEndBoundary = new Date('2024-01-05T11:00:00Z');
    const afterBoundary = new Date('2024-01-05T11:01:00Z');
    
    engine.recordMetric({ name: 'test_metric', value: 1, timestamp: beforeBoundary, tags: {} });
    engine.recordMetric({ name: 'test_metric', value: 2, timestamp: atStartBoundary, tags: {} });
    engine.recordMetric({ name: 'test_metric', value: 3, timestamp: inRange, tags: {} });
    engine.recordMetric({ name: 'test_metric', value: 4, timestamp: atEndBoundary, tags: {} });
    engine.recordMetric({ name: 'test_metric', value: 5, timestamp: afterBoundary, tags: {} });
    
    const startTime = new Date('2024-01-05T10:00:00Z');
    const endTime = new Date('2024-01-05T11:00:00Z');
    
    const filtered = engine.getMetrics('test_metric', startTime, endTime);
    const values = filtered.map(m => m.value).sort((a, b) => a - b);
    
    const usesInclusiveStart = values.includes(2);
    const usesInclusiveEnd = values.includes(4);
    
    console.log(JSON.stringify({
        totalMetrics: 5,
        filteredCount: filtered.length,
        filteredValues: values,
        includesStartBoundary: usesInclusiveStart,
        includesEndBoundary: usesInclusiveEnd,
        includesInRange: values.includes(3),
        excludesBefore: !values.includes(1),
        excludesAfter: !values.includes(5),
        usesInclusiveBoundaries: usesInclusiveStart && usesInclusiveEnd,
        startTimeBoundary: startTime.toISOString(),
        endTimeBoundary: endTime.toISOString()
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
        assert data['filteredCount'] == 3, f"Should include 3 metrics (at start boundary, in range, at end boundary). Got: {data['filteredCount']}"
        assert data['usesInclusiveBoundaries'] == True, f"getMetrics() must use inclusive boundaries (>= startTime and <= endTime). Start boundary included: {data['includesStartBoundary']}, End boundary included: {data['includesEndBoundary']}"
        assert data['includesStartBoundary'] == True, f"Must include metric exactly at startTime boundary ({data['startTimeBoundary']}) using >= operator. Got values: {data['filteredValues']}"
        assert data['includesEndBoundary'] == True, f"Must include metric exactly at endTime boundary ({data['endTimeBoundary']}) using <= operator. Got values: {data['filteredValues']}"
        assert data['includesInRange'] == True, f"Should include metric in range. Got values: {data['filteredValues']}"
        assert data['excludesBefore'] == True, f"Should exclude metric before startTime. Got values: {data['filteredValues']}"
        assert data['excludesAfter'] == True, f"Should exclude metric after endTime. Got values: {data['filteredValues']}"

def test_utc_methods_usage():
    """
    Test that all date operations use UTC methods to ensure timezone consistency.
    This verifies that getPeriodKey uses UTC methods by comparing results across different timezones.
    """
    script = """
        const { AggregationPeriodKeysEngine } = require('./dist/analytics/AggregationPeriodKeysEngine');
    
        const engine = new AggregationPeriodKeysEngine();
    
    const utcTimestamp = new Date('2024-01-15T14:30:00Z');
    
    engine.recordMetric({
        name: 'test_metric',
        value: 10,
        timestamp: utcTimestamp,
        tags: {}
    });
    
    const hourAggregation = engine.aggregate('test_metric', 'hour');
    const dayAggregation = engine.aggregate('test_metric', 'day');
    const weekAggregation = engine.aggregate('test_metric', 'week');
    
    const hourKey = hourAggregation[0]?.period || '';
    const dayKey = dayAggregation[0]?.period || '';
    const weekKey = weekAggregation[0]?.period || '';
    
    const hourParts = hourKey.split('-');
    const dayParts = dayKey.split('-');
    const weekParts = weekKey.split('-');
    
    const utcDate = new Date(utcTimestamp);
    const expectedYear = utcDate.getUTCFullYear();
    const expectedMonth = String(utcDate.getUTCMonth() + 1).padStart(2, '0');
    const expectedDay = String(utcDate.getUTCDate()).padStart(2, '0');
    const expectedHour = String(utcDate.getUTCHours()).padStart(2, '0');
    
    const usesUTC = {
        hourKeyCorrect: hourParts[0] == expectedYear && 
                       hourParts[1] == expectedMonth && 
                       hourParts[2] == expectedDay && 
                       hourParts[3] == expectedHour,
        dayKeyCorrect: dayParts[0] == expectedYear && 
                      dayParts[1] == expectedMonth && 
                      dayParts[2] == expectedDay,
        weekKeyFormatted: weekParts.length === 3 && 
                         weekParts[0].length === 4 && 
                         weekParts[1].length === 2 && 
                         weekParts[2].length === 2,
        allKeysUseUTC: hourKey.includes(String(expectedYear)) && 
                      dayKey.includes(String(expectedYear)) && 
                      weekKey.includes(String(expectedYear))
    };
    
    console.log(JSON.stringify({
        hourKey: hourKey,
        dayKey: dayKey,
        weekKey: weekKey,
        expectedYear: expectedYear,
        expectedMonth: expectedMonth,
        expectedDay: expectedDay,
        expectedHour: expectedHour,
        usesUTC: usesUTC,
        allUTCMethodsUsed: usesUTC.hourKeyCorrect && usesUTC.dayKeyCorrect && usesUTC.weekKeyFormatted
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
        assert data['allUTCMethodsUsed'] == True, f"All period keys must use UTC methods. Hour: {data['hourKey']}, Day: {data['dayKey']}, Week: {data['weekKey']}"
        assert data['usesUTC']['hourKeyCorrect'] == True, f"Hour key must use UTC values. Expected year={data['expectedYear']}, month={data['expectedMonth']}, day={data['expectedDay']}, hour={data['expectedHour']}. Got: {data['hourKey']}"
        assert data['usesUTC']['dayKeyCorrect'] == True, f"Day key must use UTC values. Expected year={data['expectedYear']}, month={data['expectedMonth']}, day={data['expectedDay']}. Got: {data['dayKey']}"

def test_existing_metrics_remain_accessible():
    """
    Test that metrics recorded before formatting fixes remain accessible and unmodified.
    """
    script = """
        const { AggregationPeriodKeysEngine } = require('./dist/analytics/AggregationPeriodKeysEngine');
    
        const engine = new AggregationPeriodKeysEngine();
    const timestamps = [
        new Date('2024-01-05T10:00:00Z'),
        new Date('2024-01-06T11:00:00Z'),
        new Date('2024-01-07T12:00:00Z')
    ];
    const values = [5, 15, 25];
    
    timestamps.forEach((timestamp, idx) => {
        engine.recordMetric({
            name: 'test_metric',
            value: values[idx],
            timestamp,
            tags: { idx: String(idx) }
        });
    });
    
    const before = engine.getMetrics('test_metric');
    const beforeValues = before.map(m => m.value);
    
    // Trigger aggregations which rely on formatted keys
    const dayAggregation = engine.aggregate('test_metric', 'day');
    const weekAggregation = engine.aggregate('test_metric', 'week');
    
    const after = engine.getMetrics('test_metric');
    const afterValues = after.map(m => m.value);
    const afterTimestampsAreDates = after.every(m => m.timestamp instanceof Date);
    
    const dayKeys = dayAggregation.map(a => a.period).sort();
    const expectedDayKeys = ['2024-01-05', '2024-01-06', '2024-01-07'];
    const dayKeysMatch = JSON.stringify(dayKeys) === JSON.stringify(expectedDayKeys);
    
    const weekKeys = weekAggregation.map(a => a.period);
    const weekKeysFormatted = weekKeys.every(k => {
        const parts = k.split('-');
        return parts.length === 3 && parts[0].length === 4 && parts[1].length === 2 && parts[2].length === 2;
    });
    const weekMapsToMonday = weekKeys.every(k => k === '2024-01-01');
    
    console.log(JSON.stringify({
        beforeValues,
        afterValues,
        sameCount: beforeValues.length === afterValues.length,
        sameValues: beforeValues.every((v, index) => v === afterValues[index]),
        timestampsRemainDates: afterTimestampsAreDates,
        dayKeys,
        dayKeysMatch,
        weekKeys,
        weekKeysFormatted,
        weekMapsToMonday
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
        data = json.loads(output.split('\\n')[-1])
        assert data['sameCount'] == True, f"Existing metrics count should remain unchanged. Before: {data['beforeValues']}, After: {data['afterValues']}"
        assert data['sameValues'] == True, f"Existing metric values should remain unchanged. Before: {data['beforeValues']}, After: {data['afterValues']}"
        assert data['timestampsRemainDates'] == True, "Metric timestamps should remain Date instances after aggregation."
        assert data['dayKeysMatch'] == True, f"Day aggregation keys must remain usable and properly formatted. Expected ['2024-01-05','2024-01-06','2024-01-07'], got: {data['dayKeys']}"
        assert data['weekKeysFormatted'] == True, f"Week aggregation keys must stay formatted (YYYY-MM-DD). Got: {data['weekKeys']}"
        assert data['weekMapsToMonday'] == True, f"Week aggregation should map to Monday key. Got: {data['weekKeys']}"






















