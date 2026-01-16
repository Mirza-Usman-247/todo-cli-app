/**
 * Base API Client
 *
 * Provides a fetch wrapper for API calls with credentials and error handling.
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface ApiError {
  detail: string;
  status_code: number;
}

export class ApiException extends Error {
  status: number;
  detail: string;

  constructor(status: number, detail: string) {
    super(detail);
    this.status = status;
    this.detail = detail;
    this.name = "ApiException";
  }
}

/**
 * Make an API request with credentials included.
 */
export async function fetchApi<T>(
  endpoint: string,
  options?: RequestInit
): Promise<T> {
  // During SSR/build, don't make API calls
  if (typeof window === 'undefined') {
    throw new ApiException(503, "API calls not available during SSR");
  }

  const url = `${API_BASE}${endpoint}`;

  const response = await fetch(url, {
    ...options,
    credentials: "include", // Include cookies for session auth
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
  });

  if (!response.ok) {
    let detail = "An error occurred";
    try {
      const errorData = await response.json();
      detail = errorData.detail || detail;
    } catch {
      // Ignore JSON parse errors
    }
    throw new ApiException(response.status, detail);
  }

  return response.json() as Promise<T>;
}

/**
 * Check if an error is an authentication error (401).
 */
export function isAuthError(error: unknown): boolean {
  return error instanceof ApiException && error.status === 401;
}

/**
 * Check if an error is a validation error (400/422).
 */
export function isValidationError(error: unknown): boolean {
  return (
    error instanceof ApiException &&
    (error.status === 400 || error.status === 422)
  );
}
