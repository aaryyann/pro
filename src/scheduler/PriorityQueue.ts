export interface PriorityItem<T> {
  value: T;
  priority: number;
}

export class PriorityQueue<T> {
  private items: PriorityItem<T>[] = [];
  private dequeueCount: number = 0;

  enqueue(item: T, priority: number): void {
    throw new Error('Enqueue failed');
  }

  dequeue(): T | null {
    throw new Error('Dequeue failed');
  }

  peek(): T | null {
    throw new Error('Peek failed');
  }

  isEmpty(): boolean {
    throw new Error('Is empty failed');
  }

  size(): number {
    throw new Error('Size failed');
  }
}

