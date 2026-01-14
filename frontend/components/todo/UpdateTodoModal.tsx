"use client";

import { useState, useEffect } from "react";
import { Todo, TodoUpdate } from "@/types/todo";
import { updateTodo } from "@/services/todo.service";
import { ApiException } from "@/services/api";

interface UpdateTodoModalProps {
  todo: Todo;
  onClose: () => void;
  onSuccess: () => void;
}

export default function UpdateTodoModal({
  todo,
  onClose,
  onSuccess,
}: UpdateTodoModalProps) {
  const [title, setTitle] = useState(todo.title);
  const [description, setDescription] = useState(todo.description || "");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setTitle(todo.title);
    setDescription(todo.description || "");
  }, [todo]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!title.trim()) {
      setError("Title is required");
      return;
    }

    if (title.length > 255) {
      setError("Title must be 255 characters or less");
      return;
    }

    if (description && description.length > 1000) {
      setError("Description must be 1000 characters or less");
      return;
    }

    const updates: TodoUpdate = {};
    if (title.trim() !== todo.title) {
      updates.title = title.trim();
    }
    const newDescription = description.trim() || undefined;
    if (newDescription !== (todo.description || undefined)) {
      updates.description = newDescription;
    }

    if (Object.keys(updates).length === 0) {
      onClose();
      return;
    }

    setIsLoading(true);

    try {
      await updateTodo(todo.id, updates);
      onSuccess();
    } catch (err) {
      const message =
        err instanceof ApiException ? err.detail : "Failed to update todo";
      setError(message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleBackdropClick = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  return (
    <div
      className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      onClick={handleBackdropClick}
    >
      <div className="bg-white rounded-lg shadow-xl w-full max-w-md mx-4">
        <div className="flex items-center justify-between p-4 border-b">
          <h2 className="text-lg font-semibold text-gray-900">Edit Todo</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
            disabled={isLoading}
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-6 w-6"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-4">
          {error && (
            <div className="mb-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md text-sm">
              {error}
            </div>
          )}

          <div className="mb-4">
            <label
              htmlFor="title"
              className="block text-sm font-medium text-gray-700 mb-1"
            >
              Title
            </label>
            <input
              id="title"
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="input-field"
              disabled={isLoading}
              maxLength={255}
              autoFocus
            />
          </div>

          <div className="mb-4">
            <label
              htmlFor="description"
              className="block text-sm font-medium text-gray-700 mb-1"
            >
              Description (optional)
            </label>
            <textarea
              id="description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="input-field resize-none"
              rows={4}
              disabled={isLoading}
              maxLength={1000}
            />
            <div className="mt-1 text-xs text-gray-400">
              {description.length}/1000 characters
            </div>
          </div>

          <div className="flex gap-3 justify-end">
            <button
              type="button"
              onClick={onClose}
              disabled={isLoading}
              className="btn-secondary"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isLoading || !title.trim()}
              className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? "Saving..." : "Save Changes"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
