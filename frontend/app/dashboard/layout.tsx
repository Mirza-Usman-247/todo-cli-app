"use client";

import { useSignOut } from "@/hooks/useAuth";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { signOut, isLoading } = useSignOut();

  return (
    <div className="min-h-screen bg-gray-100">
      <nav className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-14 items-center">
            <h1 className="text-lg font-semibold text-gray-900">Todo App</h1>
            <button
              onClick={signOut}
              disabled={isLoading}
              className="text-sm text-gray-600 hover:text-gray-900 disabled:opacity-50 font-medium"
            >
              {isLoading ? "Signing out..." : "Sign Out"}
            </button>
          </div>
        </div>
      </nav>
      <main className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {children}
      </main>
    </div>
  );
}
