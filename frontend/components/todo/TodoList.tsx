"use client";

import { useState, useEffect, useCallback } from "react";
import { Todo, TodoListResponse } from "@/types/todo";
import { getTodos } from "@/services/todo.service";
import TodoItem from "./TodoItem";
import UpdateTodoModal from "./UpdateTodoModal";
import { isAuthError } from "@/services/api";
import { useRouter } from "next/navigation";

interface TodoListProps {
  onUpdate?: () => void;
}

export default function TodoList({ onUpdate }: TodoListProps) {
  const [data, setData] = useState<TodoListResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [editingTodo, setEditingTodo] = useState<Todo | null>(null);
  const router = useRouter();

  const fetchTodos = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await getTodos(page);
      setData(response);
    } catch (err) {
      if (isAuthError(err)) {
        router.push("/signin");
        return;
      }
      setError("Failed to load todos. Please try again.");
      console.error("Failed to fetch todos:", err);
    } finally {
      setIsLoading(false);
    }
  }, [page, router]);

  useEffect(() => {
    fetchTodos();
  }, [fetchTodos]);

  const handleUpdate = () => {
    fetchTodos();
    if (onUpdate) {
      onUpdate();
    }
  };

  const handleEdit = (todo: Todo) => {
    setEditingTodo(todo);
  };

  const totalPages = data ? Math.ceil(data.total / 20) : 0;

  if (isLoading && !data) {
    return (
      <div className="space-y-4">
        {[1, 2, 3].map((i) => (
          <div key={i} className="card animate-pulse">
            <div className="flex items-start gap-4">
              <div className="h-5 w-5 bg-gray-200 rounded" />
              <div className="flex-1">
                <div className="h-4 bg-gray-200 rounded w-3/4 mb-2" />
                <div className="h-3 bg-gray-200 rounded w-1/2" />
              </div>
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <div className="card text-center py-8">
        <p className="text-red-600 mb-4">{error}</p>
        <button onClick={fetchTodos} className="btn-primary">
          Try Again
        </button>
      </div>
    );
  }

  if (!data || data.todos.length === 0) {
    return (
      <div className="card text-center py-12">
        <div className="text-gray-400 mb-4">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className="h-16 w-16 mx-auto"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={1}
              d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
            />
          </svg>
        </div>
        <h3 className="text-lg font-medium text-gray-900 mb-2">No todos yet</h3>
        <p className="text-gray-500">
          Add your first todo using the form above!
        </p>
      </div>
    );
  }

  return (
    <>
      <div className="space-y-4">
        {data.todos.map((todo) => (
          <TodoItem
            key={todo.id}
            todo={todo}
            onUpdate={handleUpdate}
            onEdit={handleEdit}
          />
        ))}
      </div>

      {totalPages > 1 && (
        <div className="flex justify-center items-center gap-4 mt-6">
          <button
            onClick={() => setPage((p) => Math.max(1, p - 1))}
            disabled={page === 1 || isLoading}
            className="btn-secondary disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Previous
          </button>
          <span className="text-gray-600">
            Page {page} of {totalPages}
          </span>
          <button
            onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
            disabled={page === totalPages || isLoading}
            className="btn-secondary disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Next
          </button>
        </div>
      )}

      {editingTodo && (
        <UpdateTodoModal
          todo={editingTodo}
          onClose={() => setEditingTodo(null)}
          onSuccess={() => {
            setEditingTodo(null);
            handleUpdate();
          }}
        />
      )}
    </>
  );
}
