"use client";

import SignUpForm from "@/components/auth/SignUpForm";

export default function SignUpPage() {
  return (
    <div className="space-y-5">
      <div className="text-center">
        <h1 className="text-2xl font-semibold text-gray-900">Create Account</h1>
        <p className="text-gray-600 mt-1.5">Get started with Todo App</p>
      </div>
      <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
        <SignUpForm />
      </div>
    </div>
  );
}
