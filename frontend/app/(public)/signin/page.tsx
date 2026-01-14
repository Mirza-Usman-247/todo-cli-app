"use client";

import SignInForm from "@/components/auth/SignInForm";

export default function SignInPage() {
  return (
    <div className="space-y-6">
      <div className="text-center">
        <h1 className="text-2xl font-bold">Sign In</h1>
        <p className="text-gray-600 mt-2">Welcome back to Todo App</p>
      </div>
      <div className="bg-white p-6 rounded-lg shadow-md">
        <SignInForm />
      </div>
    </div>
  );
}
