"use client";

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
  return (
    <AuthProvider>
      {children}
      <FloatingChatbot />
    </AuthProvider>
  );
}
