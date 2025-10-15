"use client"

import { HomeIcon, ChefHat, Bath, BedDouble, TreePine, Sun } from "lucide-react"

const rooms = [
  { id: "Living Room", icon: HomeIcon },
  { id: "Kitchen", icon: ChefHat },
  { id: "Bathroom", icon: Bath },
  { id: "Bedroom", icon: BedDouble },
  { id: "Backyard", icon: TreePine },
  { id: "Terrace", icon: Sun },
] as const

export type Room = (typeof rooms)[number]["id"]

interface RoomSelectorProps {
  selectedRoom: Room
  onRoomChange: (room: Room) => void
}

export function RoomSelector({ selectedRoom, onRoomChange }: RoomSelectorProps) {
  return (
    <div className="flex gap-1.5 overflow-x-auto w-full scrollbar-hide">
      {rooms.map(({ id, icon: Icon }) => (
        <button
          key={id}
          onClick={() => onRoomChange(id)}
          className={`min-w-[42px] h-9 px-2.5 md:px-3.5 py-1.5 rounded-full text-xs whitespace-nowrap transition-colors flex items-center gap-1.5 flex-shrink-0 touch-manipulation ${
            id === selectedRoom ? "bg-white text-gray-900" : "bg-gray-800 text-gray-400 hover:bg-gray-700"
          }`}
        >
          <Icon size={16} className="flex-shrink-0" />
          <span className="hidden sm:inline">{id}</span>
        </button>
      ))}
    </div>
  )
}
