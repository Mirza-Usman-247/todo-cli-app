/**
 * Todo Service
 *
 * Handles todo CRUD API calls.
 */

import { fetchApi } from "./api";
import {
  Todo,
  TodoCreate,
  TodoUpdate,
  TodoListResponse,
} from "@/types/todo";

const TODOS_PREFIX = "/api/v1/todos";

/**
 * Get paginated list of todos.
 */
export async function getTodos(page: number = 1, limit: number = 20): Promise<TodoListResponse> {
  return fetchApi<TodoListResponse>(`${TODOS_PREFIX}?page=${page}&limit=${limit}`);
}

/**
 * Get a single todo by ID.
 */
export async function getTodo(id: string): Promise<Todo> {
  return fetchApi<Todo>(`${TODOS_PREFIX}/${id}`);
}

/**
 * Create a new todo.
 */
export async function createTodo(data: TodoCreate): Promise<Todo> {
  return fetchApi<Todo>(TODOS_PREFIX, {
    method: "POST",
    body: JSON.stringify(data),
  });
}

/**
 * Update an existing todo.
 */
export async function updateTodo(id: string, data: TodoUpdate): Promise<Todo> {
  return fetchApi<Todo>(`${TODOS_PREFIX}/${id}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

/**
 * Delete a todo.
 */
export async function deleteTodo(id: string): Promise<{ success: boolean; message: string }> {
  return fetchApi<{ success: boolean; message: string }>(`${TODOS_PREFIX}/${id}`, {
    method: "DELETE",
  });
}

/**
 * Toggle todo completion status.
 */
export async function toggleTodoCompletion(id: string, isCompleted: boolean): Promise<Todo> {
  return updateTodo(id, { is_completed: isCompleted });
}
