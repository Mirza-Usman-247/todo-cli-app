"use client";

import { useState } from "react";
import Link from "next/link";
import { useSignUp } from "@/hooks/useAuth";

export default function SignUpForm() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [validationError, setValidationError] = useState<string | null>(null);
  const { signUp, isLoading, error } = useSignUp();

  const validatePassword = (pwd: string): string | null => {
    if (pwd.length < 8) {
      return "Password must be at least 8 characters";
    }
    if (!/[A-Z]/.test(pwd)) {
      return "Password must contain an uppercase letter";
    }
    if (!/[a-z]/.test(pwd)) {
      return "Password must contain a lowercase letter";
    }
    if (!/\d/.test(pwd)) {
      return "Password must contain a number";
    }
    return null;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setValidationError(null);

    // Validate password match
    if (password !== confirmPassword) {
      setValidationError("Passwords do not match");
      return;
    }

    // Validate password strength
    const pwdError = validatePassword(password);
    if (pwdError) {
      setValidationError(pwdError);
      return;
    }

    await signUp({ email, password });
  };

  const displayError = validationError || error;

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {displayError && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md text-sm">
          {displayError}
        </div>
      )}

      <div>
        <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
          Email
        </label>
        <input
          id="email"
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          className="input-field"
          placeholder="you@example.com"
          disabled={isLoading}
        />
      </div>

      <div>
        <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-1">
          Password
        </label>
        <input
          id="password"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          minLength={8}
          className="input-field"
          placeholder="Min 8 chars, uppercase, lowercase, number"
          disabled={isLoading}
        />
      </div>

      <div>
        <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-700 mb-1">
          Confirm Password
        </label>
        <input
          id="confirmPassword"
          type="password"
          value={confirmPassword}
          onChange={(e) => setConfirmPassword(e.target.value)}
          required
          className="input-field"
          placeholder="Confirm your password"
          disabled={isLoading}
        />
      </div>

      <button
        type="submit"
        disabled={isLoading}
        className="w-full btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {isLoading ? "Creating account..." : "Create Account"}
      </button>

      <p className="text-center text-sm text-gray-600">
        Already have an account?{" "}
        <Link href="/signin" className="text-blue-600 hover:underline">
          Sign in
        </Link>
      </p>
    </form>
  );
}
