import { Grid3X3, Lightbulb, Music2, Coffee, Sun, Thermometer, Shield, Bell, Settings } from "lucide-react"

const navItems = [
  { icon: Grid3X3, label: "Dashboard", isActive: true },
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

export function Sidebar() {
  return (
    <nav className="fixed left-0 top-0 h-screen w-20 bg-gray-900 flex flex-col items-center py-8 overflow-y-auto scrollbar-hide">
      <div className="text-xl font-light text-white tracking-tight mb-4 flex-shrink-0">sync</div>

      <div className="flex flex-col items-center space-y-6 flex-1 min-h-0 overflow-y-auto scrollbar-hide">
        <div className="flex flex-col items-center space-y-6">
          {navItems.map(({ icon: Icon, label, isActive }) => (
            <button
              key={label}
              className={`w-12 h-12 flex items-center justify-center rounded-xl transition-colors flex-shrink-0 ${
                isActive ? "bg-pink-300 text-gray-900" : "text-gray-400 hover:text-white hover:bg-gray-800/50"
              }`}
              title={label}
            >
              <Icon size={20} strokeWidth={1.5} />
            </button>
          ))}
        </div>
      </div>

      <div className="flex flex-col items-center space-y-6 mb-4 flex-shrink-0">
        {bottomItems.map(({ icon: Icon, label }) => (
          <button
            key={label}
            className="w-12 h-12 flex items-center justify-center rounded-xl text-gray-400 hover:text-white hover:bg-gray-800/50 transition-colors"
            title={label}
          >
            <Icon size={20} strokeWidth={1.5} />
          </button>
        ))}
      </div>

      <div className="relative w-16 h-16 rounded-full border-2 border-red-500 flex-shrink-0 overflow-hidden bg-gray-800">
        <img
          src="/images/design-mode/photo-1494790108377-be9c29b29330.jpeg"
          alt="User Profile"
          className="w-full h-full object-cover rounded-full"
          onError={(e) => {
            // Fallback if image fails to load
            e.currentTarget.style.display = "none"
            e.currentTarget.parentElement!.innerHTML =
              '<div class="w-full h-full bg-gray-700 rounded-full flex items-center justify-center text-white text-sm font-medium">A</div>'
          }}
        />
      </div>
    </nav>
  )
}
