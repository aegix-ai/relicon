"use client"

import { useState, useEffect } from "react"
import Link from "next/link"
import { usePathname } from "next/navigation"
import { LayoutDashboard, FolderOpen, Settings, Plus } from "lucide-react"
import { cn } from "@/lib/utils"
import { SettingsModal } from "@/components/modals/SettingsModal"
import { ProfileModal } from "@/components/modals/ProfileModal"
import Image from "next/image"
import { CubeIcon } from "@/components/icons/CubeIcon"

const navItems = [
  {
    name: "Dashboard",
    href: "/dashboard",
    icon: LayoutDashboard,
  },
  {
    name: "Creative Studio",
    href: "/dashboard/studio",
    icon: Plus,
  },
  {
    name: "Ads Archive",
    href: "/dashboard/ads",
    icon: FolderOpen,
  },
  {
    name: "Chat",
    href: "/dashboard/chat",
    icon: CubeIcon,
  },
]

export function AppSidebar() {
  const pathname = usePathname()
  const [isExpanded, setIsExpanded] = useState(false)
  const [showExpandedLogo, setShowExpandedLogo] = useState(false)
  const [showSettings, setShowSettings] = useState(false)
  const [showProfile, setShowProfile] = useState(false)

  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth >= 1200) {
        setIsExpanded(true)
        setShowExpandedLogo(true)
      } else {
        setIsExpanded(false)
        setShowExpandedLogo(false)
      }
    }

    handleResize()
    window.addEventListener("resize", handleResize)
    return () => window.removeEventListener("resize", handleResize)
  }, [])

  useEffect(() => {
    let timer: NodeJS.Timeout

    if (isExpanded && window.innerWidth >= 1200) {
      setShowExpandedLogo(true)
    } else if (isExpanded && window.innerWidth < 1200) {
      timer = setTimeout(() => {
        setShowExpandedLogo(true)
      }, 300)
    } else if (!isExpanded) {
      setShowExpandedLogo(false)
    }

    return () => clearTimeout(timer)
  }, [isExpanded])

  const handleMouseEnter = () => {
    if (window.innerWidth >= 768 && window.innerWidth < 1200) {
      setIsExpanded(true)
    }
  }

  const handleMouseLeave = () => {
    if (window.innerWidth >= 768 && window.innerWidth < 1200) {
      setIsExpanded(false)
    }
  }

  return (
    <>
      <aside
        className={cn(
          "fixed left-0 top-0 h-screen bg-[#0a0a0a] border-r border-[#1f1f1f] flex flex-col py-4 z-50 transition-all duration-300",
          isExpanded ? "w-64" : "w-16",
        )}
        onMouseEnter={handleMouseEnter}
        onMouseLeave={handleMouseLeave}
      >
        <div className="px-2 mb-6 relative h-12">
          {showExpandedLogo ? (
            <div className="w-full h-12 relative">
              <Image src="/relicon-full-logo.png" alt="Relicon" fill className="object-contain object-left" />
            </div>
          ) : (
            <div className="absolute left-0 w-12 h-12 shrink-0">
              <Image src="/relicon-icon.png" alt="Relicon" fill className="object-contain" />
            </div>
          )}
        </div>

        <nav className="flex-1 px-2 space-y-3">
          {navItems.map((item) => {
            const isActive = pathname === item.href
            const Icon = item.icon

            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "flex items-center gap-3 px-3 py-2 rounded-lg transition-colors text-sm",
                  isActive ? "bg-[#1a1a1a] text-white" : "text-gray-400 hover:text-gray-200 hover:bg-[#161616]",
                )}
                title={item.name}
              >
                <Icon className="w-5 h-5 shrink-0" />
                {isExpanded && (
                  <span className="text-sm whitespace-nowrap overflow-hidden text-ellipsis">{item.name}</span>
                )}
              </Link>
            )
          })}
        </nav>

        <div className="px-2 space-y-3 border-t border-[#1f1f1f] pt-4">
          <button
            onClick={() => setShowSettings(true)}
            className="w-full flex items-center gap-3 px-3 py-2 rounded-lg transition-colors text-sm text-gray-400 hover:text-gray-200 hover:bg-[#161616]"
            title="Settings"
          >
            <Settings className="w-5 h-5 shrink-0" />
            {isExpanded && <span className="text-sm whitespace-nowrap">Settings</span>}
          </button>

          <button
            onClick={() => setShowProfile(true)}
            className="w-full flex items-center gap-3 px-3 py-2 rounded-lg transition-colors text-sm text-gray-400 hover:text-gray-200 hover:bg-[#161616]"
            title="Profile"
          >
            <div className="w-5 h-5 rounded-full shrink-0 relative overflow-hidden bg-gray-800 ring-1 ring-gray-700">
              <Image src="/professional-business-person.png" alt="Profile" fill className="object-cover" sizes="20px" />
            </div>
            {isExpanded && <span className="text-sm whitespace-nowrap">Profile</span>}
          </button>
        </div>
      </aside>

      <SettingsModal isOpen={showSettings} onClose={() => setShowSettings(false)} />
      <ProfileModal isOpen={showProfile} onClose={() => setShowProfile(false)} />
    </>
  )
}
