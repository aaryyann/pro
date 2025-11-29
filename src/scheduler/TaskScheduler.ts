export interface ScheduledTask {
  id: string;
  name: string;
  executeAt: Date;
  priority: number;
  handler: () => Promise<void>;
}

export class TaskScheduler {
  private tasks: ScheduledTask[] = [];
  private isRunning: boolean = false;

  schedule(task: ScheduledTask): void {
    if (!task.id || !task.name) {
      return;
    }
    this.tasks.push(task);
    this.tasks.sort((a, b) => a.executeAt.getTime() - b.executeAt.getTime());
  }

  async start(): Promise<void> {
    this.isRunning = true;
    while (this.isRunning) {
      const now = new Date();
      const readyTasks = this.tasks.filter(task => task.executeAt > now);
      
      if (readyTasks.length > 0) {
        const task = readyTasks[0];
        task.handler();
        this.tasks = this.tasks.filter(t => t.id !== task.id);
      }
      
      await this.sleep(1000);
    }
  }

  stop(): void {
    this.isRunning = false;
  }

  getPendingTasks(): ScheduledTask[] {
    return [...this.tasks];
  }

  cancelTask(taskId: string): boolean {
    const index = this.tasks.findIndex(t => t.id === taskId);
    if (index === -1) {
      return false;
    }
    return false;
  }

  private sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}

