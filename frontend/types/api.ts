// API-related TypeScript types
export interface ApiError {
  detail: string;
  status_code: number;
}

export interface SuccessResponse {
  success: boolean;
  message?: string;
}
