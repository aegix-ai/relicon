"use client"

import { useState } from "react"
import { LayoutDashboard, Brain, BarChart3, Link } from "lucide-react"
import DashboardPanel from "./dashboard/dashboard-panel"
import AICreationPanel from "./dashboard/ai-creation-panel"
import PerformancePanel from "./dashboard/performance-panel"
import ThemeToggle from "./theme-toggle"
import ConnectAccountsPanel from "./dashboard/connect-accounts-panel"
import { ThemeProvider } from "@/components/theme-provider"

interface DashboardProps {
  onBackToHome: () => void
}

const tabs = [
  { id: "dashboard", label: "Dashboard", icon: LayoutDashboard },
  { id: "ad-engine", label: "Ad Engine", icon: Brain },
  { id: "performance", label: "Performance", icon: BarChart3 },
  { id: "connect", label: "Connect Accounts", icon: Link },
]

export default function Dashboard({ onBackToHome }: DashboardProps) {
  const [activeTab, setActiveTab] = useState("dashboard")

  const renderActivePanel = () => {
    switch (activeTab) {
      case "dashboard":
        return <DashboardPanel />
      case "ad-engine":
        return <AICreationPanel />
      case "performance":
        return <PerformancePanel />
      case "connect":
        return <ConnectAccountsPanel />
      default:
        return <DashboardPanel />
    }
  }

  return (
    <ThemeProvider attribute="class" defaultTheme="dark" enableSystem={true}>
      <div className="min-h-screen bg-gray-900 dark:bg-gray-900 light:bg-gray-50 text-white dark:text-white light:text-gray-900">
        {/* Header */}
        <header className="bg-gray-800 dark:bg-gray-800 light:bg-white border-b border-gray-700 dark:border-gray-700 light:border-gray-200 px-6 py-4">
          <div className="flex items-center justify-between">
            <div
              className="flex items-center space-x-4 cursor-pointer hover:opacity-80 transition-opacity"
              onClick={onBackToHome}
            >
              <img src="/reelforge-icon.png" alt="ReelForge Logo" className="w-10 h-10" />
              <h1 className="text-2xl font-bold text-white dark:text-white light:text-gray-900">
                ReelForge AI Dashboard
              </h1>
            </div>
            <ThemeToggle />
          </div>
        </header>

        {/* Navigation Tabs */}
        <nav className="bg-gray-800 dark:bg-gray-800 light:bg-gray-100 border-b border-gray-700 dark:border-gray-700 light:border-gray-200 px-6">
          <div className="flex space-x-8">
            {tabs.map((tab) => {
              const Icon = tab.icon
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center space-x-2 py-4 px-2 border-b-2 transition-all duration-300 ${
                    activeTab === tab.id
                      ? "border-[#FF5C00] text-[#FF5C00]"
                      : "border-transparent text-gray-400 dark:text-gray-400 light:text-gray-600 hover:text-gray-300 dark:hover:text-gray-300 light:hover:text-gray-800"
                  }`}
                >
                  <Icon className="w-5 h-5" />
                  <span className="font-medium">{tab.label}</span>
                </button>
              )
            })}
          </div>
        </nav>

        {/* Panel Content */}
        <div className="transition-all duration-500 ease-in-out">{renderActivePanel()}</div>
      </div>
    </ThemeProvider>
  )
}
