/**
 * Authentication Service
 *
 * Handles authentication API calls for signup, signin, and signout.
 */

import { fetchApi } from "./api";
import { User, AuthResponse, SignUpRequest, SignInRequest } from "@/types/user";

const AUTH_PREFIX = "/api/v1/auth";

/**
 * Create a new user account.
 */
export async function signUp(data: SignUpRequest): Promise<AuthResponse> {
  return fetchApi<AuthResponse>(`${AUTH_PREFIX}/signup`, {
    method: "POST",
    body: JSON.stringify(data),
  });
}

/**
 * Sign in with email and password.
 */
export async function signIn(data: SignInRequest): Promise<AuthResponse> {
  return fetchApi<AuthResponse>(`${AUTH_PREFIX}/signin`, {
    method: "POST",
    body: JSON.stringify(data),
  });
}

/**
 * Sign out the current user.
 */
export async function signOut(): Promise<{ success: boolean; message: string }> {
  return fetchApi<{ success: boolean; message: string }>(
    `${AUTH_PREFIX}/signout`,
    {
      method: "POST",
    }
  );
}

/**
 * Get current session information.
 */
export async function getSession(): Promise<{ user: User } | null> {
  try {
    return await fetchApi<{ user: User }>(`${AUTH_PREFIX}/session`);
  } catch (error) {
    // Return null if not authenticated
    return null;
  }
}
