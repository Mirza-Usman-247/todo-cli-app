"use client";

import { useState, useEffect } from "react";
import dynamic from "next/dynamic";
import { AuthProvider } from "@/components/AuthProvider";

const FloatingChatbot = dynamic(() => import("@/components/FloatingChatbot"), {
  ssr: false,
});

export default function ClientLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  return (
    <AuthProvider>
      {children}
      {mounted && <FloatingChatbot />}
    </AuthProvider>
  );
}
