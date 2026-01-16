"use client";

import { createContext, useContext, useEffect, useState, ReactNode } from "react";
import { getSession } from "@/services/auth.service";
import { User } from "@/types/user";

interface AuthContextType {
  user: User | null;
  loading: boolean;
  isAuthenticated: boolean;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  const refreshUser = async () => {
    // Don't run during SSR/build
    if (typeof window === 'undefined') {
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      console.log("AuthProvider: Fetching session...");
      const session = await getSession();
      console.log("AuthProvider: Session response:", session);
      if (session && session.user) {
        setUser(session.user);
        console.log("AuthProvider: User authenticated:", session.user);
      } else {
        setUser(null);
        console.log("AuthProvider: No user in session");
      }
    } catch (error) {
      console.error("AuthProvider: Error getting session:", error);
      setUser(null);
    } finally {
      setLoading(false);
      console.log("AuthProvider: Loading complete, user:", user);
    }
  };

  useEffect(() => {
    refreshUser();
  }, []);

  const value = {
    user,
    loading,
    isAuthenticated: !!user,
    refreshUser,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuthContext() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuthContext must be used within an AuthProvider");
  }
  return context;
}