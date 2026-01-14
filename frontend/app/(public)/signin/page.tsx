"use client";

import SignInForm from "@/components/auth/SignInForm";

export default function SignInPage() {
  return (
    <div className="space-y-5">
      <div className="text-center">
        <h1 className="text-2xl font-semibold text-gray-900">Sign In</h1>
        <p className="text-gray-600 mt-1.5">Welcome back to Todo App</p>
      </div>
      <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
        <SignInForm />
      </div>
    </div>
  );
}
