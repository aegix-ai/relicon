import { NavItem } from "./NavItem"
import { Grid3X3, Lightbulb, Music2, Coffee, Sun, Thermometer, Shield, Bell, Settings } from "lucide-react"

const navItems = [
  { icon: Grid3X3, label: "Dashboard", isActive: true, className: "bg-pink-300 text-gray-900" },
  { icon: Lightbulb, label: "Lighting" },
  { icon: Music2, label: "Media" },
  { icon: Coffee, label: "Kitchen" },
  { icon: Sun, label: "Environment" },
  { icon: Thermometer, label: "Temperature" },
  { icon: Shield, label: "Security" },
]

const bottomItems = [
  { icon: Bell, label: "Notifications" },
  { icon: Settings, label: "Settings" },
]

interface NavItemsProps {
  isCollapsed: boolean
}

export function NavItems({ isCollapsed }: NavItemsProps) {
  return (
    <div className="flex-1 flex flex-col items-center justify-between">
      <div className="flex flex-col items-center space-y-6 sm:space-y-8 mt-4">
        {navItems.map((item) => (
          <NavItem
            key={item.label}
            icon={item.icon}
            label={item.label}
            isActive={item.isActive}
            isCollapsed={isCollapsed}
            className={item.className}
          />
        ))}
      </div>

      <div className="flex flex-col items-center space-y-6 sm:space-y-8 mb-4">
        {bottomItems.map((item) => (
          <NavItem key={item.label} icon={item.icon} label={item.label} isCollapsed={isCollapsed} />
        ))}
      </div>
    </div>
  )
}
