import type { LucideIcon } from "lucide-react"

interface NavItemProps {
  icon: LucideIcon
  label: string
  isActive?: boolean
  isCollapsed: boolean
  className?: string
}

export function NavItem({ icon: Icon, label, isActive, isCollapsed, className = "" }: NavItemProps) {
  return (
    <button
      className={`w-10 h-10 sm:w-12 sm:h-12 flex items-center justify-center rounded-xl transition-colors relative group ${
        isActive ? className || "text-gray-900 bg-pink-300" : "text-gray-400 hover:text-white hover:bg-gray-800/50"
      }`}
      title={isCollapsed ? label : undefined}
    >
      <Icon size={isActive ? 20 : 18} strokeWidth={1.5} />
      {isCollapsed && (
        <div className="absolute left-14 px-2 py-1 bg-gray-800 text-white text-sm rounded opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all whitespace-nowrap">
          {label}
        </div>
      )}
    </button>
  )
}
