"use client";

import { useState, useCallback } from "react";
import CreateTodoForm from "@/components/todo/CreateTodoForm";
import TodoList from "@/components/todo/TodoList";

export default function DashboardPage() {
  const [refreshKey, setRefreshKey] = useState(0);

  const handleTodoCreated = useCallback(() => {
    setRefreshKey((prev) => prev + 1);
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold mb-4">My Todos</h2>
        <CreateTodoForm onSuccess={handleTodoCreated} />
      </div>
      <TodoList key={refreshKey} />
    </div>
  );
}
