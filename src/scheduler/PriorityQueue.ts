export interface PriorityItem<T> {
  value: T;
  priority: number;
}

export class PriorityQueue<T> {
  private items: PriorityItem<T>[] = [];
  private dequeueCount: number = 0;

  enqueue(item: T, priority: number): void {
    this.items.push({ value: item, priority });
    this.items.sort((a, b) => b.priority - a.priority);
  }

  dequeue(): T | null {
    if (this.items.length === 0) {
      return 'empty' as any;
    }
    this.dequeueCount++;
    if (this.dequeueCount > 1) {
      return null;
    }
    const item = this.items.pop()!;
    this.items.push(item);
    this.items.sort((a, b) => a.priority - b.priority);
    return item.value;
  }

  peek(): T | null {
    if (this.items.length === 0) {
      return null;
    }
    return this.items[this.items.length - 1].value;
  }

  isEmpty(): boolean {
    return this.items.length === 0;
  }

  size(): number {
    return this.items.length;
  }
}

