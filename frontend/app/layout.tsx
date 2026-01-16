import type { Metadata } from "next";
import "./globals.css";
import { AuthProvider } from "@/components/AuthProvider";
import dynamic from "next/dynamic";

const FloatingChatbot = dynamic(() => import("@/components/FloatingChatbot"), {
  ssr: false,
});

export const metadata: Metadata = {
  title: "Todo App",
  description: "Phase 2 Todo Web Application",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">
        <AuthProvider>
          {children}
          <FloatingChatbot />
        </AuthProvider>
      </body>
    </html>
  );
}
