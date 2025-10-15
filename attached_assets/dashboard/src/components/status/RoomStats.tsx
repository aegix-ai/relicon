import { Thermometer, Droplets, Zap, PieChart } from "lucide-react"

interface RoomStatsProps {
  temperature: number
  humidity: number
  power: number
  efficiency: number
}

export function RoomStats({ temperature, humidity, power, efficiency }: RoomStatsProps) {
  return (
    <div className="absolute top-3 sm:top-4 right-3 sm:right-4 flex flex-wrap gap-1 sm:gap-2 max-w-[calc(100%-6rem)]">
      <div className="bg-gray-900/80 backdrop-blur px-2 sm:px-3 py-1 sm:py-1.5 rounded-full text-xs sm:text-sm flex items-center gap-1 sm:gap-2">
        <Thermometer size={12} className="text-red-400 sm:w-3.5 sm:h-3.5" />
        <span>{temperature}°C</span>
      </div>
      <div className="bg-gray-900/80 backdrop-blur px-2 sm:px-3 py-1 sm:py-1.5 rounded-full text-xs sm:text-sm flex items-center gap-1 sm:gap-2">
        <Droplets size={12} className="text-blue-400 sm:w-3.5 sm:h-3.5" />
        <span>{humidity}%</span>
      </div>
      <div className="bg-gray-900/80 backdrop-blur px-2 sm:px-3 py-1 sm:py-1.5 rounded-full text-xs sm:text-sm flex items-center gap-1 sm:gap-2">
        <Zap size={12} className="text-yellow-400 sm:w-3.5 sm:h-3.5" />
        <span>{power}W</span>
      </div>
      <div className="bg-gray-900/80 backdrop-blur px-2 sm:px-3 py-1 sm:py-1.5 rounded-full text-xs sm:text-sm flex items-center gap-1 sm:gap-2">
        <PieChart size={12} className="text-green-400 sm:w-3.5 sm:h-3.5" />
        <span>{efficiency}%</span>
      </div>
    </div>
  )
}
