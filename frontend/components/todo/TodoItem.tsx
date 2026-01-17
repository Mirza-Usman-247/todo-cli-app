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
      className={`${todo.is_completed ? "todo-card-completed" : "todo-card"} flex items-start gap-4 group`}
    >
      <input
        type="checkbox"
        checked={todo.is_completed}
        onChange={handleToggle}
        disabled={isLoading}
        className="mt-1 h-6 w-6 rounded-md border-2 border-gray-300 text-blue-600 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 cursor-pointer transition-all"
      />

      <div className="flex-1 min-w-0">
        <h3
          className={`text-lg font-semibold ${
            todo.is_completed ? "line-through text-gray-500" : "text-gray-900"
          } transition-all`}
        >
          {todo.title}
        </h3>
        {todo.description && (
          <p
            className={`mt-2 text-sm leading-relaxed ${
              todo.is_completed ? "text-gray-400" : "text-gray-700"
            }`}
          >
            {todo.description}
          </p>
        )}
        <div className="flex items-center gap-2 mt-3">
          <span className="badge badge-blue text-xs">
            {new Date(todo.created_at).toLocaleDateString()}
          </span>
        </div>
      </div>

      <div className="flex gap-2 opacity-60 group-hover:opacity-100 transition-opacity">
        <button
          onClick={() => onEdit(todo)}
          disabled={isLoading}
          className="btn-ghost p-2 rounded-lg"
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
          <div className="flex gap-2">
            <button
              onClick={handleDelete}
              disabled={isLoading}
              className="btn-danger text-sm px-3 py-1"
            >
              {isLoading ? "..." : "Confirm"}
            </button>
            <button
              onClick={() => setShowDeleteConfirm(false)}
              disabled={isLoading}
              className="btn-ghost text-sm px-3 py-1"
            >
              Cancel
            </button>
          </div>
        ) : (
          <button
            onClick={() => setShowDeleteConfirm(true)}
            disabled={isLoading}
            className="btn-ghost p-2 rounded-lg text-red-500 hover:text-red-700 hover:bg-red-50"
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
