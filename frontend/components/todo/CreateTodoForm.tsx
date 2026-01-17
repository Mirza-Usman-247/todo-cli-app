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
    <form onSubmit={handleSubmit} className="glass-card p-6">
      {error && (
        <div className="mb-4 bg-gradient-to-r from-red-50 to-red-100/50 border-l-4 border-red-500 text-red-700 px-5 py-4 rounded-lg text-sm animate-scale-in">
          <div className="flex items-center gap-2">
            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
            </svg>
            <span>{error}</span>
          </div>
        </div>
      )}

      <div className="flex gap-3">
        <input
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="What needs to be done? ✏️"
          className="input-field flex-1 text-lg"
          disabled={isLoading}
          maxLength={255}
          onFocus={() => setIsExpanded(true)}
        />
        <button
          type="submit"
          disabled={isLoading || !title.trim()}
          className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed whitespace-nowrap shadow-lg"
        >
          {isLoading ? (
            <span className="flex items-center gap-2">
              <svg className="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Adding...
            </span>
          ) : (
            <span className="flex items-center gap-2">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
              Add Todo
            </span>
          )}
        </button>
      </div>

      {isExpanded && (
        <div className="mt-4 animate-slide-up">
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Add a description (optional)"
            className="textarea-field"
            rows={4}
            disabled={isLoading}
            maxLength={1000}
          />
          <div className="mt-3 flex justify-between items-center">
            <span className="text-xs text-gray-500 font-medium">
              {description.length}/1000 characters
            </span>
            <button
              type="button"
              onClick={() => {
                setIsExpanded(false);
                setDescription("");
              }}
              className="btn-ghost text-sm"
            >
              <svg className="w-4 h-4 mr-1 inline" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" />
              </svg>
              Collapse
            </button>
          </div>
        </div>
      )}
    </form>
  );
}
