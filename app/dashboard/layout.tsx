import type React from "react"
import type { Metadata } from "next"
import { AppSidebar } from "@/components/layout/AppSidebar"
import { ChatPanel } from "@/components/chat/ChatPanel"
import { ProtectedRoute } from "@/components/auth/ProtectedRoute"

export const metadata: Metadata = {
  title: "Relicon - AI Ad Director",
  description: "AI-powered advertising dashboard",
}

export default function DashboardLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <ProtectedRoute>
      <div className="bg-[#121212] text-gray-200 antialiased font-sans min-h-screen">
        <AppSidebar />
        <main className="ml-16 md:ml-16 xl:ml-64 min-h-screen">{children}</main>
        <ChatPanel />
      </div>
    </ProtectedRoute>
  )
}
