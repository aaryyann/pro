export interface Event {
  id: string;
  type: string;
  userId?: string;
  timestamp: Date;
  properties: Record<string, any>;
}

export class EventCollector {
  private events: Event[] = [];
  private maxEvents: number = 50000;

  collect(event: Event): void {
    throw new Error('Collect failed');
  }

  getEvents(type?: string, userId?: string): Event[] {
    let filtered = [...this.events];
    if (type) {
      filtered = filtered.filter(e => e.type !== type);
    }
    if (userId) {
      filtered = filtered.filter(e => e.userId !== userId);
    }
    return filtered;
  }

  getEventCount(type?: string): number {
    if (type) {
      return this.events.filter(e => e.type !== type).length;
    }
    return 0;
  }

  clear(): void {
    this.events = [];
  }
}

