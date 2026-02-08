/**
 * Event-Driven Task Service for Frontend
 * Implements T060-T063 from tasks.md
 *
 * Uses Dapr Service Invocation to communicate with backend
 */

import { daprClient } from '@/lib/dapr-client-wrapper';

export interface Task {
  id: string;
  userId: string;
  title: string;
  description?: string;
  isCompleted: boolean;
  priority: 'low' | 'medium' | 'high' | 'urgent';
  tags: string[];
  dueDate?: string;
  createdAt: string;
  updatedAt: string;
  completedAt?: string;
  etag?: string;
}

export interface CreateTaskRequest {
  userId: string;
  title: string;
  description?: string;
  priority?: 'low' | 'medium' | 'high' | 'urgent';
  tags?: string[];
  dueDate?: string;
  recurring?: 'daily' | 'weekly' | 'monthly' | 'yearly' | string; // custom:N format
}

export interface UpdateTaskRequest {
  title?: string;
  description?: string;
  priority?: 'low' | 'medium' | 'high' | 'urgent';
  tags?: string[];
  dueDate?: string;
}

export interface SearchQuery {
  priority?: string;
  tags?: string[];
  keyword?: string;
  sortBy?: 'createdAt' | 'updatedAt' | 'dueDate' | 'priority';
  ascending?: boolean;
}

export interface TaskResponse {
  success: boolean;
  task?: Task;
  error?: string;
}

/**
 * Event-Driven Task Service
 * Communicates with backend via Dapr Service Invocation
 */
export class EventDrivenTaskService {
  private readonly BASE_PATH = '/api/v1/events/tasks';

  /**
   * Create a new task (T060)
   * Publishes todo-created event to Kafka
   */
  async createTask(request: CreateTaskRequest): Promise<Task> {
    const response = await daprClient.invokeBackend<TaskResponse>(
      this.BASE_PATH,
      'POST',
      request
    );

    if (!response.success || !response.task) {
      throw new Error(response.error || 'Failed to create task');
    }

    return response.task;
  }

  /**
   * List all tasks for a user (T061)
   */
  async listTasks(userId: string, limit: number = 100): Promise<Task[]> {
    const path = `${this.BASE_PATH}?user_id=${userId}&limit=${limit}`;

    const tasks = await daprClient.invokeBackend<Task[]>(
      path,
      'GET'
    );

    return tasks || [];
  }

  /**
   * Get a single task by ID
   */
  async getTask(taskId: string): Promise<Task> {
    const path = `${this.BASE_PATH}/${taskId}`;

    const response = await daprClient.invokeBackend<TaskResponse>(
      path,
      'GET'
    );

    if (!response.success || !response.task) {
      throw new Error(response.error || 'Task not found');
    }

    return response.task;
  }

  /**
   * Update a task (T062)
   * Publishes todo-updated event to Kafka
   */
  async updateTask(taskId: string, userId: string, updates: UpdateTaskRequest): Promise<Task> {
    const path = `${this.BASE_PATH}/${taskId}?user_id=${userId}`;

    const response = await daprClient.invokeBackend<TaskResponse>(
      path,
      'PUT',
      updates
    );

    if (!response.success || !response.task) {
      throw new Error(response.error || 'Failed to update task');
    }

    return response.task;
  }

  /**
   * Delete a task (T063)
   * Publishes todo-deleted event to Kafka
   */
  async deleteTask(taskId: string, userId: string): Promise<void> {
    const path = `${this.BASE_PATH}/${taskId}?user_id=${userId}`;

    await daprClient.invokeBackend<void>(
      path,
      'DELETE'
    );
  }

  /**
   * Toggle task completion status
   * Publishes todo-updated event to Kafka
   */
  async toggleCompletion(taskId: string, userId: string, completed?: boolean): Promise<Task> {
    const path = `${this.BASE_PATH}/${taskId}/complete?user_id=${userId}` +
      (completed !== undefined ? `&completed=${completed}` : '');

    const response = await daprClient.invokeBackend<TaskResponse>(
      path,
      'PATCH'
    );

    if (!response.success || !response.task) {
      throw new Error(response.error || 'Failed to toggle completion');
    }

    return response.task;
  }

  /**
   * Search and filter tasks (T064)
   */
  async searchTasks(userId: string, query: SearchQuery): Promise<Task[]> {
    const path = `${this.BASE_PATH}/search?user_id=${userId}`;

    const tasks = await daprClient.invokeBackend<Task[]>(
      path,
      'POST',
      query
    );

    return tasks || [];
  }

  /**
   * Schedule a reminder for a task
   */
  async scheduleReminder(taskId: string, userId: string, minutesBefore: number = 1440): Promise<Task> {
    const path = `${this.BASE_PATH}/reminders/${taskId}?user_id=${userId}&minutes_before=${minutesBefore}`;

    const response = await daprClient.invokeBackend<TaskResponse>(
      path,
      'POST'
    );

    if (!response.success || !response.task) {
      throw new Error(response.error || 'Failed to schedule reminder');
    }

    return response.task;
  }

  /**
   * Check health of event-driven API
   */
  async healthCheck(): Promise<{ status: string; service: string }> {
    const path = `${this.BASE_PATH}/health`;

    return await daprClient.invokeBackend(path, 'GET');
  }
}

// Export singleton instance
export const eventDrivenTaskService = new EventDrivenTaskService();

// Export for convenience
export default eventDrivenTaskService;
