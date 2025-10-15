import { Logo } from "./Logo"
import { NavItems } from "./NavItems"
import { UserProfile } from "./UserProfile"

export function Sidebar() {
  return (
    <nav className="fixed left-0 top-0 h-screen w-16 sm:w-20 bg-gray-900/95 backdrop-blur-sm flex flex-col items-center py-6 sm:py-8 z-50">
      <Logo />
      <NavItems isCollapsed={true} />
      <UserProfile />
    </nav>
  )
}
