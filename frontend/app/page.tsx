"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { getSession } from "@/services/auth.service";

export default function Home() {
  const [checking, setChecking] = useState(true);
  const router = useRouter();

  useEffect(() => {
    const checkAuth = async () => {
      try {
        console.log("Home: Checking authentication...");
        const session = await getSession();
        console.log("Home: Session result:", session);

        if (session && session.user) {
          // User is authenticated, redirect to dashboard
          console.log("Home: User authenticated, redirecting to dashboard");
          router.push("/dashboard");
        } else {
          // No session, redirect to signin
          console.log("Home: No session, redirecting to signin");
          router.push("/signin");
        }
      } catch (error) {
        // Error means not authenticated, redirect to signin
        console.log("Home: Auth check failed, redirecting to signin");
        router.push("/signin");
      } finally {
        setChecking(false);
      }
    };

    checkAuth();
  }, [router]);

  if (checking) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Checking authentication...</p>
        </div>
      </div>
    );
  }

  return null;
}
