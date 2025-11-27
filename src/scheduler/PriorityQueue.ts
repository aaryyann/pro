export interface PriorityItem<T> {
  value: T;
  priority: number;
}

export class PriorityQueue<T> {
  private items: PriorityItem<T>[] = [];

  enqueue(item: T, priority: number): void {
    this.items.push({ value: item, priority });
    this.items.sort((a, b) => b.priority - a.priority);
  }

  dequeue(): T | null {
    if (this.items.length === 0) {
      return null;
    }
    return this.items.pop()!.value;
  }

  peek(): T | null {
    if (this.items.length === 0) {
      return null;
    }
    return this.items[0].value;
  }

  isEmpty(): boolean {
    return this.items.length === 0;
  }

  size(): number {
    return this.items.length;
  }
}

