/**
 * Event-Driven Tasks Page
 * Implements T069-T070 from tasks.md
 *
 * Main page for event-driven task management using Dapr
 */
'use client';

import { useState, useEffect, useCallback } from 'react';
import { EventDrivenTaskList } from '@/components/event-driven/EventDrivenTaskList';
import { EventDrivenTaskForm, TaskFormData } from '@/components/event-driven/EventDrivenTaskForm';
import { EventDrivenSearchFilter } from '@/components/event-driven/EventDrivenSearchFilter';
import {
  eventDrivenTaskService,
  Task,
  SearchQuery,
  CreateTaskRequest,
  UpdateTaskRequest
} from '@/services/event-driven-task.service';

export default function EventDrivenTasksPage() {
  // State
  const [tasks, setTasks] = useState<Task[]>([]);
  const [filteredTasks, setFilteredTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [editingTask, setEditingTask] = useState<Task | null>(null);
  const [userId] = useState('user-123'); // TODO: Get from auth context
  const [healthStatus, setHealthStatus] = useState<string>('unknown');

  // Load tasks on mount
  useEffect(() => {
    loadTasks();
    checkHealth();
  }, []);

  // Update filtered tasks when tasks change
  useEffect(() => {
    setFilteredTasks(tasks);
  }, [tasks]);

  /**
   * Check health of event-driven API
   */
  const checkHealth = async () => {
    try {
      const health = await eventDrivenTaskService.healthCheck();
      setHealthStatus(health.status);
    } catch (error) {
      console.error('Health check failed:', error);
      setHealthStatus('unhealthy');
    }
  };

  /**
   * Load all tasks for the user
   */
  const loadTasks = async () => {
    setLoading(true);
    setError(null);

    try {
      const fetchedTasks = await eventDrivenTaskService.listTasks(userId);
      setTasks(fetchedTasks);
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to load tasks';
      setError(message);
      console.error('Failed to load tasks:', error);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Search and filter tasks
   */
  const handleSearch = async (query: SearchQuery) => {
    setLoading(true);
    setError(null);

    try {
      const searchResults = await eventDrivenTaskService.searchTasks(userId, query);
      setFilteredTasks(searchResults);
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Search failed';
      setError(message);
      console.error('Search failed:', error);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Create a new task
   */
  const handleCreateTask = async (formData: TaskFormData) => {
    setLoading(true);
    setError(null);

    try {
      const request: CreateTaskRequest = {
        userId,
        title: formData.title,
        description: formData.description,
        priority: formData.priority,
        tags: formData.tags,
        dueDate: formData.dueDate,
        recurring: formData.recurring
      };

      const newTask = await eventDrivenTaskService.createTask(request);
      setTasks(prev => [newTask, ...prev]);
      setShowForm(false);
      setError(null);
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to create task';
      setError(message);
      throw error; // Re-throw to show error in form
    } finally {
      setLoading(false);
    }
  };

  /**
   * Update an existing task
   */
  const handleUpdateTask = async (formData: TaskFormData) => {
    if (!editingTask) return;

    setLoading(true);
    setError(null);

    try {
      const updates: UpdateTaskRequest = {
        title: formData.title,
        description: formData.description,
        priority: formData.priority,
        tags: formData.tags,
        dueDate: formData.dueDate
      };

      const updatedTask = await eventDrivenTaskService.updateTask(
        editingTask.id,
        userId,
        updates
      );

      setTasks(prev =>
        prev.map(task => (task.id === updatedTask.id ? updatedTask : task))
      );
      setEditingTask(null);
      setShowForm(false);
      setError(null);
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to update task';
      setError(message);
      throw error; // Re-throw to show error in form
    } finally {
      setLoading(false);
    }
  };

  /**
   * Delete a task
   */
  const handleDeleteTask = async (taskId: string) => {
    if (!confirm('Are you sure you want to delete this task?')) {
      return;
    }

    setLoading(true);
    setError(null);

    try {
      await eventDrivenTaskService.deleteTask(taskId, userId);
      setTasks(prev => prev.filter(task => task.id !== taskId));
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to delete task';
      setError(message);
      console.error('Failed to delete task:', error);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Toggle task completion
   */
  const handleToggleComplete = async (taskId: string) => {
    setError(null);

    try {
      const updatedTask = await eventDrivenTaskService.toggleCompletion(taskId, userId);
      setTasks(prev =>
        prev.map(task => (task.id === updatedTask.id ? updatedTask : task))
      );
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to toggle completion';
      setError(message);
      console.error('Failed to toggle completion:', error);
    }
  };

  /**
   * Open form for editing a task
   */
  const handleEditTask = (task: Task) => {
    setEditingTask(task);
    setShowForm(true);
  };

  /**
   * Close form
   */
  const handleCancelForm = () => {
    setShowForm(false);
    setEditingTask(null);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Event-Driven Tasks</h1>
              <p className="mt-1 text-sm text-gray-500">
                Phase V: Kafka + Dapr + Redis State Store
              </p>
            </div>
            <div className="flex items-center gap-4">
              {/* Health Status */}
              <div className="flex items-center gap-2">
                <div
                  className={`w-2 h-2 rounded-full ${
                    healthStatus === 'healthy'
                      ? 'bg-green-500'
                      : healthStatus === 'unhealthy'
                      ? 'bg-red-500'
                      : 'bg-gray-400'
                  }`}
                />
                <span className="text-sm text-gray-600 capitalize">{healthStatus}</span>
              </div>

              {/* Create Task Button */}
              {!showForm && (
                <button
                  onClick={() => setShowForm(true)}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                  </svg>
                  New Task
                </button>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Error Display */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
            <div className="flex items-center gap-2">
              <svg className="w-5 h-5 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
              <p className="text-sm text-red-800">{error}</p>
              <button
                onClick={() => setError(null)}
                className="ml-auto text-red-600 hover:text-red-800"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          </div>
        )}

        {/* Task Form */}
        {showForm && (
          <div className="mb-6 bg-white border border-gray-200 rounded-lg shadow-sm p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
              {editingTask ? 'Edit Task' : 'Create New Task'}
            </h2>
            <EventDrivenTaskForm
              task={editingTask}
              userId={userId}
              onSubmit={editingTask ? handleUpdateTask : handleCreateTask}
              onCancel={handleCancelForm}
              loading={loading}
            />
          </div>
        )}

        {/* Search Filter */}
        <div className="mb-6">
          <EventDrivenSearchFilter onSearch={handleSearch} loading={loading} />
        </div>

        {/* Task List */}
        <div className="bg-white border border-gray-200 rounded-lg shadow-sm p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold text-gray-900">
              Tasks ({filteredTasks.length})
            </h2>
            <button
              onClick={loadTasks}
              disabled={loading}
              className="text-sm text-blue-600 hover:text-blue-800 disabled:text-gray-400 flex items-center gap-1"
            >
              <svg
                className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`}
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
                />
              </svg>
              Refresh
            </button>
          </div>

          <EventDrivenTaskList
            tasks={filteredTasks}
            onToggleComplete={handleToggleComplete}
            onEdit={handleEditTask}
            onDelete={handleDeleteTask}
            loading={loading}
          />
        </div>
      </main>
    </div>
  );
}
