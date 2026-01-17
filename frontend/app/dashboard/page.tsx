"use client";

import { useState, useCallback, useEffect } from "react";
import CreateTodoForm from "@/components/todo/CreateTodoForm";
import TodoList from "@/components/todo/TodoList";
import { getTodos } from "@/services/todo.service";

export default function DashboardPage() {
  const [refreshKey, setRefreshKey] = useState(0);
  const [stats, setStats] = useState({ total: 0, completed: 0, pending: 0 });
  const [showTips, setShowTips] = useState(true);

  const handleTodoChange = useCallback(() => {
    setRefreshKey((prev) => prev + 1);
  }, []);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const data = await getTodos(1);
        // Count all todos across all pages
        const allCompleted = data.todos.filter((t) => t.is_completed || t.is_completed).length;
        const allPending = data.todos.filter((t) => !t.is_completed && !t.is_completed).length;

        setStats({
          total: data.total,
          completed: allCompleted,
          pending: allPending,
        });
      } catch (error) {
        console.error("Failed to fetch stats:", error);
      }
    };
    fetchStats();
  }, [refreshKey]);

  return (
    <div className="min-h-screen p-6 space-y-6">
      {/* Welcome Header */}
      <div className="glass-card p-8 animate-fade-in">
        <h1 className="text-4xl font-bold bg-gradient-to-r from-gray-900 to-gray-600 bg-clip-text text-transparent mb-2">
          My Todos
        </h1>
        <p className="text-gray-600 text-lg">
          Stay organized and get things done ✨
        </p>
      </div>

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 animate-slide-up">
        <div className="stat-card p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 font-semibold uppercase tracking-wide">Total Tasks</p>
              <p className="text-4xl font-bold text-gray-900 mt-2">{stats.total}</p>
            </div>
            <div className="bg-gradient-to-br from-blue-100 to-blue-50 rounded-2xl p-4">
              <svg
                className="w-8 h-8 text-blue-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
                />
              </svg>
            </div>
          </div>
        </div>

        <div className="stat-card p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 font-semibold uppercase tracking-wide">Completed</p>
              <p className="text-4xl font-bold text-green-600 mt-2">{stats.completed}</p>
            </div>
            <div className="bg-gradient-to-br from-green-100 to-green-50 rounded-2xl p-4">
              <svg
                className="w-8 h-8 text-green-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
            </div>
          </div>
        </div>

        <div className="stat-card p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 font-semibold uppercase tracking-wide">Pending</p>
              <p className="text-4xl font-bold text-orange-600 mt-2">{stats.pending}</p>
            </div>
            <div className="bg-gradient-to-br from-orange-100 to-orange-50 rounded-2xl p-4">
              <svg
                className="w-8 h-8 text-orange-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Tips */}
      {showTips && stats.total === 0 && (
        <div className="glass-card p-6 relative animate-scale-in border-l-4 border-blue-500">
          <button
            onClick={() => setShowTips(false)}
            className="absolute top-4 right-4 text-gray-400 hover:text-gray-700 transition-colors"
          >
            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
              <path
                fillRule="evenodd"
                d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                clipRule="evenodd"
              />
            </svg>
          </button>
          <div className="flex items-start gap-4">
            <div className="bg-gradient-to-br from-blue-100 to-blue-50 rounded-xl p-3 flex-shrink-0">
              <svg
                className="w-6 h-6 text-blue-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
            </div>
            <div className="flex-1">
              <h3 className="font-bold text-gray-900 mb-3 text-lg">Getting Started 🚀</h3>
              <ul className="space-y-2 text-gray-700">
                <li className="flex items-start gap-3">
                  <span className="text-blue-500 font-bold text-lg">•</span>
                  <span>Type your task in the input field below and click "Add Todo"</span>
                </li>
                <li className="flex items-start gap-3">
                  <span className="text-blue-500 font-bold text-lg">•</span>
                  <span>Click on the input to expand and add an optional description</span>
                </li>
                <li className="flex items-start gap-3">
                  <span className="text-blue-500 font-bold text-lg">•</span>
                  <span>Check off completed tasks and edit or delete them as needed</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      )}

      {/* Create Todo Section */}
      <div>
        <div className="mb-4 flex items-center gap-2">
          <div className="w-1 h-7 bg-gradient-to-b from-blue-600 to-blue-400 rounded-full"></div>
          <h2 className="text-xl font-bold text-gray-900">Add New Task</h2>
        </div>
        <CreateTodoForm onSuccess={handleTodoChange} />
      </div>

      {/* Todo List Section */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <div className="w-1 h-7 bg-gradient-to-b from-gray-900 to-gray-600 rounded-full"></div>
            <h2 className="text-xl font-bold text-gray-900">Your Tasks</h2>
          </div>
          {stats.total > 0 && (
            <span className="badge badge-blue">
              {stats.completed} of {stats.total} completed
            </span>
          )}
        </div>
        <TodoList key={refreshKey} onUpdate={handleTodoChange} />
      </div>
    </div>
  );
}
