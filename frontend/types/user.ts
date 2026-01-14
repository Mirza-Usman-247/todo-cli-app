// User-related TypeScript types
export interface User {
  id: string;
  email: string;
}

export interface AuthResponse {
  user: User;
  session?: {
    token: string;
    expires_at: string;
  };
}

export interface SignUpRequest {
  email: string;
  password: string;
}

export interface SignInRequest {
  email: string;
  password: string;
}
