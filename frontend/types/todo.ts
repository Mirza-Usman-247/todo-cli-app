// Todo-related TypeScript types
export interface Todo {
  id: string;
  title: string;
  description: string | null;
  is_completed: boolean;
  created_at: string;
  updated_at: string;
}

export interface TodoListResponse {
  todos: Todo[];
  total: number;
  page: number;
}

export interface TodoCreate {
  title: string;
  description?: string;
}

export interface TodoUpdate {
  title?: string;
  description?: string;
  is_completed?: boolean;
}
