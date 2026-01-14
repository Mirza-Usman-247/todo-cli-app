"use client";

import SignUpForm from "@/components/auth/SignUpForm";

export default function SignUpPage() {
  return (
    <div className="space-y-6">
      <div className="text-center">
        <h1 className="text-2xl font-bold">Create Account</h1>
        <p className="text-gray-600 mt-2">Get started with Todo App</p>
      </div>
      <div className="bg-white p-6 rounded-lg shadow-md">
        <SignUpForm />
      </div>
    </div>
  );
}
