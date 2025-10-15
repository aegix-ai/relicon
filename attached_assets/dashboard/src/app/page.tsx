"use client"

import { useState } from "react"
import { Sidebar } from "@/src/components/layout/Sidebar"
import { WeatherWidget } from "@/src/components/weather/WeatherWidget"
import { EnergyPanel } from "@/src/components/energy/EnergyPanel"
import { RoomSelector, type Room } from "@/src/components/header/RoomSelector"
import { LivingRoom } from "@/src/components/rooms/LivingRoom"
import { Kitchen } from "@/src/components/rooms/Kitchen"
import { Bathroom } from "@/src/components/rooms/Bathroom"
import { Bedroom } from "@/src/components/rooms/Bedroom"
import { Backyard } from "@/src/components/rooms/Backyard"
import { Terrace } from "@/src/components/rooms/Terrace"

const weatherData = {
  temperature: 16,
  windSpeed: 30,
  windSpeedChange: 6,
  pressure: 720,
  pressureChange: -20,
  rainChance: 60,
}

export default function Page() {
  const [selectedRoom, setSelectedRoom] = useState<Room>("Living Room")

  const renderRoom = () => {
    switch (selectedRoom) {
      case "Living Room":
        return <LivingRoom />
      case "Kitchen":
        return <Kitchen />
      case "Bathroom":
        return <Bathroom />
      case "Bedroom":
        return <Bedroom />
      case "Backyard":
        return <Backyard />
      case "Terrace":
        return <Terrace />
    }
  }

  return (
    <div className="h-screen bg-gray-950 text-white flex overflow-hidden">
      <div className="hidden lg:block">
        <Sidebar />
      </div>

      <main className="flex-1 h-screen p-3 sm:p-4 md:p-6 lg:p-8 lg:ml-20 overflow-y-auto scrollbar-hide">
        <div className="max-w-7xl mx-auto space-y-4 sm:space-y-6 md:space-y-8">
          <div className="flex flex-col xl:grid xl:grid-cols-12 xl:gap-8">
            {/* Left Column - Weather and Energy */}
            <div className="xl:col-span-3 space-y-4 md:space-y-6 xl:space-y-8 xl:h-[calc(100vh-4rem)]">
              <WeatherWidget data={weatherData} />
              <div className="flex-grow">
                <EnergyPanel />
              </div>
            </div>

            {/* Main Content */}
            <div className="xl:col-span-9 space-y-4 sm:space-y-6 md:space-y-8">
              <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4 mt-6 xl:mt-0">
                <h1 className="text-2xl sm:text-3xl font-bold lg:flex-shrink-0">Hi Ann!</h1>
                <div className="lg:flex-1 lg:max-w-2xl">
                  <RoomSelector selectedRoom={selectedRoom} onRoomChange={setSelectedRoom} />
                </div>
              </div>

              {renderRoom()}
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
