"use client";

import { useSignOut } from "@/hooks/useAuth";

export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { signOut, isLoading } = useSignOut();

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16 items-center">
            <h1 className="text-xl font-bold">Todo App</h1>
            <button
              onClick={signOut}
              disabled={isLoading}
              className="text-gray-600 hover:text-gray-900 disabled:opacity-50"
            >
              {isLoading ? "Signing out..." : "Sign Out"}
            </button>
          </div>
        </div>
      </nav>
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {children}
      </main>
    </div>
  );
}
