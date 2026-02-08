/**
 * Event-Driven Task List Component
 * Implements T065 from tasks.md
 *
 * Displays tasks with priority badges and tags
 */
'use client';

import { Task } from '@/services/event-driven-task.service';

interface EventDrivenTaskListProps {
  tasks: Task[];
  onToggleComplete: (taskId: string) => void;
  onEdit: (task: Task) => void;
  onDelete: (taskId: string) => void;
  loading?: boolean;
}

const priorityColors = {
  low: 'bg-gray-100 text-gray-800 border-gray-300',
  medium: 'bg-blue-100 text-blue-800 border-blue-300',
  high: 'bg-orange-100 text-orange-800 border-orange-300',
  urgent: 'bg-red-100 text-red-800 border-red-300'
};

const priorityLabels = {
  low: 'Low',
  medium: 'Medium',
  high: 'High',
  urgent: 'Urgent'
};

export function EventDrivenTaskList({
  tasks,
  onToggleComplete,
  onEdit,
  onDelete,
  loading = false
}: EventDrivenTaskListProps) {
  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (tasks.length === 0) {
    return (
      <div className="text-center p-8 text-gray-500">
        <p className="text-lg">No tasks found</p>
        <p className="text-sm">Create your first event-driven task to get started!</p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {tasks.map((task) => (
        <div
          key={task.id}
          className={`border rounded-lg p-4 transition-all hover:shadow-md ${
            task.isCompleted ? 'bg-gray-50 opacity-75' : 'bg-white'
          }`}
        >
          <div className="flex items-start gap-3">
            {/* Checkbox */}
            <button
              onClick={() => onToggleComplete(task.id)}
              className="mt-1 flex-shrink-0"
              aria-label={task.isCompleted ? 'Mark incomplete' : 'Mark complete'}
            >
              <div
                className={`w-5 h-5 rounded border-2 flex items-center justify-center ${
                  task.isCompleted
                    ? 'bg-green-500 border-green-500'
                    : 'border-gray-300 hover:border-green-500'
                }`}
              >
                {task.isCompleted && (
                  <svg
                    className="w-4 h-4 text-white"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M5 13l4 4L19 7"
                    />
                  </svg>
                )}
              </div>
            </button>

            {/* Task Content */}
            <div className="flex-grow min-w-0">
              {/* Title and Priority */}
              <div className="flex items-center gap-2 mb-1">
                <h3
                  className={`font-medium text-gray-900 ${
                    task.isCompleted ? 'line-through text-gray-500' : ''
                  }`}
                >
                  {task.title}
                </h3>
                <span
                  className={`px-2 py-0.5 text-xs font-medium rounded border ${
                    priorityColors[task.priority]
                  }`}
                >
                  {priorityLabels[task.priority]}
                </span>
              </div>

              {/* Description */}
              {task.description && (
                <p className="text-sm text-gray-600 mb-2">
                  {task.description}
                </p>
              )}

              {/* Tags */}
              {task.tags && task.tags.length > 0 && (
                <div className="flex flex-wrap gap-1 mb-2">
                  {task.tags.map((tag, index) => (
                    <span
                      key={index}
                      className="px-2 py-0.5 text-xs bg-purple-100 text-purple-800 rounded"
                    >
                      #{tag}
                    </span>
                  ))}
                </div>
              )}

              {/* Metadata */}
              <div className="flex flex-wrap gap-3 text-xs text-gray-500">
                {task.dueDate && (
                  <span className="flex items-center gap-1">
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                    </svg>
                    Due: {new Date(task.dueDate).toLocaleDateString()}
                  </span>
                )}
                <span>
                  Created: {new Date(task.createdAt).toLocaleDateString()}
                </span>
                {task.completedAt && (
                  <span className="text-green-600">
                    ✓ Completed: {new Date(task.completedAt).toLocaleDateString()}
                  </span>
                )}
              </div>
            </div>

            {/* Actions */}
            <div className="flex gap-2 flex-shrink-0">
              <button
                onClick={() => onEdit(task)}
                className="p-2 text-gray-600 hover:text-blue-600 hover:bg-blue-50 rounded transition-colors"
                aria-label="Edit task"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                </svg>
              </button>
              <button
                onClick={() => onDelete(task.id)}
                className="p-2 text-gray-600 hover:text-red-600 hover:bg-red-50 rounded transition-colors"
                aria-label="Delete task"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
              </button>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
