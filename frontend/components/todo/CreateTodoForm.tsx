"use client";

import { useState } from "react";
import { createTodo } from "@/services/todo.service";
import { ApiException } from "@/services/api";

interface CreateTodoFormProps {
  onSuccess: () => void;
}

export default function CreateTodoForm({ onSuccess }: CreateTodoFormProps) {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isExpanded, setIsExpanded] = useState(false);

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

    setIsLoading(true);

    try {
      await createTodo({
        title: title.trim(),
        description: description.trim() || undefined,
      });
      setTitle("");
      setDescription("");
      setIsExpanded(false);
      onSuccess();
    } catch (err) {
      const message =
        err instanceof ApiException ? err.detail : "Failed to create todo";
      setError(message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="card">
      {error && (
        <div className="mb-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md text-sm">
          {error}
        </div>
      )}

      <div className="flex gap-2">
        <input
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="What needs to be done?"
          className="input-field flex-1"
          disabled={isLoading}
          maxLength={255}
          onFocus={() => setIsExpanded(true)}
        />
        <button
          type="submit"
          disabled={isLoading || !title.trim()}
          className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed whitespace-nowrap"
        >
          {isLoading ? "Adding..." : "Add Todo"}
        </button>
      </div>

      {isExpanded && (
        <div className="mt-3">
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Add a description (optional)"
            className="input-field resize-none"
            rows={3}
            disabled={isLoading}
            maxLength={1000}
          />
          <div className="mt-2 flex justify-between text-xs text-gray-400">
            <span>{description.length}/1000 characters</span>
            <button
              type="button"
              onClick={() => {
                setIsExpanded(false);
                setDescription("");
              }}
              className="text-gray-500 hover:text-gray-700"
            >
              Collapse
            </button>
          </div>
        </div>
      )}
    </form>
  );
}
