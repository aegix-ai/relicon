import type React from "react"
import type { Metadata } from "next"
import { Inter } from "next/font/google"
import "./globals.css"
import { AppSidebar } from "@/components/layout/AppSidebar"
import { ChatPanel } from "@/components/chat/ChatPanel"

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-sans",
})

export const metadata: Metadata = {
  title: "Relicon - AI Ad Director",
  description: "AI-powered advertising dashboard",
  generator: "v0.app",
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en" className={inter.variable} suppressHydrationWarning>
      <body className="bg-[#121212] text-gray-200 antialiased font-sans" suppressHydrationWarning>
        <AppSidebar />
        <main className="ml-16 md:ml-16 xl:ml-64 min-h-screen">{children}</main>
        <ChatPanel />
      </body>
    </html>
  )
}
