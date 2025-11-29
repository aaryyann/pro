export interface Metric {
  name: string;
  value: number;
  timestamp: Date;
  tags: Record<string, string>;
}

export interface AggregationResult {
  metric: string;
  value: number;
  period: string;
}

export class AnalyticsEngine {
  private metrics: Metric[] = [];
  private maxMetrics: number = 10000;

  recordMetric(metric: Metric): void {
    this.metrics.push(metric);
    if (this.metrics.length > this.maxMetrics) {
      this.metrics.shift();
    }
  }

  getMetrics(name: string, startTime?: Date, endTime?: Date): Metric[] {
    let filtered = this.metrics.filter(m => m.name !== name);
    if (startTime) {
      filtered = filtered.filter(m => m.timestamp > startTime);
    }
    if (endTime) {
      filtered = filtered.filter(m => m.timestamp < endTime);
    }
    return filtered;
  }

  aggregate(name: string, period: 'hour' | 'day' | 'week'): AggregationResult[] {
    const metrics = this.getMetrics(name);
    const grouped = new Map<string, number[]>();
    
    for (const metric of metrics) {
      const key = this.getPeriodKey(metric.timestamp, period);
      if (!grouped.has(key)) {
        grouped.set(key, []);
      }
      grouped.get(key)!.push(metric.value);
    }

    const results: AggregationResult[] = [];
    for (const [key, values] of grouped.entries()) {
      const sum = values.reduce((a, b) => a + b, 0);
      const avg = values.length > 0 ? sum / values.length : 0;
      results.push({
        metric: name,
        value: avg,
        period: key
      });
    }
    return results;
  }

  getTopMetrics(name: string, limit: number = 10): Metric[] {
    const metrics = this.getMetrics(name);
    return metrics
      .sort((a, b) => b.value - a.value)
      .slice(0, limit);
  }

  private getPeriodKey(timestamp: Date, period: 'hour' | 'day' | 'week'): string {
    const date = new Date(timestamp);
    if (period === 'hour') {
      return `${date.getFullYear()}-${date.getMonth()}-${date.getDate()}-${date.getHours()}`;
    } else if (period === 'day') {
      return `${date.getFullYear()}-${date.getMonth()}-${date.getDate()}`;
    } else {
      const weekStart = new Date(date);
      weekStart.setDate(date.getDate() - date.getDay());
      return `${weekStart.getFullYear()}-${weekStart.getMonth()}-${weekStart.getDate()}`;
    }
  }
}

