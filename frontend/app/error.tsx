"use client";

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-50">
      <div className="text-center max-w-md">
        <h1 className="text-6xl font-bold text-red-600">Error</h1>
        <p className="mt-4 text-xl text-gray-900">Something went wrong</p>
        <p className="mt-2 text-gray-600">{error.message}</p>
        <div className="mt-6 space-x-4">
          <button
            onClick={reset}
            className="inline-block px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Try Again
          </button>
          <a
            href="/"
            className="inline-block px-6 py-3 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
          >
            Go Home
          </a>
        </div>
      </div>
    </div>
  );
}
