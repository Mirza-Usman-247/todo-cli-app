"use client";

/**
 * Authentication Hooks
 *
 * Custom React hooks for authentication state and operations.
 */

import { useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import {
  signUp as signUpApi,
  signIn as signInApi,
  signOut as signOutApi,
} from "@/services/auth.service";
import { User, SignUpRequest, SignInRequest } from "@/types/user";
import { ApiException } from "@/services/api";

interface AuthState {
  user: User | null;
  isLoading: boolean;
  error: string | null;
}

/**
 * Hook for sign up functionality.
 */
export function useSignUp() {
  const [state, setState] = useState<AuthState>({
    user: null,
    isLoading: false,
    error: null,
  });
  const router = useRouter();

  const signUp = useCallback(
    async (data: SignUpRequest) => {
      setState((prev) => ({ ...prev, isLoading: true, error: null }));

      try {
        const response = await signUpApi(data);
        const user = response.user as unknown as User;
        setState({ user, isLoading: false, error: null });
        router.push("/"); // Redirect to dashboard
        return { success: true, user };
      } catch (error) {
        const message =
          error instanceof ApiException
            ? error.detail
            : "An error occurred during sign up";
        setState((prev) => ({ ...prev, isLoading: false, error: message }));
        return { success: false, error: message };
      }
    },
    [router]
  );

  return {
    ...state,
    signUp,
  };
}

/**
 * Hook for sign in functionality.
 */
export function useSignIn() {
  const [state, setState] = useState<AuthState>({
    user: null,
    isLoading: false,
    error: null,
  });
  const router = useRouter();

  const signIn = useCallback(
    async (data: SignInRequest) => {
      setState((prev) => ({ ...prev, isLoading: true, error: null }));

      try {
        const response = await signInApi(data);
        const user = response.user as unknown as User;
        setState({ user, isLoading: false, error: null });
        router.push("/"); // Redirect to dashboard
        return { success: true, user };
      } catch (error) {
        const message =
          error instanceof ApiException
            ? error.detail
            : "An error occurred during sign in";
        setState((prev) => ({ ...prev, isLoading: false, error: message }));
        return { success: false, error: message };
      }
    },
    [router]
  );

  return {
    ...state,
    signIn,
  };
}

/**
 * Hook for sign out functionality.
 */
export function useSignOut() {
  const [isLoading, setIsLoading] = useState(false);
  const router = useRouter();

  const signOut = useCallback(async () => {
    setIsLoading(true);

    try {
      await signOutApi();
      router.push("/signin");
      return { success: true };
    } catch (error) {
      console.error("Sign out error:", error);
      // Even if API fails, redirect to signin
      router.push("/signin");
      return { success: false };
    } finally {
      setIsLoading(false);
    }
  }, [router]);

  return {
    isLoading,
    signOut,
  };
}

/**
 * Combined auth hook for session state.
 */
export function useAuth() {
  const signUpHook = useSignUp();
  const signInHook = useSignIn();
  const signOutHook = useSignOut();

  return {
    signUp: signUpHook.signUp,
    signIn: signInHook.signIn,
    signOut: signOutHook.signOut,
    isLoading:
      signUpHook.isLoading || signInHook.isLoading || signOutHook.isLoading,
  };
}
