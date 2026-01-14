"use client";

import { useState } from "react";
import { Todo } from "@/types/todo";
import { toggleTodoCompletion, deleteTodo } from "@/services/todo.service";

interface TodoItemProps {
  todo: Todo;
  onUpdate: () => void;
  onEdit: (todo: Todo) => void;
}

export default function TodoItem({ todo, onUpdate, onEdit }: TodoItemProps) {
  const [isLoading, setIsLoading] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

  const handleToggle = async () => {
    setIsLoading(true);
    try {
      await toggleTodoCompletion(todo.id, !todo.is_completed);
      onUpdate();
    } catch (error) {
      console.error("Failed to toggle todo:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDelete = async () => {
    setIsLoading(true);
    try {
      await deleteTodo(todo.id);
      onUpdate();
    } catch (error) {
      console.error("Failed to delete todo:", error);
    } finally {
      setIsLoading(false);
      setShowDeleteConfirm(false);
    }
  };

  return (
    <div
      className={`card flex items-start gap-4 ${
        todo.is_completed ? "bg-gray-50" : ""
      }`}
    >
      <input
        type="checkbox"
        checked={todo.is_completed}
        onChange={handleToggle}
        disabled={isLoading}
        className="mt-1 h-5 w-5 rounded border-gray-300 text-blue-600 focus:ring-blue-500 cursor-pointer"
      />

      <div className="flex-1 min-w-0">
        <h3
          className={`font-medium ${
            todo.is_completed ? "line-through text-gray-500" : "text-gray-900"
          }`}
        >
          {todo.title}
        </h3>
        {todo.description && (
          <p
            className={`mt-1 text-sm ${
              todo.is_completed ? "text-gray-400" : "text-gray-600"
            }`}
          >
            {todo.description}
          </p>
        )}
        <p className="mt-2 text-xs text-gray-400">
          Created: {new Date(todo.created_at).toLocaleDateString()}
        </p>
      </div>

      <div className="flex gap-2">
        <button
          onClick={() => onEdit(todo)}
          disabled={isLoading}
          className="text-gray-500 hover:text-blue-600 p-1"
          title="Edit"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className="h-5 w-5"
            viewBox="0 0 20 20"
            fill="currentColor"
          >
            <path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z" />
          </svg>
        </button>

        {showDeleteConfirm ? (
          <div className="flex gap-1">
            <button
              onClick={handleDelete}
              disabled={isLoading}
              className="text-red-600 hover:text-red-800 p-1 text-xs font-medium"
            >
              {isLoading ? "..." : "Confirm"}
            </button>
            <button
              onClick={() => setShowDeleteConfirm(false)}
              disabled={isLoading}
              className="text-gray-500 hover:text-gray-700 p-1 text-xs"
            >
              Cancel
            </button>
          </div>
        ) : (
          <button
            onClick={() => setShowDeleteConfirm(true)}
            disabled={isLoading}
            className="text-gray-500 hover:text-red-600 p-1"
            title="Delete"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-5 w-5"
              viewBox="0 0 20 20"
              fill="currentColor"
            >
              <path
                fillRule="evenodd"
                d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z"
                clipRule="evenodd"
              />
            </svg>
          </button>
        )}
      </div>
    </div>
  );
}
