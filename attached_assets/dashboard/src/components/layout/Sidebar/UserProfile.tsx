export function UserProfile() {
  return (
    <div className="w-10 h-10 sm:w-12 sm:h-12 rounded-full overflow-hidden border-2 border-red-500">
      <img
        src="https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=100&h=100&fit=crop&crop=faces"
        alt="User Profile"
        className="w-full h-full object-cover"
      />
    </div>
  )
}
